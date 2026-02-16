# Napkin

## Corrections
| Date | Source | What Went Wrong | What To Do Instead |
|------|--------|----------------|-------------------|
| 2026-02-16 | user | Browser up/down (CC 20/21) not working in Traktor | FIXED: CC 021 was set to "Direct" instead of "Dec" mode - changed to Dec and now working |

## User Preferences
- (accumulate here as you learn them)

## Patterns That Work
- IAC Driver MIDI setup is working correctly for Play/Pause, Cue, Sync, Load, Crossfader commands
- All deck control and mixer commands working via IAC Driver → Traktor
- Super Xtreme Mapper can be used to visually edit TSI mapping files (easier than Traktor's UI)

## Patterns That Don't Work
- (approaches that failed and why)

## Domain Notes
- Project: AI DJ automation using Traktor Pro 3
- Hardware: Kontrol X1 mk2 + Kontrol Z1 controllers
- Architecture: Python AI DJ → IAC Driver → Traktor (+ X1 mk2 + Z1 for manual control)
- **MIDI Mapping Status: ✅ ALL WORKING** (14 input commands + 4 output feedback)

## Hardware Controller Button Combinations
- **X1 mk2 MIDI mode:** SHIFT + both left and right LOAD buttons (arrows)
- **Z1 MIDI mode:** MODE + both CUE buttons (A and B)
- **Z1 mk2 MIDI mode:** --- button + ☰ button
- **Recommended:** Keep both in Native mode for LED feedback and coexistence with automation
