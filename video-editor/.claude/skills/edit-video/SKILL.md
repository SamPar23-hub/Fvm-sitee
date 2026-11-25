---
name: edit-video
description: Edit a reel end to end in one of the FVM styles (A–E). Use whenever the user hands over raw footage and says "edit this", "edit this in Style X", or similar.
---
# Edit a reel (orchestrator)

Run these in order. Don't ask questions mid-way unless footage is missing or unusable.

1. **Intake.** Find the footage (path given, or newest video in ~/Downloads / ~/Movies). Probe it (`ffprobe`). Note: talking head? b-roll? voiceover? length?
2. **Pick the style.** Use the one named. If none, choose from README.md and say why in one line.
3. **Read** `presets/style-x.md` and `presets/style-x.json`.
4. **Rough cut + captions + grade + audio:** `python3 tools/reel.py <file> --style X [--title "..."]` (see `rough-cut`, `captions`, `color-grade`, `audio-polish`).
5. **Check the transcript** in `work/<clip>/words.json`. Fix misheard words (keep slang), rerun (the transcript is cached, so reruns are fast).
6. **Graphics / b-roll** if the style calls for it (A, C, D, E) → `graphics` skill.
7. **Sound** → `sound-design` skill.
8. **Look at it.** Contact sheet: `ffmpeg -i out.mp4 -vf "fps=2,scale=270:-1,tile=6x4" -frames:v 1 sheet.jpg`, then view it. Fix anything off.
9. **Hand off for review** → `final-cut` skill if SpliceKit is running, otherwise send the MP4.
10. After notes are applied and approved → `export`, then `learn`.
