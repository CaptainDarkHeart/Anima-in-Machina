#!/usr/bin/env python3
"""Analyze custom playlist and match with library."""

import sys
import json
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from track_selector.library import TrackLibrary


def load_custom_playlist(file_path: Path) -> list[tuple[str, str]]:
    """Load custom playlist and parse Title - Artist format."""
    tracks = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            # Format: "Title - Artist"
            if ' - ' in line:
                parts = line.split(' - ', 1)
                title = parts[0].strip()
                artist = parts[1].strip()
                tracks.append((title, artist))

    return tracks


def find_track_in_library(library: TrackLibrary, title: str, artist: str):
    """Find a track in the library by title and artist."""
    # Try exact match first
    for track in library.tracks:
        if track.title.lower() == title.lower() and track.artist.lower() == artist.lower():
            return track

    # Try partial match
    for track in library.tracks:
        if title.lower() in track.title.lower() and artist.lower() in track.artist.lower():
            return track

    # Try artist match only
    for track in library.tracks:
        if artist.lower() in track.artist.lower():
            return track

    return None


def main():
    """Main analysis function."""
    playlist_file = Path("custom_playlist.txt")
    library_file = Path("traktor-library.json")

    if not playlist_file.exists():
        print(f"Error: Playlist file not found: {playlist_file}")
        sys.exit(1)

    if not library_file.exists():
        print(f"Error: Library not found: {library_file}")
        sys.exit(1)

    # Load library
    print(f"Loading library: {library_file}")
    library = TrackLibrary(library_file)
    print(f"✓ Loaded {len(library.tracks)} tracks\n")

    # Load custom playlist
    print(f"Loading custom playlist: {playlist_file}")
    playlist_tracks = load_custom_playlist(playlist_file)
    print(f"✓ Loaded {len(playlist_tracks)} tracks\n")

    # Analyze playlist
    print("="*80)
    print("PLAYLIST ANALYSIS")
    print("="*80)
    print()

    matched = []
    not_found = []

    for i, (title, artist) in enumerate(playlist_tracks, 1):
        track = find_track_in_library(library, title, artist)

        if track:
            matched.append(track)
            print(f"{i:2d}. ✓ {artist} - {title}")
            print(f"    {track.bpm:.1f} BPM | E{track.energy_level}")
        else:
            not_found.append((title, artist))
            print(f"{i:2d}. ✗ {artist} - {title}")
            print(f"    NOT FOUND IN LIBRARY")
        print()

    # Summary
    print("="*80)
    print("SUMMARY")
    print("="*80)
    print(f"Total tracks: {len(playlist_tracks)}")
    print(f"Matched: {len(matched)}")
    print(f"Not found: {len(not_found)}")

    if matched:
        bpms = [t.bpm for t in matched]
        energies = [t.energy_level for t in matched]

        print(f"\nMatched Tracks Analysis:")
        print(f"  BPM range: {min(bpms):.1f} - {max(bpms):.1f}")
        print(f"  Average BPM: {sum(bpms)/len(bpms):.1f}")
        print(f"  Energy range: {min(energies)} - {max(energies)}")
        print(f"  Average energy: {sum(energies)/len(energies):.1f}")

        # BPM distribution
        print(f"\n  BPM distribution:")
        bpm_counts = {}
        for track in matched:
            bpm_int = int(track.bpm)
            bpm_counts[bpm_int] = bpm_counts.get(bpm_int, 0) + 1

        for bpm in sorted(bpm_counts.keys()):
            print(f"    {bpm} BPM: {bpm_counts[bpm]} tracks")

    if not_found:
        print(f"\nNot found in library:")
        for title, artist in not_found:
            print(f"  - {artist} - {title}")

    # Create M3U if we have matches
    if matched:
        m3u_path = Path("custom_playlist.m3u")
        with open(m3u_path, 'w') as f:
            f.write("#EXTM3U\n")
            f.write("#PLAYLIST:Custom Playlist\n\n")
            for track in matched:
                duration_int = int(track.duration)
                f.write(f"#EXTINF:{duration_int},{track.artist} - {track.title}\n")
                f.write(f"{track.file_path}\n")

        print(f"\n✓ Created M3U playlist: {m3u_path}")


if __name__ == '__main__':
    main()
