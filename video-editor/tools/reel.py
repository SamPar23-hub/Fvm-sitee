#!/usr/bin/env python3
"""
reel.py — the automated reel pipeline.

  python3 tools/reel.py RAW.mp4 --style B
  python3 tools/reel.py RAW.mp4 --style A --title "Realtors turn one listing into 6 reels"

Steps: transcribe (word timestamps) -> rough cut (drop silences/fillers)
-> grade -> captions (per style) -> audio polish -> loudness -> 1080x1920 export.

Everything a style needs lives in presets/style-<x>.json. Taste notes for
Claude live next to it in presets/style-<x>.md.

Outputs go to work/<clip-name>/ :
  words.json      word timestamps of the raw clip (cached; edit + rerun to fix words)
  cutlist.json    kept segments in source time (used for Final Cut / FCPXML)
  captions.ass    styled captions on the cut timeline
  <name>_style<X>.mp4  final render
"""
import argparse, json, os, re, subprocess, sys, shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FONTS = ROOT / "assets" / "fonts"
FILLERS = {"um", "uh", "erm", "uhm", "hmm", "mm"}


def sh(cmd, **kw):
    r = subprocess.run(cmd, capture_output=True, text=True, **kw)
    if r.returncode != 0:
        sys.exit(f"command failed: {' '.join(map(str, cmd))}\n{r.stderr[-3000:]}")
    return r


def probe(path):
    out = sh(["ffprobe", "-v", "error", "-show_entries", "format=duration:stream=codec_type,width,height,r_frame_rate",
              "-of", "json", str(path)]).stdout
    j = json.loads(out)
    v = next(s for s in j["streams"] if s["codec_type"] == "video")
    num, den = map(int, v["r_frame_rate"].split("/"))
    return {"dur": float(j["format"]["duration"]), "w": v["width"], "h": v["height"], "fps": num / den,
            "audio": any(s["codec_type"] == "audio" for s in j["streams"])}


# ---------------------------------------------------------------- transcribe
def transcribe(src, work, model):
    cache = work / "words.json"
    if cache.exists():
        return json.loads(cache.read_text())
    pcm = work / "audio16k.f32"
    sh(["ffmpeg", "-v", "error", "-y", "-i", str(src), "-ac", "1", "-ar", "16000", "-f", "f32le", str(pcm)])
    import numpy as np
    audio = np.fromfile(pcm, dtype=np.float32)
    words = None
    try:  # WhisperX: best word timing (forced alignment)
        import whisperx
        dev = "cpu"
        m = whisperx.load_model(model, dev, compute_type="int8", language="en")
        res = m.transcribe(audio, batch_size=8, language="en")
        am, meta = whisperx.load_align_model(language_code="en", device=dev)
        res = whisperx.align(res["segments"], am, meta, audio, dev)
        words = [{"w": w["word"].strip(), "s": round(w["start"], 3), "e": round(w["end"], 3)}
                 for w in res["word_segments"] if "start" in w]
        print("transcribed with WhisperX")
    except ImportError:
        from faster_whisper import WhisperModel
        m = WhisperModel(model, device="cpu", compute_type="int8")
        segs, _ = m.transcribe(audio, word_timestamps=True, language="en")
        words = [{"w": w.word.strip(), "s": round(w.start, 3), "e": round(w.end, 3)} for s in segs for w in s.words]
        print("transcribed with faster-whisper (install whisperx for tighter word timing)")
    pcm.unlink(missing_ok=True)
    cache.write_text(json.dumps(words, indent=1))
    return words


# ---------------------------------------------------------------- rough cut
def plan_cuts(words, dur, cut):
    """Group words into kept segments; any gap > max_pause becomes a cut."""
    ws = [w for w in words if not (cut.get("drop_fillers", True) and re.sub(r"\W", "", w["w"].lower()) in FILLERS)]
    if not ws:
        return [(0.0, dur)], []
    segs, cur = [], [ws[0]]
    for w in ws[1:]:
        if w["s"] - cur[-1]["e"] > cut["max_pause"]:
            segs.append(cur); cur = [w]
        else:
            cur.append(w)
    segs.append(cur)
    out = []
    for g in segs:
        s = max(0.0, g[0]["s"] - cut["pad_in"])
        e = min(dur, g[-1]["e"] + cut["pad_out"])
        if out and s <= out[-1][1]:
            out[-1] = (out[-1][0], e)
        else:
            out.append((s, e))
    return out, ws


