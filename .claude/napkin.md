# Napkin

## Corrections
| Date | Source | What Went Wrong | What To Do Instead |
|------|--------|----------------|-------------------|
| 2026-02-16 | user | Browser up/down (CC 20/21) not working in Traktor | FIXED: CC 021 was set to "Direct" instead of "Dec" mode - changed to Dec and now working |

## User Preferences
- (accumulate here as you learn them)

## Patterns That Work
- **Reading Traktor analysis from NML** via `xml.etree.ElementTree` — fast, reliable, no external deps. BPM from `TEMPO BPM`, anchor from `CUE_V2 TYPE=4 START`, key from `INFO KEY`, duration from `INFO PLAYTIME_FLOAT * 1000`, gain from `LOUDNESS PEAK_DB/PERCEIVED_DB/ANALYZED_DB`.
- **Bar-arithmetic cue placement** using Traktor's own BPM + beatgrid anchor produces musically correct, on-beat cue positions. Percentage estimates (10%/35%/65%) work well for deep house; snap_to_bar() aligns them precisely.
- **Librosa energy envelope for breakdown detection:** load at 22050Hz mono, compute RMS with hop_length=512, find lowest-energy 30s rolling window in the 40-80% zone. Snap result to nearest bar. Sanity-check: must be after groove + 8 bars and before 85% of track.
- IAC Driver MIDI setup is working correctly for Play/Pause, Cue, Sync, Load, Crossfader commands
- All deck control and mixer commands working via IAC Driver → Traktor
- Super Xtreme Mapper can be used to visually edit TSI mapping files (easier than Traktor's UI)
- X1 mk2 and Z1 in Native mode work alongside IAC Driver automation - all three active simultaneously
- Native mode controllers don't show raw MIDI in Python listeners but DO control Traktor (test with physical buttons)
- EQ control via IAC → Generic MIDI mapping uses CC 50-57 (see TRAKTOR_MIDI_MAPPING_GUIDE.md) ✅ CONFIRMED WORKING
- Mixer FX Adjust (CC 56/57) works — "Filter" assignment not found in Traktor; use "Mixer FX Adjust" instead
- EQ bass swap runs in a separate thread concurrent with execute_crossfade() - both share same duration
- blend dict must carry 'score' key for EQ style selection — added in calculate_intelligent_blend()

## Patterns That Don't Work
- **Stripes files cannot be linked to NML entries programmatically.** The stripes filename is a proprietary hash; AUDIO_ID in NML is a raw base64 waveform fingerprint blob — NOT a `TRAKTOR4:HASH` string. Duration-based matching (even at correct 48kHz) is unreliable: 1 match, 2 ambiguous, 25 unmatched across 28 tracks.
- **Duration matching at 44100Hz fails for m4a tracks.** All Best of Deep Dub Tech House tracks are AAC/m4a at 48000Hz. Always use 48000 for sample count arithmetic.
- **Transients file size matching is a false positive.** Every "match" pointed to the same file — size-based deduplication is non-functional.
- **LSTM cue detector with random weights produces meaningless output.** The old `cue_detector.py` had no trained model file — all cue positions were random. Never use untrained ML models as a substitute for rule-based placement.

## MCP Server Architecture (v0.2.0)
- **NML is the primary source.** `collection.nml` contains BPM, beatgrid anchor (ms), key (Camelot), gain (peak/perceived/analyzed), duration, existing cues — all of Traktor's own analysis.
- **Librosa is secondary/optional.** Used only for energy envelope + breakdown detection. Runs at 22050Hz for speed. Never re-derive BPM from audio when NML has it.
- **Cue slot layout:** Slot 1 always protected; Slot 2=Beat (~10%), Slot 3=Breakdown (~65% or librosa-detected), Slot 4=Groove (32-bar loop at ~35%), Slot 5=End (32 bars before end).
- **Bar arithmetic:** `bar_ms = 4 * (60000 / bpm)`. Snap to bar: `anchor_ms + round((ms - anchor_ms) / bar_ms) * bar_ms`.
- **CUE_V2 TYPE=4 is the beatgrid anchor** — read-only, never written. `anchor_ms` comes from its `START` attribute (milliseconds as float).
- **Camelot key is in `INFO KEY` attribute** (e.g. "8m"), not `MUSICAL_KEY VALUE` (integer). Use the string directly.
- **Default NML path:** `~/Documents/Native Instruments/Traktor 3.11.1/collection.nml` — always use this, no user input needed.
- **NMLReader.find_entry() deduplication:** prefers entries with AutoGrid (TYPE=4 CUE_V2), then most recently modified. Handles tracks in multiple playlists.
- **suggest_cue_points auto-writes** to NML and creates a timestamped backup before every write. No dry-run mode needed — backup is the safety net.

## Domain Notes
- Project: AI DJ automation using Traktor Pro 3
- Hardware: Kontrol X1 mk2 + Kontrol Z1 controllers
- Architecture: Python AI DJ → IAC Driver → Traktor (+ X1 mk2 + Z1 for manual control)
- **MIDI Mapping Status: ✅ ALL WORKING** (22 input commands + 4 output feedback — includes EQ + Mixer FX)
- **Hardware Integration Status: ✅ ALL WORKING** (X1 mk2 + Z1 + IAC Driver all active)
- **Intelligent Mixing: ✅ IMPLEMENTED** - Parser extracts mix planning data from text notes for informed transitions

## Hardware Controller Button Combinations
- **X1 mk2 MIDI mode:** SHIFT + both left and right LOAD buttons (arrows)
- **Z1 MIDI mode:** MODE + both CUE buttons (A and B)
- **Z1 mk2 MIDI mode:** --- button + ☰ button
- **Recommended:** Keep both in Native mode for LED feedback and coexistence with automation
