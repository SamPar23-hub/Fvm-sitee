---
name: color-grade
description: Apply a style's look to iPhone footage. Use for every edit and when the user asks for brighter, darker or more cinematic.
---
# Color grade

**No LUTs** (owner's call; footage is iPhone). Each style JSON has `grade.ffmpeg`:
- **A, B, C — natural:** exposure slightly down, highlights pulled in, a hair more contrast/saturation.
- **D, E — dark/moody:** exposure clearly down, contrast up, saturation down, shadows deeper. D can go B&W for the emotional section (`hue=s=0`).

Rules: skin must stay natural. On already-dark indoor footage, lower highlights rather than overall brightness. In Final Cut, do the same with a Color Board/Wheels adjustment on an adjustment-layer title spanning the timeline.
