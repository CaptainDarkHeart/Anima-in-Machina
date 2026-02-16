#!/usr/bin/env python3
"""
Test script for audio analysis functionality.

Usage:
    python test_audio_analysis.py <audio_file.mp3>
"""

import sys
import json
from pathlib import Path
from audio_analyzer import AudioAnalyzer


def format_time(seconds: float) -> str:
    """Format seconds as MM:SS."""
    mins = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{mins}:{secs:02d}"


def print_analysis(analysis: Dict):
    """Pretty print analysis results."""
    print("\n" + "="*70)
    print("AUDIO ANALYSIS RESULTS")
    print("="*70)

    # Basic info
    print(f"\n📁 File: {Path(analysis['file_path']).name}")
    print(f"⏱  Duration: {format_time(analysis['duration'])}")

    # Tempo
    tempo = analysis['tempo']
    print(f"\n🥁 TEMPO")
    print(f"   BPM: {tempo['bpm']:.1f}")
    print(f"   Confidence: {tempo['confidence']:.1%}")
    print(f"   Beats detected: {tempo['beat_count']}")
    print(f"   First beat: {tempo['first_beat_time']:.2f}s")

    # Harmony
    harmony = analysis['harmony']
    print(f"\n🎹 HARMONY")
    print(f"   Key: {harmony['full_key']}")
    print(f"   Confidence: {harmony['confidence']:.1%}")

    # Energy
    energy = analysis['energy']
    print(f"\n⚡ ENERGY")
    print(f"   Overall: {energy['overall']:.3f}")
    print(f"   Peak: {energy['peak']:.3f}")
    print(f"   Segments: {len(energy['segments'])}")

    # Energy profile (simplified visualization)
    print(f"\n   Energy over time:")
    segments = energy['segments'][:10]  # First 10 segments
    for seg in segments:
        bar_length = int(seg['energy'] * 40)
        bar = '█' * bar_length
        print(f"   {format_time(seg['start_time'])}: {bar} {seg['energy']:.3f}")

    # Cue points
    cue_points = analysis['cue_points']
    print(f"\n📍 CUE POINTS")
    print(f"   Intro: {format_time(cue_points['intro_start'])} - {format_time(cue_points['intro_end'])}")
    print(f"   Outro: {format_time(cue_points['outro_start'])} - {format_time(cue_points['outro_end'])}")

    if 'breakdown' in cue_points:
        bd = cue_points['breakdown']
        print(f"   Breakdown: {format_time(bd['start'])} - {format_time(bd['end'])} ({bd['duration']:.1f}s)")

    if 'build' in cue_points:
        build = cue_points['build']
        print(f"   Build: {format_time(build['start'])} - {format_time(build['end'])} ({build['duration']:.1f}s)")

    if 'drop' in cue_points:
        drop = cue_points['drop']
        print(f"   Drop: {format_time(drop['time'])} (intensity: {drop['intensity']:.3f})")

    # Spectral
    spectral = analysis['spectral']
    print(f"\n🌈 SPECTRAL")
    print(f"   Brightness: {spectral['brightness']:.0f} Hz")
    print(f"   Rolloff: {spectral['rolloff']:.0f} Hz")
    print(f"   Percussiveness: {spectral['percussiveness']:.3f}")

    print("\n" + "="*70)


def test_compatibility(file1: str, file2: str):
    """Test compatibility between two tracks."""
    print("\n" + "="*70)
    print("TRACK COMPATIBILITY TEST")
    print("="*70)

    analyzer = AudioAnalyzer()

    print(f"\nAnalyzing: {Path(file1).name}")
    analysis1 = analyzer.analyze_track(file1)

    print(f"Analyzing: {Path(file2).name}")
    analysis2 = analyzer.analyze_track(file2)

    # Check compatibility
    compat = analyzer.are_tracks_compatible(analysis1, analysis2)

    print(f"\n🎯 COMPATIBILITY SCORE: {compat['score']:.0f}/100")

    if compat['compatible']:
        print("✓ Tracks are compatible for mixing")
    else:
        print("✗ Tracks may be difficult to mix")

    if compat['reasons']:
        print(f"\nReasons:")
        for reason in compat['reasons']:
            print(f"  • {reason}")

    # Show mix points
    print(f"\n📍 RECOMMENDED MIX POINTS")
    print(f"\nTrack 1: {Path(file1).name}")
    print(f"  Mix out at: {format_time(analyzer.get_mix_out_point(analysis1))}")

    print(f"\nTrack 2: {Path(file2).name}")
    print(f"  Mix in at: {format_time(analyzer.get_mix_in_point(analysis2))}")

    print("\n" + "="*70)


def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  Single file:  python test_audio_analysis.py <audio_file.mp3>")
        print("  Compare two:  python test_audio_analysis.py <file1.mp3> <file2.mp3>")
        sys.exit(1)

    file1 = sys.argv[1]

    if not Path(file1).exists():
        print(f"Error: File not found: {file1}")
        sys.exit(1)

    # Single file analysis
    if len(sys.argv) == 2:
        print("Analyzing audio file (this may take 10-30 seconds)...")

        analyzer = AudioAnalyzer()
        analysis = analyzer.analyze_track(file1)

        print_analysis(analysis)

        # Show cache location
        cache_path = analyzer._get_cache_path(file1)
        print(f"\n💾 Analysis cached at: {cache_path}")

    # Two file comparison
    elif len(sys.argv) == 3:
        file2 = sys.argv[2]

        if not Path(file2).exists():
            print(f"Error: File not found: {file2}")
            sys.exit(1)

        test_compatibility(file1, file2)


if __name__ == "__main__":
    main()
