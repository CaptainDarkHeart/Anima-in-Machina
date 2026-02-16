#!/usr/bin/env python3
"""
Automated MIDI Mapping Test
Sends all MIDI commands with delays so you can watch what happens in Traktor.
"""

import mido
import time
import sys

def test_all_mappings():
    """Send all MIDI commands automatically."""

    print("""
╔══════════════════════════════════════════════════════════════╗
║         AUTOMATED TRAKTOR MIDI MAPPING TEST                  ║
╚══════════════════════════════════════════════════════════════╝

SETUP CHECKLIST:
□ Traktor Pro 3 is open
□ IAC Driver Bus 1 is configured in Controller Manager
□ Generic MIDI device is ACTIVE
□ Load a track to Deck A
□ Load a track to Deck B
□ Browser is visible with some tracks
□ Traktor window is visible so you can see what happens

This script will send MIDI commands automatically.
Watch Traktor and note which commands work and which don't.

Starting in 3 seconds...
""")

    time.sleep(3)

    # Connect to MIDI
    print("\nConnecting to IAC Driver Bus 1...")
    try:
        output = mido.open_output("IAC Driver Bus 1")
        print("✓ Connected\n")
    except Exception as e:
        print(f"✗ Failed to connect: {e}")
        print("\nAvailable MIDI outputs:")
        for port in mido.get_output_names():
            print(f"  - {port}")
        return

    print("="*70)
    print("STARTING TESTS - WATCH TRAKTOR!")
    print("="*70 + "\n")

    # Test cases
    tests = [
        ('Deck A - Play/Pause', 1, 127, 'Deck A should start/pause'),
        ('Deck A - Cue', 3, 127, 'Deck A should jump to cue'),
        ('Deck A - Sync', 5, 127, 'Deck A sync should activate'),
        ('Deck A - Load Selected', 7, 127, 'Should load selected track to Deck A'),

        ('Deck B - Play/Pause', 2, 127, 'Deck B should start/pause'),
        ('Deck B - Cue', 4, 127, 'Deck B should jump to cue'),
        ('Deck B - Sync', 6, 127, 'Deck B sync should activate'),
        ('Deck B - Load Selected', 8, 127, 'Should load selected track to Deck B'),

        ('Crossfader - Full Left', 10, 0, 'Crossfader → full LEFT'),
        ('Crossfader - Center', 10, 64, 'Crossfader → CENTER'),
        ('Crossfader - Full Right', 10, 127, 'Crossfader → full RIGHT'),
        ('Crossfader - Back Center', 10, 64, 'Crossfader → CENTER again'),

        ('Browser - Track Down', 21, 127, 'Browser should move DOWN'),
        ('Browser - Track Down', 21, 127, 'Browser should move DOWN again'),
        ('Browser - Track Up', 20, 127, 'Browser should move UP'),
        ('Browser - Track Up', 20, 127, 'Browser should move UP again'),

        ('Deck A - Tempo Reset', 30, 127, 'Deck A tempo should reset'),
        ('Deck B - Tempo Reset', 31, 127, 'Deck B tempo should reset'),
    ]

    # Run tests
    for i, (name, cc, value, expected) in enumerate(tests):
        print(f"[{i+1:2d}/{len(tests)}] {name}")
        print(f"      CC: {cc:3d} | Value: {value:3d}")
        print(f"      Expected: {expected}")

        # Send MIDI
        msg = mido.Message('control_change', control=cc, value=value, channel=0)
        output.send(msg)
        print(f"      → SENT at {time.strftime('%H:%M:%S')}")

        # Wait between commands
        time.sleep(2)
        print()

    # Crossfader sweep test
    print("\n" + "="*70)
    print("BONUS TEST: Crossfader Sweep")
    print("="*70 + "\n")
    print("Watch the crossfader - it should smoothly sweep left to right...\n")

    for i in range(0, 128, 4):
        output.send(mido.Message('control_change', control=10, value=i, channel=0))
        time.sleep(0.05)

    print("✓ Crossfader sweep complete\n")

    # Close
    output.close()

    print("\n" + "="*70)
    print("TEST COMPLETE")
    print("="*70)
    print("""
NEXT STEPS:

1. Which commands worked?
   - Make a note of which actions you saw happen in Traktor

2. Which commands did NOTHING?
   - These mappings are broken or missing

3. Common issues:
   - If NOTHING worked → IAC Driver not configured or not active
   - If some worked → Wrong CC numbers, channels, or assignments
   - If crossfader didn't move → Wrong interaction mode (needs Direct)
   - If buttons did opposite → Wrong toggle/direct setting

4. To fix broken mappings:
   Open Traktor → Preferences → Controller Manager → Generic MIDI

   For each BROKEN command, verify:
   - ✓ MIDI Channel: Ch01 (channel 0)
   - ✓ CC Number: Matches table above
   - ✓ Assignment: Correct deck (A or B) and function
   - ✓ Interaction Mode: Toggle (buttons) or Direct (crossfader)
   - ✓ Type: Button (play/cue/etc) or Fader/Knob (crossfader)

5. Need detailed mapping guide?
   → See TRAKTOR_MIDI_MAPPING_GUIDE.md
   → See MAPPING_VERIFICATION_CHECKLIST.md

""")


if __name__ == "__main__":
    try:
        test_all_mappings()
    except KeyboardInterrupt:
        print("\n\nTest cancelled.")
        sys.exit(0)
    except Exception as e:
        print(f"\n\nError: {e}")
        import traceback
        traceback.print_exc()
