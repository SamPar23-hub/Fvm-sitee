---
name: rough-cut
description: Transcribe footage with word-level timestamps and cut out pauses, fillers and bad takes. Use for the cutting step of any reel.
---
# Rough cut

- `tools/reel.py` transcribes (WhisperX if installed, else faster-whisper `large-v3`) and caches `work/<clip>/words.json`.
- Cuts: any gap over `cut.max_pause` (per style) becomes a cut; padding `pad_in`/`pad_out` keeps word edges clean. Fillers (um/uh) are dropped.
- **Retakes:** if a line is said twice, keep the **last good take**. Delete the earlier words from `words.json` (or set their text to `um`) and rerun.
- Never cut inside a word. If a word sounds clipped, raise `pad_out` for that style.
- `cutlist.json` holds kept segments in source time. Use it to rebuild the cut in Final Cut.
- When the owner fixes a cut by hand, find the pattern (pause too long? breath kept?) and update the style JSON so it doesn't happen again.
