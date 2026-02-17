#!/usr/bin/env python3
"""
Hybrid Audio Analyzer - Combining Stripes + Librosa
====================================================

This script integrates:
1. Traktor Stripes analysis (structural detection: breakdowns, builds, drops)
2. Librosa beat detection (precise beat-level timestamps)

The result is intelligent cue point placement that combines:
- WHAT (structure from stripes): "Breakdown detected"
- WHERE (precision from librosa): "At beat 187 (93.12 seconds)"

Usage:
    python hybrid_analyzer.py <audio_file> <stripes_file>

Example:
    python hybrid_analyzer.py "track.mp3" "~/Documents/.../Stripes/000/ABC123"
"""

import sys
import librosa
import numpy as np
from pathlib import Path
from typing import List, Dict, Tuple, Optional
import json

# Import stripes analyzer
import sys
sys.path.insert(0, str(Path(__file__).parent))
from stripes_to_cuepoints import StripesAnalyzer


class HybridAnalyzer:
    """Combines Stripes structural analysis with Librosa beat detection."""

    def __init__(self, audio_path: str, stripes_path: str, sample_rate: int = 22050):
        """
        Initialize hybrid analyzer.

        Args:
            audio_path: Path to audio file
            stripes_path: Path to Traktor stripes file
            sample_rate: Sample rate for librosa analysis
        """
        self.audio_path = Path(audio_path)
        self.stripes_path = Path(stripes_path)
        self.sample_rate = sample_rate

        # Analysis results
        self.audio = None
        self.sr = None
        self.duration = 0.0
        self.beats = None
        self.beat_times = None
        self.stripes_cues = None
        self.final_cues = None

    def analyze(self) -> Dict:
        """
        Perform complete hybrid analysis.

        Returns:
            Dictionary with all analysis results
        """
        print("=" * 60)
        print("HYBRID ANALYSIS: Stripes + Librosa")
        print("=" * 60)

        # Step 1: Load and analyze audio with Librosa
        print("\n[1/4] Loading audio and detecting beats (Librosa)...")
        self._load_audio()
        self._detect_beats()

        # Step 2: Analyze stripes for structure
        print("\n[2/4] Analyzing track structure (Traktor Stripes)...")
        self._analyze_stripes()

        # Step 3: Merge analyses
        print("\n[3/4] Aligning structure to beats...")
        self._merge_analyses()

        # Step 4: Generate final cue points
        print("\n[4/4] Generating intelligent cue points...")
        results = self._generate_results()

        print(f"\n{'=' * 60}")
        print(f"Analysis complete! Found {len(self.final_cues)} cue points")
        print(f"{'=' * 60}\n")

        return results

    def _load_audio(self):
        """Load audio file with Librosa."""
        if not self.audio_path.exists():
            raise FileNotFoundError(f"Audio file not found: {self.audio_path}")

        print(f"  Loading: {self.audio_path.name}")
        self.audio, self.sr = librosa.load(str(self.audio_path), sr=self.sample_rate)
        self.duration = librosa.get_duration(y=self.audio, sr=self.sr)
        print(f"  Duration: {self.duration:.2f} seconds")
        print(f"  Sample rate: {self.sr} Hz")

    def _detect_beats(self):
        """Detect beats using Librosa."""
        print("  Detecting beats...")
        tempo, beat_frames = librosa.beat.beat_track(y=self.audio, sr=self.sr)
        self.beat_times = librosa.frames_to_time(beat_frames, sr=self.sr)
        self.beats = beat_frames
        self.tempo = float(tempo) if hasattr(tempo, '__iter__') else tempo

        print(f"  Tempo: {self.tempo:.1f} BPM")
        print(f"  Beats detected: {len(self.beat_times)}")

    def _analyze_stripes(self):
        """Analyze Traktor stripes file for structure."""
        if not self.stripes_path.exists():
            raise FileNotFoundError(f"Stripes file not found: {self.stripes_path}")

        print(f"  Analyzing: {self.stripes_path.name}")

        # Parse stripes file
        stripes = StripesAnalyzer(self.stripes_path)
        stripes.parse_file()
        stripes.set_track_duration(self.duration)

        # Get structure-based cue points
        self.stripes_cues = stripes.suggest_cue_points()

        print(f"  Structural features detected:")
        breakdown_count = len([c for c in self.stripes_cues if c['type'] == 'breakdown'])
        buildup_count = len([c for c in self.stripes_cues if c['type'] == 'buildup'])
        drop_count = len([c for c in self.stripes_cues if c['type'] == 'drop'])

        print(f"    - Breakdowns: {breakdown_count}")
        print(f"    - Build-ups: {buildup_count}")
        print(f"    - Drops: {drop_count}")

    def _merge_analyses(self):
        """
        Merge stripes structural analysis with Librosa beat detection.

        For each structural feature from stripes:
        1. Find the approximate time from stripes analysis
        2. Snap to the nearest beat from Librosa
        3. Enhance with beat-precise timing
        """
        print("  Aligning structural features to beats...")

        merged_cues = []

        for cue in self.stripes_cues:
            # Get approximate time from stripes
            approx_time = cue['time']

            # Snap to nearest beat
            beat_time, beat_number = self._snap_to_nearest_beat(approx_time)

            # Create enhanced cue point
            enhanced_cue = {
                'type': cue['type'],
                'name': cue['name'],
                'description': cue['description'],
                'stripes_time': approx_time,  # Original stripes detection
                'beat_time': beat_time,        # Beat-aligned time
                'beat_number': beat_number,    # Which beat (for visual reference)
                'time_adjustment': beat_time - approx_time,  # How much we adjusted
            }

            merged_cues.append(enhanced_cue)

        self.final_cues = merged_cues

        print(f"  Aligned {len(merged_cues)} cue points to beats")
        print(f"  Average adjustment: {np.mean([abs(c['time_adjustment']) for c in merged_cues]):.3f}s")

    def _snap_to_nearest_beat(self, time: float) -> Tuple[float, int]:
        """
        Snap a time to the nearest beat.

        Args:
            time: Time in seconds

        Returns:
            Tuple of (beat_time, beat_number)
        """
        if len(self.beat_times) == 0:
            return (time, 0)

        # Find nearest beat
        idx = np.argmin(np.abs(self.beat_times - time))
        beat_time = self.beat_times[idx]
        beat_number = idx + 1  # 1-indexed for human readability

        return (float(beat_time), int(beat_number))

    def _generate_results(self) -> Dict:
        """Generate final analysis results."""
        return {
            'file': str(self.audio_path),
            'duration': self.duration,
            'tempo': self._calculate_bpm(),
            'total_beats': len(self.beat_times),
            'cue_points': self.final_cues,
            'summary': self._generate_summary(),
        }

    def _calculate_bpm(self) -> float:
        """Calculate BPM from detected beats."""
        if len(self.beat_times) < 2:
            return 0.0

        beat_intervals = np.diff(self.beat_times)
        avg_interval = np.mean(beat_intervals)
        bpm = 60.0 / avg_interval
        return float(bpm)

    def _generate_summary(self) -> Dict:
        """Generate summary statistics."""
        cue_types = {}
        for cue in self.final_cues:
            cue_type = cue['type']
            if cue_type not in cue_types:
                cue_types[cue_type] = []
            cue_types[cue_type].append(cue)

        return {
            'total_cue_points': len(self.final_cues),
            'breakdowns': len(cue_types.get('breakdown', [])),
            'buildups': len(cue_types.get('buildup', [])),
            'drops': len(cue_types.get('drop', [])),
            'load_points': len(cue_types.get('load', [])),
        }

    def print_cue_points(self):
        """Print cue points in a readable format."""
        if not self.final_cues:
            print("No cue points generated yet. Run analyze() first.")
            return

        print("\n" + "=" * 80)
        print("INTELLIGENT CUE POINTS (Stripes Structure + Librosa Beat Precision)")
        print("=" * 80)

        for i, cue in enumerate(self.final_cues, 1):
            print(f"\n{i}. {cue['name']} ({cue['type'].upper()})")
            print(f"   Time: {cue['beat_time']:.2f}s (Beat #{cue['beat_number']})")
            print(f"   Description: {cue['description']}")

            # Show alignment details if significant adjustment
            if abs(cue['time_adjustment']) > 0.1:
                print(f"   [Aligned from {cue['stripes_time']:.2f}s → {cue['beat_time']:.2f}s]")

        print(f"\n{'=' * 80}")

    def save_to_file(self, output_path: Optional[str] = None):
        """
        Save analysis results to JSON file.

        Args:
            output_path: Output file path (optional)
        """
        if output_path is None:
            output_path = self.audio_path.parent / f"{self.audio_path.stem}_analysis.json"
        else:
            output_path = Path(output_path)

        results = self._generate_results()

        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2)

        print(f"\nAnalysis saved to: {output_path}")

    def export_traktor_cues(self) -> List[Dict]:
        """
        Export cue points in a format ready for Traktor NML integration.

        Returns:
            List of cue point dictionaries with Traktor-compatible metadata
        """
        traktor_cues = []

        # Color mapping for Traktor cue points
        color_map = {
            'load': 0,       # Blue - Load point
            'breakdown': 1,  # Green - Mix in
            'buildup': 2,    # Yellow - Structure
            'drop': 3,       # Orange - Important moment
        }

        for cue in self.final_cues:
            traktor_cue = {
                'name': cue['name'],
                'time': cue['beat_time'],
                'type': 0,  # Cue (not loop)
                'color': color_map.get(cue['type'], 4),  # Default to red
                'description': cue['description'],
            }
            traktor_cues.append(traktor_cue)

        return traktor_cues


