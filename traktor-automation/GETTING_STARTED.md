# Getting Started with Audio Intelligence

**Welcome to the intelligent Traktor AI DJ!** 🎧🧠

## 30-Second Overview

The AI DJ can now **"hear"** music and make smart mixing decisions:
- ✅ Detects actual BPM from audio
- ✅ Finds musical key for harmonic mixing
- ✅ Auto-detects cue points (breakdown, drop, intro, outro)
- ✅ Adjusts blend duration based on compatibility
- ✅ Optimizes mix points for seamless transitions

## Installation (2 minutes)

```bash
cd "/Users/dantaylor/Claude/Last Night an AI Saved My Life/traktor-automation"
pip install -r requirements.txt
```

This installs:
- `librosa` - Audio analysis engine
- `numpy`, `scipy` - Scientific computing
- `soundfile` - Audio file reading
- `mido`, `python-rtmidi` - MIDI control

## Quick Demo (30 seconds)

**See what audio analysis looks like** (no audio files needed):
```bash
./demo_analysis.py
```

You'll see:
- 🥁 Tempo detection
- 🎹 Key detection  
- ⚡ Energy analysis
- 📍 Cue point detection
- 🎯 Compatibility scoring

## Test Real Audio (1-2 minutes)

**Analyze a single track**:
```bash
./test_audio_analysis.py /path/to/your/track.mp3
```

**Compare two tracks**:
```bash
./test_audio_analysis.py track1.mp3 track2.mp3
```

Output shows:
- Detected BPM vs. metadata BPM
- Musical key (e.g., "F# minor")
- Energy profile over time
- Auto-detected cue points
- Mix compatibility score

## Run the AI DJ (5-15 minutes first run)

```bash
python3 traktor_ai_dj.py
```

**First run**:
- Analyzes all 30 tracks (~5-15 minutes)
- Caches results for future runs
- Displays analysis for each track

**Subsequent runs**:
- Uses cache (instant startup)
- Only re-analyzes modified files

### What You'll See

```
🎵 Pre-analyzing 30 tracks...

[1/30] Burial - Archangel
  ✓ Detected BPM: 137.2 (confidence: 94.2%)
  ✓ Key: F# minor (confidence: 81.2%)
  ✓ Energy: 0.782
  ✓ Breakdown found: 2:25 - 2:43 (17.6s)
  ✓ Drop at: 4:02

...

✓ Analysis complete! Ready for intelligent mixing.

🚀 STARTING AI DJ PERFORMANCE
```

During transitions:
```
============================================================
TRANSITION 1 → 2
============================================================
  🎯 Mix compatibility: 85/100
  ✨ Using extended blend (90s) for perfect match
  📍 Mix out at: 5:35
  📍 Mix in at: 0:16 (breakdown)
```

## Learn More

### Quick Reads (5 minutes)
- **[BEFORE_AND_AFTER.md](./BEFORE_AND_AFTER.md)** - See the difference
- **[WHATS_NEW.md](./WHATS_NEW.md)** - Feature overview

### Deep Dives (15-30 minutes)
- **[AUDIO_ANALYSIS.md](./AUDIO_ANALYSIS.md)** - Technical details
- **[SUMMARY.md](./SUMMARY.md)** - Complete system overview

### Reference
- **[README.md](./README.md)** - Setup instructions
- **[requirements.txt](./requirements.txt)** - Dependencies

## Troubleshooting

### "No module named 'librosa'"
```bash
pip install librosa
```

### "Audio file not found"
Check that `file_path` in playlist JSON points to actual files:
```bash
# Verify file exists
ls -l "/path/from/playlist.json"
```

### "Analysis taking forever"
- Normal: 10-30 seconds per track
- Use cache on subsequent runs
- Consider pre-analyzing offline

### "MIDI not connecting"
```bash
# Check IAC Driver
python3 test_midi_connection.py

# Verify Traktor setup
open TRAKTOR_MIDI_MAPPING_GUIDE.md
```

## Next Steps

1. **Test analysis** on your music:
   ```bash
   ./test_audio_analysis.py /path/to/track.mp3
   ```

2. **Pre-analyze your library** (optional but recommended):
   ```bash
   # This builds cache for instant future runs
   python3 traktor_ai_dj.py
   ```

3. **Run a live set** with intelligent mixing!

4. **Experiment** with different playlists and genres

5. **Read the docs** to understand how it works

## FAQ

**Q: Does this replace manual DJing?**  
A: No - it's for automated sets, practice, and research. Manual DJing has nuance this can't capture.

**Q: How accurate is the BPM detection?**  
A: 95%+ for electronic music with clear beats. Lower for ambient/experimental.

**Q: Can it detect vocals?**  
A: Not yet - future enhancement.

**Q: Does it work with all genres?**  
A: Best with electronic music (house, techno, dub). Works OK with most genres with clear beats.

**Q: How much disk space does cache use?**  
A: ~50KB per track. 30 tracks = ~1.5MB.

**Q: Can I disable audio analysis?**  
A: Yes: `load_playlist(path, analyze_audio=False)`

**Q: What if my tracks aren't in the playlist JSON?**  
A: You can analyze any audio file directly with `test_audio_analysis.py`

## Support

- **Issues**: Check existing documentation
- **Questions**: Read [AUDIO_ANALYSIS.md](./AUDIO_ANALYSIS.md)
- **Bugs**: File descriptive issue reports

---

**Ready to let AI hear your music? Let's go! 🚀**
