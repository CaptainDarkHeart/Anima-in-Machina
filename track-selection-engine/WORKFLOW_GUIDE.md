# Track Selection Engine - Complete Workflow Guide

Step-by-step guide to using the Track Selection Engine for building perfect deep space house DJ sets.

---

## Workflow Overview

```
1. Build Library → 2. Analyze Tracks → 3. Generate Playlists → 4. Refine & Mix
```

---

## Phase 1: Build Your Track Library

### Step 1: Scan Your Music Collection

```bash
# Scan your entire deep house collection
track-selector create /Users/dantaylor/Music/Deep-House \
  --library deep-house-library.json
```

**What this does:**
- Scans all WAV, AIFF, MP3, FLAC files
- Extracts BPM, artist, title from file tags
- Creates searchable database
- Saves to JSON file

**Expected output:**
```
Scanning directory: /Users/dantaylor/Music/Deep-House
✓ Added 1,247 tracks to library
✓ Library saved to: deep-house-library.json

Library Statistics:
  Total tracks: 1,247
  BPM range: 115.0 - 128.0
  Average BPM: 121.3
```

### Step 2: Verify Library

```bash
track-selector stats --library deep-house-library.json
```

Review:
- Total track count (need at least 50+ for good playlists)
- BPM distribution
- Energy levels

---

## Phase 2: Enhance Track Metadata

The initial scan extracts basic metadata. For better playlists, enhance manually or using the AI DJ MCP Server.

### Option A: Manual Enhancement

Edit `deep-house-library.json` to add:

```json
{
  "tracks": [
    {
      "file_path": "/Music/Stimming - Una Pena.wav",
      "title": "Una Pena",
      "artist": "Stimming",
      "bpm": 122.3,
      "key": "1A",           // Add key
      "energy_level": 5,     // Add energy (1-10)
      "textures": [          // Add textures
        "atmospheric",
        "hypnotic"
      ],
      "label": "Lucidflow",  // Add label
      "journey_position": "core"  // Add position
    }
  ]
}
```

### Option B: Use AI DJ MCP Server (Layer 2)

Ask Claude to analyze tracks:

```
Analyze /Music/Stimming - Una Pena.wav and detect:
- BPM (verify)
- Cue points
- Energy level
```

Update library JSON with AI-detected values.

---

## Phase 3: Generate Your First Playlist

### Example 1: 3-Hour A Minor Journey

```bash
track-selector generate 180 \
  --library deep-house-library.json \
  --output "Deep-Space-Journey-180min" \
  --key 1A \
  --progression gradual_build \
  --blend 75 \
  --min-bpm 120 \
  --max-bpm 124 \
  --m3u
```

**Parameters explained:**
- `180` - 3 hours
- `--key 1A` - A Minor center
- `--progression gradual_build` - Classic arc
- `--blend 75` - 75-second extended blends
- `--min-bpm 120 --max-bpm 124` - Tight BPM range
- `--m3u` - Export for Mixxx/Traktor

**Output:**
```
✓ Playlist generated: 28 tracks
  Total duration: 182.3 minutes

PLAYLIST: Deep Space Journey - 180min
================================================================================

 1. Shlomi Aber - Sketch of Transitions (Dub)
    120.2 BPM | 1A | E3 | 6:42
    └─ Blend: 75s

 2. Stimming - Una Pena (Traktor Edit)
    122.3 BPM | 1A | E5 | 6:16
    └─ Blend: 75s

[... 26 more tracks ...]

✓ Saved playlist to: Deep-Space-Journey-180min.json
✓ Saved M3U playlist to: Deep-Space-Journey-180min.m3u
```

### Example 2: Opening Set (Warm-Up)

```bash
track-selector generate 90 \
  --library deep-house-library.json \
  --output "Warm-Up-90min" \
  --progression gradual_build \
  --blend 60 \
  --min-bpm 118 \
  --max-bpm 122 \
  --m3u
```

Lower BPM range for opening set.

### Example 3: Peak Hour Set

```bash
track-selector generate 120 \
  --library deep-house-library.json \
  --output "Peak-Hour-120min" \
  --progression peak_and_descent \
  --blend 60 \
  --min-bpm 122 \
  --max-bpm 126 \
  --m3u
```

Higher BPM, peak-and-descent energy.

---

## Phase 4: Review and Refine Playlist

### Step 1: Inspect Generated Playlist

Open `Deep-Space-Journey-180min.json`:

```json
{
  "name": "Deep Space Journey - 180min",
  "tracks": [...],
  "transitions": [
    {
      "track_a": {...},
      "track_b": {...},
      "start_time_a": 301.5,
      "start_time_b": 0.0,
      "blend_duration": 75,
      "bpm_compatible": true,
      "key_compatible": true,
      "strategy": "extended_blend",
      "notes": "Blend from Una Pena to Blurred over 75s | Harmonic mix"
    }
  ]
}
```

**Check:**
- Track order makes sense
- Energy progression flows
- BPM/key compatibility
- Transition notes

### Step 2: Manual Adjustments

If needed, reorder tracks in JSON or regenerate with different parameters.

