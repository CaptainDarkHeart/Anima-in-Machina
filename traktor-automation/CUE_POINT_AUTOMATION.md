# Traktor Cue Point Automation via MIDI

## Goal

Automatically set Traktor cue points based on Librosa audio analysis:
- Intro/Outro markers
- Breakdown points (perfect for mixing in)
- Build-up sections
- Drop points (energy peaks)
- Beat grid verification

## Traktor's Cue Point System

### Cue Point Types in Traktor Pro 3

1. **Load Marker** (white) - Where track loads by default
2. **Cue Points (Hotcues)** - 8 per deck, color-coded
3. **Grid Marker** - Beatgrid anchor point
4. **Loop In/Out** - Loop markers

### MIDI Access to Cue Points

Traktor exposes these MIDI-mappable functions:

#### Setting Cue Points
```
Deck A/B > Cue > Store Hotcue 1-8
Deck A/B > Cue > Delete Hotcue 1-8
```

#### Jumping to Cue Points
```
Deck A/B > Cue > Select/Set+Store Hotcue 1-8
```

#### Setting Load Marker
```
Deck A/B > Track > Set Beatjump Load Marker
```

## How Traktor Stores Cue Points

Traktor stores cue points in `collection.nml`:

```xml
<ENTRY>
  <LOCATION DIR="Music/" FILE="track.mp3"/>
  <CUE_V2 NAME="Intro" TYPE="0" START="16.234" LEN="0.000" HOTCUE="0"/>
  <CUE_V2 NAME="Breakdown" TYPE="0" START="145.234" LEN="0.000" HOTCUE="1"/>
  <CUE_V2 NAME="Drop" TYPE="0" START="242.456" LEN="0.000" HOTCUE="2"/>
</ENTRY>
```

**Key fields**:
- `NAME`: Cue point name
- `START`: Time in seconds (float)
- `HOTCUE`: Slot number (0-7 for hotcues 1-8)
- `TYPE`: 0 = cue point, 4 = loop

## Challenge: Time-Based Positioning

### The Problem

**MIDI can't directly set cue point at specific time**

Traktor's MIDI interface allows:
- ✅ Store cue at **current playback position**
- ✅ Jump to existing cue points
- ❌ Store cue at **arbitrary time** (e.g., 2:34.5)

### The Solution: Seek & Store

To set a cue point at a specific time:

1. **Seek to target time**
2. **Store cue point**
3. **Return to original position** (optional)

## Implementation Strategies

### Strategy 1: Seek + Store (MIDI-based)

**Pros**: Pure MIDI, no file manipulation
**Cons**: Requires precise seeking, playback manipulation

```python
def set_cue_point(deck: int, time_seconds: float, hotcue_slot: int):
    """
    Set a cue point at specific time via MIDI.

    Steps:
    1. Seek to target time
    2. Store hotcue at that position
    3. Return to playback position
    """
    # 1. Seek to target time
    #    Problem: No direct "seek to time" MIDI command
    #    Need to use: Beatjump, Loop Move, or manual scrubbing

    # 2. Store hotcue
    send_cc(MIDI_CC[f'deck_{deck}_store_hotcue_{hotcue_slot}'], 127)

    # 3. Return to original position
    #    Jump back to load marker or use Beatjump
```

**Seeking Options**:

a) **Beatjump** (most accurate for beat-aligned cues)
```
Deck A/B > Track > Beatjump +/- [size]
```
- Jump in beat increments (1, 2, 4, 8, 16, 32 beats)
- Snap to beatgrid

b) **Jog Wheel Simulation**
```
Deck A/B > Deck Common > Jog Wheel (Scratch mode off)
```
- Continuous control, harder to target exact time

c) **Loop Move**
```
Deck A/B > Loop Recorder > Loop Move +/-
```
- Move loop position, requires active loop

### Strategy 2: Direct NML Manipulation

**Pros**: Precise control, set all cues at once
**Cons**: Requires Traktor restart, file parsing/writing

