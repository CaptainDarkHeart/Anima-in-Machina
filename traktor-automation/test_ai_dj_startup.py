#!/usr/bin/env python3
"""Quick test of AI DJ startup without infinite loop."""

import json
import mido

print("\n" + "="*60)
print("TRAKTOR AI DJ - STARTUP TEST")
print("="*60 + "\n")

# Test 1: MIDI Connection
print("Test 1: MIDI Ports")
print("-" * 60)
output_ports = mido.get_output_names()
input_ports = mido.get_input_names()

print(f"Output ports: {output_ports}")
print(f"Input ports: {input_ports}")

if "IAC Driver Bus 1" in output_ports and "IAC Driver Bus 1" in input_ports:
    print("✅ IAC Driver Bus 1 available")
else:
    print("❌ IAC Driver Bus 1 NOT available")
    exit(1)

# Test 2: Connect to MIDI
print("\nTest 2: MIDI Connection")
print("-" * 60)
try:
    output = mido.open_output("IAC Driver Bus 1")
    input_port = mido.open_input("IAC Driver Bus 1")
    print("✅ Successfully connected to IAC Driver Bus 1")

    # Test send
    print("\nTest 3: Send MIDI Message")
    print("-" * 60)
    msg = mido.Message('control_change', control=1, value=127)
    output.send(msg)
    print(f"✅ Sent test message: {msg}")

    output.close()
    input_port.close()

except Exception as e:
    print(f"❌ MIDI connection failed: {e}")
    exit(1)

# Test 3: Load Playlist
print("\nTest 4: Load Playlist")
print("-" * 60)
playlist_path = "/Users/dantaylor/Claude/Last Night an AI Saved My Life/track-selection-engine/best-of-deep-dub-tech-house-ai-ordered.json"

try:
    with open(playlist_path, 'r') as f:
        playlist = json.load(f)

    print(f"✅ Loaded playlist: {playlist['name']}")
    print(f"   Tracks: {len(playlist['tracks'])}")
    print(f"   Duration: {playlist['journey_arc']['duration_minutes']} minutes")
    print(f"   First track: {playlist['tracks'][0]['artist']} - {playlist['tracks'][0]['title']}")

except Exception as e:
    print(f"❌ Playlist loading failed: {e}")
    exit(1)

print("\n" + "="*60)
print("✅ ALL TESTS PASSED!")
print("="*60)
print("\nThe AI DJ system is ready to run.")
print("Run: python3 traktor_ai_dj.py")
print("\nMake sure Traktor is running with your playlist loaded!")
print("="*60 + "\n")
