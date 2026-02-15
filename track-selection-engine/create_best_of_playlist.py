#!/usr/bin/env python3
"""Create playlist directly from Best of Deep Dub Tech House directory."""

import sys
import json
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from track_selector.models import TrackMetadata, Playlist, JourneyArc, Transition


# Your custom playlist in order
PLAYLIST_ORDER = [
    "Prof. Fee 2009 (Dub Taylor D. Mark Remix).m4a",
    "Helping Witness (Helly Larson Remix).m4a",
    "Berlin.m4a",
    "The Tribe.m4a",
    "Femur.m4a",
    "Crossing.m4a",
    "Dychotomie (Riccicomoto Bipolar Session).m4a",
    "Solid.m4a",
    "Full Focus.m4a",
    "Magnetic Swift (Klartraum Dream Remix).m4a",
    "Dreams.m4a",
    "Brotha Herve.m4a",
    "Worthy of Me (Klartraum Remix).m4a",
    "Wout 6.m4a",
    "Immortal.m4a",
    "Ball of Fur.m4a",
    "Melon Collie Dub (Shayde Remix).m4a",
    "Days of Glory (Dub Session).m4a",
    "Voyage.m4a",
    "Flamingo Park (Helly Larson Remix).m4a",
    "Maurice.m4a",
    "Those Who Be Happy (Klartraum Remix).m4a",
    "Dub Terminal.m4a",
    "Amazonas Santiago (Riccicomoto Para Dub).m4a",
    "Smooth Bass Phunk.m4a",
    "Contra emozione (Helmut Ebritsch Club Remix).m4a",
    "Behind Me (Riccicomoto Remix).m4a",
    "Last Lullaby (Nadja Lind Lucid Moment Remix).m4a",
    "When We Get Started Here.m4a",
    "Reflections.m4a",
]


def parse_filename_to_metadata(file_path: Path, library) -> TrackMetadata:
    """Parse filename and match with library data for BPM/duration."""
    filename = file_path.stem

    # Try to find in library for BPM data
    matched_track = None
    for track in library.tracks:
        if filename.lower() in track.title.lower() or track.title.lower() in filename.lower():
            matched_track = track
            break

    # Parse artist and title from filename
    if ' - ' in filename:
        parts = filename.split(' - ', 1)
        artist = parts[0].strip()
        title = parts[1].strip()
    else:
        # Extract from parentheses or brackets
        import re
        match = re.search(r'\((.*?)\)', filename)
        if match:
            artist = match.group(1)
            title = filename.replace(f'({artist})', '').strip()
        else:
            artist = "Unknown"
            title = filename

    # Use library data if found, otherwise estimate
    if matched_track:
        bpm = matched_track.bpm
        duration = matched_track.duration
        energy = matched_track.energy_level
    else:
        bpm = 123.0  # Default deep house BPM
        duration = 420.0  # Default 7 minutes
        energy = 5

    return TrackMetadata(
        file_path=file_path,
        title=title,
        artist=artist,
        bpm=bpm,
        duration=duration,
        energy_level=energy
    )


