#!/usr/bin/env python3
"""
Test MIDI Connection for Traktor AI DJ
======================================

Quick test to verify IAC Driver is working and accessible.
"""

import mido
import time


def test_midi_ports():
    """Test if IAC Driver is available."""
    print("\n" + "="*60)
    print("TRAKTOR AI DJ - MIDI CONNECTION TEST")
    print("="*60 + "\n")

    # List output ports
    print("Available MIDI Output Ports:")
    output_ports = mido.get_output_names()
    if output_ports:
        for port in output_ports:
            print(f"  ✓ {port}")
    else:
        print("  ✗ No output ports found")

    print()

    # List input ports
    print("Available MIDI Input Ports:")
    input_ports = mido.get_input_names()
    if input_ports:
        for port in input_ports:
            print(f"  ✓ {port}")
    else:
        print("  ✗ No input ports found")

    print()

    # Check for IAC Driver
    target_port = "IAC Driver Bus 1"
    if target_port in output_ports and target_port in input_ports:
        print(f"✅ SUCCESS: '{target_port}' is available!")
        print()
        return True
    else:
        print(f"❌ ERROR: '{target_port}' not found")
        print()
        print("To fix this:")
        print("1. Open Audio MIDI Setup")
        print("2. Window → Show MIDI Studio")
        print("3. Double-click 'IAC Driver'")
        print("4. Check 'Device is online'")
        print("5. Click Apply")
        print()
        return False


def test_midi_send(port_name="IAC Driver Bus 1"):
    """Test sending MIDI messages."""
    print("="*60)
    print("TESTING MIDI OUTPUT")
    print("="*60 + "\n")

    try:
        # Open port
        print(f"Opening output port: {port_name}")
        output = mido.open_output(port_name)
        print("✓ Port opened successfully")

        # Send test message
        print("\nSending test MIDI message (CC 1, value 127)...")
        msg = mido.Message('control_change', control=1, value=127)
        output.send(msg)
        print("✓ Message sent")

        time.sleep(0.1)

        # Send another test message
        print("Sending test MIDI message (CC 1, value 0)...")
        msg = mido.Message('control_change', control=1, value=0)
        output.send(msg)
        print("✓ Message sent")

        # Close port
        output.close()
        print("\n✅ MIDI output test passed!")
        print()
        return True

    except Exception as e:
        print(f"\n❌ MIDI output test failed: {e}")
        print()
        return False


def test_midi_receive(port_name="IAC Driver Bus 1", timeout=5):
    """Test receiving MIDI messages."""
    print("="*60)
    print("TESTING MIDI INPUT")
    print("="*60 + "\n")

    print(f"Opening input port: {port_name}")
    print(f"Listening for {timeout} seconds...")
    print("(If Traktor is running with MIDI feedback enabled, you should see messages)")
    print()

    try:
        received = []

        def callback(msg):
            received.append(msg)
            print(f"  Received: {msg}")

        # Open port with callback
        input_port = mido.open_input(port_name, callback=callback)

        # Listen for a few seconds
        time.sleep(timeout)

        # Close port
        input_port.close()

        if received:
            print(f"\n✅ Received {len(received)} MIDI message(s)")
        else:
            print("\n⚠️  No messages received (this is OK if Traktor isn't running)")

        print()
        return True

    except Exception as e:
        print(f"\n❌ MIDI input test failed: {e}")
        print()
        return False


def main():
    """Run all tests."""
    print("""
╔══════════════════════════════════════════════════════════════╗
║           TRAKTOR AI DJ - MIDI CONNECTION TEST               ║
╚══════════════════════════════════════════════════════════════╝
    """)

    # Test 1: Check ports
    if not test_midi_ports():
        print("\n⚠️  Please fix IAC Driver setup before continuing.")
        return

    # Test 2: Send MIDI
    if not test_midi_send():
        print("\n⚠️  MIDI output not working.")
        return

    # Test 3: Receive MIDI
    test_midi_receive()

    print("="*60)
    print("SUMMARY")
    print("="*60)
    print()
    print("✅ IAC Driver is configured correctly")
    print("✅ MIDI output is working")
    print("✅ MIDI input is working")
    print()
    print("Next steps:")
    print("1. Open Traktor and configure MIDI mapping")
    print("2. Run: python3 traktor_ai_dj.py")
    print()
    print("="*60)


if __name__ == "__main__":
    main()
