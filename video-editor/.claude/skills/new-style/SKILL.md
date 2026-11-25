---
name: new-style
description: Turn a reference reel into a new style preset. Use when the user shares a video or link and says "make a style like this" or "copy this style".
---
# New style from a reference

1. Get the video: `yt-dlp <link>` (Instagram may need `--cookies-from-browser safari`) or use the file they sent.
2. Measure: duration, cut times (`select='gt(scene,0.3)'`), loudness (`ebur128`), resolution.
3. Look: contact sheet at 3 fps and a few full frames. Note caption font/size/position/animation, b-roll rhythm, graphics, grade, sound.
4. Write `presets/style-<next letter>.json` (start from the closest existing style) and `presets/style-<x>.md` (taste notes), and add a row to README.md and `references/README.md`.
5. For tricky effects, recreate them **one at a time** against the reference before calling the style done.
