# Cue Point Automation - Quick Start

Automatically set Traktor cue points from audio analysis in **3 simple steps**.

## What This Does

The AI analyzes your tracks and automatically sets cue points in Traktor:

- 🔵 **Intro End** - Where intro finishes (perfect for mixing in)
- 🟢 **Breakdown** - Low energy section (ideal mix-in point)
- 🟡 **Build** - Rising energy (leading to drop)
- 🔴 **Drop** - Peak energy moment
- 🟣 **Outro** - Where outro starts (mix-out point)

## Method: NML File Writing

This method directly writes cue points to Traktor's collection file (`collection.nml`).

**Pros**:
- ✅ Sample-accurate precision
- ✅ Set all cues at once
- ✅ No MIDI seeking required

**Cons**:
- ⚠️ Requires Traktor restart to see cues
- ⚠️ Must backup collection first

## Step 1: Test Collection Reading

First, verify we can read your collection:

```bash
./test_nml_reader.py
```

Expected output:
```
======================================================================
TRAKTOR COLLECTION INFO
======================================================================

📁 Collection: /Users/you/Documents/.../collection.nml
🎵 Total tracks: 1523

======================================================================
SAMPLE TRACKS
======================================================================

Track 1: Burial - Archangel.mp3
  Cue points: 3
    • Intro
      Time: 16.2s
      Hotcue: 1
      ...
```

If successful, continue to step 2.

## Step 2: Set Cues for Single Track (Test)

Test with one track first:

```bash
./traktor_nml_writer.py /path/to/track.mp3
```

What happens:
1. Analyzes track with Librosa (~15 seconds)
2. Detects cue points (intro, breakdown, drop, outro)
3. Writes to collection.nml (with backup)
4. Displays results

Expected output:
```
🎵 Processing: track.mp3
🎧 Analyzing audio...
  ✓ Detected BPM: 122.3 (confidence: 94.2%)
  ✓ Key: F# minor
  ✓ Energy: 0.782
  ✓ Breakdown found: 2:25 - 2:43

✓ Intro End: 32.4s → Hotcue 1
✓ Breakdown: 145.2s → Hotcue 2
✓ Drop: 242.4s → Hotcue 3
✓ Outro: 334.8s → Hotcue 4
✅ Added 4 cue points

💾 Backup created: collection.backup_20260216_143022.nml
✅ Collection saved

🎉 Done! Restart Traktor to see new cue points.
```

### Verify in Traktor

1. **Restart Traktor** (required to reload collection)
2. **Load the track** you just processed
3. **Look at the deck** - you should see 4-5 colored hotcue markers
4. **Click each hotcue** to jump to those points

If you see the cues, it worked! Proceed to step 3.

## Step 3: Batch Process Playlist

Process all tracks in your playlist:

```bash
./traktor_nml_writer.py ../track-selection-engine/best-of-deep-dub-tech-house-ai-ordered.json
```

What happens:
1. Loads playlist JSON
2. Analyzes each track (~10-30s per track)
3. Writes all cue points to collection
4. Creates backup

Expected timeline for 30 tracks:
- Analysis: 5-15 minutes (using cache if available)
- Writing: <1 second
- Total: ~5-15 minutes

Example output:
```
📋 Loading playlist: best-of-deep-dub-tech-house-ai-ordered.json

🎵 Processing 30 tracks...

[1/30] Burial - Archangel
  🎧 Analyzing audio...
  ✓ Intro End: 32.4s → Hotcue 1
  ✓ Breakdown: 145.2s → Hotcue 2
  ✓ Build: 225.6s → Hotcue 3
  ✓ Drop: 242.4s → Hotcue 4
  ✓ Outro: 334.8s → Hotcue 5
  ✅ Added 5 cue points

[2/30] Basic Channel - Phylyps Trak II
  🎧 Analyzing audio...
  ✓ Intro End: 28.1s → Hotcue 1
  ✓ Breakdown: 112.5s → Hotcue 2
  ✓ Outro: 301.2s → Hotcue 3
  ✅ Added 3 cue points

...

[30/30] Moritz von Oswald - Silencio
  ...

✅ Processed 30/30 tracks

💾 Backup created: collection.backup_20260216_143534.nml
✅ Collection saved

🎉 Done! Restart Traktor to see new cue points.
```

### Verify in Traktor

