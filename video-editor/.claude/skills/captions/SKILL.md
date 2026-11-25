---
name: captions
description: Make captions in the right style (chunk, build, stack, single) and fix wording. Use whenever captions are created or changed.
---
# Captions

`tools/reel.py` writes `work/<clip>/captions.ass` and burns it in. Modes (set in style JSON):
- **chunk** (A, B): 2–5 words, following the phrasing. No one-word orphans.
- **build** (C): words pile up and wrap, then clear at phrase end.
- **stack** (D): 1–4 huge caps words stacked vertically.
- **single** (E): one word at a time, lights up as spoken.

Fix wording in `words.json` (keep slang and the speaker's grammar). Size/position/font: edit the style JSON, never hard-code. Fonts live in `assets/fonts`. On the Mac they must be installed (double-click) for Final Cut titles; ffmpeg reads them from the folder.
For Final Cut: SpliceKit's Social Media Captions can make editable titles; match the style's font/size/position.
