# AI DJ MCP Server — Installation Guide

## Prerequisites

- **Python 3.10+**
- **Traktor Pro 3** with tracks already analysed (beatgrid required for cue writing)
- **macOS** (NML default path is macOS-specific; other platforms need a custom path)

---

## Step 1: Install Python package

```bash
cd /Users/dantaylor/Claude/Anima-in-Machina/ai-dj-mcp-server
pip install -e .
```

This installs `mcp`, `librosa`, `soundfile`, `numpy`, and `scipy`.

Verify:

```bash
python3 -c "from ai_dj_mcp import server; print('OK')"
```

---

## Step 2: Configure Claude Desktop

Edit `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "ai-dj": {
      "command": "python3",
      "args": ["-m", "ai_dj_mcp"],
      "cwd": "/Users/dantaylor/Claude/Anima-in-Machina/ai-dj-mcp-server/src"
    }
  }
}
```

The `cwd` must point to the `src/` directory (where the `ai_dj_mcp` package lives).

---

## Step 3: Restart Claude Desktop

Completely quit and relaunch Claude Desktop. The MCP server starts on demand when Claude makes its first tool call.

---

## Step 4: Verify

Ask Claude:

```
What AI DJ tools do you have?
```

Claude should list five tools: `get_track_info`, `suggest_cue_points`, `write_cue_points`, `suggest_transition`, `analyze_library_track`.

---

## NML requirements

The server reads and writes `~/Documents/Native Instruments/Traktor 3.11.1/collection.nml`.

For `suggest_cue_points` and `write_cue_points` to work:
1. The track must have been loaded into Traktor at least once (it must appear in the collection)
2. The track must have been **analysed** in Traktor so it has a beatgrid (CUE_V2 TYPE=4)

To check: load the track in Traktor, open the Track Info panel, confirm "Beat Grid" is green.

---

## Troubleshooting

### "Track not found in collection.nml"

The filename must match exactly as stored in Traktor — e.g. `Dreams.m4a`, not a full path or display title.

To find the exact filename:
```bash
grep -o 'FILE="[^"]*Dreams[^"]*"' ~/Documents/Native\ Instruments/Traktor\ 3.11.1/collection.nml
```

### "Track has no beatgrid"

Open Traktor → load the track → click Analyse (or right-click → Analyse in the browser). Wait for the waveform to render.

### "Module 'ai_dj_mcp' not found"

Confirm `cwd` in the config points to `.../ai-dj-mcp-server/src`, then run `pip install -e .` again from the project root.

### librosa import error

```bash
pip install librosa soundfile numpy scipy
```

### Tools not appearing in Claude Desktop

Check logs at `~/Library/Logs/Claude/`. Common causes:
- Invalid JSON in `claude_desktop_config.json`
- Wrong `cwd` (must be absolute, no `~`)
- Python not on PATH — use the full path: `"command": "/usr/bin/python3"`

### After writing cues, Traktor doesn't show them

Traktor reads the NML only at startup. Quit and relaunch Traktor.

---

## Uninstall

1. Remove `"ai-dj"` entry from `claude_desktop_config.json`
2. `pip uninstall ai-dj-mcp-server`
