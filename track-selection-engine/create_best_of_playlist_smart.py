#!/usr/bin/env python3
"""Create intelligently ordered playlist from Best of Deep Dub Tech House tracks."""

import sys
import json
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from track_selector.models import TrackMetadata, Playlist, JourneyArc, Transition
from track_selector.library import TrackLibrary
from track_selector.journey_planner import JourneyPlanner


def parse_filename_to_metadata(file_path: Path, library) -> TrackMetadata:
    """Parse filename and match with library data for BPM/duration."""
    filename = file_path.stem

    # Try to find in library for BPM data
    matched_track = None
    for track in library.tracks:
        # Fuzzy match on title
        if filename.lower() in track.title.lower() or track.title.lower() in filename.lower():
            matched_track = track
            break

    # Parse artist and title from filename
    # Common patterns in the filenames
    import re

    # Try to extract artist from parentheses (e.g., "Song Title (Artist Remix)")
    remix_match = re.search(r'\((.*?(?:Remix|Mix|Dub|Session).*?)\)', filename)
    if remix_match:
        title_part = filename[:remix_match.start()].strip()
        remix_part = remix_match.group(1)

        # Look for artist before the remix indicator
        artist_match = re.search(r'(.*?)\s+(?:Remix|Mix|Dub)', remix_part)
        if artist_match:
            artist = artist_match.group(1).strip()
            title = f"{title_part} ({remix_part})"
        else:
            artist = "Unknown"
            title = filename
    else:
        # No remix, just use filename as title
        artist = "Unknown"
        title = filename

    # Use library data if found, otherwise estimate
    if matched_track:
        bpm = matched_track.bpm
        duration = matched_track.duration
        energy = matched_track.energy_level
        # Use library artist if available
        if matched_track.artist != "Unknown":
            artist = matched_track.artist
    else:
        bpm = 123.0  # Default deep house BPM
        duration = 420.0  # Default 7 minutes
        # Estimate energy from BPM
        if bpm < 120:
            energy = 3
        elif bpm < 123:
            energy = 4
        elif bpm < 126:
            energy = 5
        elif bpm < 128:
            energy = 6
        else:
            energy = 7

    return TrackMetadata(
        file_path=file_path,
        title=title,
        artist=artist,
        bpm=bpm,
        duration=duration,
        energy_level=energy
    )


