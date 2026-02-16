# Quick Reference Card

**Traktor AI DJ - Audio Intelligence & Cue Point Automation**

---

## 🚀 Quick Commands

### Analyze Audio
```bash
# Single track
./test_audio_analysis.py /path/to/track.mp3

# Compare two tracks
./test_audio_analysis.py track1.mp3 track2.mp3

# Demo (no audio needed)
./demo_analysis.py
```

### Set Cue Points
```bash
# Check collection
./test_nml_reader.py

# Single track
./traktor_nml_writer.py /path/to/track.mp3

# Entire playlist
./traktor_nml_writer.py playlist.json

# Verify results
./verify_playlist_cues.py
```

### Run AI DJ
```bash
# With audio intelligence
python3 traktor_ai_dj.py
```

---

## 📁 File Locations

### Code
- `audio_analyzer.py` - Audio analysis engine
- `traktor_ai_dj.py` - Main AI DJ controller
- `traktor_nml_writer.py` - Cue point writer

### Data
- **Cache**: `~/.cache/traktor_ai_dj/`
- **Collection**: `~/Documents/Native Instruments/Traktor 3.11.1/collection.nml`
- **Backup**: `collection.backup_TIMESTAMP.nml`
- **Playlist**: `../track-selection-engine/*.json`

### Documentation
- `SESSION_SUMMARY.md` - Complete overview
- `CUE_QUICK_START.md` - 3-step guide
- `AUDIO_ANALYSIS.md` - Technical details
- `INDEX.md` - Full documentation index

---

## 🎯 Cue Point Colors

| Color | Name | Hotcue | Purpose |
|-------|------|--------|---------|
| 🔵 Blue | Intro End | 1 | Good mix-in point |
| 🟢 Green | Breakdown | 2 | **Best mix-in** (low energy) |
| 🟡 Yellow | Build | 3 | Pre-drop (rising energy) |
| 🔴 Red | Drop | 4 | Peak energy |
| 🟣 Purple | Outro | 5 | Good mix-out point |

---

## 📊 What Gets Analyzed

### Audio Features
- **Tempo**: BPM + confidence (85-95% accuracy)
- **Beats**: Precise beat timestamps
- **Energy**: RMS energy over time
- **Key**: Musical key + mode (e.g., "F# minor")
- **Cue Points**: 5 types auto-detected
- **Spectral**: Brightness, rolloff, percussiveness

### Compatibility Check
- Tempo difference (within 6% OK)
- Key compatibility (Camelot wheel)
- Energy difference (<30% smooth)
- **Score**: 0-100 (>80 = perfect match)

---

## 🎚 Blend Duration Logic

| Score | Duration | Description |
|-------|----------|-------------|
| > 80 | 90s | Perfect match → Extended blend |
| 50-80 | 75s | Good match → Normal blend |
| < 50 | 30s | Poor match → Quick blend |

---

## ⚡ Performance

### First Run (Analysis)
- **Per track**: 10-30 seconds
- **30 tracks**: 5-15 minutes
- **Result**: Cached forever

### Subsequent Runs (Cached)
- **Per track**: <1 second
- **30 tracks**: Instant
- **Storage**: ~50KB per track

---

## 🔄 Typical Workflow

### 1. Prepare Playlist
```bash
# Create or load playlist JSON
cd ../track-selection-engine
# Your playlist: best-of-deep-dub-tech-house-ai-ordered.json
```

### 2. Set Cue Points
```bash
cd ../traktor-automation
./traktor_nml_writer.py ../track-selection-engine/playlist.json
# Wait 5-15 minutes (first run)
# Restart Traktor
```

### 3. Verify
```bash
./verify_playlist_cues.py
# Should show 100% with cues
```

### 4. Run DJ
```bash
python3 traktor_ai_dj.py
# AI DJ with intelligent mixing
```

---

## 🛠 Troubleshooting

### "Collection not found"
```bash
# Find it
find ~/Documents -name "collection.nml"

# Use custom path
./traktor_nml_writer.py track.mp3 /path/to/collection.nml
```

### "Track not found in collection"
1. Import track to Traktor first
2. Let Traktor analyze it
3. Close Traktor
4. Run cue writer

### "Cues not appearing"
1. Fully quit Traktor (not just minimize)
2. Reopen Traktor
3. Load the specific track
4. Check for colored hotcue markers

### "No module named 'librosa'"
```bash
pip install -r requirements.txt
```

---

## 💾 Safety & Backups

### Automatic Backups
Every cue write creates:
```
collection.backup_20260216_143022.nml
```

### Manual Backup
```bash
cp ~/Documents/Native\ Instruments/Traktor\ 3.11.1/collection.nml \
   ~/Documents/Native\ Instruments/Traktor\ 3.11.1/collection.SAFE.nml
```

### Restore
```bash
# Quit Traktor first!
cp collection.backup_TIMESTAMP.nml collection.nml
```

---

## 📈 Stats from Test Run

**Playlist**: Best of Deep Dub Tech House
**Date**: Feb 16, 2026

| Metric | Value |
|--------|-------|
| Tracks processed | 30/30 (100%) |
| Total cue points | 121 |
| Avg cues/track | 4.0 |
| Processing time | ~7 minutes |
| Success rate | 100% ✅ |

---

## 🎓 Tips

### For Best Results
- ✅ Use electronic music with clear beats
- ✅ Let analysis run first time (builds cache)
- ✅ Verify a few tracks before batch processing
- ✅ Always backup collection before writing

### For Mixing
- 🟢 **Breakdown** = Best mix-in point
- 🟣 **Outro** = Start mixing out here
- 🔴 **Drop** = Peak energy (don't mix in here)
- 🟡 **Build** = Anticipation (good for suspense)

### For Performance
- Cache is your friend (instant after first run)
- Pre-analyze playlists before sessions
- Use verification script to check results

---

## 📞 Help & Documentation

### Quick Start
- `GETTING_STARTED.md` - New user guide
- `CUE_QUICK_START.md` - 3-step cue setup

### Technical Details
- `AUDIO_ANALYSIS.md` - How it works
- `CUE_POINT_AUTOMATION.md` - Implementation

### Complete Overview
- `SESSION_SUMMARY.md` - Today's work
- `INDEX.md` - Full documentation index

---

## 🎉 You Now Have

✅ Audio analysis (Librosa)
✅ Intelligent mixing (compatibility scoring)
✅ Automatic cue points (121 set!)
✅ Dynamic blend duration (30-90s)
✅ Structure detection (5 cue types)
✅ Batch processing (entire playlists)
✅ Safety (automatic backups)
✅ Speed (caching system)

---

**AI DJ with EARS 👂, BRAIN 🧠, and MEMORY 💾**

**Last Night an AI Saved My Life - and knew exactly when!** 🎧🤖
