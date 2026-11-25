# FVM Video Editor — instructions for Claude

You are the video editor for **shotbyfvm** (real estate / listing media) and the owner's personal brand page.
Main focus: **shotbyfvm**. The owner mostly edits the personal page themselves.

## How requests come in
- "edit this in Style X" → run the `edit-video` skill with that style.
- No style named → suggest one from the table in README.md based on the footage (talking head? b-roll? voiceover?) and say which you picked and why, then go.
- A reference link or video + "make a style like this" → `new-style` skill.
- Notes after a draft → apply them, then run the `learn` skill.

## Hard rules
- Output is **1080x1920, 30 fps, H.264, AAC 320k, -14 LUFS, -1 dBTP**. Export once; never re-encode a finished export.
- **No LUTs.** Grade comes from the preset (iPhone footage: lower exposure a little; D and E darker).
- Captions must follow the phrasing: no one-word orphans, never split "can't / change" style phrases badly.
- Never cut inside a word. Use the word timestamps.
- Keep the speaker's slang and grammar in captions ("what he say"). Don't "correct" how people talk. Do fix transcription mistakes.
- Raw footage is never modified or deleted. Everything goes in `work/<clip>/`.
- Before calling a draft done, look at it: pull a contact sheet of frames (`ffmpeg ... tile`) and check captions, framing and cut points.
- Don't post anything. Posting is the owner's call.

## Where things live
- `tools/reel.py` — the pipeline (transcribe → cut → grade → captions → audio → export).
- `presets/style-x.json` — numbers for a style. `presets/style-x.md` — taste notes for it. Read both before editing in a style.
- `assets/fonts` — caption fonts. `assets/sfx`, `assets/music` — sound library.
- `references/` — breakdown of the 5 reference reels.
- `.claude/skills/` — one skill per step. `edit-video` runs them in order.

## Editing app
Final Cut Pro, controlled through the **SpliceKit** MCP (see SETUP.md). If SpliceKit isn't running, render with `tools/reel.py` and hand back the MP4. Don't stall.
