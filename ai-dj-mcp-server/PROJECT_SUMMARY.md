# AI DJ MCP Server — Project Summary

Version 0.2.0 — Traktor-first architecture

---

## What it does

An MCP server that lets Claude read Traktor Pro 3 analysis data and write cue points directly to `collection.nml`. Traktor's own analysis (BPM, beatgrid, key, loudness) is the authoritative source; librosa is optional for energy-envelope breakdown detection.

---

## Architecture

```
Claude ←─ MCP ─→ AI DJ MCP Server
                        │
               ┌────────┴────────────┐
               ↓                     ↓
        collection.nml          librosa (optional)
        (PRIMARY source)        energy envelope,
        BPM, beatgrid anchor,   breakdown detection,
        Camelot key, loudness,  BPM cross-check
        existing cues
```

**Key principle:** Never re-derive BPM from audio when Traktor's NML has it. Traktor's beatgrid anchor provides millisecond-precise bar boundaries; all cue positions snap to those boundaries.

---

## Source modules

### `nml_reader.py`
- Parses `collection.nml` using `xml.etree.ElementTree`
- `NMLReader.find_entry(filename)` — deduplication logic (prefers gridded entries, then most recently modified)
- `NMLReader.get_track_data(filename)` — returns BPM, anchor_ms, duration_ms, key_camelot, key_name, loudness, existing_cues, has_grid
- `NMLReader.write_cues(filename, specs, overwrite)` — writes CUE_V2 elements, protects slot 1, auto-backups before write
- `camelot_compatible(key1, key2)` — Camelot wheel compatibility (same, relative, adjacent ±1)
- `CAMELOT_POSITIONS`, `KEY_NAMES` — lookup tables for all 24 Camelot positions

### `traktor_track.py`
- `TraktorTrack` dataclass — holds NML fields (primary) + librosa fields (secondary, populated on demand)
- `TraktorTrack.from_nml_data(data)` — constructs from NMLReader dict
- `TraktorTrack.load_librosa_analysis(audio_path)` — loads at 22050 Hz mono, computes RMS envelope, detects breakdown (lowest-energy 30s window in 40–80% zone)
- `TraktorTrack.suggest_cue_positions()` — bar-arithmetic positions (Beat ~10%, Groove ~35%, Breakdown ~65% or detected, End ~32 bars before end), with sanity checks and flags
- `TraktorTrack.to_cue_specs(positions, overwrite)` — converts to NMLReader.write_cues() format
- `bars_to_ms(bars, bpm)`, `snap_to_bar(ms, bpm, anchor_ms)` — bar arithmetic helpers

### `server.py`
- MCP tool declarations and async implementations for all five tools
- Shared `NMLReader` instance (lazy-loaded, cached)
- librosa runs in executor thread to avoid blocking the async event loop
- Error handling: tool errors return `TextContent` with error message, not exceptions

---

## Tools

| Tool | Description |
|------|-------------|
| `get_track_info` | Read-only NML lookup — fast, no audio |
| `suggest_cue_points` | Calculate bar-snapped cue positions + write to NML |
| `write_cue_points` | Write manually specified positions to NML |
| `suggest_transition` | BPM + Camelot key analysis + EQ strategy |
| `analyze_library_track` | Full NML + librosa analysis (read-only) |

---

## Cue slot layout

| Slot | Name | Calculation | Type |
|------|------|-------------|------|
| 1 | — | Always protected | — |
| 2 | Beat | `snap_to_bar(duration * 0.10)` | hot cue |
| 3 | Breakdown | `snap_to_bar(duration * 0.65)` or librosa energy dip | hot cue |
| 4 | Groove | `snap_to_bar(duration * 0.35)`, 32-bar loop | saved loop |
| 5 | End | `snap_to_bar(duration - 32_bars)` | hot cue |

Bar arithmetic: `bar_ms = 4 × (60000 / bpm)`

---

## NML safety rules

- **Slot 1 is always protected** — never written or removed
- **Auto-backup before every write** — timestamped `collection_backup_YYYYMMDD_HHMMSS.nml`
- **CUE_V2 TYPE=4 (beatgrid anchor) is read-only** — never touched by the writer
- **Default: skip occupied slots** — `overwrite=False` preserves existing cues; only write if user explicitly passes `overwrite=True`
- **Restart Traktor after writes** — Traktor reads NML only at startup

---

## Dependencies

| Package | Purpose |
|---------|---------|
| `mcp >= 1.0.0` | Model Context Protocol SDK |
| `librosa >= 0.10.0` | Audio analysis (optional path) |
| `soundfile >= 0.12.1` | Audio I/O for librosa |
| `numpy >= 1.26.0` | Array arithmetic |
| `scipy >= 1.11.0` | Rolling window convolution |

No PyTorch. No LSTM. No trained models required.

---

## What was removed in v0.2

The original v0.1 architecture used:
- `track.py` — librosa beat/BPM detection as primary source
- `cue_detector.py` — untrained PyTorch LSTM (produced random cue positions)
- Tools: `analyze_track`, `detect_cue_points`, `extract_features`, `calculate_bpm_compatibility`

All of these were replaced. Traktor's beatgrid is far more accurate than librosa BPM detection for music that has already been loaded and analysed in Traktor. The LSTM had no trained weights and was generating meaningless output.

---

## File structure

```
ai-dj-mcp-server/
├── pyproject.toml          # Package config, v0.2.0, dependencies
├── requirements.txt        # Flat dependency list
├── README.md               # Overview, tool table, cue logic, quick install
├── INSTALLATION.md         # Step-by-step setup and troubleshooting
├── QUICK_REFERENCE.md      # Prompt examples, tables, cheat sheet
├── USAGE_EXAMPLES.md       # Full worked examples with sample output
├── PROJECT_SUMMARY.md      # This file — architecture and design notes
├── test_track_analysis.py  # Manual test script
└── src/
    └── ai_dj_mcp/
        ├── __init__.py     # Version string (0.2.0)
        ├── __main__.py     # `python -m ai_dj_mcp` entry point
        ├── nml_reader.py   # NML parsing, Camelot logic, cue writing
        ├── traktor_track.py # TraktorTrack model, bar arithmetic, librosa
        └── server.py       # MCP tool declarations and implementations
```