def main():
    """Main entry point."""
    if len(sys.argv) < 3:
        print("Usage: python hybrid_analyzer.py <audio_file> <stripes_file>")
        print("\nExample:")
        print('  python hybrid_analyzer.py "track.mp3" "~/Documents/.../Stripes/000/ABC123"')
        print("\nThis will:")
        print("  1. Detect beats with Librosa (precise timing)")
        print("  2. Detect structure with Stripes (breakdowns, builds, drops)")
        print("  3. Align structure to beats for intelligent cue points")
        return 1

    audio_file = Path(sys.argv[1]).expanduser()
    stripes_file = Path(sys.argv[2]).expanduser()

    # Validate files exist
    if not audio_file.exists():
        print(f"Error: Audio file not found: {audio_file}")
        return 1

    if not stripes_file.exists():
        print(f"Error: Stripes file not found: {stripes_file}")
        return 1

    # Run hybrid analysis
    try:
        analyzer = HybridAnalyzer(str(audio_file), str(stripes_file))
        results = analyzer.analyze()

        # Print results
        analyzer.print_cue_points()

        # Print summary
        summary = results['summary']
        print(f"\nSummary:")
        print(f"  Track: {audio_file.name}")
        print(f"  Duration: {results['duration']:.2f}s")
        print(f"  Tempo: {results['tempo']:.1f} BPM")
        print(f"  Total Cue Points: {summary['total_cue_points']}")
        print(f"    - Load points: {summary['load_points']}")
        print(f"    - Breakdowns: {summary['breakdowns']}")
        print(f"    - Build-ups: {summary['buildups']}")
        print(f"    - Drops: {summary['drops']}")

        # Save to file
        analyzer.save_to_file()

        # Export Traktor-ready cues
        traktor_cues = analyzer.export_traktor_cues()
        print(f"\nGenerated {len(traktor_cues)} Traktor-ready cue points")

        return 0

    except Exception as e:
        print(f"Error during analysis: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
