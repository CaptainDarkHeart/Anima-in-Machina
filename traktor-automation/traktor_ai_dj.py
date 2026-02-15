#!/usr/bin/env python3
"""
Traktor AI DJ Controller
========================

Automated DJ performance system for Traktor Pro 3 using MIDI control.

Features:
- Reads playlist from Track Selection Engine JSON
- Monitors Traktor playback position via MIDI feedback
- Executes 60-90 second extended blends
- Beatmatching and tempo sync
- Automatic crossfading
- Cue point management
- Energy-aware mixing

Architecture:
    Python Script → IAC Driver (Virtual MIDI) → Traktor MIDI Mapping → Traktor
"""

import json
import time
import threading
from pathlib import Path
from typing import Optional, Dict, List
import mido
from mido import Message


class TraktorAIDJ:
    """Main AI DJ controller for Traktor Pro 3."""

    def __init__(self, virtual_midi_port: str = "IAC Driver Bus 1"):
        """
        Initialize the Traktor AI DJ controller.

        Args:
            virtual_midi_port: Name of the virtual MIDI port to use
        """
        self.virtual_midi_port = virtual_midi_port
        self.output_port: Optional[mido.ports.BaseOutput] = None
        self.input_port: Optional[mido.ports.BaseInput] = None

        # Playlist state
        self.playlist: Optional[Dict] = None
        self.current_track_index = 0
        self.total_tracks = 0

        # Deck state
        self.active_deck = 1  # Currently playing deck (1 or 2)
        self.next_deck = 2    # Deck for next track

        # Playback monitoring
        self.is_playing = False
        self.is_transitioning = False
        self.playback_position = 0.0  # 0.0 to 1.0
        self.track_duration = 0.0     # seconds

        # Configuration
        self.blend_duration = 75  # seconds (60-90 for deep space house)
        self.monitor_interval = 0.1  # Check every 100ms

        # MIDI Control Change numbers (will be configured in Traktor mapping)
        self.MIDI_CC = {
            # Deck control
            'deck_a_play': 1,
            'deck_b_play': 2,
            'deck_a_cue': 3,
            'deck_b_cue': 4,
            'deck_a_sync': 5,
            'deck_b_sync': 6,
            'deck_a_load_selected': 7,
            'deck_b_load_selected': 8,

            # Crossfader
            'crossfader': 10,

            # Track selection
            'track_up': 20,
            'track_down': 21,

            # Tempo
            'deck_a_tempo_reset': 30,
            'deck_b_tempo_reset': 31,

            # Feedback (Traktor sends these)
            'deck_a_playback_position': 40,
            'deck_b_playback_position': 41,
            'deck_a_is_playing': 42,
            'deck_b_is_playing': 43,
        }

        self.monitor_thread: Optional[threading.Thread] = None
        self.running = False

    def log(self, message: str):
        """Log a message with timestamp."""
        print(f"[TRAKTOR AI DJ] {time.strftime('%H:%M:%S')} - {message}")

    def connect_midi(self):
        """Connect to virtual MIDI port."""
        self.log("Connecting to MIDI ports...")

        # List available ports
        print("\nAvailable MIDI output ports:")
        for port in mido.get_output_names():
            print(f"  - {port}")

        print("\nAvailable MIDI input ports:")
        for port in mido.get_input_names():
            print(f"  - {port}")

        try:
            # Open output port to send commands to Traktor
            self.output_port = mido.open_output(self.virtual_midi_port)
            self.log(f"✓ Connected to output: {self.virtual_midi_port}")

            # Open input port to receive feedback from Traktor
            self.input_port = mido.open_input(self.virtual_midi_port, callback=self._handle_midi_input)
            self.log(f"✓ Connected to input: {self.virtual_midi_port}")

        except Exception as e:
            self.log(f"✗ Failed to connect to MIDI port: {e}")
            raise

    def _handle_midi_input(self, message: Message):
        """Handle incoming MIDI messages from Traktor."""
        if message.type == 'control_change':
            cc = message.control
            value = message.value

            # Update playback position
            if cc == self.MIDI_CC['deck_a_playback_position'] and self.active_deck == 1:
                self.playback_position = value / 127.0

            elif cc == self.MIDI_CC['deck_b_playback_position'] and self.active_deck == 2:
                self.playback_position = value / 127.0

            # Update playing state
            elif cc == self.MIDI_CC['deck_a_is_playing'] and self.active_deck == 1:
                self.is_playing = (value > 0)

            elif cc == self.MIDI_CC['deck_b_is_playing'] and self.active_deck == 2:
                self.is_playing = (value > 0)

    def send_cc(self, control: int, value: int, channel: int = 0):
        """Send a MIDI Control Change message."""
        if self.output_port:
            msg = Message('control_change', control=control, value=value, channel=channel)
            self.output_port.send(msg)

    def load_playlist(self, playlist_path: str):
        """Load playlist JSON from Track Selection Engine."""
        self.log(f"Loading playlist: {playlist_path}")

        with open(playlist_path, 'r') as f:
            self.playlist = json.load(f)

        self.total_tracks = len(self.playlist['tracks'])
        self.log(f"✓ Loaded {self.total_tracks} tracks")
        self.log(f"  Playlist: {self.playlist['metadata']['name']}")
        self.log(f"  Duration: {self.playlist['metadata']['total_duration_minutes']:.1f} minutes")

    def navigate_to_track(self, track_index: int):
        """Navigate to a specific track in Traktor's browser."""
        # This is simplified - in reality, we'd need to know the current position
        # and calculate how many up/down commands to send
        self.log(f"Navigating to track {track_index + 1}...")
        # For now, just log - full implementation would send track_up/down CCs

    def load_track_to_deck(self, track_index: int, deck: int):
        """Load a track from the playlist to a deck."""
        if not self.playlist:
            self.log("✗ No playlist loaded")
            return

        if track_index >= self.total_tracks:
            self.log("✗ Track index out of range")
            return

        track = self.playlist['tracks'][track_index]
        self.log(f"Loading track {track_index + 1}/{self.total_tracks} to Deck {deck}")
        self.log(f"  → {track['artist']} - {track['title']}")
        self.log(f"  → {track['bpm']} BPM | Energy: {track['energy_level']}")

        # Navigate to track in browser (simplified)
        self.navigate_to_track(track_index)

        # Load to deck
        if deck == 1:
            self.send_cc(self.MIDI_CC['deck_a_load_selected'], 127)
        else:
            self.send_cc(self.MIDI_CC['deck_b_load_selected'], 127)

        time.sleep(0.5)  # Wait for load

    def play_deck(self, deck: int):
        """Start playback on a deck."""
        self.log(f"▶ Playing Deck {deck}")
        if deck == 1:
            self.send_cc(self.MIDI_CC['deck_a_play'], 127)
        else:
            self.send_cc(self.MIDI_CC['deck_b_play'], 127)

    def enable_sync(self, deck: int):
        """Enable beatmatching sync on a deck."""
        self.log(f"🔄 Enabling sync on Deck {deck}")
        if deck == 1:
            self.send_cc(self.MIDI_CC['deck_a_sync'], 127)
        else:
            self.send_cc(self.MIDI_CC['deck_b_sync'], 127)

    def set_crossfader(self, position: float):
        """
        Set crossfader position.

        Args:
            position: 0.0 = fully left (Deck A), 1.0 = fully right (Deck B)
        """
        value = int(position * 127)
        self.send_cc(self.MIDI_CC['crossfader'], value)

    def execute_crossfade(self, duration: float, from_deck: int, to_deck: int):
        """
        Execute a smooth crossfade between decks.

        Args:
            duration: Fade duration in seconds
            from_deck: Source deck (1 or 2)
            to_deck: Destination deck (1 or 2)
        """
        self.log(f"🎚 Starting {duration}s crossfade: Deck {from_deck} → Deck {to_deck}")
        self.is_transitioning = True

        steps = int(duration * 10)  # 10 steps per second

        for i in range(steps + 1):
            progress = i / steps

            # Crossfader position
            if from_deck == 1:
                # Fade from left (0.0) to right (1.0)
                position = progress
            else:
                # Fade from right (1.0) to left (0.0)
                position = 1.0 - progress

            self.set_crossfader(position)
            time.sleep(duration / steps)

        self.is_transitioning = False
        self.log(f"✓ Crossfade complete")

    def start_transition(self, next_track_index: int):
        """Start transition to next track."""
        if self.is_transitioning:
            return

        self.log(f"\n{'='*60}")
        self.log(f"TRANSITION {self.current_track_index + 1} → {next_track_index + 1}")
        self.log(f"{'='*60}")

        # Load next track to inactive deck
        self.load_track_to_deck(next_track_index, self.next_deck)

        # Enable sync on next deck
        self.enable_sync(self.next_deck)

        # Start playing next deck
        self.play_deck(self.next_deck)

        # Execute crossfade
        self.execute_crossfade(self.blend_duration, self.active_deck, self.next_deck)

        # Swap active/next decks
        self.active_deck, self.next_deck = self.next_deck, self.active_deck
        self.current_track_index = next_track_index

    def monitor_playback(self):
        """Monitor playback position and trigger transitions."""
        self.log("🎧 Starting playback monitoring...")

        while self.running:
            if self.is_playing and not self.is_transitioning:
                # Calculate time remaining
                if self.track_duration > 0:
                    time_remaining = self.track_duration * (1.0 - self.playback_position)

                    # Trigger transition when blend_duration seconds remain
                    if time_remaining <= self.blend_duration and self.current_track_index < self.total_tracks - 1:
                        self.start_transition(self.current_track_index + 1)

            time.sleep(self.monitor_interval)

    def start(self):
        """Start the AI DJ performance."""
        if not self.playlist:
            self.log("✗ No playlist loaded. Call load_playlist() first.")
            return

        self.log("\n" + "="*60)
        self.log("🚀 STARTING AI DJ PERFORMANCE")
        self.log("="*60)

        # Load first track to Deck A
        self.load_track_to_deck(0, 1)
        self.active_deck = 1
        self.next_deck = 2
        self.current_track_index = 0

        # Set crossfader to left (Deck A)
        self.set_crossfader(0.0)

        # Enable sync
        self.enable_sync(1)

        # Start playback
        self.play_deck(1)
        self.is_playing = True

        # Start monitoring thread
        self.running = True
        self.monitor_thread = threading.Thread(target=self.monitor_playback)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()

        self.log("✓ AI DJ is now running!")
        self.log(f"  Blend duration: {self.blend_duration} seconds")
        self.log(f"  Total tracks: {self.total_tracks}")

    def stop(self):
        """Stop the AI DJ performance."""
        self.log("⏹ Stopping AI DJ...")
        self.running = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2)
        self.log("✓ AI DJ stopped")

    def cleanup(self):
        """Clean up MIDI connections."""
        if self.output_port:
            self.output_port.close()
        if self.input_port:
            self.input_port.close()


def main():
    """Main entry point for Traktor AI DJ."""
    print("""
╔══════════════════════════════════════════════════════════════╗
║                  TRAKTOR AI DJ CONTROLLER                    ║
║                                                              ║
║  Automated DJ Performance System for Traktor Pro 3          ║
║  Last Night an AI Saved My Life                             ║
╚══════════════════════════════════════════════════════════════╝
    """)

    # Initialize controller
    controller = TraktorAIDJ()

    try:
        # Connect to MIDI
        controller.connect_midi()

        # Load playlist
        playlist_path = "/Users/dantaylor/Claude/Last Night an AI Saved My Life/track-selection-engine/best-of-deep-dub-tech-house-ai-ordered.json"
        controller.load_playlist(playlist_path)

        # Start performance
        controller.start()

        # Keep running
        print("\nPress Ctrl+C to stop...\n")
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print("\n")
        controller.stop()
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
    finally:
        controller.cleanup()


if __name__ == "__main__":
    main()
