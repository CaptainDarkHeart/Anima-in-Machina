#!/usr/bin/env python3
"""
Browser Navigation Test
Tests different methods of browser navigation to find what works.
"""

import mido
import time

def test_browser_navigation():
    print("""
╔══════════════════════════════════════════════════════════════╗
║            BROWSER NAVIGATION DIAGNOSTIC                     ║
╚══════════════════════════════════════════════════════════════╝

SETUP:
1. Open Traktor
2. Make sure browser is VISIBLE
3. Click in the browser area (give it focus)
4. Make sure you have tracks in a playlist

This will test browser navigation with different MIDI values...
""")

    try:
        output = mido.open_output("IAC Driver Bus 1")
        print("✓ Connected to IAC Driver Bus 1\n")
    except Exception as e:
        print(f"✗ Failed to connect: {e}")
        return

    print("="*70)
    print("TEST 1: Track Down (CC 21) with different values")
    print("="*70 + "\n")

    test_values = [127, 64, 1]

    for value in test_values:
        print(f"Sending CC 21 = {value}...")
        output.send(mido.Message('control_change', control=21, value=value, channel=0))
        time.sleep(1)

    print("\n" + "="*70)
    print("TEST 2: Track Up (CC 20) with different values")
    print("="*70 + "\n")

    for value in test_values:
        print(f"Sending CC 20 = {value}...")
        output.send(mido.Message('control_change', control=20, value=value, channel=0))
        time.sleep(1)

    print("\n" + "="*70)
    print("TEST 3: Rapid down movement (should move 5 tracks down)")
    print("="*70 + "\n")

    for i in range(5):
        output.send(mido.Message('control_change', control=21, value=127, channel=0))
        print(f"  Down {i+1}")
        time.sleep(0.3)

    print("\n" + "="*70)
    print("TEST 4: Rapid up movement (should move 5 tracks up)")
    print("="*70 + "\n")

    for i in range(5):
        output.send(mido.Message('control_change', control=20, value=127, channel=0))
        print(f"  Up {i+1}")
        time.sleep(0.3)

    print("\n" + "="*70)
    print("TEST 5: Try with Note messages (alternative method)")
    print("="*70 + "\n")

    print("Down with Note On/Off...")
    for i in range(3):
        output.send(mido.Message('note_on', note=21, velocity=127, channel=0))
        time.sleep(0.05)
        output.send(mido.Message('note_off', note=21, velocity=0, channel=0))
        print(f"  Note Down {i+1}")
        time.sleep(0.3)

    print("\nUp with Note On/Off...")
    for i in range(3):
        output.send(mido.Message('note_on', note=20, velocity=127, channel=0))
        time.sleep(0.05)
        output.send(mido.Message('note_off', note=20, velocity=0, channel=0))
        print(f"  Note Up {i+1}")
        time.sleep(0.3)

    output.close()

    print("\n" + "="*70)
    print("DIAGNOSIS")
    print("="*70)
    print("""
Did ANY of the tests move the browser selection?

If YES:
  - Note which test/value worked
  - Update your Traktor mapping to use that method
  - See BROWSER_NAVIGATION_FIX.md for the exact settings

If NO:
  - The browser mapping is missing or incorrect
  - Go to Traktor → Preferences → Controller Manager → Generic MIDI
  - Check if there's ANY mapping for CC 20 or CC 21
  - If not, add them using the guide in BROWSER_NAVIGATION_FIX.md

Most common fix:
  Assignment: Browser > List > Select Next Track (for CC 20)
  Assignment: Browser > List > Select Previous Track (for CC 21)
  Interaction Mode: Direct
  Type: Button
  Set to value: ON

Alternative fix:
  Assignment: Browser > List > Select Up/Down (for both)
  Interaction Mode: Inc (for CC 20) or Dec (for CC 21)
  Type: Button
""")

if __name__ == "__main__":
    try:
        test_browser_navigation()
    except KeyboardInterrupt:
        print("\n\nTest cancelled.")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
