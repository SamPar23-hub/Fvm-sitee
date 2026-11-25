# FVM Video Editor

Claude edits our reels. You drop in raw footage, say which style, and it runs the whole edit.

```
edit ~/Downloads/clip.mov in Style C
```

## The 5 styles

| Style | Name | Use it for | Look |
|---|---|---|---|
| **A** | Talking Head + Cards | Teaching, tips, "how we shoot a listing" | Natural, slightly darker |
| **B** | Raw Selfie | Quick thoughts, behind the scenes | Natural, slightly darker |
| **C** | Cinematic Voiceover | Listing tours, lifestyle | Natural, slightly darker |
| **D** | Cinematic Statement | Motivational / brand pieces | Dark, moody, letterboxed |
| **E** | Story Vlog | Personal stories, client wins | Dark, moody |

Full breakdown of each reference reel: `references/README.md`. The rules for each style: `presets/style-x.md` (taste) and `presets/style-x.json` (numbers).

## What happens when you say "edit this"

1. **Intake.** Finds the footage.
2. **Rough cut.** Transcribes every word with timestamps, cuts pauses, "ums" and bad takes.
3. **Audio.** Cleans noise, evens out the voice, sets loudness to -14 LUFS.
4. **Grade.** No LUT. iPhone footage with exposure pulled down a little (A–C) or dark and moody (D, E).
5. **Captions and graphics.** In that style's look.
6. **Sound.** Sound effects on graphics, music under the voice.
7. **Review.** Lands in Final Cut (via SpliceKit) or as an MP4. You give notes.
8. **Learn.** Your notes get written back into the style so the next one comes out right first try.
9. **Export.** 1080x1920 vertical, ready for Instagram and TikTok.

## Quick run (no Final Cut needed)

```bash
python3 tools/reel.py ~/Downloads/clip.mov --style B
python3 tools/reel.py ~/Downloads/clip.mov --style A --title "How we shoot a listing in 1 hour"
```

Result lands in `work/<clip name>/`.

First-time setup on the Mac: `SETUP.md`.
