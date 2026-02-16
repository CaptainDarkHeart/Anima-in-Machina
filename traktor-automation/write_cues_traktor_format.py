#!/usr/bin/env python3
"""
Write cues using Traktor's timestamp format (appears to be milliseconds for some entries)
"""
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from audio_analyzer import AudioAnalyzer
from traktor_nml_writer import TraktorNMLWriter

def main():
    playlist_path = sys.argv[1] if len(sys.argv) > 1 else '../track-selection-engine/best-of-deep-dub-tech-house-ai-ordered.json'

    # Load playlist
    with open(playlist_path) as f:
        playlist_data = json.load(f)

    # Handle different formats
    if isinstance(playlist_data, dict) and 'tracks' in playlist_data:
        tracks = playlist_data['tracks']
    elif isinstance(playlist_data, list):
        tracks = playlist_data
    else:
        tracks = []

    file_paths = [track['file_path'] if isinstance(track, dict) else track for track in tracks]

    print(f"📋 Processing {len(file_paths)} tracks with Traktor timestamp format...\n")

    # Initialize
    analyzer = AudioAnalyzer()
    writer = TraktorNMLWriter()

    for i, file_path in enumerate(file_paths, 1):
        # Extract title from path
        from pathlib import Path
        filename = Path(file_path).stem

        print(f"[{i}/{len(file_paths)}] {filename}")

        # Analyze audio
        analysis = analyzer.analyze_track(file_path)
        if not analysis:
            print(f"  ⚠️  Could not analyze")
            continue

        # Find entry in collection
        entries = writer.find_track_entry(file_path)
        if not entries:
            print(f"  ⚠️  Not found in collection")
            continue

        print(f"  ℹ️  Found {len(entries)} entries - writing cues to all")

        # Extract cue times from analysis
        cues_data = analysis.get('cue_points', {})

        # Add cues using TRAKTOR FORMAT (multiply by 1000)
        cue_mapping = [
            ('intro_end', 'Intro End', 0, 0),
            ('breakdown', 'Breakdown', 1, 1),
            ('build', 'Build', 2, 2),
            ('drop', 'Drop', 3, 3),
            ('outro', 'Outro', 4, 4),
        ]

        for entry in entries:
            # Remove existing cues
            for cue in list(entry.findall('CUE_V2')):
                entry.remove(cue)

            # Add cues with Traktor format (timestamps * 1000)
            for cue_key, cue_name, slot, color in cue_mapping:
                if cue_key in cues_data:
                    time_seconds = cues_data[cue_key]
                    # MULTIPLY BY 1000 for Traktor format!
                    time_traktor = time_seconds * 1000

                    writer.add_cue_point(entry, cue_name, time_traktor, slot, color)
                    print(f"  ✓ {cue_name}: {time_seconds:.1f}s (stored as {time_traktor:.3f}) → Hotcue {slot+1}")

        print()

    # Save
    writer.save()
    print(f"\n✅ Done! Cues written in Traktor format (timestamps × 1000)")
    print("🎯 Restart Traktor and check if cues appear correctly!")

if __name__ == '__main__':
    main()
