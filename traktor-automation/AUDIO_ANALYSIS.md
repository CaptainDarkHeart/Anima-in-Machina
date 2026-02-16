# Audio Analysis System for Traktor AI DJ

The Traktor AI DJ now has **ears** - it can actually "hear" and analyze the music it's playing using Librosa.

## What It Does

### 1. **Tempo Analysis** 🥁
- Detects actual BPM from audio (not just metadata)
- Measures beat stability/confidence
- Finds precise beat locations
- Compares detected vs. metadata BPM

**Use case**: Catch incorrect BPM tags, find tempo variations

### 2. **Energy Analysis** ⚡
- Measures RMS energy throughout the track
- Segments track into 8-second windows
- Tracks energy peaks and valleys
- Calculates overall energy profile

**Use case**: Match energy levels for smooth transitions, avoid jarring jumps

### 3. **Harmonic Analysis** 🎹
- Estimates musical key (C, D, E, etc.)
- Determines mode (major/minor)
- Calculates key confidence
- Checks harmonic compatibility between tracks

**Use case**: Harmonic mixing (keys that sound good together)

### 4. **Cue Point Detection** 📍

The system automatically finds:

#### **Intro** (0:00 - first 16 bars)
- Clean start section for mixing in
- Usually minimal elements

#### **Outro** (last 16 bars - end)
- Natural ending section
- Good for mixing out

#### **Breakdown** 🌊
- Low energy sections
- Perfect for mixing in during quiet moments
- Typically after a drop or in the middle

#### **Build** 📈
- Rising energy sections
- Leading up to a drop
- Creates anticipation

#### **Drop** 💥
- Sudden energy increases
- Main impact moments
- Peak energy sections

**Use case**: Know exactly when to mix in/out for seamless blends

### 5. **Spectral Analysis** 🌈
- Brightness (spectral centroid)
- Frequency rolloff
- Percussiveness (zero-crossing rate)

**Use case**: Match tracks with similar tonal characteristics

## How It Works

### Analysis Cache
```
~/.cache/traktor_ai_dj/
├── track1_1234567890.json
├── track2_1234567891.json
└── ...
```

Each track is analyzed once and cached. Cache includes file modification time, so re-analyzing happens automatically if the file changes.

### Intelligent Mixing

The DJ now makes smart decisions:

1. **Pre-load analysis**: All tracks analyzed at startup
2. **Compatibility check**: Compares current vs. next track
3. **Dynamic blend duration**:
   - Poor compatibility → 30s quick blend
   - Good match → 75s normal blend
   - Perfect match → 90s extended blend
4. **Optimal mix points**:
   - Mix out during outro or before energy drops
   - Mix in during breakdown or intro

### Example Output

```
🎵 Analyzing audio: Artist - Track Title
  ✓ Detected BPM: 122.3 (confidence: 94.2%)
  ✓ Key: G minor (confidence: 78.5%)
  ✓ Energy: 0.78
  ✓ Breakdown found: 124.5s - 140.2s (15.7s)
  ✓ Drop at: 180.3s

TRANSITION 1 → 2
=============================================================
  🎯 Mix compatibility: 85/100
  ✨ Using extended blend (90s) for perfect match
  📍 Mix out at: 215.4s
  📍 Mix in at: 16.2s (breakdown)
```

## Librosa vs. Alternatives

### Why Librosa?

✅ **Pros**:
- Industry standard for music analysis
- Excellent beat detection
- Rich feature extraction (harmony, spectral, rhythm)
- Well-documented and maintained
- Pure Python (easy to integrate)

❌ **Cons**:
- Not real-time (pre-analysis required)
- CPU intensive
- Slower than some alternatives

### Alternatives Considered

**Essentia** (by Music Technology Group, Barcelona)
- More accurate for some tasks
- Real-time capable
- Harder to install (C++ dependencies)
- Less Pythonic

**Aubio**
- Faster, lighter weight
- Good for real-time onset detection
- Fewer high-level features
- Less actively developed

**Sonic Visualiser / Vamp Plugins**
- Great for visualization
- Not designed for programmatic use
- Manual workflow