```python
import xml.etree.ElementTree as ET

def set_cues_in_nml(track_path: str, cue_points: List[Dict]):
    """
    Directly write cue points to collection.nml

    Requires:
    1. Parse collection.nml
    2. Find track entry
    3. Add/update CUE_V2 elements
    4. Write back to file
    5. Restart Traktor to reload
    """
    # Parse NML
    tree = ET.parse('/path/to/collection.nml')
    root = tree.getroot()

    # Find track
    for entry in root.findall('.//ENTRY'):
        location = entry.find('LOCATION')
        if location.get('FILE') == track_path:
            # Add cue points
            for i, cue in enumerate(cue_points):
                cue_elem = ET.SubElement(entry, 'CUE_V2')
                cue_elem.set('NAME', cue['name'])
                cue_elem.set('TYPE', '0')
                cue_elem.set('START', str(cue['time']))
                cue_elem.set('HOTCUE', str(i))

    # Write back
    tree.write('collection.nml')
```

### Strategy 3: Hybrid Approach (Recommended)

**Combine both strategies**:

1. **Pre-session**: Use NML manipulation to set all cue points
2. **During session**: Use MIDI for dynamic cues

## Practical Implementation

### Step 1: Add MIDI Mappings for Hotcues

Extend the MIDI mapping with:

```python
# In traktor_ai_dj.py
self.MIDI_CC = {
    # ... existing mappings ...

    # Hotcue storage (deck A)
    'deck_a_store_hotcue_1': 50,
    'deck_a_store_hotcue_2': 51,
    'deck_a_store_hotcue_3': 52,
    'deck_a_store_hotcue_4': 53,
    'deck_a_store_hotcue_5': 54,
    'deck_a_store_hotcue_6': 55,
    'deck_a_store_hotcue_7': 56,
    'deck_a_store_hotcue_8': 57,

    # Hotcue storage (deck B)
    'deck_b_store_hotcue_1': 58,
    'deck_b_store_hotcue_2': 59,
    'deck_b_store_hotcue_3': 60,
    'deck_b_store_hotcue_4': 61,
    'deck_b_store_hotcue_5': 62,
    'deck_b_store_hotcue_6': 63,
    'deck_b_store_hotcue_7': 64,
    'deck_b_store_hotcue_8': 65,

    # Hotcue jumps (deck A)
    'deck_a_jump_hotcue_1': 66,
    'deck_a_jump_hotcue_2': 67,
    # ... etc

    # Beatjump (for seeking)
    'deck_a_beatjump_forward': 80,
    'deck_a_beatjump_backward': 81,
    'deck_b_beatjump_forward': 82,
    'deck_b_beatjump_backward': 83,
}
```

### Traktor MIDI Mapping Setup

In Traktor Controller Manager:

| Function | Type | CC# | Assignment |
|----------|------|-----|------------|
| Store Hotcue 1 (A) | In | 50 | Deck A > Cue > Store Hotcue 1 |
| Store Hotcue 2 (A) | In | 51 | Deck A > Cue > Store Hotcue 2 |
| ... | ... | ... | ... |
| Beatjump Fwd (A) | In | 80 | Deck A > Track > Beatjump +32 |
| Beatjump Back (A) | In | 81 | Deck A > Track > Beatjump -32 |

### Step 2: Implement Seeking Functions

```python
def seek_to_beat(self, deck: int, target_beat: int):
    """
    Seek to specific beat using beatjump.

    Args:
        deck: 1 or 2
        target_beat: Beat number to seek to
    """
    # Get current position in beats
    current_beat = self.get_current_beat(deck)
    beat_diff = target_beat - current_beat

    # Jump in 32-beat increments
    while abs(beat_diff) >= 32:
        if beat_diff > 0:
            self.beatjump_forward(deck, 32)
            beat_diff -= 32
        else:
            self.beatjump_backward(deck, 32)
            beat_diff += 32

    # Fine-tune with smaller jumps
    while abs(beat_diff) >= 1:
        if beat_diff > 0:
            self.beatjump_forward(deck, 1)
            beat_diff -= 1
        else:
            self.beatjump_backward(deck, 1)
            beat_diff += 1

def time_to_beats(self, time_seconds: float, bpm: float) -> int:
    """Convert time to beat number."""
    beats_per_second = bpm / 60.0
    return int(time_seconds * beats_per_second)
```

### Step 3: Auto-Set Cue Points from Analysis

