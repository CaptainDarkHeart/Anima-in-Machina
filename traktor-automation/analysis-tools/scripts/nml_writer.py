#!/usr/bin/env python3
"""
NML Writer - Write Cue Points to Traktor Collection
===================================================

This module handles reading and writing cue points to Traktor's collection.nml file.

Features:
- Parse NML XML structure
- Find tracks by file path
- Add/update cue points
- Preserve existing data
- Backup before modifications

Usage:
    from nml_writer import NMLWriter

    writer = NMLWriter()
    writer.add_cue_points_to_track(audio_file, cue_points)
    writer.save()
"""

import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import List, Dict, Optional
import shutil
from datetime import datetime


class NMLWriter:
    """Write intelligent cue points to Traktor's collection.nml file."""

    def __init__(self, nml_path: Optional[str] = None):
        """
        Initialize NML writer.

        Args:
            nml_path: Path to collection.nml (auto-detected if None)
        """
        if nml_path:
            self.nml_path = Path(nml_path)
        else:
            self.nml_path = self._find_nml()

        self.tree = None
        self.root = None
        self.modified = False

    def _find_nml(self) -> Path:
        """Find Traktor's collection.nml file."""
        default_path = Path.home() / "Documents" / "Native Instruments" / "Traktor 3.11.1" / "collection.nml"

        if default_path.exists():
            return default_path

        raise FileNotFoundError(
            f"collection.nml not found at {default_path}. "
            "Please specify path manually."
        )

    def load(self):
        """Load the NML file."""
        print(f"Loading NML: {self.nml_path}")
        self.tree = ET.parse(str(self.nml_path))
        self.root = self.tree.getroot()
        print(f"  Loaded successfully")

    def backup(self):
        """Create a backup of the NML file before modifications."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = self.nml_path.parent / f"collection_backup_{timestamp}.nml"

        shutil.copy2(self.nml_path, backup_path)
        print(f"Backup created: {backup_path}")
        return backup_path

    def find_track_entry(self, audio_file: Path) -> Optional[ET.Element]:
        """
        Find the ENTRY element for a given audio file.

        Args:
            audio_file: Path to the audio file

        Returns:
            The ENTRY XML element, or None if not found
        """
        # Normalize the path for comparison
        file_name = audio_file.name

        # Search all ENTRY elements
        collection = self.root.find('.//COLLECTION')
        if collection is None:
            return None

        for entry in collection.findall('ENTRY'):
            location = entry.find('LOCATION')
            if location is not None:
                nml_file = location.get('FILE')
                if nml_file == file_name:
                    return entry

        return None

    def remove_existing_cues(self, entry: ET.Element, keep_autogrid: bool = True):
        """
        Remove existing cue points from an entry.

        Args:
            entry: The ENTRY XML element
            keep_autogrid: If True, keeps the AutoGrid cue point
        """
        cues_to_remove = []

        for cue in entry.findall('CUE_V2'):
            cue_name = cue.get('NAME', '')
            if keep_autogrid and cue_name == 'AutoGrid':
                continue
            cues_to_remove.append(cue)

        for cue in cues_to_remove:
            entry.remove(cue)

    def add_cue_point(
        self,
        entry: ET.Element,
        name: str,
        start_ms: float,
        cue_type: int = 0,
        hotcue: int = 0,
        displ_order: int = 0
    ):
        """
        Add a cue point to a track entry.

        Args:
            entry: The ENTRY XML element
            name: Cue point name
            start_ms: Start position in milliseconds
            cue_type: Type (0=cue, 4=grid, etc.)
            hotcue: Hotcue number (0=not a hotcue)
            displ_order: Display order
        """
        cue = ET.SubElement(entry, 'CUE_V2')
        cue.set('NAME', name)
        cue.set('DISPL_ORDER', str(displ_order))
        cue.set('TYPE', str(cue_type))
        cue.set('START', f"{start_ms:.6f}")
        cue.set('LEN', "0.000000")
        cue.set('REPEATS', "-1")
        cue.set('HOTCUE', str(hotcue))

    def add_cue_points_to_track(
        self,
        audio_file: Path,
        cue_points: List[Dict],
        replace_existing: bool = True,
        keep_autogrid: bool = True
    ) -> bool:
        """
        Add cue points to a track in the NML file.

        Args:
            audio_file: Path to the audio file
            cue_points: List of cue point dictionaries from hybrid analyzer
            replace_existing: If True, replaces existing cue points
            keep_autogrid: If True, keeps the AutoGrid cue point

        Returns:
            True if successful, False otherwise
        """
        if self.tree is None:
            self.load()

        # Find the track entry
        entry = self.find_track_entry(audio_file)

        if entry is None:
            print(f"  ❌ Track not found in NML: {audio_file.name}")
            return False

        # Remove existing cues if requested
        if replace_existing:
            self.remove_existing_cues(entry, keep_autogrid=keep_autogrid)

        # Traktor cue type mapping
        type_map = {
            'load': 0,       # Regular cue
            'breakdown': 0,  # Regular cue (green)
            'buildup': 0,    # Regular cue (yellow)
            'drop': 0,       # Regular cue (orange)
        }

        # Add new cue points
        for i, cue in enumerate(cue_points):
            # Convert seconds to milliseconds
            # Use beat_time (beat-aligned) if available, otherwise fall back to time
            time_seconds = cue.get('beat_time', cue.get('time', 0.0))
            start_ms = time_seconds * 1000.0

            # Get cue type
            cue_type = type_map.get(cue['type'], 0)

            # Create name
            name = cue['name']

            self.add_cue_point(
                entry=entry,
                name=name,
                start_ms=start_ms,
                cue_type=cue_type,
                hotcue=0,  # Not a hotcue
                displ_order=i
            )

        self.modified = True
        print(f"  ✅ Added {len(cue_points)} cue points to {audio_file.name}")
        return True

    def save(self, create_backup: bool = True):
        """
        Save the modified NML file.

        Args:
            create_backup: If True, creates a backup before saving
        """
        if not self.modified:
            print("No modifications made, skipping save")
            return

        if create_backup:
            self.backup()

        # Write the XML file
        self.tree.write(
            str(self.nml_path),
            encoding='UTF-8',
            xml_declaration=True
        )

        print(f"✅ NML file saved: {self.nml_path}")
        self.modified = False

    def batch_add_cue_points(
        self,
        analysis_files: List[Path],
        replace_existing: bool = True
    ):
        """
        Batch add cue points from multiple analysis JSON files.

        Args:
            analysis_files: List of paths to analysis JSON files
            replace_existing: If True, replaces existing cue points
        """
        import json

        if self.tree is None:
            self.load()

        successful = 0
        failed = 0

        for analysis_file in analysis_files:
            try:
                # Load analysis
                with open(analysis_file, 'r') as f:
                    analysis = json.load(f)

                # Get audio file path
                audio_file = Path(analysis['file'])

                # Get cue points
                cue_points = analysis['cue_points']

                # Add to NML
                success = self.add_cue_points_to_track(
                    audio_file,
                    cue_points,
                    replace_existing=replace_existing
                )

                if success:
                    successful += 1
                else:
                    failed += 1

            except Exception as e:
                print(f"  ❌ Error processing {analysis_file.name}: {e}")
                failed += 1

        print(f"\n{'=' * 60}")
        print(f"Batch processing complete:")
        print(f"  ✅ Successful: {successful}")
        print(f"  ❌ Failed: {failed}")
        print(f"{'=' * 60}\n")

        return successful, failed


def main():
    """Main entry point for testing."""
    import sys
    import json

    if len(sys.argv) < 2:
        print("Usage: python nml_writer.py <analysis_json_file> [nml_path]")
        print("\nExample:")
        print('  python nml_writer.py "Dreams_analysis.json"')
        return 1

    analysis_file = Path(sys.argv[1])
    nml_path = sys.argv[2] if len(sys.argv) > 2 else None

    if not analysis_file.exists():
        print(f"Error: Analysis file not found: {analysis_file}")
        return 1

    # Load analysis
    with open(analysis_file, 'r') as f:
        analysis = json.load(f)

    # Create NML writer
    writer = NMLWriter(nml_path)
    writer.load()

    # Get audio file and cue points
    audio_file = Path(analysis['file'])
    cue_points = analysis['cue_points']

    print(f"\nAdding {len(cue_points)} cue points to {audio_file.name}...")

    # Add cue points
    success = writer.add_cue_points_to_track(
        audio_file,
        cue_points,
        replace_existing=True,
        keep_autogrid=True
    )

    if success:
        # Save
        writer.save()
        print("\n✅ Cue points successfully written to NML!")
    else:
        print("\n❌ Failed to write cue points")
        return 1

    return 0


if __name__ == '__main__':
    sys.exit(main())
