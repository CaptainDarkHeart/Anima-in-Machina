# AI DJ MCP Server — Usage Examples

All examples assume the server is running and tracks have been analysed in Traktor.

---

## 1. Check what Traktor knows about a track

**Prompt:**
```
Get track info for "Stimming - Una Pena.m4a"
```

**Response:**
```
Track Info: Stimming - Una Pena.m4a

Traktor Analysis (from collection.nml):
  BPM:         122.000
  Key:         8m  (Bb min)
  Duration:    6:16.45
  Beatgrid:    ✓ beatgrid present
  Anchor:      0.123s

Loudness / Auto-gain:
  Peak:        -3.21 dB
  Perceived:   -8.44 dB
  Analyzed:    -6.12 dB

Existing cue points:
  Slot 2: 0:37.84  Beat
  Slot 3: 4:05.12  Breakdown
  Slot 4: 2:12.56  Groove  [loop 52.2s]
  Slot 5: 5:24.00  End
```

Use this to verify Traktor's analysis before writing cues, or to confirm what slots are already occupied.

---

## 2. Auto-write cue points (NML only)

**Prompt:**
```
Suggest cue points for "Lucidflow - Atmospheric Journey.m4a"
```

**Response:**
```
Cue Points: Lucidflow - Atmospheric Journey.m4a
Source: nml
BPM: 120.000  |  Anchor: 0.084ms  |  Duration: 412.3s

Calculated positions (bar-snapped):
  Slot 2  Beat:      41.08s  (0:41.08)
  Slot 3  Breakdown: 268.15s  (4:28.15)
  Slot 4  Groove:    144.30s  (2:24.30)  [loop 64.0s]
  Slot 5  End:       348.15s  (5:48.15)

  📋 Beat: estimated at ~10% — verify kick entry in Traktor
  📋 Breakdown: estimated at ~65% — verify in Traktor

✅ Written to collection.nml (backup: collection_backup_20260219_143022.nml):
   Slot 2 (Beat): 41.08s
   Slot 3 (Breakdown): 268.15s
   Slot 4 (Groove): 144.30s  [loop 64.0s]
   Slot 5 (End): 348.15s

⚠️  Restart Traktor to load the updated collection.
```

The positions are bar-snapped to Traktor's beatgrid. Verify the Beat cue in Traktor since the 10% estimate may not land on the first kick of the intro.

---

## 3. Auto-write cues with librosa breakdown detection

Providing the audio path lets the server find the actual energy low point instead of estimating at 65%.

**Prompt:**
```
Suggest cue points for "Lucidflow - Atmospheric Journey.m4a"
using /Users/dantaylor/Music/Lucidflow - Atmospheric Journey.m4a
```

**Response excerpt:**
```
Source: nml+librosa
...
  📋 Breakdown: detected at 261.3s by energy analysis
  📋 BPM verified: Traktor 120.000 ≈ librosa 120.1 ✓
```

librosa scans the 40–80% zone for the lowest-energy 30-second window and snaps the result to the nearest bar.

---

## 4. Overwrite existing cues

By default, occupied slots are skipped. To replace them:

**Prompt:**
```
Suggest cue points for "Lucidflow - Atmospheric Journey.m4a" — overwrite existing
```

Or explicitly: `overwrite=true`. The server will remove the old cues in slots 2–5 and write the new ones. Slot 1 is always protected regardless.

---

## 5. Manually write a specific cue

After reviewing the auto-suggestions in Traktor, you may want to adjust one position.

**Prompt:**
```
Write a cue point for "Lucidflow - Atmospheric Journey.m4a":
  slot 3, name "Breakdown", time 261300ms, overwrite existing
```

**Response:**
```
Write Cue Points: Lucidflow - Atmospheric Journey.m4a

✅ Written (backup: collection_backup_20260219_143155.nml):
   Slot 3 (Breakdown): 261.30s

⚠️  Restart Traktor to load the updated collection.
```

---

## 6. Plan a transition between two tracks

**Prompt:**
```
Suggest a transition from "Lucidflow - Atmospheric Journey.m4a"
to "Echocord - Deep Pulse.m4a"
```

**Response:**
```
Transition Analysis
==================================================

Outgoing: Lucidflow - Atmospheric Journey.m4a
  BPM: 120.000  |  Key: 9m (F min)  |  Duration: 6:52.30

Incoming: Echocord - Deep Pulse.m4a
  BPM: 121.800  |  Key: 8m (Bb min)  |  Duration: 6:29.67

BPM:  ✓ Direct beatmatch  (ratio 0.985)
      Adjust by 1.8 BPM

Key:  ✓ adjacent key — energy shift mix

Timing (32-bar blend at 120.0 BPM = 64s):
  Start blend at:   5:48.30 into outgoing track
  Incoming starts:  from beginning

Suggested technique:
  1. At blend start, bring incoming up under the outgoing bass
  2. Over 32s: cut bass on outgoing, add bass on incoming
  3. Use mid-EQ swell to mask the transition
  4. Trim outgoing highs as incoming establishes

  ✓ Loudness match: 1.2 dB difference (acceptable)
```

To use a longer or shorter blend:

**Prompt:**
```
Suggest transition from "Track A.m4a" to "Track B.m4a" with a 16-bar blend
```

---

## 7. Full analysis with librosa cross-check

**Prompt:**
```
Analyze "Lucidflow - Atmospheric Journey.m4a" at
/Users/dantaylor/Music/Lucidflow - Atmospheric Journey.m4a
```

**Response:**
```
Full Analysis: Lucidflow - Atmospheric Journey.m4a
============================================================

── Traktor (collection.nml) ──────────────────────────────
  BPM:       120.000
  Key:       9m  (F min)
  Duration:  6:52.30
  Beatgrid:  ✓ present
  Anchor:    0.084ms
  Peak dB:   -2.45
  Perceived: -7.88 dB

── librosa ──────────────────────────────────────────────
  BPM:       120.1  ✓ agree
  Beats:     826 detected
  Breakdown: 261.3s detected by energy analysis

── Suggested cue positions ───────────────────────────────
  Slot 2  Beat:      0:41.08
  Slot 3  Breakdown: 4:21.30
  Slot 4  Groove:    2:24.30  [loop 64s]
  Slot 5  End:       5:48.30
  Source: nml+librosa

  📋 Breakdown: detected at 261.3s by energy analysis
  📋 BPM verified: Traktor 120.000 ≈ librosa 120.1 ✓
```

This does not write anything — it's a read-only analysis. Use `suggest_cue_points` to write.

---

## 8. Batch workflow: process a playlist

To process multiple tracks in sequence, describe them to Claude:

**Prompt:**
```
For each of these tracks, suggest cue points (NML only):
- "Stimming - Una Pena.m4a"
- "Lucidflow - Atmospheric Journey.m4a"
- "Echocord - Deep Pulse.m4a"
Skip any track that already has cues in slots 2-5.
```

Claude will call `get_track_info` to check existing cues first, then call `suggest_cue_points` only for tracks with empty slots.

---

## Tips

- **Filenames must match exactly** — use `get_track_info` to confirm a track is in the collection before writing
- **Always restart Traktor** after writing — cues won't appear until Traktor re-reads the NML
- **Verify Beat cues** — the 10% position may not land on the first kick; nudge it in Traktor if needed
- **Groove is a loop** — slot 4 is a 32-bar saved loop, not a hot cue; make sure Traktor's Loop Recorder is off when you trigger it
- **Backups accumulate** — periodically clean up old `collection_backup_*.nml` files from your Traktor folder
