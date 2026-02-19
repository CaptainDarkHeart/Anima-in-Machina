# Track Selection Engine

Intelligent playlist generation for deep space house DJ sets using journey arc philosophy.

---

## What's in this directory

| File / Dir | What it is |
|------------|-----------|
| `src/track_selector/` | Python package — `track-selector` CLI |
| `best-of-deep-dub-tech-house-ai-ordered.json` | AI-ordered 30-track playlist (primary data file) |
| `best-of-deep-dub-tech-house-ai-ordered.m3u` | M3U import for Traktor |
| `best-of-deep-dub-tech-house.json` | Unordered source playlist |
| `traktor-library.json` | Track library scanned from Traktor collection |
| `traktor-library-detailed.json` | Library with extended metadata |
| `create_best_of_playlist.py` | Builds the Best of Deep Dub playlist with hardcoded order + metadata |
| `create_best_of_playlist_smart.py` | Variant using the journey planner scoring |
| `create_custom_playlist.py` | Builds a playlist from `custom_playlist.txt` |
| `analyze_custom_playlist.py` | Matches a text playlist against the library |
| `import_bpm_list.py` | Imports BPM data from a markdown list into the library |
| `import_detailed_list.py` | Imports extended metadata |
| `import_with_file_paths.py` | Imports with resolved audio file paths |

---

## The `track-selector` CLI

A command-line tool for scanning libraries and generating playlists programmatically.

### Install

```bash
cd track-selection-engine
pip install -e .
```

### Commands

#### Create a track library from a directory

```bash
track-selector create /path/to/your/music --library my-library.json
```

Scans WAV, AIFF, MP3, FLAC files and extracts metadata via mutagen.

#### View library statistics

```bash
track-selector stats --library my-library.json
```

#### Generate a playlist

```bash
track-selector generate 180 \
  --library my-library.json \
  --output my-journey \
  --key 1A \
  --progression gradual_build \
  --blend 75 \
  --min-bpm 120 \
  --max-bpm 124 \
  --m3u
```

Produces `my-journey.json` and `my-journey.m3u`.

#### List tracks

```bash
track-selector list --bpm 122        # Filter by BPM (±2)
track-selector list --key 1A         # Filter by Camelot key
track-selector list --energy 5       # Filter by energy level (±1)
```

### Full `generate` options

| Option | Default | Description |
|--------|---------|-------------|
| `duration` | (required) | Duration in minutes |
| `--library` | `library.json` | Library file |
| `--output` | `playlist` | Output filename (no extension) |
| `--key` | — | Camelot key center (e.g. `1A`) |
| `--min-bpm` | 118 | Minimum BPM |
| `--max-bpm` | 124 | Maximum BPM |
| `--progression` | `gradual_build` | `gradual_build`, `peak_and_descent`, `steady` |
| `--blend` | 60 | Blend duration in seconds |
| `--strict-key` | false | Only use harmonically compatible tracks |
| `--m3u` | false | Also save M3U |

---

## Energy progression types

| Type | Arc |
|------|-----|
| `gradual_build` | E2→E4 (opening) → E5→E7 (peak) → E5 (descent) |
| `peak_and_descent` | Build to climax, then wind down |
| `steady` | E5–E6 throughout |

---

## Camelot key system

Compatible mixes: same key (1A→1A), ±1 on the circle (1A→2A or 12A), or same number different mode (1A→1B).

---

## Python API

```python
from track_selector.library import TrackLibrary
from track_selector.journey_planner import JourneyPlanner
from track_selector.models import MusicalKey

library = TrackLibrary(Path("my-library.json"))
planner = JourneyPlanner(library)

journey = planner.create_journey_arc(
    duration_minutes=120,
    key_center=MusicalKey.A_MINOR,
    bpm_range=(120, 124),
    energy_progression="gradual_build",
    blend_duration=75
)

playlist = planner.generate_playlist(journey, strict_key=True)
playlist.to_json(Path("output.json"))
playlist.to_m3u(Path("output.m3u"))
```

---

## Data files

### `best-of-deep-dub-tech-house-ai-ordered.json`

The primary playlist — 30 tracks from the Best of Deep Dub Tech House collection, ordered for a 165-200 minute journey. This is what `traktor_ai_dj.py` reads at runtime.

**Import into Traktor:**
- Browser → Right-click → Import Playlist → select `best-of-deep-dub-tech-house-ai-ordered.m3u`

### `traktor-library.json` / `traktor-library-detailed.json`

Track library built from the Traktor collection. Use `import_bpm_list.py` or `import_detailed_list.py` to rebuild from updated metadata.

---

## Integration

### With Traktor MIDI Automation (`traktor-automation/`)

`traktor_ai_dj.py` reads `best-of-deep-dub-tech-house-ai-ordered.json` directly for track order and metadata. The `--playlist` flag on `deep_house_cue_writer.py` also accepts this file.

### With AI DJ MCP Server (`ai-dj-mcp-server/`)

The MCP server reads cue/BPM data from Traktor's `collection.nml`, not from these JSON files. To update playlist metadata with Traktor's analysis, use `get_track_info` per track and add results to the library JSON manually.

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| "No suitable opener found" | Library has no low-energy tracks; try `--progression steady` |
| "Could not find suitable track" | BPM/key constraints too tight; widen range or remove `--strict-key` |
| Empty library after scan | Check file formats and directory path |
| Playlist too short | Reduce `--blend` duration |
