#!/usr/bin/env python3
"""Import BPM list from Music_BPM_List.md into track library."""

import sys
import re
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from track_selector.library import TrackLibrary
from track_selector.models import TrackMetadata


def parse_bpm_list(file_path: Path, music_root: Path) -> list[TrackMetadata]:
    """Parse the BPM list markdown file."""
    tracks = []

    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # Skip header (first 4 lines: title, ---, table header, separator)
    for line in lines[4:]:
        line = line.strip()
        if not line or not line.startswith('|'):
            continue

        # Parse table row: | Track Name | BPM |
        parts = [p.strip() for p in line.split('|')]
        if len(parts) < 4:  # Should be ['', 'Track Name', 'BPM', '']
            continue

        track_name = parts[1]
        try:
            bpm = float(parts[2])
        except (ValueError, IndexError):
            continue

        # Skip invalid BPMs
        if bpm < 60 or bpm > 200:
            continue

        # Try to parse artist and title
        artist = "Unknown"
        title = track_name

        # Common patterns: "Artist - Title" or "01-Artist - Title"
        if ' - ' in track_name:
            # Remove leading numbers like "01-"
            cleaned = re.sub(r'^\d+-', '', track_name)
            if ' - ' in cleaned:
                parts = cleaned.split(' - ', 1)
                artist = parts[0].strip()
                title = parts[1].strip()

        # Estimate energy level from BPM (rough heuristic)
        # Lower BPM = lower energy, higher BPM = higher energy
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

        # Create track metadata
        # Note: We don't have actual file paths, so we'll use placeholder
        track = TrackMetadata(
            file_path=music_root / f"{track_name}.wav",  # Placeholder
            title=title,
            artist=artist,
            bpm=bpm,
            duration=360.0,  # Assume 6 minutes average
            energy_level=energy
        )

        tracks.append(track)

    return tracks


def main():
    """Main import function."""
    # Paths
    bpm_list_file = Path("/Users/dantaylor/Desktop/Music_BPM_List.md")
    music_root = Path("/Volumes/TRAKTOR/Traktor/Music")
    output_file = Path("traktor-library.json")

    if not bpm_list_file.exists():
        print(f"Error: BPM list not found at {bpm_list_file}")
        sys.exit(1)

    print(f"Reading BPM list from: {bpm_list_file}")
    tracks = parse_bpm_list(bpm_list_file, music_root)

    print(f"Parsed {len(tracks)} tracks")

    # Create library
    library = TrackLibrary()

    for track in tracks:
        library.add_track(track)

    # Save library
    library.library_path = output_file
    library.save()

    print(f"✓ Library saved to: {output_file}")

    # Show stats
    stats = library.stats()
    print(f"\nLibrary Statistics:")
    print(f"  Total tracks: {stats['total_tracks']}")
    print(f"  BPM range: {stats['bpm_range'][0]:.1f} - {stats['bpm_range'][1]:.1f}")
    print(f"  Average BPM: {stats['bpm_average']:.1f}")

    # Show BPM distribution
    print(f"\nBPM Distribution:")
    bpm_counts = {}
    for track in tracks:
        bpm_int = int(track.bpm)
        bpm_counts[bpm_int] = bpm_counts.get(bpm_int, 0) + 1

    # Show top 10 most common BPMs
    top_bpms = sorted(bpm_counts.items(), key=lambda x: x[1], reverse=True)[:10]
    for bpm, count in top_bpms:
        print(f"  {bpm} BPM: {count} tracks")


if __name__ == '__main__':
    main()