1. **Restart Traktor**
2. **Load any track** from the playlist
3. **Check hotcues** - should see 3-5 colored markers per track
4. **Try jumping** between cues while track plays

## Understanding the Cue Points

### Intro End (Blue, Hotcue 1)
- End of intro section (usually 16-32 bars)
- Track has established rhythm
- Good for mixing in

### Breakdown (Green, Hotcue 2)
- Low energy section
- Often minimal (just kick drum or bass)
- **Best point to mix in** - creates seamless blend

### Build (Yellow/Orange, Hotcue 3)
- Rising energy section
- Leads up to drop
- Good for anticipation

### Drop (Red, Hotcue 4)
- Peak energy moment
- Full frequency spectrum
- Avoid mixing in here (too busy)

### Outro (Purple, Hotcue 5)
- Start of outro/ending
- **Good point to start mixing out**
- Energy typically decreasing

## Using Cues During AI DJ Set

Once cues are set, the AI DJ can use them:

```python
# In future update:
# AI DJ automatically jumps to breakdown for mix-in
# Instead of starting at 0:00, starts at breakdown cue
```

This creates smoother transitions because both tracks are in low-energy sections.

## Advanced: Custom Cue Points

Edit `traktor_nml_writer.py` to customize:

```python
def add_cues_from_analysis(self, file_path: str, analysis: Dict):
    # ... existing code ...

    # Add custom cue (e.g., vocal start)
    if 'vocal_start' in analysis:
        self.add_cue_point(entry, 'Vocal', analysis['vocal_start'], 6,
                         color=5)  # Custom color
```

## Backup & Safety

### Automatic Backups

Every time you write cues, a timestamped backup is created:
```
collection.nml
collection.backup_20260216_143022.nml
collection.backup_20260216_143534.nml
...
```

### Manual Backup

Before first run:
```bash
cp ~/Documents/Native\ Instruments/Traktor\ 3.0/collection.nml \
   ~/Documents/Native\ Instruments/Traktor\ 3.0/collection.SAFE_BACKUP.nml
```

### Restore from Backup

If something goes wrong:
```bash
# Stop Traktor first!

# Restore from backup
cp ~/Documents/Native\ Instruments/Traktor\ 3.0/collection.backup_20260216_143022.nml \
   ~/Documents/Native\ Instruments/Traktor\ 3.0/collection.nml

# Restart Traktor
```

## Troubleshooting

### "Collection not found"

Check paths:
```bash
# Find collection
find ~/Documents -name "collection.nml" 2>/dev/null

# Use custom path
./traktor_nml_writer.py track.mp3 /path/to/collection.nml
```

### "Track not found in collection"

The track must be in Traktor's collection first:
1. Open Traktor
2. Import the track/folder
3. Wait for Traktor to analyze
4. Close Traktor
5. Run cue writer

### Cues not appearing after restart

- Check Traktor actually restarted (quit completely, not just minimized)
- Verify collection.nml was modified (check timestamp)
- Load the specific track (don't rely on browser preview)
- Check Console.app for Traktor errors

### Wrong cue times

Audio analysis isn't perfect:
- BPM detection: 85-95% accurate
- Breakdown detection: 70-80% accurate
- Adjust manually in Traktor if needed

### Cues overwrite existing ones

By design - script removes existing cues in same slots before writing new ones.

To preserve manual cues, edit `add_cue_point()`:
```python
# Don't remove existing cues
# for existing_cue in entry.findall('CUE_V2'):
#     if int(existing_cue.get('HOTCUE', -1)) == slot:
#         entry.remove(existing_cue)
```

## What's Next

After setting cues:

1. **Manual review**: Load each track, verify cues make sense
2. **Adjust if needed**: Traktor lets you drag/move cues
3. **Run AI DJ**: Cues are now set for intelligent mixing
4. **Future**: AI DJ will use cues to jump to optimal mix points

## Files

- **`traktor_nml_writer.py`** - Main cue writer (320 lines)
- **`test_nml_reader.py`** - Collection reader/inspector (200 lines)
- **`CUE_POINT_AUTOMATION.md`** - Technical documentation
- **`CUE_QUICK_START.md`** - This guide

## Resources

- Traktor collection.nml format: Native Instruments documentation
- Librosa accuracy: 85-95% for clear electronic music
- Cue point best practices: DJ technique guides

---

**Give your AI DJ perfect memory - automatically!** 🎧💾🤖
