# Setup on the Mac (one time)

Open Terminal and run these one at a time.

## 1. Basics
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```
```bash
brew install ffmpeg python@3.12 uv git node yt-dlp
```

## 2. Transcription (word-level timestamps)
```bash
cd /path/to/video-editor && uv venv && source .venv/bin/activate && uv pip install whisperx faster-whisper numpy
```
First run downloads the `large-v3` model (~3 GB). After that it's offline.

## 3. Claude Code
```bash
npm install -g @anthropic-ai/claude-code
```
Then open this folder with Claude Code (`cd video-editor && claude`) or pick it as the project folder in the Claude desktop app. `CLAUDE.md` loads automatically.

## 4. Final Cut Pro → SpliceKit
SpliceKit lets Claude drive Final Cut (~200 tools: blade, trim, titles, captions, color, export).

1. Download the latest release: https://github.com/elliotttate/SpliceKit/releases/latest
   (A more actively maintained fork, SpliceKit v4, is at https://splicekit.fcp.cafe.)
2. Unzip, open the app, click **Patch**. It makes a *copy* of Final Cut in `~/Applications/SpliceKit/`. Your normal Final Cut isn't touched.
3. Click **Launch FCP**. That patched copy has to be open whenever Claude edits.
4. Connect it to Claude. The patcher usually does this. If not, add this to `video-editor/.mcp.json` (change `YOURNAME`):
```json
{
  "mcpServers": {
    "splicekit": {
      "command": "/Users/YOURNAME/.venvs/splicekit-mcp/bin/python",
      "args": ["/Applications/SpliceKit.app/Contents/Resources/mcp/server.py"]
    }
  }
}
```
5. Test: ask Claude "check the SpliceKit connection and add a marker at 2 seconds."

## 5. Optional
- **HyperFrames** (animated cards, bumpers, title graphics): https://github.com/heygen-com/hyperframes. Ask Claude to install it and keep its skills scoped to this project only.
- **ClearerVoice-Studio** (heavy noise/hum cleanup): only if the built-in denoise isn't enough.
