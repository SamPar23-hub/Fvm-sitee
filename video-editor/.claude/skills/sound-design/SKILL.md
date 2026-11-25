---
name: sound-design
description: Add sound effects and background music matched to the style. Use after graphics are placed.
---
# Sound design

- **SFX** live in `assets/sfx` (name files by what they are: `click_soft.wav`, `whoosh_short.wav`, `boom_low.wav`). If something is missing, synthesize it (Python/ffmpeg) and save it there.
- A: soft click per card. B: none. C: whoosh on bumper and stylized word. D: low booms on big words. E: risers into the payoff.
- **Music** in `assets/music` or found royalty-free. ~14–16 dB under voice, fade in/out, duck under speech (`sidechaincompress`).
- Mix stays at -14 LUFS overall after loudnorm.