def create_intelligent_order(tracks: list) -> list:
    """
    Create intelligent track order based on:
    - BPM progression
    - Energy curve (gradual build)
    - Smooth transitions
    """
    # Sort tracks by BPM first to understand range
    tracks_by_bpm = sorted(tracks, key=lambda t: t.bpm)

    # Create energy curve for 30 tracks (gradual build)
    # Opening (tracks 1-8): Energy 3-4 (low BPM)
    # Building (tracks 9-16): Energy 4-5 (mid BPM)
    # Core (tracks 17-24): Energy 5-6 (mid-high BPM)
    # Peak (tracks 25-28): Energy 6-7 (high BPM)
    # Descent (tracks 29-30): Energy 5-6 (back down)

    energy_curve = (
        [3, 3, 3, 4, 4, 4, 4, 4] +      # Opening (8 tracks)
        [4, 5, 5, 5, 5, 5, 5, 5] +      # Building (8 tracks)
        [5, 6, 6, 6, 6, 6, 6, 6] +      # Core (8 tracks)
        [6, 7, 7, 7] +                   # Peak (4 tracks)
        [6, 5]                           # Descent (2 tracks)
    )

    ordered_tracks = []
    available_tracks = tracks.copy()

    for target_energy in energy_curve:
        # Find best match for this energy level
        best_track = None
        best_score = -1000

        for track in available_tracks:
            score = 0

            # Energy match (most important)
            energy_diff = abs(track.energy_level - target_energy)
            score -= energy_diff * 10

            # BPM smoothness (prefer gradual changes)
            if ordered_tracks:
                last_track = ordered_tracks[-1]
                bpm_diff = abs(track.bpm - last_track.bpm)

                # Penalize large BPM jumps
                if bpm_diff > 6:
                    score -= bpm_diff * 2
                # Reward small changes
                elif bpm_diff < 3:
                    score += 5

                # Reward upward BPM trend in building phase
                if len(ordered_tracks) < 24 and track.bpm > last_track.bpm:
                    score += 3

                # Reward downward BPM in descent
                if len(ordered_tracks) >= 28 and track.bpm < last_track.bpm:
                    score += 3

            if score > best_score:
                best_score = score
                best_track = track

        if best_track:
            ordered_tracks.append(best_track)
            available_tracks.remove(best_track)

    return ordered_tracks


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
    library = TrackLibrary(library_file) if library_file.exists() else None

    print(f"\n{'='*80}")
    print("ANALYZING TRACKS: Best of Deep Dub Tech House")
    print(f"{'='*80}\n")

    # Scan directory for all M4A files
    tracks = []
    for file_path in sorted(music_dir.glob("*.m4a")):
        track = parse_filename_to_metadata(file_path, library)
        tracks.append(track)
        print(f"✓ {track.artist} - {track.title}")
        print(f"  {track.bpm:.1f} BPM | E{track.energy_level} | {track.duration/60:.1f}min")

    print(f"\n{'='*80}")
    print(f"CREATING INTELLIGENT TRACK ORDER")
    print(f"{'='*80}\n")
    print("Using gradual build energy progression:")
    print("  Opening (1-8):   Energy 3-4 (atmospheric)")
    print("  Building (9-16): Energy 4-5 (developing)")
    print("  Core (17-24):    Energy 5-6 (engaging)")
    print("  Peak (25-28):    Energy 6-7 (peak moments)")
    print("  Descent (29-30): Energy 5-6 (wind down)")
    print()

    # Create intelligent order
    ordered_tracks = create_intelligent_order(tracks)

    # Display ordered playlist
    print(f"{'='*80}")
    print("ORDERED PLAYLIST")
    print(f"{'='*80}\n")

    for i, track in enumerate(ordered_tracks, 1):
        print(f"{i:2d}. {track.artist} - {track.title}")
        print(f"    {track.bpm:.1f} BPM | E{track.energy_level}")
        if i < len(ordered_tracks):
            next_track = ordered_tracks[i]
            bpm_diff = next_track.bpm - track.bpm
            print(f"    └─ Next: {bpm_diff:+.1f} BPM change")
        print()

    # Summary
    bpms = [t.bpm for t in ordered_tracks]
    energies = [t.energy_level for t in ordered_tracks]
    total_duration = sum([t.duration for t in ordered_tracks])

    print(f"{'='*80}")
    print("PLAYLIST ANALYSIS")
    print(f"{'='*80}")
    print(f"Total tracks: {len(ordered_tracks)}")
    print(f"BPM range: {min(bpms):.1f} - {max(bpms):.1f}")
    print(f"Average BPM: {sum(bpms)/len(bpms):.1f}")
    print(f"Energy range: {min(energies)} - {max(energies)}")
    print(f"Total duration: {total_duration/60:.1f} minutes ({total_duration/3600:.1f} hours)")

    # Show BPM progression
    print(f"\nBPM Progression:")
    for i in range(0, len(ordered_tracks), 5):
        chunk = ordered_tracks[i:i+5]
        bpm_str = ", ".join([f"{t.bpm:.0f}" for t in chunk])
        print(f"  Tracks {i+1}-{min(i+5, len(ordered_tracks))}: {bpm_str} BPM")

    # Create journey arc
    journey_arc = JourneyArc(
        name="Best of Deep Dub Tech House - AI Ordered",
        description="30-track intelligently ordered journey through deep space house",
        duration_minutes=int(total_duration / 60),
        bpm_range=(min(bpms), max(bpms)),
        blend_duration=75,
        preferred_labels=["Lucidflow", "Echocord"],
        energy_curve=energies
    )

    # Create transitions
    transitions = []
    for i in range(len(ordered_tracks) - 1):
        track_a = ordered_tracks[i]
        track_b = ordered_tracks[i + 1]

        bpm_compatible = abs(track_a.bpm - track_b.bpm) < 6
        energy_compatible = abs(track_a.energy_level - track_b.energy_level) <= 2

        transition = Transition(
            track_a=track_a,
            track_b=track_b,
            start_time_a=max(0, track_a.duration - 75),
            start_time_b=0,
            blend_duration=75,
            bpm_compatible=bpm_compatible,
            energy_compatible=energy_compatible,
            strategy="extended_blend",
            notes=f"75s blend | BPM: {track_a.bpm:.0f}→{track_b.bpm:.0f} | Energy: {track_a.energy_level}→{track_b.energy_level}"
        )
        transitions.append(transition)

    # Create playlist
    playlist = Playlist(
        name="Best-of-Deep-Dub-Tech-House-AI-Ordered",
        journey_arc=journey_arc,
        tracks=ordered_tracks,
        transitions=transitions,
        created_at=datetime.now().isoformat()
    )

    playlist.calculate_duration()

    # Save JSON
    json_path = Path("best-of-deep-dub-tech-house-ai-ordered.json")
    playlist.to_json(json_path)
    print(f"\n✓ Saved playlist: {json_path}")

    # Save M3U
    m3u_path = Path("best-of-deep-dub-tech-house-ai-ordered.m3u")
    playlist.to_m3u(m3u_path)
    print(f"✓ Saved M3U: {m3u_path}")

    # Create Mixxx loader script
    mixxx_script_path = Path("best-of-deep-dub-tech-house-ai-ordered.mixxx.js")

    mixxx_playlist = {
        'name': playlist.name,
        'tracks': [t.to_dict() for t in ordered_tracks],
        'transitions': [tr.to_dict() for tr in transitions]
    }

    with open(mixxx_script_path, 'w') as f:
        f.write(f"// Auto-generated AI-ordered playlist: {playlist.name}\n")
        f.write(f"// Created: {datetime.now().isoformat()}\n")
        f.write(f"// Energy progression: gradual build with peak and descent\n\n")
        f.write(f"var playlist = {json.dumps(mixxx_playlist, indent=2)};\n\n")
        f.write("// Load into AI DJ Controller\n")
        f.write("if (typeof AI_DJ_Controller !== 'undefined') {\n")
        f.write("    AI_DJ_Controller.loadPlaylist(playlist);\n")
        f.write(f"    print('Playlist loaded: {playlist.name}');\n")
        f.write("    print('Total tracks: ' + playlist.tracks.length);\n")
        f.write("    print('Ready to start automated performance!');\n")
        f.write("} else {\n")
        f.write("    print('ERROR: AI DJ Controller not found!');\n")
        f.write("}\n")

    print(f"✓ Saved Mixxx script: {mixxx_script_path}")

    print(f"\n{'='*80}")
    print("NEXT STEPS")
    print(f"{'='*80}")
    print("1. Review the track order above")
    print("2. Import M3U into Traktor or Mixxx")
    print("3. For Mixxx automation:")
    print(f"   load('{mixxx_script_path.absolute()}');")
    print("   AI_DJ_Controller.start();")
    print("\nThe AI has ordered your tracks for optimal energy flow!")


if __name__ == '__main__':
    main()
