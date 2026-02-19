# Traktor AI DJ — Automation System

Python automation for Traktor Pro 3 via IAC Driver MIDI, with hardware coexistence (X1 mk2 + Z1) and NML-based cue point writing.

---

## Architecture

```
Python AI DJ ──MIDI CC──> IAC Driver Bus 1 ──> Traktor Pro 3
                                                    ↑ ↓
                               ┌────────────────────┴─┴────────────────────┐
                               │                                            │
                          X1 mk2 (USB, Native mode)              Z1 (USB, Native mode)
                          deck control + LEDs                    crossfader + EQ + audio
```

All three can control Traktor simultaneously. The IAC Driver sends automation commands; the controllers provide manual override and full LED/audio feedback without conflicting.

---

## Core files

| File | Purpose |
|------|---------|
| `traktor_ai_dj.py` | Main AI DJ controller — MIDI automation, crossfader, EQ bass swap, soft-takeover |
| `intelligent_dj.py` | `IntelligentDJ` subclass — uses `MixPlanParser` for structured transition data |
| `mix_plan_parser.py` | Parses text mix plan files into `TrackMixPlan` dataclasses |
| `deep_house_cue_writer.py` | CLI script — writes Beat/Groove/Breakdown/End cues to collection.nml |
| `check_dir_entries.py` | Inspect NML entries by directory substring |
| `compare_cues.py` | Compare cue points across two NML entries for the same track |
| `diagnose_nml.py` | Print raw XML of a track entry — useful for debugging NML issues |
| `strip_old_cues.py` | Remove stripes-generated TYPE=0/HOTCUE=0 cues that clutter waveforms |
| `manual_cues_log.json` | Ground-truth DJ cue placements (for reference/training) |
| `data/lucidflow_mix_plan.txt` | Example mix plan file for `MixPlanParser` |
| `mappings/AI_DJ_IAC_Working.tsi` | Confirmed-working Traktor MIDI mapping file |
| `Traktor_AI_DJ_MIDI_Mapping.tsi` | Original mapping file (kept for reference) |

---

## MIDI CC map (IAC Driver → Traktor)

### Deck control (Python → Traktor)

| CC | Function |
|----|----------|
| 1 | Deck A Play/Pause |
| 2 | Deck B Play/Pause |
| 3 | Deck A Cue |
| 4 | Deck B Cue |
| 5 | Deck A Sync |
| 6 | Deck B Sync |
| 7 | Deck A Load Selected |
| 8 | Deck B Load Selected |
| 10 | Crossfader (0=left, 127=right) |
| 20 | Browser Navigate Up |
| 21 | Browser Navigate Down |
| 30 | Deck A Tempo Reset |
| 31 | Deck B Tempo Reset |

### EQ / Mixer FX (Python → Traktor)

| CC | Function |
|----|----------|
| 50 | Deck A EQ High |
| 51 | Deck A EQ Mid |
| 52 | Deck A EQ Low |
| 53 | Deck B EQ High |
| 54 | Deck B EQ Mid |
| 55 | Deck B EQ Low |
| 56 | Deck A Mixer FX Adjust |
| 57 | Deck B Mixer FX Adjust |

All EQ/filter values: 0 = full cut, 64 = 0 dB (centre), 127 = boost.

### Feedback (Traktor → Python)

| CC | Function |
|----|----------|
| 40 | Deck A Playback Position (0–127) |
| 41 | Deck B Playback Position (0–127) |
| 42 | Deck A Is Playing |
| 43 | Deck B Is Playing |

---

## EQ bass swap

`execute_eq_bass_swap(from_deck, to_deck, duration, style)` runs in a separate thread concurrent with `execute_crossfade()`. Two styles:

- **`deep_house`** (default) — S-curve bass cut on outgoing (0–50%), then S-curve bass in on incoming (50–100%)
- **`tech_house`** — faster cut (0–40%), earlier bring-in (30–80%)

Z1 soft-takeover: if the Z1 sends a CC in the EQ range (50–57) while automation is running, that band pauses until the physical knob crosses back through the last commanded value.

---

## Cue point writer (deep_house_cue_writer.py)

Writes four cue points to `collection.nml` using Traktor's own BPM and beatgrid anchor. No audio analysis required.

