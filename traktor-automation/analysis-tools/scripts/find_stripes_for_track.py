#!/usr/bin/env python3
"""
Find Stripes File for Audio Track
==================================

Helper script to find the corresponding Traktor stripes file for an audio track.

Strategy:
1. Calculate audio file duration with librosa
2. Search all stripes files for matching duration
3. Return likely matches

Usage:
    python find_stripes_for_track.py <audio_file>

Example:
    python find_stripes_for_track.py "/Volumes/TRAKTOR/.../Dreams.m4a"
"""

import sys
import librosa
from pathlib import Path
from typing import List, Tuple
import os

# Import stripes analyzer
sys.path.insert(0, str(Path(__file__).parent))
from stripes_to_cuepoints import StripesAnalyzer


def get_audio_duration(audio_file: str) -> float:
    """Get duration of audio file using librosa."""
    print(f"Analyzing audio file: {Path(audio_file).name}")
    y, sr = librosa.load(audio_file, sr=22050)
    duration = librosa.get_duration(y=y, sr=sr)
    print(f"  Duration: {duration:.2f} seconds ({duration/60:.2f} minutes)")
    return duration


def estimate_stripes_duration(stripes_file: Path) -> float:
    """
    Estimate track duration from stripes file.

    Stripes files have ~87,000 samples per track.
    The ratio is roughly: samples / 240 ≈ duration_seconds
    """
    file_size = stripes_file.stat().st_size

    # Parse stripes to get sample count
    try:
        analyzer = StripesAnalyzer(stripes_file)
        samples = analyzer.parse_file()

        # Rough estimation: ~240 samples per second
        estimated_duration = len(samples) / 240.0
        return estimated_duration
    except Exception:
        return 0.0


def find_matching_stripes(
    audio_duration: float,
    stripes_dir: Path,
    tolerance: float = 5.0
) -> List[Tuple[Path, float, float]]:
    """
    Find stripes files with matching duration.

    Args:
        audio_duration: Duration of audio file in seconds
        stripes_dir: Traktor stripes directory
        tolerance: Duration tolerance in seconds

    Returns:
        List of (stripes_file, estimated_duration, duration_diff) tuples
    """
    matches = []

    print(f"\nSearching for stripes files in: {stripes_dir}")
    print(f"  Looking for duration: {audio_duration:.2f}s (±{tolerance}s)")

    # Search all subdirectories
    subdirs = sorted([d for d in stripes_dir.iterdir() if d.is_dir()])
    total_files = 0

    for subdir in subdirs:
        stripes_files = list(subdir.iterdir())
        total_files += len(stripes_files)

        for stripes_file in stripes_files:
            # Skip hidden files
            if stripes_file.name.startswith('.'):
                continue

            # Estimate duration
            estimated_duration = estimate_stripes_duration(stripes_file)

            if estimated_duration == 0:
                continue

            # Check if duration matches
            duration_diff = abs(estimated_duration - audio_duration)

            if duration_diff <= tolerance:
                matches.append((stripes_file, estimated_duration, duration_diff))

    print(f"  Searched {total_files} stripes files in {len(subdirs)} subdirectories")
    return matches


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python find_stripes_for_track.py <audio_file>")
        print("\nExample:")
        print('  python find_stripes_for_track.py "/Volumes/TRAKTOR/.../Dreams.m4a"')
        return 1

    audio_file = Path(sys.argv[1]).expanduser()

    if not audio_file.exists():
        print(f"Error: Audio file not found: {audio_file}")
        return 1

    # Find Traktor stripes directory
    stripes_dir = Path.home() / "Documents" / "Native Instruments" / "Traktor 3.11.1" / "Stripes"

    if not stripes_dir.exists():
        print(f"Error: Stripes directory not found: {stripes_dir}")
        return 1

    print("=" * 80)
    print("FINDING STRIPES FILE FOR TRACK")
    print("=" * 80)

    # Get audio duration
    audio_duration = get_audio_duration(str(audio_file))

    # Find matching stripes files
    matches = find_matching_stripes(audio_duration, stripes_dir, tolerance=5.0)

    # Display results
    print(f"\n{'=' * 80}")
    print(f"RESULTS: Found {len(matches)} potential match(es)")
    print(f"{'=' * 80}\n")

    if not matches:
        print("❌ No matching stripes files found")
        print("\nThis could mean:")
        print("  1. The track hasn't been analyzed in Traktor yet")
        print("  2. The duration estimation is off")
        print("  3. The stripes file is in a different location")
        print("\nSolution: Open Traktor and analyze this track first")
        return 0

    # Sort by closest match
    matches.sort(key=lambda x: x[2])

    for i, (stripes_file, estimated_duration, duration_diff) in enumerate(matches, 1):
        print(f"{i}. {stripes_file.parent.name}/{stripes_file.name}")
        print(f"   Estimated duration: {estimated_duration:.2f}s")
        print(f"   Difference: {duration_diff:.2f}s")
        print(f"   Confidence: {'HIGH' if duration_diff < 1.0 else 'MEDIUM' if duration_diff < 3.0 else 'LOW'}")

        if i == 1:
            print(f"\n   ⭐ BEST MATCH - Use this for hybrid analysis:")
            print(f"   python hybrid_analyzer.py \\ ")
            print(f"     \"{audio_file}\" \\ ")
            print(f"     \"{stripes_file}\"")

        print()

    return 0


if __name__ == '__main__':
    sys.exit(main())
