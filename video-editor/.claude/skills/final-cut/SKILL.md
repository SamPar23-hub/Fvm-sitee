---
name: final-cut
description: Put the edit into Final Cut Pro through the SpliceKit MCP for review and tweaks. Use when the owner wants it in Final Cut or SpliceKit is connected.
---
# Final Cut (SpliceKit)

Needs the **patched** Final Cut copy (`~/Applications/SpliceKit/`) open; the bridge listens on 127.0.0.1:9876. Check with a cheap call first; if it's down, ask the owner to launch it from the SpliceKit app, and meanwhile hand back the MP4.

1. New project: 1080x1920, 30 fps.
2. Import the raw clip; rebuild the cut from `work/<clip>/cutlist.json` (blade + delete, or append the in/out ranges).
3. Add captions as titles (style's font/size/position) or import the rendered caption/graphics layers.
4. Grade with an adjustment layer; add SFX/music on their own roles (Dialogue / Effects / Music).
5. Tell the owner it's on the timeline. When they make manual changes, read the timeline back and run `learn`.

If a step is clumsy, build it as a reusable SpliceKit command (plugin/MCP tool) instead of repeating the workaround.
