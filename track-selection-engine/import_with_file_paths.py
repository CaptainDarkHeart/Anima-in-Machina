#!/usr/bin/env python3
"""Import BPM list and match with actual audio files on disk."""

import sys
import re
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from track_selector.library import TrackLibrary
from track_selector.models import TrackMetadata


def parse_bpm_list(file_path: Path) -> dict[str, float]:
    """Parse BPM list and return dict of {track_name: bpm}."""
    bpm_map = {}

    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # Skip header
    for line in lines[4:]:
        line = line.strip()
        if not line or not line.startswith('|'):
            continue

        parts = [p.strip() for p in line.split('|')]
        if len(parts) < 4:
            continue

        track_name = parts[1]
        try:
            bpm = float(parts[2])
        except (ValueError, IndexError):
            continue

        if 60 <= bpm <= 200:  # Valid BPM range
            bpm_map[track_name] = bpm

    return bpm_map


def scan_music_directory(music_dir: Path, bpm_map: dict[str, float]) -> list[TrackMetadata]:
    """Scan music directory and match files with BPM data."""
    tracks = []
    extensions = {'.mp3', '.m4a', '.wav', '.aiff', '.flac'}

    print(f"Scanning {music_dir}...")

    file_count = 0
    matched_count = 0

    for file_path in music_dir.rglob('*'):
        if file_path.suffix.lower() not in extensions:
            continue

        if file_path.name.startswith('._'):
            continue

        file_count += 1

        # Get clean filename without extension
        clean_name = file_path.stem

        # Try to find BPM
        bpm = None

        # Exact match
        if clean_name in bpm_map:
            bpm = bpm_map[clean_name]
        else:
            # Try fuzzy match (remove special characters, compare)
            clean_normalized = re.sub(r'[^\w\s]', '', clean_name.lower())
            for bpm_name, bpm_value in bpm_map.items():
                bpm_normalized = re.sub(r'[^\w\s]', '', bpm_name.lower())
                if clean_normalized == bpm_normalized:
                    bpm = bpm_value
                    break

        if not bpm:
            # Default to 123 BPM if not found
            bpm = 123.0
        else:
            matched_count += 1

        # Parse artist and title
        artist = "Unknown"
        title = clean_name

        if ' - ' in clean_name:
            cleaned = re.sub(r'^\d+-', '', clean_name)
            if ' - ' in cleaned:
                parts = cleaned.split(' - ', 1)
                artist = parts[0].strip()
                title = parts[1].strip()

        # Estimate energy from BPM
        if bpm < 115:
            energy = 2
        elif bpm < 120:
            energy = 3
        elif bpm < 123:
            energy = 4
        elif bpm < 126:
            energy = 5
        elif bpm < 128:
            energy = 6
        elif bpm < 130:
            energy = 7
        else:
            energy = 8

        # Get actual file size for duration estimate
        try:
            file_size_mb = file_path.stat().st_size / (1024 * 1024)
            # Rough estimate: 1 MB per minute for 320kbps MP3
            duration = file_size_mb * 60
        except:
            duration = 360.0  # Default 6 minutes

        track = TrackMetadata(
            file_path=file_path,
            title=title,
            artist=artist,
            bpm=bpm,
            duration=duration,
            energy_level=energy
        )

        tracks.append(track)

        if file_count % 100 == 0:
            print(f"  Processed {file_count} files, matched {matched_count} BPMs...")

    print(f"✓ Scanned {file_count} files")
    print(f"✓ Matched {matched_count} BPMs ({matched_count/file_count*100:.1f}%)")

    return tracks


def main():
    """Main import function."""
    bpm_list_file = Path("/Users/dantaylor/Desktop/Music_BPM_List.md")
    music_dir = Path("/Volumes/TRAKTOR/Traktor/Music")
    output_file = Path("traktor-library-with-paths.json")

    if not bpm_list_file.exists():
        print(f"Error: BPM list not found: {bpm_list_file}")
        sys.exit(1)

    if not music_dir.exists():
        print(f"Error: Music directory not found: {music_dir}")
        sys.exit(1)

    # Parse BPM list
    print("Parsing BPM list...")
    bpm_map = parse_bpm_list(bpm_list_file)
    print(f"✓ Loaded {len(bpm_map)} BPM entries")

    # Scan music directory
    tracks = scan_music_directory(music_dir, bpm_map)

    # Create library
    print("\nBuilding library...")
    library = TrackLibrary()

    for track in tracks:
        library.add_track(track)

    # Save
    library.library_path = output_file
    library.save()
    print(f"✓ Library saved to: {output_file}")

    # Stats
    stats = library.stats()
    print(f"\nLibrary Statistics:")
    print(f"  Total tracks: {stats['total_tracks']}")
    print(f"  BPM range: {stats['bpm_range'][0]:.1f} - {stats['bpm_range'][1]:.1f}")
    print(f"  Average BPM: {stats['bpm_average']:.1f}")


if __name__ == '__main__':
    main()