```bash
# Dry run — preview without writing
python3 deep_house_cue_writer.py --track "Nadja Lind - Spherical.m4a" --dry-run

# Single track
python3 deep_house_cue_writer.py --track "Nadja Lind - Spherical.m4a"

# Full playlist
python3 deep_house_cue_writer.py --playlist ../track-selection-engine/best-of-deep-dub-tech-house.json

# Overwrite slots 2–5 (slot 1 always protected)
python3 deep_house_cue_writer.py --playlist ... --overwrite
```

Cue layout:

| Slot | Name | Position |
|------|------|----------|
| 1 | (protected) | never touched |
| 2 | Beat | ~10% of track |
| 3 | Breakdown | ~65% of track |
| 4 | Groove | ~35%, 32-bar loop |
| 5 | End | 32 bars before end |

Note: `deep_house_cue_writer.py` uses `TYPE_LOOP = 4` internally. The MCP server's `nml_reader.py` uses `TYPE_LOOP = 5`. Both produce working loops in Traktor. The MCP server is the preferred path for new cue writing.

Automatic backup: `collection_backup_YYYYMMDD_HHMMSS.nml` is created before any write.

---

## NML utility scripts

```bash
# Show all NML entries for a directory substring
python3 check_dir_entries.py "Best of Deep Dub Tech House"

# Compare cue points between two entries of the same track
python3 compare_cues.py

# Print raw XML of a track entry
python3 diagnose_nml.py "Prof. Fee 2009 (Dub Taylor D. Mark Remix).m4a"

# Strip stripes-generated cues (TYPE=0 HOTCUE=0) — dry run first
python3 strip_old_cues.py --dry-run
python3 strip_old_cues.py
```

---

## Running the AI DJ

### Prerequisites

```bash
pip install -r requirements.txt
# mido, python-rtmidi, librosa, numpy, scipy, soundfile
```

Traktor must be open with the playlist loaded and IAC Driver Bus 1 enabled.

### Quick start

```bash
# Verify IAC Driver + MIDI connections
python3 test_midi_connection.py

# Verify all three devices (IAC + X1 mk2 + Z1)
python3 verify_all_three_devices.py

# Run the full AI DJ
python3 traktor_ai_dj.py

# Or use the launch script
./START_AI_DJ.sh
```

### Run with mix plan intelligence

```bash
python3 intelligent_dj.py
# reads data/lucidflow_mix_plan.txt by default
```

---

## Hardware setup

See `HARDWARE_MIDI_SETUP.md` for X1 mk2 + Z1 setup including:
- How to put each controller into Native mode (vs MIDI mode)
- Why Native mode is recommended (LEDs + audio interface stay active)
- Button combinations for mode switching

**MIDI mapping:** import `mappings/AI_DJ_IAC_Working.tsi` into Traktor. This is the confirmed-working TSI. See `TRAKTOR_MIDI_MAPPING_GUIDE.md` for the full mapping table and Traktor setup steps.

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| IAC Driver not found | Open Audio MIDI Setup → IAC Driver → Device is online |
| Traktor not responding | Check Controller Manager: In-Port and Out-Port both = IAC Driver Bus 1 |
| Browser up/down (CC 20/21) not working | Set mapping Interaction Mode to "Dec" not "Direct" |
| Crossfader not smooth | Set Resolution to Fine (256), disable Soft Takeover in Traktor mapping |
| EQ CC not working | Verify CCs 50–57 are mapped to EQ High/Mid/Low and Mixer FX Adjust |
| Cues not appearing after write | Restart Traktor — it only reads NML at startup |

---

## Documentation

| File | Contents |
|------|----------|
| `TRAKTOR_MIDI_MAPPING_GUIDE.md` | Complete CC table, Traktor setup instructions |
| `HARDWARE_MIDI_SETUP.md` | X1 mk2 + Z1 native mode setup, coexistence with IAC |
| `INTELLIGENT_MIXING.md` | Mix plan format, `MixPlanParser` usage, transition data |
| `CUE_POINT_AUTOMATION.md` | NML cue writing internals, TYPE values, safety rules |
| `CUE_QUICK_START.md` | Three-step cue writing quickstart |
| `SETUP_INSTRUCTIONS.md` | Full setup guide with troubleshooting |
| `SUPER_XTREME_MAPPER_GUIDE.md` | Using Super Xtreme Mapper to edit TSI files visually |
| `QUICK_REFERENCE.md` | Command cheat sheet |
| `analysis-tools/NML_SAFETY_GUIDE.md` | NML safety rules — what never to delete |
