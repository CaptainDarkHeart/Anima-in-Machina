# AI DJ MCP Server

An MCP server that exposes Traktor Pro 3 analysis data and cue-point writing to Claude. Traktor's own analysis (BPM, beatgrid, key, loudness) is the primary source of truth; librosa is an optional enhancement for breakdown detection.

## Architecture

```
Claude ←─ MCP ─→ AI DJ MCP Server
                        │
               ┌────────┴────────┐
               ↓                 ↓
        collection.nml      librosa (optional)
        (primary source)    (energy envelope,
        BPM, key,           breakdown detection)
        beatgrid, cues
```

**Data hierarchy:**
- **PRIMARY** — Traktor's analysis in `collection.nml` (BPM, beatgrid anchor, Camelot key, loudness, existing cues)
- **SECONDARY** — librosa on raw audio (energy envelope, BPM cross-check, breakdown detection)

Never re-derive BPM from audio when the NML has it.

## Tools

| Tool | Description |
|------|-------------|
| `get_track_info` | Read Traktor analysis from collection.nml — fast, no audio loading |
| `suggest_cue_points` | Calculate bar-snapped cue positions and write to collection.nml |
| `write_cue_points` | Write exact cue positions manually to collection.nml |
| `suggest_transition` | BPM + Camelot key compatibility and EQ transition strategy |
| `analyze_library_track` | Full analysis: Traktor NML data + librosa BPM cross-check + breakdown |

### Cue slot layout

| Slot | Name | Description |
|------|------|-------------|
| 1 | — | Always protected (never written) |
| 2 | Beat | First bar of the intro |
| 3 | Breakdown | Structural breakdown start |
| 4 | Groove | 32-bar saved loop in the groove pocket |
| 5 | End | Mix-out marker (~32 bars before end) |

### Cue position logic

All positions are snapped to bar boundaries using Traktor's BPM and beatgrid anchor:

- **Beat** — bar boundary nearest 10% of track duration
- **Groove** — bar boundary nearest 35%, with 32-bar loop
- **Breakdown** — bar boundary nearest 65%, or librosa-detected lowest-energy 30s window in the 40–80% zone (if `audio_path` provided)
- **End** — 32 bars before end

Bar arithmetic: `bar_ms = 4 × (60000 / bpm)`

## Installation

### Prerequisites

- Python 3.10+
- Traktor Pro 3 (tracks must be analysed — beatgrid required for cue writing)

### Install

```bash
cd ai-dj-mcp-server
pip install -e .
```

librosa is included as a dependency but only used when `audio_path` is supplied to `suggest_cue_points` or `analyze_library_track`.

### Configure Claude Desktop

`~/Library/Application Support/Claude/claude_desktop_config.json`:

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

Restart Claude Desktop after editing the config.

## NML path

The server reads from the default Traktor 3.11.1 location:

```
~/Documents/Native Instruments/Traktor 3.11.1/collection.nml
```

A timestamped backup is created automatically before every write:

```
collection_backup_YYYYMMDD_HHMMSS.nml
```

**Always restart Traktor after writing cues** — Traktor only reads the NML at startup.

## Supported audio formats (librosa)

WAV, AIFF, MP3, M4A/AAC, FLAC. For m4a tracks (common in Traktor libraries), audio is loaded at 22050 Hz mono for speed.

## Source files

```
ai-dj-mcp-server/
├── pyproject.toml
├── requirements.txt
├── README.md
├── INSTALLATION.md
├── QUICK_REFERENCE.md
├── USAGE_EXAMPLES.md
├── PROJECT_SUMMARY.md
└── src/
    └── ai_dj_mcp/
        ├── __init__.py         # Version (0.2.0)
        ├── __main__.py         # Entry point
        ├── nml_reader.py       # NML parsing, Camelot logic, cue writing
        ├── traktor_track.py    # TraktorTrack model, bar arithmetic, librosa analysis
        └── server.py           # MCP tool declarations and implementations
```
