#!/usr/bin/env python3
"""
Traktor Collection NML Writer
==============================

Write cue points directly to Traktor's collection.nml file.

This allows setting precise cue points from audio analysis without
needing to use MIDI seeking (which is less accurate).

Usage:
    from traktor_nml_writer import TraktorNMLWriter
    from audio_analyzer import AudioAnalyzer

    # Analyze track
    analyzer = AudioAnalyzer()
    analysis = analyzer.analyze_track('track.mp3')

    # Write cues to collection
    writer = TraktorNMLWriter()
    writer.load_collection()
    writer.add_cues_from_analysis('track.mp3', analysis)
    writer.save_collection(backup=True)
"""

import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Optional
import shutil
from datetime import datetime


class TraktorNMLWriter:
    """Write cue points to Traktor's collection.nml file."""

    # Traktor cue point colors
    COLORS = {
        'intro': 0,      # Blue
        'breakdown': 1,  # Green
        'build': 2,      # Yellow/Orange
        'drop': 3,       # Red
        'outro': 4,      # Purple
    }

    def __init__(self, collection_path: Optional[str] = None):
        """
        Initialize NML writer.

        Args:
            collection_path: Path to collection.nml
                           (defaults to standard Traktor location)
        """
        if collection_path is None:
            # Try to find Traktor collection automatically
            possible_paths = [
                Path.home() / "Documents/Native Instruments/Traktor 3.11.1/collection.nml",
                Path.home() / "Documents/Native Instruments/Traktor 3.0/collection.nml",
                Path.home() / "Documents/Native Instruments/Traktor 2.11/collection.nml",
            ]

            for path in possible_paths:
                if path.exists():
                    collection_path = str(path)
                    break
            else:
                # Default to 3.0 if none found
                collection_path = str(Path.home() /
                    "Documents/Native Instruments/Traktor 3.0/collection.nml")

        self.collection_path = Path(collection_path)
        self.tree: Optional[ET.ElementTree] = None
        self.root: Optional[ET.Element] = None

    def load_collection(self) -> bool:
        """
        Load and parse collection.nml

        Returns:
            True if successful, False otherwise
        """
        if not self.collection_path.exists():
            print(f"❌ Collection not found: {self.collection_path}")
            return False

        try:
            self.tree = ET.parse(str(self.collection_path))
            self.root = self.tree.getroot()
            print(f"✅ Loaded collection: {self.collection_path}")
            return True
        except ET.ParseError as e:
            print(f"❌ Failed to parse collection.nml: {e}")
            return False

    def find_track_entry(self, file_path: str) -> Optional[ET.Element]:
        """
        Find track entry in collection by file path.

        Returns ALL matching entries (to handle duplicates).

        Args:
            file_path: Path to audio file (can be relative or absolute)

        Returns:
            List of XML Elements for matching track entries
        """
        if self.root is None:
            return []

        # Get filename and parent directory for matching
        file_path_obj = Path(file_path)
        target_filename = file_path_obj.name
        target_parent = file_path_obj.parent.name  # e.g., "Best of Deep Dub Tech House"

        # Find ALL matching entries
        matching_entries = []

        for entry in self.root.findall('.//ENTRY'):
            location = entry.find('LOCATION')
            if location is not None:
                entry_file = location.get('FILE', '')

                # Check if filename matches
                if entry_file == target_filename:
                    matching_entries.append(entry)

        return matching_entries

    def add_cue_point(self, entry: ET.Element, name: str, time: float,
                      slot: int, color: Optional[int] = None):
        """
        Add a single cue point to a track entry.

        Args:
            entry: Track entry XML element
            name: Cue point name
            time: Time in seconds (float)
            slot: Hotcue slot (0-7 for hotcues 1-8)
            color: Color code (0-4, optional)
        """
        # Remove existing cue in this slot
        for existing_cue in entry.findall('CUE_V2'):
            if int(existing_cue.get('HOTCUE', -1)) == slot:
                entry.remove(existing_cue)

        # Create new cue point
        cue = ET.SubElement(entry, 'CUE_V2')
        cue.set('NAME', name)
        cue.set('DISPL_ORDER', str(slot))  # Display order matches hotcue slot
        cue.set('TYPE', '0')  # 0 = cue point, 4 = loop
        cue.set('START', f"{time:.3f}")
        cue.set('LEN', '0.000')
        cue.set('REPEATS', '-1')
        cue.set('HOTCUE', str(slot))

        if color is not None:
            cue.set('COLOR', str(color))

    def add_cues_from_analysis(self, file_path: str, analysis: Dict) -> bool:
        """
        Add cue points from audio analysis results.

        Writes to ALL matching entries (handles duplicates in collection).

        Args:
            file_path: Path to audio file
            analysis: Analysis dict from AudioAnalyzer

        Returns:
            True if successful, False otherwise
        """
        entries = self.find_track_entry(file_path)
        if not entries:
            print(f"❌ Track not found in collection: {Path(file_path).name}")
            return False

        if len(entries) > 1:
            print(f"  ℹ️  Found {len(entries)} entries - writing cues to all")

        cue_points_data = analysis.get('cue_points', {})

        # Write cues to ALL matching entries
        total_cues_added = 0
        for entry in entries:
            cues_added = 0
            slot = 0

            # Intro end
            if 'intro_end' in cue_points_data:
                intro_time = cue_points_data['intro_end']
                self.add_cue_point(entry, 'Intro End', intro_time, slot,
                                 color=self.COLORS['intro'])
                slot += 1
                cues_added += 1

            # Breakdown
            if 'breakdown' in cue_points_data:
                breakdown = cue_points_data['breakdown']
                breakdown_time = breakdown['start']
                self.add_cue_point(entry, 'Breakdown', breakdown_time, slot,
                                 color=self.COLORS['breakdown'])
                slot += 1
                cues_added += 1

            # Build
            if 'build' in cue_points_data:
                build = cue_points_data['build']
                build_time = build['start']
                self.add_cue_point(entry, 'Build', build_time, slot,
                                 color=self.COLORS['build'])
                slot += 1
                cues_added += 1

            # Drop
            if 'drop' in cue_points_data:
                drop = cue_points_data['drop']
                drop_time = drop['time']
                self.add_cue_point(entry, 'Drop', drop_time, slot,
                                 color=self.COLORS['drop'])
                slot += 1
                cues_added += 1

            # Outro start
            if 'outro_start' in cue_points_data:
                outro_time = cue_points_data['outro_start']
                self.add_cue_point(entry, 'Outro', outro_time, slot,
                                 color=self.COLORS['outro'])
                slot += 1
                cues_added += 1

            total_cues_added = max(total_cues_added, cues_added)

        if total_cues_added == 0:
            print(f"  ⚠️ No cue points to add")
            return False

        # Print summary (once, not per entry)
        if 'intro_end' in cue_points_data:
            print(f"  ✓ Intro End: {cue_points_data['intro_end']:.1f}s → Hotcue 1")
        if 'breakdown' in cue_points_data:
            print(f"  ✓ Breakdown: {cue_points_data['breakdown']['start']:.1f}s → Hotcue 2")
        if 'build' in cue_points_data:
            print(f"  ✓ Build: {cue_points_data['build']['start']:.1f}s → Hotcue 3")
        if 'drop' in cue_points_data:
            print(f"  ✓ Drop: {cue_points_data['drop']['time']:.1f}s → Hotcue 4")
        if 'outro_start' in cue_points_data:
            print(f"  ✓ Outro: {cue_points_data['outro_start']:.1f}s → Hotcue 5")

        print(f"  ✅ Added {total_cues_added} cue points")
        return True

    def save_collection(self, backup: bool = True) -> bool:
        """
        Save collection.nml (with optional backup).

        Args:
            backup: Whether to create backup before saving

        Returns:
            True if successful, False otherwise
        """
        if self.tree is None:
            print("❌ No collection loaded")
            return False

        try:
            # Create backup
            if backup:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                backup_path = self.collection_path.with_suffix(f'.backup_{timestamp}.nml')
                shutil.copy2(self.collection_path, backup_path)
                print(f"💾 Backup created: {backup_path}")

            # Write collection
            self.tree.write(str(self.collection_path),
                          encoding='utf-8',
                          xml_declaration=True)
            print(f"✅ Collection saved: {self.collection_path}")
            return True

        except Exception as e:
            print(f"❌ Failed to save collection: {e}")
            return False

    def batch_add_cues(self, playlist: Dict) -> int:
        """
        Add cue points for all tracks in a playlist.

        Args:
            playlist: Playlist dict with 'tracks' list

        Returns:
            Number of tracks processed successfully
        """
        from audio_analyzer import AudioAnalyzer

        analyzer = AudioAnalyzer()
        success_count = 0

        tracks = playlist.get('tracks', [])
        total = len(tracks)

        print(f"\n🎵 Processing {total} tracks...\n")

        for i, track in enumerate(tracks):
            print(f"[{i+1}/{total}] {track['artist']} - {track['title']}")

            file_path = track.get('file_path')
            if not file_path or not Path(file_path).exists():
                print(f"  ⚠️ File not found: {file_path}")
                continue

            # Analyze track
            print(f"  🎧 Analyzing audio...")
            analysis = analyzer.analyze_track(file_path)

            # Add cues
            if self.add_cues_from_analysis(file_path, analysis):
                success_count += 1

            print()

        return success_count