```python
def set_analyzed_cue_points(self, track_index: int, deck: int):
    """
    Set cue points based on audio analysis.

    Args:
        track_index: Track index in playlist
        deck: Deck to set cues on (1 or 2)
    """
    analysis = self.track_analyses.get(track_index)
    if not analysis:
        self.log("⚠ No analysis available for cue points")
        return

    track = self.playlist['tracks'][track_index]
    bpm = analysis['tempo']['bpm']
    cue_points_data = analysis['cue_points']

    cue_map = [
        # (name, time, hotcue_slot)
        ('Intro', cue_points_data.get('intro_end', 0), 1),
    ]

    # Add breakdown if detected
    if 'breakdown' in cue_points_data:
        breakdown = cue_points_data['breakdown']
        cue_map.append(('Breakdown', breakdown['start'], 2))

    # Add build if detected
    if 'build' in cue_points_data:
        build = cue_points_data['build']
        cue_map.append(('Build', build['start'], 3))

    # Add drop if detected
    if 'drop' in cue_points_data:
        drop = cue_points_data['drop']
        cue_map.append(('Drop', drop['time'], 4))

    # Add outro
    cue_map.append(('Outro', cue_points_data.get('outro_start', 0), 5))

    self.log(f"📍 Setting {len(cue_map)} cue points from audio analysis")

    # Pause deck while setting cues
    was_playing = self.is_playing
    if was_playing:
        self.pause_deck(deck)

    # Set each cue point
    for name, time, slot in cue_map:
        beat = self.time_to_beats(time, bpm)
        self.log(f"  Setting {name} at {time:.1f}s (beat {beat}) → Hotcue {slot}")

        # Seek to beat
        self.seek_to_beat(deck, beat)

        # Store hotcue
        self.store_hotcue(deck, slot)

        # Wait for Traktor to process
        time.sleep(0.1)

    # Return to start
    self.seek_to_beat(deck, 0)

    # Resume playback if was playing
    if was_playing:
        self.play_deck(deck)

    self.log(f"✓ Cue points set for: {track['artist']} - {track['title']}")
```

## Alternative: NML File Automation

For batch processing or pre-session setup:

```python
import xml.etree.ElementTree as ET
from pathlib import Path

class TraktorNMLCueWriter:
    """Write cue points directly to Traktor collection.nml"""

    def __init__(self, collection_path: str = None):
        if collection_path is None:
            # Default Traktor collection location
            collection_path = str(Path.home() /
                "Documents/Native Instruments/Traktor 3.0/collection.nml")

        self.collection_path = collection_path
        self.tree = None
        self.root = None

    def load_collection(self):
        """Load and parse collection.nml"""
        self.tree = ET.parse(self.collection_path)
        self.root = self.tree.getroot()

    def find_track_entry(self, file_path: str):
        """Find track entry in collection by file path"""
        for entry in self.root.findall('.//ENTRY'):
            location = entry.find('LOCATION')
            if location is not None:
                entry_file = location.get('FILE', '')
                if Path(entry_file).name == Path(file_path).name:
                    return entry
        return None

    def add_cue_points(self, file_path: str, cue_points: List[Dict]):
        """
        Add cue points to a track.

        Args:
            file_path: Path to audio file
            cue_points: List of dicts with keys:
                - name: Cue point name
                - time: Time in seconds (float)
                - slot: Hotcue slot (0-7)
        """
        entry = self.find_track_entry(file_path)
        if entry is None:
            print(f"Track not found in collection: {file_path}")
            return False

        # Remove existing cues for these slots
        existing_cues = entry.findall('CUE_V2')
        for cue in existing_cues:
            hotcue = int(cue.get('HOTCUE', -1))
            if hotcue in [cp['slot'] for cp in cue_points]:
                entry.remove(cue)

        # Add new cues
        for cue in cue_points:
            cue_elem = ET.SubElement(entry, 'CUE_V2')
            cue_elem.set('NAME', cue['name'])
            cue_elem.set('TYPE', '0')  # 0 = cue point
            cue_elem.set('START', f"{cue['time']:.3f}")
            cue_elem.set('LEN', '0.000')
            cue_elem.set('HOTCUE', str(cue['slot']))

        return True

    def save_collection(self, backup: bool = True):
        """Save collection.nml (with optional backup)"""
        if backup:
            backup_path = f"{self.collection_path}.backup"
            import shutil
            shutil.copy2(self.collection_path, backup_path)
            print(f"Backup created: {backup_path}")

        self.tree.write(self.collection_path, encoding='utf-8', xml_declaration=True)
        print(f"Collection saved: {self.collection_path}")
```

