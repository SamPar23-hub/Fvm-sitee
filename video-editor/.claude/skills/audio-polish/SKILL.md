---
name: audio-polish
description: Clean and level the voice to reel loudness. Use for every edit, and when the user says the audio is quiet, noisy or buzzy.
---
# Audio polish

Chain (per style JSON `audio.chain`): high-pass 80 Hz → light FFT denoise → compressor 3:1 → limiter, then **two-pass loudnorm to -14 LUFS, -1 dBTP**.

- Heavy hum/buzz/room noise: raise denoise (`afftdn=nf=-30`) or run ClearerVoice-Studio (`MossFormer2_SE_48K`) on the extracted audio first, then rerun.
- Music sits ~14–16 dB under the voice. SFX are short and never louder than the voice.
- Check: `ffmpeg -i out.mp4 -af ebur128=peak=true -f null -` → I ≈ -14, peak ≤ -1.