def main():
    """Command-line interface for NML writer."""
    import sys
    import json

    if len(sys.argv) < 2:
        print("""
Traktor NML Cue Point Writer
=============================

Usage:
    # Add cues from analysis to single track
    python3 traktor_nml_writer.py track.mp3

    # Batch process playlist
    python3 traktor_nml_writer.py playlist.json

    # Specify custom collection path
    python3 traktor_nml_writer.py track.mp3 /path/to/collection.nml
        """)
        sys.exit(1)

    input_path = sys.argv[1]
    collection_path = sys.argv[2] if len(sys.argv) > 2 else None

    # Initialize writer
    writer = TraktorNMLWriter(collection_path)

    if not writer.load_collection():
        sys.exit(1)

    # Check if input is playlist or single track
    input_file = Path(input_path)

    if input_file.suffix == '.json':
        # Batch process playlist
        print(f"📋 Loading playlist: {input_file}")
        with open(input_file, 'r') as f:
            playlist = json.load(f)

        success_count = writer.batch_add_cues(playlist)

        print(f"\n✅ Processed {success_count}/{len(playlist['tracks'])} tracks")

    else:
        # Single track
        print(f"🎵 Processing: {input_file.name}")

        if not input_file.exists():
            print(f"❌ File not found: {input_file}")
            sys.exit(1)

        # Analyze
        from audio_analyzer import AudioAnalyzer
        analyzer = AudioAnalyzer()

        print("🎧 Analyzing audio...")
        analysis = analyzer.analyze_track(str(input_file))

        # Add cues
        writer.add_cues_from_analysis(str(input_file), analysis)

    # Save
    if writer.save_collection(backup=True):
        print("\n🎉 Done! Restart Traktor to see new cue points.")
    else:
        print("\n❌ Failed to save collection")
        sys.exit(1)


if __name__ == "__main__":
    main()