### Usage:

```python
from audio_analyzer import AudioAnalyzer

# Analyze track
analyzer = AudioAnalyzer()
analysis = analyzer.analyze_track('track.mp3')

# Prepare cue points
cue_points = []

if 'breakdown' in analysis['cue_points']:
    breakdown = analysis['cue_points']['breakdown']
    cue_points.append({
        'name': 'Breakdown',
        'time': breakdown['start'],
        'slot': 1
    })

if 'drop' in analysis['cue_points']:
    drop = analysis['cue_points']['drop']
    cue_points.append({
        'name': 'Drop',
        'time': drop['time'],
        'slot': 2
    })

# Write to collection
nml_writer = TraktorNMLCueWriter()
nml_writer.load_collection()
nml_writer.add_cue_points('track.mp3', cue_points)
nml_writer.save_collection(backup=True)

print("Cue points written! Restart Traktor to see them.")
```

## Recommended Workflow

### Option A: Pre-Session Setup (NML Method)

Best for: Preparing a set in advance

```bash
# 1. Analyze all tracks and write cues to collection
python3 batch_set_cues.py playlist.json

# 2. Restart Traktor to load new cues

# 3. Run AI DJ (cues already set!)
python3 traktor_ai_dj.py
```

### Option B: Live Setup (MIDI Method)

Best for: Dynamic, on-the-fly cue setting

```python
# When loading track to deck:
def load_track_to_deck(self, track_index: int, deck: int):
    # ... existing code ...

    # After loading, set cue points from analysis
    if analysis:
        self.set_analyzed_cue_points(track_index, deck)
```

### Option C: Hybrid (Recommended)

1. **Before session**: Use NML method to set cues for entire playlist
2. **During session**: MIDI method can add/update cues if needed
3. **After session**: Save any new cues back to NML

## Cue Point Color Coding

Traktor hotcues can be color-coded. Suggested scheme:

```python
CUE_COLORS = {
    'intro': 0,      # Blue
    'breakdown': 1,  # Green
    'build': 2,      # Yellow/Orange
    'drop': 3,       # Red
    'outro': 4,      # Purple
}
```

In NML:
```xml
<CUE_V2 NAME="Drop" TYPE="0" START="242.456" HOTCUE="2" COLOR="3"/>
```

## Testing Plan

### Phase 1: NML Writing
```bash
# Test 1: Read collection.nml
python3 test_nml_reader.py

# Test 2: Write single cue
python3 test_nml_write_cue.py

# Test 3: Verify in Traktor
# Open Traktor, check track has cue point
```

### Phase 2: MIDI Seeking
```bash
# Test 1: Beatjump commands
python3 test_beatjump.py

# Test 2: Seek to specific beat
python3 test_seek_to_beat.py

# Test 3: Store hotcue at position
python3 test_store_hotcue.py
```

### Phase 3: Integration
```bash
# Test 1: Set cues from analysis
python3 test_auto_set_cues.py track.mp3

# Test 2: Full workflow with AI DJ
python3 traktor_ai_dj.py --set-cues
```

## Limitations & Considerations

### Timing Precision
- MIDI beatjump: ±1 beat accuracy
- NML direct write: Sample-accurate
- **Recommendation**: Use NML for precise cues

### Performance Impact
- Setting 5 cues via MIDI: ~2-3 seconds (seeking + storing)
- May interrupt playback flow
- **Recommendation**: Set cues before playback or during track load

### Traktor Restart
- NML changes require Traktor restart
- **Workaround**: Use MIDI for live session, NML for preparation

### Collection.nml Safety
- Always backup before writing
- Parse carefully (XML can be finicky)
- Test with copy of collection first

## Next Steps

1. **Implement NML writer** (safest, most accurate)
2. **Test with single track** (verify cues appear in Traktor)
3. **Batch process playlist** (set all cues at once)
4. **Add MIDI method** (for dynamic cue setting)
5. **Integrate with AI DJ** (optional auto-cue mode)

## Resources

- Traktor Pro 3 MIDI Implementation (Native Instruments)
- collection.nml format documentation
- Librosa beat tracking accuracy: 85-95%

---

**Ready to give Traktor AI ears AND memory?** 🎧🧠💾
