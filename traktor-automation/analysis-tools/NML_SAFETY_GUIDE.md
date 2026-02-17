# NML Safety Guide - CRITICAL INFORMATION

## ⚠️ WARNING: Protecting Traktor's Essential Cue Points

### The Problem

Traktor uses specific cue points that are **essential** for proper track operation:

1. **Floating Cue Point** (Hotcue 1, TYPE=4)
   - Always the first cue point in a track
   - Starting point for all cue point work
   - Starting point for storing loops
   - **MUST NEVER BE DELETED**

2. **AutoGrid** (TYPE=4)
   - Traktor's beatgrid anchor point
   - Critical for beat sync
   - Should be preserved

3. **User's Manual Cue Points**
   - Manually placed by DJ during preparation
   - Contain DJ's knowledge and preferences
   - **Take precedence over automated cue points**

### The Critical Fix

**NEVER** use `replace_existing=True` when adding cue points!

```python
# ❌ WRONG - Deletes all existing cue points
writer.add_cue_points_to_track(audio_file, cue_points, replace_existing=True)

# ✅ CORRECT - Only adds new cue points
writer.add_cue_points_to_track(audio_file, cue_points, replace_existing=False)
```

## Safe Usage

### Adding Cue Points to Tracks

```python
from nml_writer import NMLWriter

writer = NMLWriter()
writer.load()

# This will ADD cue points without deleting existing ones
writer.add_cue_points_to_track(
    audio_file=Path("track.m4a"),
    cue_points=analysis['cue_points'],
    replace_existing=False  # CRITICAL: Must be False!
)

writer.save()  # Automatic backup created
```

### Batch Processing

```python
from nml_writer import NMLWriter

writer = NMLWriter()
writer.load()

# Batch add - will NOT delete existing cue points
successful, failed = writer.batch_add_cue_points(
    analysis_files,
    replace_existing=False  # Default is False for safety
)

writer.save()
```

## Understanding Traktor's Cue Point Types

### TYPE Values

- `TYPE="0"` - Regular cue point (the ones we add)
- `TYPE="4"` - Grid marker / Floating cue point (DO NOT DELETE!)

### HOTCUE Values

- `HOTCUE="0"` - Not a hotcue (our automated cue points)
- `HOTCUE="1"` - Hotcue 1 (Floating Cue Point - CRITICAL!)
- `HOTCUE="2-8"` - Other hotcues (user-assigned)

### Example from NML

```xml
<!-- Floating Cue Point - NEVER DELETE THIS! -->
<CUE_V2 NAME="AutoGrid" TYPE="4" START="176.029772" HOTCUE="1" />

<!-- User's manual cue points - PRESERVE THESE! -->
<CUE_V2 NAME="Mix In" TYPE="0" START="15000.0" HOTCUE="0" />
<CUE_V2 NAME="Drop" TYPE="0" START="95000.0" HOTCUE="0" />

<!-- Our automated cue points - OK to add -->
<CUE_V2 NAME="Build 1" TYPE="0" START="200000.0" HOTCUE="0" />
```

## Recovery from Mistakes

### If You Accidentally Deleted Cue Points

1. **Check for backups** - NML writer creates automatic backups
   ```bash
   ls -lt ~/Documents/Native\ Instruments/Traktor\ 3.11.1/collection_backup_*.nml
   ```

2. **Restore from backup**
   ```bash
   cp collection_backup_YYYYMMDD_HHMMSS.nml collection.nml
   ```

3. **Restart Traktor** to load the restored collection

### Backup Locations

Backups are created in the same directory as collection.nml:
```
~/Documents/Native Instruments/Traktor 3.11.1/
├── collection.nml
├── collection_backup_20260217_111542.nml
├── collection_backup_20260217_111608.nml
└── ...
```

## Best Practices

### 1. Always Test on One Track First

```python
# Test on a single track before batch processing
writer.add_cue_points_to_track(
    test_track,
    test_cue_points,
    replace_existing=False
)
writer.save()

# Check in Traktor that existing cue points are preserved
# Then proceed with batch processing
```

### 2. Check Traktor After Adding Cue Points

1. Open Traktor
2. Load a processed track
3. Verify:
   - ✅ Floating Cue Point (Hotcue 1) still exists
   - ✅ Manual cue points preserved
   - ✅ New automated cue points added

### 3. Manual Cue Points Take Precedence

If you've manually placed cue points on tracks:
- **DO NOT** run batch processing with `replace_existing=True`
- The automated system should **supplement**, not **replace** your work
- Your DJ knowledge > Automated analysis

## Workflow Recommendations

### For New Tracks (Not Yet Prepared)

1. Run hybrid analysis
2. Write cue points to NML with `replace_existing=False`
3. Review in Traktor
4. Manually adjust as needed

### For Already Prepared Tracks

1. **DO NOT** run automated cue point writing
2. Your manual cue points are more valuable
3. Use analysis for reference only
4. Manually add any insights from analysis

### For Mixed Collections

1. Identify which tracks have manual cue points
2. Only process tracks without manual preparation
3. Skip tracks that are already prepared

## Technical Details

### Cue Point Structure

```xml
<CUE_V2
    NAME="Cue Point Name"
    DISPL_ORDER="0"
    TYPE="0"
    START="123456.789"  <!-- Milliseconds -->
    LEN="0.000000"
    REPEATS="-1"
    HOTCUE="0"
/>
```

### Critical Attributes

- `NAME` - Cue point name (visible in Traktor)
- `TYPE` - 0=cue, 4=grid marker
- `START` - Position in milliseconds (beat-precise)
- `HOTCUE` - 0=not hotcue, 1-8=hotcue number

## Code Defaults

All functions now default to **safe mode**:

```python
# nml_writer.py defaults
def add_cue_points_to_track(..., replace_existing=False):  # ✅ Safe default

def batch_add_cue_points(..., replace_existing=False):  # ✅ Safe default
```

## Summary

**Golden Rules:**

1. ⛔ **NEVER** delete existing cue points
2. ✅ **ALWAYS** use `replace_existing=False`
3. 💾 **ALWAYS** check backups exist
4. 🎧 **ALWAYS** verify in Traktor after processing
5. 👤 **Manual cue points > Automated cue points**

---

**Last Updated**: February 17, 2026
**Status**: Critical safety guidelines - READ BEFORE using NML writer