### Step 3: Test in Traktor

1. Import the M3U into Traktor (Browser → Right-click → Import Playlist)
2. Use `deep_house_cue_writer.py --playlist ...` to write cue points
3. Restart Traktor, load the playlist, test the transitions

---

## Phase 5: Execute the Journey

### Preparation Checklist

- [ ] Playlist imported into Traktor
- [ ] Cue points written via `deep_house_cue_writer.py` (or MCP server)
- [ ] Traktor restarted to load new cues
- [ ] Beat grids verified in Traktor
- [ ] Transition notes reviewed
- [ ] `traktor_ai_dj.py` MIDI connection tested

### During the Mix

Follow the generated transitions:

```
Track 1: Stimming - Una Pena
  ↓ Start blend at 5:01 (301s)
  ↓ 75-second blend
Track 2: Sasha Carassi - Blurred
  ↓ Start blend at 6:47
  ↓ 75-second blend
Track 3: ...
```

Use transition notes for mixing strategy.

---

## Advanced Workflows

### Workflow A: Label-Specific Journey

Create Lucidflow-only set:

1. Filter library for Lucidflow tracks:
```bash
track-selector list --library deep-house-library.json > lucidflow-tracks.txt
```

2. Manually create filtered library JSON

3. Generate playlist from filtered library

### Workflow B: Key-Centric Journey (Strict Harmonic)

```bash
track-selector generate 120 \
  --library deep-house-library.json \
  --key 1A \
  --strict-key \
  --output "A-Minor-Journey"
```

Only uses A Minor compatible keys (12A, 2A, 1A, 1B).

### Workflow C: Multi-Genre Exploration

Build separate libraries:

```bash
# Deep house library
track-selector create /Music/Deep-House --library deep-house.json

# Dub techno library
track-selector create /Music/Dub-Techno --library dub-techno.json

# Minimal library
track-selector create /Music/Minimal --library minimal.json
```

Generate playlists from each, then combine manually.

---

## Integration with Full System

### Knowledge Base (`docs/`)
The deep space house philosophy documented in `docs/` guides the engine's energy progressions, key preferences, and label aesthetics.

### AI DJ MCP Server (`ai-dj-mcp-server/`)
Use Claude to check Traktor's analysis before updating library metadata:

```
Get track info for "Stimming - Una Pena.m4a"
```

Then update the library JSON with BPM, key, and cue positions from Traktor.

### Track Selection Engine (this directory)
Generate intelligent playlists following your philosophy.

### Traktor MIDI Automation (`traktor-automation/`)
`traktor_ai_dj.py` reads `best-of-deep-dub-tech-house-ai-ordered.json` and executes the mix via MIDI.

---

## Example: Full 3-Hour Set Workflow

### 1. Scan Library (One-Time)
```bash
track-selector create /Music/Deep-Space-House \
  --library my-collection.json
```

### 2. Get Traktor analysis with Claude
```
Get track info for "Nadja Lind - Spherical.m4a"
```

Use `get_track_info` for each key track to fetch BPM and Camelot key from collection.nml.

### 3. Update Library JSON
Add Traktor's BPM/key data to the library file.

### 4. Generate Playlist
```bash
track-selector generate 180 \
  --library my-collection.json \
  --output "Tonight-Journey" \
  --key 1A \
  --progression gradual_build \
  --blend 75 \
  --m3u
```

### 5. Review in Traktor
- Load tracks
- Set cue points using transition times
- Verify beat grids

### 6. Perform!
Follow the journey arc, using the generated transitions as your guide.

---

## Tips for Best Results

### Library Quality
- **Size matters**: 100+ tracks minimum for variety
- **Consistent tagging**: Use same BPM analysis method
- **Accurate keys**: Use Mixed In Key or Claude analysis
- **Energy classification**: Be consistent with 1-10 scale

### Playlist Generation
- **Start conservative**: Use default parameters first
- **Iterate**: Generate multiple versions, pick the best
- **Trust the algorithm**: The scoring system understands your philosophy
- **Manual touch**: Swap 1-2 tracks if needed

### Mixing Execution
- **Verify BPM**: Double-check Traktor's BPM matches library
- **Set cues precisely**: Use transition times as exact references
- **Trust the blend**: 75-second blends work for deep space house
- **Adjust live**: Use transition notes as guidance, not rules

---

## Troubleshooting

### Problem: Playlist too short
**Solution**: Reduce blend duration or increase duration target
```bash
--blend 60  # Instead of 75
```

### Problem: Energy jumps too much
**Solution**: Use steady progression
```bash
--progression steady
```

### Problem: Wrong vibe/labels
**Solution**: Filter library or edit preferred_labels in code

### Problem: Too many BPM mismatches
**Solution**: Widen BPM range
```bash
--min-bpm 118 --max-bpm 126  # Wider range
```

---

## Next Steps

1. ✅ Build your library
2. ✅ Generate first test playlist
3. ✅ Review and refine
4. ✅ Import into Traktor, write cue points
5. ✅ Run `traktor_ai_dj.py` for full automation

---

**You're now ready to generate perfect deep space house journeys automatically!** 🚀🎧
