#!/usr/bin/env python3
"""
Test script to read and display Traktor collection.nml structure.

This helps understand the NML format before writing to it.
"""

import xml.etree.ElementTree as ET
from pathlib import Path


def find_collection_nml():
    """Find Traktor collection.nml in standard locations."""
    possible_paths = [
        Path.home() / "Documents/Native Instruments/Traktor 3.11.1/collection.nml",
        Path.home() / "Documents/Native Instruments/Traktor 3.0/collection.nml",
        Path.home() / "Documents/Native Instruments/Traktor 2.11/collection.nml",
        Path.home() / "Documents/Native Instruments/Traktor/collection.nml",
    ]

    for path in possible_paths:
        if path.exists():
            return path

    return None


def read_collection_info(collection_path):
    """Read and display basic collection info."""
    print("="*70)
    print("TRAKTOR COLLECTION INFO")
    print("="*70)
    print()

    tree = ET.parse(str(collection_path))
    root = tree.getroot()

    # Get collection info
    collection = root.find('COLLECTION')
    if collection is not None:
        num_entries = len(collection.findall('ENTRY'))
        print(f"📁 Collection: {collection_path}")
        print(f"🎵 Total tracks: {num_entries}")
        print()

    return tree, root


def show_sample_track(root, max_tracks=3):
    """Show structure of sample tracks."""
    print("="*70)
    print("SAMPLE TRACKS")
    print("="*70)
    print()

    entries = root.findall('.//ENTRY')

    for i, entry in enumerate(entries[:max_tracks]):
        # Get track info
        location = entry.find('LOCATION')
        if location is not None:
            file_path = location.get('FILE', 'Unknown')
            print(f"Track {i+1}: {Path(file_path).name}")
        else:
            print(f"Track {i+1}: Unknown")

        # Get cue points
        cues = entry.findall('CUE_V2')
        if cues:
            print(f"  Cue points: {len(cues)}")
            for cue in cues:
                name = cue.get('NAME', 'Unnamed')
                start = cue.get('START', '0')
                hotcue = cue.get('HOTCUE', 'N/A')
                cue_type = cue.get('TYPE', '0')
                color = cue.get('COLOR', 'None')

                print(f"    • {name}")
                print(f"      Time: {float(start):.1f}s")
                print(f"      Hotcue: {int(hotcue) + 1 if hotcue != 'N/A' else 'N/A'}")
                print(f"      Type: {'Cue' if cue_type == '0' else 'Loop'}")
                print(f"      Color: {color}")
        else:
            print(f"  Cue points: None")

        # Get tempo info
        tempo = entry.find('.//TEMPO')
        if tempo is not None:
            bpm = tempo.get('BPM', 'Unknown')
            print(f"  BPM: {float(bpm):.1f}")

        print()


def show_cue_statistics(root):
    """Show statistics about cue points in collection."""
    print("="*70)
    print("CUE POINT STATISTICS")
    print("="*70)
    print()

    entries = root.findall('.//ENTRY')

    total_tracks = len(entries)
    tracks_with_cues = 0
    total_cues = 0
    cue_names = {}

    for entry in entries:
        cues = entry.findall('CUE_V2')
        if cues:
            tracks_with_cues += 1
            total_cues += len(cues)

            for cue in cues:
                name = cue.get('NAME', 'Unnamed')
                cue_names[name] = cue_names.get(name, 0) + 1

    print(f"Total tracks: {total_tracks}")
    print(f"Tracks with cues: {tracks_with_cues} ({tracks_with_cues/total_tracks*100:.1f}%)")
    print(f"Total cue points: {total_cues}")
    if tracks_with_cues > 0:
        print(f"Average cues per track (with cues): {total_cues/tracks_with_cues:.1f}")
    print()

    if cue_names:
        print("Most common cue names:")
        sorted_cues = sorted(cue_names.items(), key=lambda x: x[1], reverse=True)
        for name, count in sorted_cues[:10]:
            print(f"  {name}: {count}")


def check_track_in_collection(root, filename):
    """Check if a specific track is in the collection."""
    print("="*70)
    print("TRACK SEARCH")
    print("="*70)
    print()

    print(f"Searching for: {filename}")
    print()

    for entry in root.findall('.//ENTRY'):
        location = entry.find('LOCATION')
        if location is not None:
            entry_file = location.get('FILE', '')
            if Path(entry_file).name.lower() == filename.lower():
                print(f"✅ Found: {entry_file}")

                # Show existing cues
                cues = entry.findall('CUE_V2')
                if cues:
                    print(f"\nExisting cue points: {len(cues)}")
                    for cue in cues:
                        name = cue.get('NAME', 'Unnamed')
                        start = cue.get('START', '0')
                        hotcue = cue.get('HOTCUE', 'N/A')
                        print(f"  • {name} at {float(start):.1f}s (Hotcue {int(hotcue)+1 if hotcue != 'N/A' else 'N/A'})")
                else:
                    print("\nNo existing cue points")

                return True

    print("❌ Track not found in collection")
    return False


def main():
    import sys

    # Find collection
    collection_path = find_collection_nml()

    if collection_path is None:
        print("❌ Traktor collection.nml not found")
        print("\nSearched:")
        print("  ~/Documents/Native Instruments/Traktor 3.0/collection.nml")
        print("  ~/Documents/Native Instruments/Traktor 2.11/collection.nml")
        print("  ~/Documents/Native Instruments/Traktor/collection.nml")
        print("\nIf your collection is elsewhere, specify the path:")
        print("  python3 test_nml_reader.py /path/to/collection.nml")
        sys.exit(1)

    # Or use provided path
    if len(sys.argv) > 1:
        collection_path = Path(sys.argv[1])
        if not collection_path.exists():
            print(f"❌ File not found: {collection_path}")
            sys.exit(1)

    try:
        # Read collection
        tree, root = read_collection_info(collection_path)

        # Show sample tracks
        show_sample_track(root, max_tracks=3)

        # Show statistics
        show_cue_statistics(root)

        # Search for specific track if provided
        if len(sys.argv) > 2:
            filename = sys.argv[2]
            check_track_in_collection(root, filename)

        print("="*70)
        print("\n✅ Collection read successfully!")
        print("\nTo search for a specific track:")
        print(f"  python3 test_nml_reader.py '{collection_path}' 'track_name.mp3'")
        print()

    except ET.ParseError as e:
        print(f"❌ Failed to parse collection.nml: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