def remap(words, segs):
    """Move word times from source time to cut-timeline time."""
    out, offset = [], []
    t = 0.0
    for s, e in segs:
        offset.append((s, e, t)); t += e - s
    for w in words:
        for s, e, o in offset:
            if s <= w["s"] < e:
                out.append({**w, "s": o + w["s"] - s, "e": o + min(w["e"], e) - s}); break
    return out, t


# ---------------------------------------------------------------- captions (ASS)
def ass_time(t):
    t = max(0, t); h = int(t // 3600); m = int(t % 3600 // 60); s = t % 60
    return f"{h}:{m:02d}:{s:05.2f}"


def ass_color(hexrgb, alpha=0):
    hexrgb = hexrgb.lstrip("#"); r, g, b = hexrgb[0:2], hexrgb[2:4], hexrgb[4:6]
    return f"&H{alpha:02X}{b}{g}{r}".upper()


def clean(w, upper):
    w = w.strip()
    w = re.sub(r"[.,!?;:]+$", "", w) if True else w
    return w.upper() if upper else w


def groups(words, lo, hi):
    """Split words into caption chunks of lo..hi words that follow the phrasing.
    1) split into phrases at punctuation, 2) glue phrases shorter than `lo` onto a
    neighbour (backward if it ends a sentence, e.g. "bro."; forward otherwise, e.g. "Yo,"),
    3) cut long phrases into balanced chunks so there are no one-word orphans."""
    phrases, cur = [], []
    for w in words:
        cur.append(w)
        if re.search(r"[.,!?;:]$", w["w"]):
            phrases.append(cur); cur = []
    if cur:
        phrases.append(cur)
    merged = []
    carry = []
    for p in phrases:
        p = carry + p; carry = []
        if len(p) < lo:
            if re.search(r"[.!?]$", p[-1]["w"]) and merged and not re.search(r"[.!?]$", merged[-1][-1]["w"]):
                merged[-1] += p
            else:
                carry = p
            continue
        merged.append(p)
    if carry:
        if merged:
            merged[-1] += carry
        else:
            merged.append(carry)
    out = []
    for p in merged:
        n = -(-len(p) // hi)  # ceil
        size = -(-len(p) // n)
        for i in range(0, len(p), size):
            out.append(p[i:i + size])
    return out


def build_ass(words, total, cap, title, W=1080, H=1920):
    st = cap["style"]
    upper = cap.get("uppercase", False)
    styles = [("Cap", st)]
    if title:
        styles.append(("Title", cap["title_style"]))
    wm = cap.get("watermark")
    if wm:
        styles.append(("Mark", {"font": wm.get("font", "Barlow Condensed SemiBold"), "size": wm.get("size", 26),
                                "shadow": 1, "shadow_alpha": 140, "align": 5, "spacing": 1}))
    lines = ["[Script Info]", "ScriptType: v4.00+", f"PlayResX: {W}", f"PlayResY: {H}", "WrapStyle: 0",
             "ScaledBorderAndShadow: yes", "", "[V4+ Styles]",
             "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, "
             "Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, "
             "MarginR, MarginV, Encoding"]
    for name, s in styles:
        lines.append(
            f"Style: {name},{s['font']},{s['size']},{ass_color(s.get('color', '#FFFFFF'))},&H000000FF,"
            f"{ass_color(s.get('outline_color', '#000000'))},{ass_color(s.get('shadow_color', '#000000'), s.get('shadow_alpha', 96))},"
            f"{-1 if s.get('bold') else 0},{-1 if s.get('italic') else 0},0,0,100,100,{s.get('spacing', 0)},0,1,"
            f"{s.get('outline', 0)},{s.get('shadow', 0)},{s.get('align', 2)},60,60,{s.get('margin_v', 0)},1")
    lines += ["", "[Events]", "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"]
    pos = f"\\pos({W // 2},{int(st['y'] * H)})"
    pop = cap.get("pop", True)
    anim = "\\fscx92\\fscy92\\t(0,90,\\fscx100\\fscy100)" if pop else ""
    fade = "\\fad(60,0)" if cap.get("fade", True) else ""
    mode = cap["mode"]
    ev = []
    if mode == "chunk":  # 2–5 words at a time (styles A, B)
        gs = groups(words, cap["min_words"], cap["max_words"])
        for i, g in enumerate(gs):
            s = g[0]["s"]; e = gs[i + 1][0]["s"] if i + 1 < len(gs) and gs[i + 1][0]["s"] - g[-1]["e"] < 0.6 else g[-1]["e"] + 0.15
            txt = " ".join(clean(w["w"], upper) for w in g)
            ev.append((s, e, "Cap", f"{{{pos}{anim}{fade}}}{txt}"))
    elif mode == "build":  # words accumulate, wrap, then clear (style C)
        for g in groups(words, cap["min_words"], cap["max_words"]):
            end = g[-1]["e"] + 0.2
            for j, w in enumerate(g):
                s = w["s"]; e = g[j + 1]["s"] if j + 1 < len(g) else end
                shown = wrap([clean(x["w"], upper) for x in g[: j + 1]], cap.get("wrap", 18))
                ev.append((s, e, "Cap", f"{{{pos}}}{shown}"))
    elif mode == "stack":  # big stacked caps, 1–4 words build vertically (style D)
        for g in groups(words, 1, cap["max_words"]):
            end = g[-1]["e"] + 0.15
            for j, w in enumerate(g):
                s = w["s"]; e = g[j + 1]["s"] if j + 1 < len(g) else end
                shown = "\\N".join(clean(x["w"], True) for x in g[: j + 1])
                ev.append((s, e, "Cap", f"{{{pos}}}{shown}"))
    elif mode == "single":  # one word at a time (style E)
        for i, w in enumerate(words):
            s = w["s"]; e = min(words[i + 1]["s"], w["e"] + 0.25) if i + 1 < len(words) else w["e"] + 0.3
            ev.append((s, e, "Cap", f"{{{pos}\\alpha&H70&\\t(0,80,\\alpha&H00&)}}{clean(w['w'], upper)}"))
    if title:
        ts = cap["title_style"]
        tpos = f"\\pos({W // 2},{int(ts['y'] * H)})"
        ev.append((0, min(total, cap.get("title_secs", 4.0)), "Title", f"{{{tpos}\\fad(150,200)}}{title}"))
    if wm:  # Instagram glyph + @handle, whole video (style E)
        x, y = int(wm["x"] * W), int(wm["y"] * H)
        k = wm.get("icon", 40) / 34
        box = "m 8 0 l 26 0 b 31 0 34 3 34 8 l 34 26 b 34 31 31 34 26 34 l 8 34 b 3 34 0 31 0 26 l 0 8 b 0 3 3 0 8 0"
        ring = "m 17 9 b 21.4 9 25 12.6 25 17 b 25 21.4 21.4 25 17 25 b 12.6 25 9 21.4 9 17 b 9 12.6 12.6 9 17 9"
        dot = "m 26 6 b 27.4 6 28 6.6 28 8 b 28 9.4 27.4 10 26 10 b 24.6 10 24 9.4 24 8 b 24 6.6 24.6 6 26 6"
        sc = f"\\fscx{int(k * 100)}\\fscy{int(k * 100)}"
        icon = f"\\an5\\pos({x},{y}){sc}\\1a&HFF&\\3c&HFFFFFF&\\bord2.2\\shad0"
        ev.append((0, total, "Mark", f"{{{icon}\\p1}}{box} {ring}{{\\p0}}"))
        ev.append((0, total, "Mark", f"{{\\an5\\pos({x},{y}){sc}\\bord0\\shad0\\p1}}{dot}{{\\p0}}"))
        ev.append((0, total, "Mark", f"{{\\an5\\pos({x},{y + int(wm.get('icon', 40) * 0.95)})}}{wm['handle']}"))
    for s, e, sty, txt in ev:
        lines.append(f"Dialogue: 0,{ass_time(s)},{ass_time(min(e, total))},{sty},,0,0,0,,{txt}")
    return "\n".join(lines) + "\n"


def wrap(ws, n):
    out, line = [], ""
    for w in ws:
        if line and len(line) + 1 + len(w) > n:
            out.append(line); line = w
        else:
            line = f"{line} {w}".strip()
    out.append(line)
    return "\\N".join(out)


# ---------------------------------------------------------------- render
def render(src, info, segs, preset, ass_path, out, work):
    W, H = 1080, 1920
    v = preset["video"]
    punch = v.get("punch_in", [1.0])
    grade = preset["grade"]["ffmpeg"]
    a = preset["audio"]
    parts, n = [], len(segs)
    for i, (s, e) in enumerate(segs):
        z = punch[i % len(punch)]
        parts.append(
            f"[0:v]trim={s:.3f}:{e:.3f},setpts=PTS-STARTPTS,"
            f"scale={W}*{z}:{H}*{z}:force_original_aspect_ratio=increase,"
            f"crop={W}:{H}:(iw-{W})/2:(ih-{H})*{v.get('crop_y', 0.35)},setsar=1,fps={v.get('fps', 30)}[v{i}];"
            f"[0:a]atrim={s:.3f}:{e:.3f},asetpts=PTS-STARTPTS,"
            f"afade=t=in:d=0.01,afade=t=out:st={max(0, e - s - 0.012):.3f}:d=0.012[a{i}];")
    concat = "".join(f"[v{i}][a{i}]" for i in range(n)) + f"concat=n={n}:v=1:a=1[vc][ac];"
    fontsdir = str(FONTS)
    post = f",{v['post']}" if v.get("post") else ""  # e.g. letterbox bars for style D
    vchain = f"[vc]{grade}{post},ass={ass_path.name}:fontsdir={fontsdir},format=yuv420p[vo];"
    achain = f"[ac]{a['chain']}[ao]"
    fc = "".join(parts) + concat + vchain + achain
    tmp = work / "pre_loudnorm.mp4"
    sh(["ffmpeg", "-v", "error", "-y", "-i", str(src), "-filter_complex", fc, "-map", "[vo]", "-map", "[ao]",
        "-c:v", "libx264", "-preset", "slow", "-crf", "17", "-profile:v", "high", "-c:a", "pcm_s16le",
        "-movflags", "+faststart", str(tmp.with_suffix(".mov"))], cwd=work)
    tmp = tmp.with_suffix(".mov")
    # two-pass loudness to the style's target (reels: -14 LUFS, -1 dBTP)
    L = a["lufs"]
    m = sh(["ffmpeg", "-i", str(tmp), "-af", f"loudnorm=I={L}:TP=-1:LRA=9:print_format=json", "-f", "null", "-"]).stderr
    j = json.loads(m[m.rfind("{"):m.rfind("}") + 1])
    ln = (f"loudnorm=I={L}:TP=-1:LRA=9:measured_I={j['input_i']}:measured_TP={j['input_tp']}:"
          f"measured_LRA={j['input_lra']}:measured_thresh={j['input_thresh']}:offset={j['target_offset']}:linear=true")
    sh(["ffmpeg", "-v", "error", "-y", "-i", str(tmp), "-af", ln + ",aresample=48000", "-c:v", "copy",
        "-c:a", "aac", "-b:a", "320k", "-movflags", "+faststart", str(out)])
    tmp.unlink(missing_ok=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("input")
    ap.add_argument("--style", required=True, help="A, B, C, D or E")
    ap.add_argument("--title", help="hook title shown at the top (styles A and E)")
    ap.add_argument("--model", default="large-v3")
    ap.add_argument("--out", help="output folder (default: work/<name>)")
    args = ap.parse_args()

    src = Path(args.input).resolve()
    preset = json.loads((ROOT / "presets" / f"style-{args.style.lower()}.json").read_text())
    work = Path(args.out).resolve() if args.out else ROOT / "work" / src.stem
    work.mkdir(parents=True, exist_ok=True)
    info = probe(src)

    words = transcribe(src, work, args.model)
    segs, kept_words = plan_cuts(words, info["dur"], preset["cut"])
    (work / "cutlist.json").write_text(json.dumps({"source": str(src), "fps": info["fps"],
                                                   "segments": [{"in": round(s, 3), "out": round(e, 3)} for s, e in segs]}, indent=1))
    tw, total = remap(kept_words, segs)
    title = args.title or (None if not preset["captions"].get("title_style") else None)
    ass = work / "captions.ass"
    ass.write_text(build_ass(tw, total, preset["captions"], title))
    out = work / f"{src.stem}_style{args.style.upper()}.mp4"
    render(src, info, segs, preset, ass, out, work)
    print(f"raw {info['dur']:.1f}s -> cut {total:.1f}s in {len(segs)} segments")
    print(f"done: {out}")


if __name__ == "__main__":
    main()
