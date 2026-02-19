# Track Selection Engine

Intelligent playlist generation for deep space house DJ sets using journey arc philosophy.

> Full documentation: **[track-selection-engine/README.md](../../track-selection-engine/README.md)**
> Workflow guide: **[track-selection-engine/WORKFLOW_GUIDE.md](../../track-selection-engine/WORKFLOW_GUIDE.md)**

---

## What it does

Transforms a music library into a scored, journey-arc playlist — selecting tracks by BPM range, Camelot key, energy level, and label preference, then generating blend timing for each transition.

---

## Four source modules

| Module | Purpose |
|--------|---------|
| `models.py` | `TrackMetadata`, `JourneyArc`, `Playlist`, `Transition` dataclasses |
| `library.py` | Scan directories, extract metadata via mutagen, index and filter |
| `journey_planner.py` | Energy curve generation, compatible track selection, transition scoring |
| `cli.py` | `create`, `stats`, `generate`, `list` commands |

---

## Quick start

```bash
cd track-selection-engine
pip install -e .

# Scan your music
track-selector create /path/to/music --library my-library.json

# Generate a 3-hour A Minor journey
track-selector generate 180 \
  --library my-library.json \
  --key 1A \
  --progression gradual_build \
  --blend 75 \
  --m3u
```

---

## Energy progressions

| Type | Arc |
|------|-----|
| `gradual_build` | E2→E4 (opening) → E5→E7 (peak) → E5 (descent) |
| `peak_and_descent` | Build to climax, then wind down |
| `steady` | E5–E6 throughout |

---

## System integration

```
Knowledge Base (docs/)
  ↓ philosophy guides energy curves and label preferences
Track Selection Engine (track-selection-engine/)
  ↓ outputs best-of-deep-dub-tech-house-ai-ordered.json
AI DJ MCP Server (ai-dj-mcp-server/)
  ↓ reads collection.nml for BPM/key to verify/enrich library metadata
Traktor MIDI Automation (traktor-automation/)
  ↓ traktor_ai_dj.py reads the JSON and executes the mix via IAC Driver
```

**Note on Layer 2:** The MCP server reads Traktor's `collection.nml` — it does not analyze raw audio files. To update library JSON with accurate BPM/key data, use `get_track_info` per track and copy results into the library manually.

---

## Primary data file

`best-of-deep-dub-tech-house-ai-ordered.json` — 30-track playlist, AI-ordered for a 165–200 minute journey. This is the live runtime file consumed by `traktor_ai_dj.py`.

Import into Traktor: Browser → Right-click → Import Playlist → `best-of-deep-dub-tech-house-ai-ordered.m3u`
