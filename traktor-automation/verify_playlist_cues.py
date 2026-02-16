#!/usr/bin/env python3
"""
Verify cue points were set correctly for entire playlist.

Shows which tracks have cues and which don't.
"""

import json
import xml.etree.ElementTree as ET
from pathlib import Path


def load_playlist(playlist_path):
    """Load playlist JSON."""
    with open(playlist_path, 'r') as f:
        return json.load(f)


def load_collection(collection_path):
    """Load Traktor collection."""
    tree = ET.parse(str(collection_path))
    return tree.getroot()


def find_track_cues(root, filename):
    """Find cues for a track by filename."""
    for entry in root.findall('.//ENTRY'):
        location = entry.find('LOCATION')
        if location is not None:
            entry_file = location.get('FILE', '')
            if Path(entry_file).name.lower() == filename.lower():
                # Get cues
                cues = []
                for cue in entry.findall('CUE_V2'):
                    cues.append({
                        'name': cue.get('NAME', 'Unnamed'),
                        'time': float(cue.get('START', 0)),
                        'hotcue': int(cue.get('HOTCUE', -1)),
                    })
                return sorted(cues, key=lambda x: x['hotcue'])
    return None


def format_time(seconds):
    """Format seconds as MM:SS."""
    mins = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{mins}:{secs:02d}"


def main():
    # Paths
    playlist_path = Path("../track-selection-engine/best-of-deep-dub-tech-house-ai-ordered.json")
    collection_path = Path.home() / "Documents/Native Instruments/Traktor 3.11.1/collection.nml"

    if not playlist_path.exists():
        print(f"❌ Playlist not found: {playlist_path}")
        return

    if not collection_path.exists():
        print(f"❌ Collection not found: {collection_path}")
        return

    # Load
    print("Loading playlist and collection...")
    playlist = load_playlist(playlist_path)
    root = load_collection(collection_path)

    tracks = playlist['tracks']
    print(f"\n{'='*80}")
    print(f"CUE POINT VERIFICATION - {playlist['name']}")
    print(f"{'='*80}\n")

    total = len(tracks)
    with_cues = 0
    total_cues = 0

    for i, track in enumerate(tracks):
        # Get filename
        file_path = track.get('file_path', '')
        if not file_path:
            print(f"[{i+1}/{total}] ⚠️  No file path: {track['artist']} - {track['title']}")
            continue

        filename = Path(file_path).name

        # Find cues
        cues = find_track_cues(root, filename)

        if cues is None:
            print(f"[{i+1}/{total}] ❌ Not in collection: {track['artist']} - {track['title']}")
        elif len(cues) == 0:
            print(f"[{i+1}/{total}] ⚠️  No cues: {track['artist']} - {track['title']}")
        else:
            with_cues += 1
            total_cues += len(cues)

            # Show cues
            cue_summary = ', '.join([f"{c['name']} ({format_time(c['time'])})" for c in cues])
            print(f"[{i+1}/{total}] ✅ {len(cues)} cues: {track['artist']} - {track['title']}")
            print(f"          {cue_summary}")

    # Summary
    print(f"\n{'='*80}")
    print(f"SUMMARY")
    print(f"{'='*80}")
    print(f"Total tracks: {total}")
    print(f"Tracks with cues: {with_cues} ({with_cues/total*100:.1f}%)")
    print(f"Total cue points: {total_cues}")
    print(f"Average cues per track: {total_cues/total:.1f}")
    print()

    if with_cues == total:
        print("🎉 Perfect! All tracks have cue points!")
        print("\n✅ Ready to:")
        print("   1. Restart Traktor")
        print("   2. Load any track from the playlist")
        print("   3. See the colored hotcue markers")
        print("   4. Run AI DJ with intelligent mixing!")
    else:
        missing = total - with_cues
        print(f"⚠️  {missing} tracks missing cues")
        print("   Re-run: ./traktor_nml_writer.py playlist.json")


if __name__ == "__main__":
    main()
