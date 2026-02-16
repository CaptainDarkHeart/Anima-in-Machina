#!/usr/bin/env python3
"""
MIDI Mapping Diagnostic Tool
Tests each individual MIDI command to identify which mappings work and which don't.
"""

import mido
import time
import sys

def test_midi_mapping():
    """Test each MIDI mapping individually."""

    print("""
╔══════════════════════════════════════════════════════════════╗
║            TRAKTOR MIDI MAPPING DIAGNOSTIC TOOL              ║
╚══════════════════════════════════════════════════════════════╝

This tool will test each MIDI mapping one by one.
Watch Traktor and report what happens.

SETUP:
1. Open Traktor Pro 3
2. Make sure IAC Driver Bus 1 is in Controller Manager
3. Load any track to Deck A and Deck B
4. Watch what happens in Traktor as each test runs

Press Enter to start, or Ctrl+C to quit...
""")

    input()

    # Connect to MIDI
    print("\n[1/3] Connecting to IAC Driver Bus 1...")
    try:
        output = mido.open_output("IAC Driver Bus 1")
        print("✓ Connected to IAC Driver Bus 1\n")
    except Exception as e:
        print(f"✗ Failed to connect: {e}")
        print("\nAvailable MIDI outputs:")
        for port in mido.get_output_names():
            print(f"  - {port}")
        return

    # Define test cases
    tests = [
        # Deck A Tests
        {
            'name': 'Deck A - Play/Pause',
            'cc': 1,
            'value': 127,
            'expected': 'Deck A should start playing (or pause if already playing)',
            'category': 'Deck A'
        },
        {
            'name': 'Deck A - Cue',
            'cc': 3,
            'value': 127,
            'expected': 'Deck A should jump to cue point',
            'category': 'Deck A'
        },
        {
            'name': 'Deck A - Sync',
            'cc': 5,
            'value': 127,
            'expected': 'Deck A sync should activate (master tempo)',
            'category': 'Deck A'
        },
        {
            'name': 'Deck A - Load Selected',
            'cc': 7,
            'value': 127,
            'expected': 'Deck A should load the selected track from browser',
            'category': 'Deck A'
        },

        # Deck B Tests
        {
            'name': 'Deck B - Play/Pause',
            'cc': 2,
            'value': 127,
            'expected': 'Deck B should start playing (or pause if already playing)',
            'category': 'Deck B'
        },
        {
            'name': 'Deck B - Cue',
            'cc': 4,
            'value': 127,
            'expected': 'Deck B should jump to cue point',
            'category': 'Deck B'
        },
        {
            'name': 'Deck B - Sync',
            'cc': 6,
            'value': 127,
            'expected': 'Deck B sync should activate (master tempo)',
            'category': 'Deck B'
        },
        {
            'name': 'Deck B - Load Selected',
            'cc': 8,
            'value': 127,
            'expected': 'Deck B should load the selected track from browser',
            'category': 'Deck B'
        },

        # Crossfader Test
        {
            'name': 'Crossfader - Full Left',
            'cc': 10,
            'value': 0,
            'expected': 'Crossfader should move to full left (Deck A)',
            'category': 'Mixer'
        },
        {
            'name': 'Crossfader - Center',
            'cc': 10,
            'value': 64,
            'expected': 'Crossfader should move to center',
            'category': 'Mixer'
        },
        {
            'name': 'Crossfader - Full Right',
            'cc': 10,
            'value': 127,
            'expected': 'Crossfader should move to full right (Deck B)',
            'category': 'Mixer'
        },

        # Browser Tests
        {
            'name': 'Browser - Track Up',
            'cc': 20,
            'value': 127,
            'expected': 'Browser selection should move up one track',
            'category': 'Browser'
        },
        {
            'name': 'Browser - Track Down',
            'cc': 21,
            'value': 127,
            'expected': 'Browser selection should move down one track',
            'category': 'Browser'
        },

        # Tempo Reset
        {
            'name': 'Deck A - Tempo Reset',
            'cc': 30,
            'value': 127,
            'expected': 'Deck A tempo should reset to track BPM',
            'category': 'Deck A'
        },
        {
            'name': 'Deck B - Tempo Reset',
            'cc': 31,
            'value': 127,
            'expected': 'Deck B tempo should reset to track BPM',
            'category': 'Deck B'
        },
    ]

    # Run tests
    print("\n[2/3] Running MIDI mapping tests...\n")
    print("="*70)

    results = {'passed': [], 'failed': [], 'unknown': []}

    for i, test in enumerate(tests):
        print(f"\n[Test {i+1}/{len(tests)}] {test['name']}")
        print(f"  Category: {test['category']}")
        print(f"  MIDI: Ch01.CC.{test['cc']:03d} = {test['value']}")
        print(f"  Expected: {test['expected']}")

        # Send MIDI command
        msg = mido.Message('control_change', control=test['cc'], value=test['value'], channel=0)
        output.send(msg)
        print(f"  → Sent MIDI command")

        # Wait for user to observe
        time.sleep(1.5)

        # Ask user if it worked
        response = input("\n  Did it work? [y/n/s(skip)]: ").lower().strip()

        if response == 'y':
            results['passed'].append(test)
            print("  ✓ PASSED\n")
        elif response == 'n':
            results['failed'].append(test)
            print("  ✗ FAILED\n")
        elif response == 's':
            results['unknown'].append(test)
            print("  ⊘ SKIPPED\n")
        else:
            results['unknown'].append(test)
            print("  ? UNKNOWN\n")

        print("-"*70)

    # Close MIDI
    output.close()

    # Show results
    print("\n" + "="*70)
    print("\n[3/3] TEST RESULTS SUMMARY\n")

    print(f"✓ PASSED: {len(results['passed'])}")
    for test in results['passed']:
        print(f"  ✓ {test['name']} (CC {test['cc']})")

    print(f"\n✗ FAILED: {len(results['failed'])}")
    for test in results['failed']:
        print(f"  ✗ {test['name']} (CC {test['cc']})")

    if results['unknown']:
        print(f"\n? SKIPPED/UNKNOWN: {len(results['unknown'])}")
        for test in results['unknown']:
            print(f"  ? {test['name']} (CC {test['cc']})")

    # Provide diagnosis
    print("\n" + "="*70)
    print("\nDIAGNOSIS:\n")

    if len(results['failed']) == 0:
        print("🎉 All tests passed! Your MIDI mapping is working correctly.")
    elif len(results['failed']) == len(tests):
        print("⚠️  ALL tests failed. Possible issues:")
        print("  1. IAC Driver not configured in Traktor Controller Manager")
        print("  2. Generic MIDI device not active")
        print("  3. Wrong MIDI port selected in Traktor")
        print("  4. No mappings configured at all")
        print("\n→ Check TRAKTOR_MIDI_MAPPING_GUIDE.md")
    else:
        print("⚠️  Some tests failed. Common issues:\n")

        # Analyze failure patterns
        failed_categories = {}
        for test in results['failed']:
            cat = test['category']
            if cat not in failed_categories:
                failed_categories[cat] = []
            failed_categories[cat].append(test)

        for category, tests_failed in failed_categories.items():
            print(f"  {category}: {len(tests_failed)} failed")
            for test in tests_failed:
                print(f"    - {test['name']} (CC {test['cc']})")

        print("\nPOSSIBLE FIXES:")
        print("  1. Check CC numbers in Traktor mapping match exactly")
        print("  2. Verify MIDI channel is Ch01 (channel 0)")
        print("  3. Check 'Interaction Mode' (Toggle vs Direct)")
        print("  4. Verify assignment targets (Deck A vs Deck B)")
        print("  5. Make sure 'Type of Controller' is correct (Button vs Fader)")
        print("\n→ See MAPPING_VERIFICATION_CHECKLIST.md for detailed checks")

    print("\n" + "="*70)
    print("\nFor failed mappings, check:")
    print("  Traktor → Preferences → Controller Manager → Generic MIDI")
    print("\n")


if __name__ == "__main__":
    try:
        test_midi_mapping()
    except KeyboardInterrupt:
        print("\n\nTest cancelled by user.")
        sys.exit(0)
