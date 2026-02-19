# AI DJ MCP Server — Overview

An MCP (Model Context Protocol) server that gives Claude direct access to Traktor Pro 3 analysis data and the ability to write cue points to `collection.nml`. Traktor's own beatgrid is the authoritative data source.

> Full technical documentation: **[ai-dj-mcp-server/README.md](../../ai-dj-mcp-server/README.md)**

---

## What it does

Claude can read and write to your Traktor library without touching Traktor itself. Key capabilities:

- Read BPM, Camelot key, loudness, and existing cue points from `collection.nml`
- Write bar-snapped cue points (Beat, Groove, Breakdown, End) to `collection.nml`
- Plan transitions using Camelot wheel compatibility and BPM ratios
- Optionally use librosa for energy-envelope breakdown detection

All NML writes create automatic timestamped backups. Slot 1 (Traktor's floating cue) is always protected.

---

## Architecture

```
Claude ←─ MCP ─→ AI DJ MCP Server
                        │
               ┌────────┴────────────┐
               ↓                     ↓
        collection.nml          librosa (optional)
        (PRIMARY source)        breakdown detection
        BPM, beatgrid anchor,   only used when
        Camelot key, loudness,  audio_path provided
        existing cues
```

The server never re-derives BPM from audio when Traktor's beatgrid has it.

---

## Five tools

| Tool | What it does |
|------|-------------|
| `get_track_info` | Read BPM, key, cues from NML — fast, no audio loading |
| `suggest_cue_points` | Calculate bar-snapped cue positions and write to NML |
| `write_cue_points` | Write manually specified positions to NML |
| `suggest_transition` | BPM + Camelot key compatibility, EQ swap strategy |
| `analyze_library_track` | Full NML + librosa cross-check (read-only) |

---

## Cue slot layout

| Slot | Name | Position | Type |
|------|------|----------|------|
| 1 | (protected) | — | never touched |
| 2 | Beat | ~10% of track | hot cue |
| 3 | Breakdown | ~65% (or librosa-detected) | hot cue |
| 4 | Groove | ~35%, 32-bar loop | saved loop |
| 5 | End | 32 bars before end | hot cue |

All positions are bar-snapped to Traktor's beatgrid anchor using: `bar_ms = 4 × (60000 / bpm)`.

---

## Example prompts

```
Get track info for "Stimming - Una Pena.m4a"

Suggest cue points for "Stimming - Una Pena.m4a"

Suggest transition from "Track A.m4a" to "Track B.m4a"

Analyze "Stimming - Una Pena.m4a" at
/Volumes/TRAKTOR/Music/Stimming - Una Pena.m4a
```

---

## Installation

```bash
cd /Users/dantaylor/Claude/Anima-in-Machina/ai-dj-mcp-server
pip install -e .
```

Claude Desktop config (`~/Library/Application Support/Claude/claude_desktop_config.json`):

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

Restart Claude Desktop after editing. **Restart Traktor after writing cues** — it only reads the NML at startup.

---

## Source files

```
ai-dj-mcp-server/src/ai_dj_mcp/
├── __init__.py         # Version (0.2.0)
├── __main__.py         # Entry point
├── nml_reader.py       # NML parsing, Camelot logic, cue writing, auto-backup
├── traktor_track.py    # TraktorTrack model, bar arithmetic, librosa analysis
└── server.py           # MCP tool declarations and async implementations
```

---

## NML path

```
~/Documents/Native Instruments/Traktor 3.11.1/collection.nml
```

Backups saved as `collection_backup_YYYYMMDD_HHMMSS.nml` in the same directory.

---

## Relationship to other tools

| Tool | Uses NML? | Uses audio? | Writes cues? |
|------|-----------|-------------|--------------|
| `get_track_info` | yes | no | no |
| `suggest_cue_points` | yes (primary) | optional | yes |
| `analyze_library_track` | yes (primary) | yes | no |
| `deep_house_cue_writer.py` (traktor-automation) | yes | no | yes |

Both the MCP server and `deep_house_cue_writer.py` write to the same `collection.nml`. The MCP server is the preferred path — it has better deduplication logic and slot protection.