**Madmom**
- Excellent beat tracking
- Neural network models
- Limited to rhythm analysis
- Less versatile

### For Your Use Case

**Current choice: Librosa** is perfect because:
1. We pre-analyze tracks (not real-time)
2. Need comprehensive features (beats, energy, harmony, cues)
3. Python integration is crucial
4. Community support is excellent

**Future consideration**: If you want real-time audio visualization or faster processing, consider:
- **Essentia** for production systems
- **Aubio** for real-time onset detection
- **audiowaveform** for waveform visualization (see below)

## Next Steps: Visual Analysis

### Waveform Visualization with audiowaveform

```bash
# Install audiowaveform
brew install audiowaveform

# Generate waveform data
audiowaveform -i track.mp3 -o track.json --pixels-per-second 20
```

**Benefits**:
- Visual cue point confirmation
- See energy structure at a glance
- Traktor-style waveform display
- Fast generation

**Integration idea**: Combine Librosa analysis + audiowaveform visualization
```python
# Librosa detects cue points
analysis = analyzer.analyze_track("track.mp3")
breakdown_time = analysis['cue_points']['breakdown']['start']

# audiowaveform shows visual confirmation
# Display waveform with breakdown marker at breakdown_time
```

### Traktor Beatgrid Analysis

Traktor stores beatgrids in its collection.nml file:
```xml
<ENTRY>
  <TEMPO BPM="122.000000" BPM_QUALITY="100.000000">
    <BEATS_V2>
      <BEAT VALUE="0.123" BEAT_IDX="1"/>
      <BEAT VALUE="0.615" BEAT_IDX="2"/>
      ...
    </BEATS_V2>
  </TEMPO>
</ENTRY>
```

**Future integration**:
1. Parse collection.nml
2. Extract existing beatgrid
3. Compare with Librosa beat detection
4. Sync AI DJ cue points with Traktor cue points

## Installation

```bash
cd traktor-automation
pip install -r requirements.txt
```

Note: Librosa has many dependencies (numpy, scipy, etc.). First install may take a few minutes.

## Usage

```python
from traktor_ai_dj import TraktorAIDJ

# Create controller
dj = TraktorAIDJ()
dj.connect_midi()

# Load playlist (automatically analyzes all tracks)
dj.load_playlist("playlist.json", analyze_audio=True)

# Start AI DJ with intelligent mixing
dj.start()
```

## Performance

**Analysis time**: ~10-30 seconds per track (depending on length and CPU)

**Recommendations**:
- Pre-analyze playlists offline
- Use cache (automatic)
- For live use, analyze during the previous track
- Consider analyzing entire library in advance

## Advanced: Custom Analysis

```python
from audio_analyzer import AudioAnalyzer

analyzer = AudioAnalyzer()

# Analyze single track
analysis = analyzer.analyze_track("track.mp3")

# Get mix points
mix_in = analyzer.get_mix_in_point(analysis)
mix_out = analyzer.get_mix_out_point(analysis)

# Check compatibility
analysis1 = analyzer.analyze_track("track1.mp3")
analysis2 = analyzer.analyze_track("track2.mp3")
compat = analyzer.are_tracks_compatible(analysis1, analysis2)

print(f"Compatibility: {compat['score']}/100")
print(f"Reasons: {compat['reasons']}")
```

## Future Enhancements

1. **Real-time listening**: Analyze Traktor's audio output to detect actual playback position and energy
2. **Machine learning**: Train on your mixing style to learn preferences
3. **Phrase detection**: Find 8/16/32 bar phrases automatically
4. **Vocal detection**: Identify vocal sections vs. instrumentals
5. **Genre classification**: Auto-tag tracks by detected genre
6. **BPM adjustment**: Automatically pitch tracks to match keys
7. **Visual feedback**: Generate waveform displays with cue markers

## Credits

- **Librosa**: McFee et al. (2015)
- **Deep space house mixing theory**: Larry Heard, Moritz von Oswald
- **Harmonic mixing**: Mark Davis (Camelot wheel)
