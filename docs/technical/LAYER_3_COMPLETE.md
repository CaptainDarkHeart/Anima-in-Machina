# Layer 3: Track Selection Engine - COMPLETE ✅

**Intelligent playlist generation using deep space house philosophy**

---

## 🎉 What Was Built

Layer 3 is a complete **Track Selection Engine** that transforms your music library into perfectly curated deep space house DJ sets.

### Core Components

1. **Data Models** (`models.py`)
   - TrackMetadata - Complete track information
   - JourneyArc - Journey arc templates
   - Playlist - Generated playlists with transitions
   - Camelot key system integration
   - Energy/texture classification

2. **Track Library** (`library.py`)
   - Scan music directories
   - Extract metadata from audio files
   - Index by key, BPM, energy
   - Compatibility matching
   - Search and filter capabilities

3. **Journey Planner** (`journey_planner.py`)
   - Create journey arcs
   - Generate energy curves
   - Select compatible tracks
   - Plan smooth transitions
   - Score track compatibility

4. **CLI Tool** (`cli.py`)
   - `create` - Build track library
   - `generate` - Create playlists
   - `stats` - View library statistics
   - `list` - Search tracks

---

## 🚀 Quick Start

### Installation

```bash
cd track-selection-engine
pip install -e .
```

### Create Library

```bash
track-selector create /path/to/music --library my-library.json
```

### Generate Playlist

```bash
track-selector generate 180 \
  --library my-library.json \
  --output "Deep-Journey" \
  --key 1A \
  --progression gradual_build \
  --blend 75 \
  --m3u
```

---

## 🎯 Deep Space House Philosophy Implementation

### From Your Knowledge Base

✅ **60-90 second extended blends** - Configurable blend duration
✅ **A Minor harmonic journeys** - Camelot key system with 1A center
✅ **Gradual energy progression** - Energy curve generation (1-10 scale)
✅ **Label-aware aesthetics** - Preferred labels (Lucidflow, Echocord, etc.)
✅ **Texture classification** - Atmospheric, hypnotic, dub, minimal
✅ **Journey position** - Opener, builder, peak, closer

### Energy Progression Types

**Gradual Build** (Default)
```
2-3-4 → 4-5-6 → 6-7-8 → 7-6-5
Opening   Build   Peak    Descent
```

**Peak and Descent**
```
2-3-4-5-6-7-8 → 7-6-5-4-3
    Build          Descent
```

**Steady**
```
5-6-5-6-5-6
  Consistent groove
```

---

## 📊 How It Works

### 1. Track Library Management

```python
library = TrackLibrary()
library.scan_directory("/Music/Deep-House")
library.save("library.json")

# Find tracks
tracks = library.find_tracks_by_key(MusicalKey.A_MINOR)
compatible = library.get_compatible_tracks(reference_track)
```

### 2. Journey Arc Creation

```python
planner = JourneyPlanner(library)

journey_arc = planner.create_journey_arc(
    duration_minutes=180,
    key_center=MusicalKey.A_MINOR,
    bpm_range=(120, 124),
    energy_progression="gradual_build",
    blend_duration=75
)
```

### 3. Playlist Generation

```python
playlist = planner.generate_playlist(
    journey_arc,
    strict_key=True,  # Only compatible keys
    prefer_labels=True  # Prefer Lucidflow, etc.
)

playlist.to_json("output.json")
playlist.to_m3u("output.m3u")
```

### 4. Transition Planning

Each transition includes:
- Start time for Track A (outro point)
- Start time for Track B (intro point)
- Blend duration
- Compatibility checks (BPM, key, energy, texture)
- Mixing strategy notes

---

## 🎼 Musical Key System

### Camelot Wheel Implementation

```
Minor Keys (A):          Major Keys (B):
1A  - A Minor           1B  - C Major
2A  - E Minor           2B  - G Major
3A  - B Minor           3B  - D Major
... (all 12 keys)
```

### Compatible Mixing Rules

✅ Same key (1A → 1A)
✅ ±1 on circle (1A → 2A or 12A)
✅ Relative major/minor (1A ↔ 1B)

---

## 📁 Project Structure

```
track-selection-engine/
├── README.md                      # Overview & usage
├── WORKFLOW_GUIDE.md              # Step-by-step workflows
├── pyproject.toml                 # Package config
├── requirements.txt               # Dependencies
│
└── src/track_selector/
    ├── __init__.py
    ├── models.py                  # Data models
    ├── library.py                 # Track library management
    ├── journey_planner.py         # Journey arc & playlist generation
    └── cli.py                     # Command-line interface
```

---

## 🔗 Integration with Other Layers

### Layer 1: Knowledge Base ✅
Your documented philosophy guides:
- Energy progression curves
- Blend durations (60-90s)
- Label preferences
- Texture requirements

### Layer 2: AI DJ MCP Server ✅
Enhance library with AI analysis:
```
Ask Claude: "Analyze this track and provide BPM, key, energy level, cue points"
→ Update library JSON with results
→ Generate better playlists
```

### Layer 3: Track Selection Engine ✅ (Current)
Generate intelligent playlists:
```bash
track-selector generate 180 --key 1A --progression gradual_build
→ Perfect journey arc playlist
→ JSON + M3U output
```

