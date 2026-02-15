#!/usr/bin/env python3
"""Create custom playlist from track list and match with library."""

import sys
import json
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from track_selector.library import TrackLibrary
from track_selector.models import Playlist, JourneyArc, Transition


# Your custom 30-track playlist
CUSTOM_TRACKS = [
    ("Prof. Fee 2009 (Dub Taylor D. Mark Remix)", "Patrick Lindsey"),
    ("Helping Witness (Helly Larson Remix)", "Klartraum"),
    ("Berlin", "Justin Berkovi & Sevington"),
    ("The Tribe", "Tim Engelhardt"),
    ("Femur", "Counrad"),
    ("Crossing", "Helly Larson"),
    ("Dychotomie (Riccicomoto Bipolar Session)", "Nadja Lind & Riccicomoto"),
    ("Solid", "Dimmish"),
    ("Full Focus", "Terje Saether"),
    ("Magnetic Swift (Klartraum Dream Remix)", "Helly Larson & Riccicomoto"),
    ("Dreams", "D. Diggler"),
    ("Brotha Herve", "Nadja Lind"),
    ("Worthy of Me (Klartraum Remix)", "Timmus"),
    ("Wout 6", "Jonas Franzen"),
    ("Immortal (feat. Hansekind)", "Riccicomoto"),
    ("Ball of Fur", "G-Man & Nadja Lind"),
    ("Melon Collie Dub (Shayde Remix)", "Franksen"),
    ("Days of Glory (Dub Session)", "Riccicomoto"),
    ("Voyage", "Nadja Lind"),
    ("Flamingo Park (Helly Larson Remix)", "Helmut Ebritsch"),
    ("Maurice", "Andy Bach"),
    ("Those Who Be Happy (Klartraum Remix)", "Riccicomoto"),
    ("Dub Terminal", "Dave Marian"),
    ("Amazonas Santiago (Riccicomoto Para Dub)", "Klartraum"),
    ("Smooth Bass Phunk", "Helmut Ebritsch"),
    ("Contra emozione (Helmut Ebritsch Club Remix)", "Stefan Weise & i.qu"),
    ("Behind Me (Riccicomoto Remix)", "Weisses Licht"),
    ("Last Lullaby (Nadja Lind Lucid Moment Remix)", "Digital South"),
    ("When We Get Started Here", "Riccicomoto"),
    ("Reflections", "Brickman"),
]


def fuzzy_match(title1, title2):
    """Simple fuzzy matching for track titles."""
    # Normalize: lowercase, remove special chars
    import re
    t1 = re.sub(r'[^\w\s]', '', title1.lower())
    t2 = re.sub(r'[^\w\s]', '', title2.lower())

    # Check if one contains the other
    if t1 in t2 or t2 in t1:
        return True

    # Check word overlap
    words1 = set(t1.split())
    words2 = set(t2.split())
    overlap = len(words1 & words2) / max(len(words1), len(words2))

    return overlap > 0.5


def find_track(library, title, artist):
    """Find track in library by title and artist."""
    # Try exact match first
    for track in library.tracks:
        if track.title.lower() == title.lower() and track.artist.lower() == artist.lower():
            return track

    # Try fuzzy title match with artist match
    for track in library.tracks:
        if fuzzy_match(title, track.title) and artist.lower() in track.artist.lower():
            return track

    # Try artist match only
    for track in library.tracks:
        if artist.lower() in track.artist.lower() and fuzzy_match(title, track.title):
            return track

    return None


def main():
    """Main function."""
    library_file = Path("traktor-library-detailed.json")

    if not library_file.exists():
        print(f"Error: Library not found: {library_file}")
        sys.exit(1)

    print("Loading library...")
    library = TrackLibrary(library_file)
    print(f"✓ Loaded {len(library.tracks)} tracks\n")

    print("="*80)
    print("CUSTOM PLAYLIST: Lucidflow/Klartraum Journey (30 tracks)")
    print("="*80)
    print()

    matched = []
    not_found = []

    for i, (title, artist) in enumerate(CUSTOM_TRACKS, 1):
        track = find_track(library, title, artist)

        if track:
            matched.append(track)
            print(f"{i:2d}. ✓ {artist} - {title}")
            print(f"    {track.bpm:.1f} BPM | E{track.energy_level} | {track.duration/60:.1f}min")
        else:
            not_found.append((title, artist))
            print(f"{i:2d}. ✗ {artist} - {title}")
            print(f"    NOT FOUND IN LIBRARY")
        print()

    # Summary
    print("="*80)
    print("SUMMARY")
    print("="*80)
    print(f"Total tracks: {len(CUSTOM_TRACKS)}")
    print(f"Matched: {len(matched)}")
    print(f"Not found: {len(not_found)}")

    if matched:
        bpms = [t.bpm for t in matched]
        energies = [t.energy_level for t in matched]
        durations = [t.duration for t in matched]

        print(f"\nMatched Tracks Analysis:")
        print(f"  BPM range: {min(bpms):.1f} - {max(bpms):.1f}")
        print(f"  Average BPM: {sum(bpms)/len(bpms):.1f}")
        print(f"  Energy range: {min(energies)} - {max(energies)}")
        print(f"  Average energy: {sum(energies)/len(energies):.1f}")
        print(f"  Total duration: {sum(durations)/60:.1f} minutes")

    if not_found:
        print(f"\nNot found in library:")
        for title, artist in not_found:
            print(f"  - {artist} - {title}")

    # Create playlist if we have matches
    if matched:
        # Create journey arc
        journey_arc = JourneyArc(
            name="Lucidflow/Klartraum Journey",
            description="Custom 30-track deep space house journey",
            duration_minutes=int(sum([t.duration for t in matched]) / 60),
            bpm_range=(min([t.bpm for t in matched]), max([t.bpm for t in matched])),
            blend_duration=75
        )

        # Create transitions
        transitions = []
        for i in range(len(matched) - 1):
            track_a = matched[i]
            track_b = matched[i + 1]

            # Simple transition
            transition = Transition(
                track_a=track_a,
                track_b=track_b,
                start_time_a=max(0, track_a.duration - 75),
                start_time_b=0,
                blend_duration=75,
                strategy="extended_blend",
                notes=f"Blend from {track_a.title} to {track_b.title}"
            )
            transitions.append(transition)

        # Create playlist
        playlist = Playlist(
            name="Lucidflow-Klartraum-Journey",
            journey_arc=journey_arc,
            tracks=matched,
            transitions=transitions
        )

        playlist.calculate_duration()

        # Save JSON
        json_path = Path("lucidflow-klartraum-journey.json")
        playlist.to_json(json_path)
        print(f"\n✓ Saved playlist: {json_path}")

        # Save M3U
        m3u_path = Path("lucidflow-klartraum-journey.m3u")
        playlist.to_m3u(m3u_path)
        print(f"✓ Saved M3U: {m3u_path}")

        # Show playlist
        print(f"\n{'='*80}")
        print(f"PLAYLIST CREATED")
        print(f"{'='*80}\n")

        for i, track in enumerate(matched, 1):
            print(f"{i:2d}. {track.artist} - {track.title}")
            print(f"    {track.bpm:.1f} BPM | E{track.energy_level}")
            if i < len(matched):
                print(f"    └─ Blend: 75s")
            print()


if __name__ == '__main__':
    main()