def main():
    """Main function."""
    # Paths
    music_dir = Path("/Volumes/TRAKTOR/Traktor/Music/2026/Best of Deep Dub Tech House")
    library_file = Path("traktor-library-detailed.json")

    if not music_dir.exists():
        print(f"Error: Directory not found: {music_dir}")
        sys.exit(1)

    # Load library for BPM/duration data
    print("Loading library for BPM data...")
    from track_selector.library import TrackLibrary
    library = TrackLibrary(library_file) if library_file.exists() else None

    print(f"\n{'='*80}")
    print("CREATING PLAYLIST: Best of Deep Dub Tech House")
    print(f"{'='*80}\n")

    # Build track list
    tracks = []
    found_count = 0

    for i, filename in enumerate(PLAYLIST_ORDER, 1):
        file_path = music_dir / filename

        if file_path.exists():
            track = parse_filename_to_metadata(file_path, library)
            tracks.append(track)
            found_count += 1

            print(f"{i:2d}. ✓ {track.artist} - {track.title}")
            print(f"    {track.bpm:.1f} BPM | E{track.energy_level} | {track.duration/60:.1f}min")
            print(f"    {file_path}")
        else:
            print(f"{i:2d}. ✗ NOT FOUND: {filename}")
        print()

    # Summary
    print(f"{'='*80}")
    print("SUMMARY")
    print(f"{'='*80}")
    print(f"Total tracks: {len(PLAYLIST_ORDER)}")
    print(f"Found: {found_count}")
    print(f"Missing: {len(PLAYLIST_ORDER) - found_count}")

    if tracks:
        bpms = [t.bpm for t in tracks]
        energies = [t.energy_level for t in tracks]
        total_duration = sum([t.duration for t in tracks])

        print(f"\nPlaylist Analysis:")
        print(f"  BPM range: {min(bpms):.1f} - {max(bpms):.1f}")
        print(f"  Average BPM: {sum(bpms)/len(bpms):.1f}")
        print(f"  Energy range: {min(energies)} - {max(energies)}")
        print(f"  Total duration: {total_duration/60:.1f} minutes ({total_duration/3600:.1f} hours)")

        # Create journey arc
        journey_arc = JourneyArc(
            name="Best of Deep Dub Tech House",
            description="30-track journey through deep space house - Lucidflow/Klartraum focused",
            duration_minutes=int(total_duration / 60),
            bpm_range=(min(bpms), max(bpms)),
            blend_duration=75,
            preferred_labels=["Lucidflow", "Echocord"]
        )

        # Create transitions
        transitions = []
        for i in range(len(tracks) - 1):
            track_a = tracks[i]
            track_b = tracks[i + 1]

            transition = Transition(
                track_a=track_a,
                track_b=track_b,
                start_time_a=max(0, track_a.duration - 75),
                start_time_b=0,
                blend_duration=75,
                bpm_compatible=abs(track_a.bpm - track_b.bpm) < 6,
                strategy="extended_blend",
                notes=f"75-second blend from {track_a.title} to {track_b.title}"
            )
            transitions.append(transition)

        # Create playlist
        playlist = Playlist(
            name="Best-of-Deep-Dub-Tech-House",
            journey_arc=journey_arc,
            tracks=tracks,
            transitions=transitions,
            created_at=datetime.now().isoformat()
        )

        playlist.calculate_duration()

        # Save JSON
        json_path = Path("best-of-deep-dub-tech-house.json")
        playlist.to_json(json_path)
        print(f"\n✓ Saved playlist: {json_path}")

        # Save M3U
        m3u_path = Path("best-of-deep-dub-tech-house.m3u")
        playlist.to_m3u(m3u_path)
        print(f"✓ Saved M3U: {m3u_path}")

        # Create Mixxx loader script
        mixxx_script_path = Path("best-of-deep-dub-tech-house.mixxx.js")

        # Convert to Mixxx format
        mixxx_playlist = {
            'name': playlist.name,
            'tracks': [t.to_dict() for t in tracks],
            'transitions': [tr.to_dict() for tr in transitions]
        }

        with open(mixxx_script_path, 'w') as f:
            f.write(f"// Auto-generated playlist: {playlist.name}\n")
            f.write(f"// Created: {datetime.now().isoformat()}\n\n")
            f.write(f"var playlist = {json.dumps(mixxx_playlist, indent=2)};\n\n")
            f.write("// Load into AI DJ Controller\n")
            f.write("if (typeof AI_DJ_Controller !== 'undefined') {\n")
            f.write("    AI_DJ_Controller.loadPlaylist(playlist);\n")
            f.write(f"    print('Playlist loaded: {playlist.name}');\n")
            f.write("    print('Total tracks: ' + playlist.tracks.length);\n")
            f.write("} else {\n")
            f.write("    print('ERROR: AI DJ Controller not found!');\n")
            f.write("}\n")

        print(f"✓ Saved Mixxx script: {mixxx_script_path}")

        print(f"\n{'='*80}")
        print("NEXT STEPS")
        print(f"{'='*80}")
        print("1. Import M3U into Traktor or Mixxx")
        print("2. For Mixxx automation:")
        print(f"   load('{mixxx_script_path.absolute()}');")
        print("   AI_DJ_Controller.start();")


if __name__ == '__main__':
    main()