### Layer 4: Mixxx Controller ⏭️ (Next)
Automatic execution:
```
Playlist JSON → Mixxx JavaScript Controller → Automated mixing
```

---

## 💡 Example Workflows

### Workflow 1: Quick 3-Hour Set

```bash
# Create library (one-time)
track-selector create /Music/Deep-House

# Generate playlist
track-selector generate 180 \
  --key 1A \
  --progression gradual_build \
  --blend 75 \
  --m3u

# Import to Mixxx
Open Deep-Space-Journey-180min.m3u in Mixxx
```

### Workflow 2: Harmonic Journey (Strict Key)

```bash
track-selector generate 120 \
  --key 1A \
  --strict-key \
  --progression gradual_build
```

Only uses A Minor-compatible keys.

### Workflow 3: Opening Set (Low Energy)

```bash
track-selector generate 90 \
  --progression gradual_build \
  --min-bpm 118 \
  --max-bpm 122
```

Lower BPM, gentle energy build.

---

## 📈 Output Formats

### JSON Playlist
Complete data with transitions:
```json
{
  "name": "Deep Space Journey - 180min",
  "tracks": [...],
  "transitions": [
    {
      "start_time_a": 301.5,
      "start_time_b": 0.0,
      "blend_duration": 75,
      "bpm_compatible": true,
      "key_compatible": true,
      "strategy": "extended_blend"
    }
  ]
}
```

### M3U Playlist
Standard format for Mixxx/Traktor:
```
#EXTM3U
#PLAYLIST:Deep Space Journey

#EXTINF:376,Stimming - Una Pena
/Music/Stimming - Una Pena.wav
```

---

## 🎓 Command Examples

```bash
# Create library
track-selector create /Music/Deep-House

# View statistics
track-selector stats

# Generate 3-hour A Minor journey
track-selector generate 180 --key 1A --blend 75 --m3u

# List tracks at 122 BPM
track-selector list --bpm 122

# List tracks in A Minor
track-selector list --key 1A

# List high-energy tracks
track-selector list --energy 7
```

---

## ⚙️ Configuration Options

### Journey Arc Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `duration` | Set length (minutes) | Required |
| `--key` | Key center (1A-12A, 1B-12B) | None |
| `--min-bpm` | Minimum BPM | 118 |
| `--max-bpm` | Maximum BPM | 124 |
| `--progression` | Energy curve type | gradual_build |
| `--blend` | Blend duration (seconds) | 60 |
| `--strict-key` | Only compatible keys | False |
| `--m3u` | Export M3U format | False |

---

## 🔮 What's Next?

### Immediate Use Cases

1. **Analyze your library** - Scan and categorize tracks
2. **Generate test playlists** - Create 60-90 min sets
3. **Refine metadata** - Add keys, energy levels, textures
4. **Plan DJ sets** - Use for gig preparation

### Future Enhancements

#### Layer 4: Mixxx Controller Integration
- Read playlist JSON
- Auto-load tracks
- Execute transitions
- Real-time mixing

#### Advanced Features
- Web interface for library management
- Collaborative playlist building
- Machine learning for energy detection
- Spotify/SoundCloud integration

---

## 📚 Documentation

### Core Docs
- **[README.md](track-selection-engine/README.md)** - Overview & usage
- **[WORKFLOW_GUIDE.md](track-selection-engine/WORKFLOW_GUIDE.md)** - Step-by-step workflows

### Quick Reference
```bash
# Help
track-selector --help
track-selector generate --help

# Version
pip show track-selection-engine
```

---

## 🎯 Success Metrics

✅ **Data Models**: Complete track/playlist representation
✅ **Library Management**: Scan, index, search, filter
✅ **Journey Planning**: Energy curves, compatibility
✅ **Playlist Generation**: Smart selection, transitions
✅ **CLI Tool**: 4 commands (create, stats, generate, list)
✅ **Documentation**: README + Workflow Guide
✅ **Output Formats**: JSON + M3U

---

## 🙏 Credits

### Built On
- **pandas** - Data analysis
- **mutagen** - Audio metadata extraction
- **Your Knowledge Base** - Deep space house philosophy

### Implements Philosophy From
- EXAMPLE_JOURNEY_ARCS.md
- LABEL_GUIDE.md
- TRANSITION_TECHNIQUES.md
- TRAKTOR_SETUP_GUIDE.md

---

## 🎉 Layer 3 Complete!

You now have a complete intelligent playlist generator that:
- Understands your deep space house philosophy
- Generates perfect journey arcs
- Plans smooth transitions
- Respects harmonic mixing
- Exports to standard formats

### The 3-Layer System So Far

```
✅ Layer 1: Knowledge Base
   Your documented deep space house expertise

✅ Layer 2: AI DJ MCP Server
   Claude can analyze tracks for you

✅ Layer 3: Track Selection Engine
   Intelligent playlist generation

⏭️ Layer 4: Mixxx Controller
   Automated execution (next!)
```

---

**Start generating perfect deep space house journeys today!** 🚀🎧

```bash
cd track-selection-engine
pip install -e .
track-selector create /your/music/directory
track-selector generate 180 --key 1A --blend 75
```
