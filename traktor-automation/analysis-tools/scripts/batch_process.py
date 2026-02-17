#!/usr/bin/env python3
"""
Batch Process Tracks with Hybrid Analysis
==========================================

Process a directory of audio files with hybrid Stripes + Librosa analysis.

This script:
1. Finds all audio files in a directory
2. Attempts to locate corresponding Traktor stripes files
3. Runs hybrid analysis on each track
4. Saves results to JSON files
5. Generates a summary report

Usage:
    python batch_process.py <music_directory> [--stripes-dir PATH] [--output-dir PATH]

Example:
    python batch_process.py "/Volumes/TRAKTOR/Traktor/Music/2026/Best of Deep Dub Tech House"
"""

import sys
import argparse
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import json
import hashlib
import xml.etree.ElementTree as ET
from datetime import datetime
import traceback

# Import hybrid analyzer
sys.path.insert(0, str(Path(__file__).parent))
from hybrid_analyzer import HybridAnalyzer


class BatchProcessor:
    """Batch process audio files with hybrid analysis."""

    def __init__(
        self,
        music_dir: str,
        stripes_dir: Optional[str] = None,
        output_dir: Optional[str] = None,
        collection_nml: Optional[str] = None
    ):
        """
        Initialize batch processor.

        Args:
            music_dir: Directory containing audio files
            stripes_dir: Traktor stripes directory (auto-detected if None)
            output_dir: Output directory for results (defaults to music_dir/analysis)
            collection_nml: Path to collection.nml for track mapping
        """
        self.music_dir = Path(music_dir)
        self.stripes_dir = self._find_stripes_dir(stripes_dir)
        self.output_dir = Path(output_dir) if output_dir else self.music_dir / "analysis"
        self.collection_nml = Path(collection_nml) if collection_nml else self._find_collection_nml()

        # Results
        self.results = []
        self.errors = []
        self.successful = 0
        self.failed = 0
        self.skipped = 0

    def _find_stripes_dir(self, custom_path: Optional[str]) -> Path:
        """Find Traktor stripes directory."""
        if custom_path:
            return Path(custom_path)

        # Default Traktor location
        default_path = Path.home() / "Documents" / "Native Instruments" / "Traktor 3.11.1" / "Stripes"

        if default_path.exists():
            return default_path

        raise FileNotFoundError(
            f"Stripes directory not found at {default_path}. "
            "Please specify with --stripes-dir"
        )

    def _find_collection_nml(self) -> Optional[Path]:
        """Find Traktor collection.nml file."""
        default_path = Path.home() / "Documents" / "Native Instruments" / "Traktor 3.11.1" / "collection.nml"

        if default_path.exists():
            return default_path

        return None

    def find_audio_files(self) -> List[Path]:
        """Find all audio files in the music directory."""
        audio_extensions = {'.mp3', '.m4a', '.flac', '.wav', '.aiff', '.aif'}
        audio_files = []

        for ext in audio_extensions:
            audio_files.extend(self.music_dir.glob(f"*{ext}"))

        return sorted(audio_files)

    def find_stripes_file(self, audio_file: Path) -> Optional[Path]:
        """
        Find the corresponding stripes file for an audio file.

        Strategy:
        1. Try to find via collection.nml lookup (TODO)
        2. Search all stripes subdirectories for matching duration
        3. Use filename heuristics

        Args:
            audio_file: Path to audio file

        Returns:
            Path to stripes file, or None if not found
        """
        # TODO: Implement collection.nml lookup
        # For now, we'll return None and let the user know this feature is coming

        return None

    def process_track(self, audio_file: Path, stripes_file: Optional[Path] = None) -> Dict:
        """
        Process a single track with hybrid analysis.

        Args:
            audio_file: Path to audio file
            stripes_file: Path to stripes file (optional)

        Returns:
            Analysis results dictionary
        """
        print(f"\n{'=' * 80}")
        print(f"Processing: {audio_file.name}")
        print(f"{'=' * 80}")

        if not stripes_file:
            print("⚠️  No stripes file found - using Librosa-only analysis")
            # TODO: Fall back to Librosa-only analysis
            return {
                'file': str(audio_file),
                'status': 'skipped',
                'reason': 'No stripes file found',
            }

        try:
            # Run hybrid analysis
            analyzer = HybridAnalyzer(str(audio_file), str(stripes_file))
            results = analyzer.analyze()

            # Save individual track analysis
            output_file = self.output_dir / f"{audio_file.stem}_analysis.json"
            analyzer.save_to_file(str(output_file))

            # Add metadata
            results['status'] = 'success'
            results['audio_file'] = str(audio_file)
            results['stripes_file'] = str(stripes_file)
            results['output_file'] = str(output_file)
            results['processed_at'] = datetime.now().isoformat()

            self.successful += 1
            return results

        except Exception as e:
            error_msg = f"Error processing {audio_file.name}: {str(e)}"
            print(f"❌ {error_msg}")
            traceback.print_exc()

            self.failed += 1
            self.errors.append({
                'file': str(audio_file),
                'error': str(e),
                'traceback': traceback.format_exc()
            })

            return {
                'file': str(audio_file),
                'status': 'error',
                'error': str(e),
            }

    def process_all(self, manual_stripes_mapping: Optional[Dict[str, str]] = None):
        """
        Process all tracks in the music directory.

        Args:
            manual_stripes_mapping: Optional dict mapping audio filenames to stripes file paths
        """
        print(f"\n{'=' * 80}")
        print(f"BATCH PROCESSING: Hybrid Analysis")
        print(f"{'=' * 80}")
        print(f"Music directory: {self.music_dir}")
        print(f"Stripes directory: {self.stripes_dir}")
        print(f"Output directory: {self.output_dir}")
        print(f"{'=' * 80}\n")

        # Create output directory
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Find all audio files
        audio_files = self.find_audio_files()
        print(f"Found {len(audio_files)} audio files\n")

        if len(audio_files) == 0:
            print("No audio files found. Exiting.")
            return

        # Process each file
        for i, audio_file in enumerate(audio_files, 1):
            print(f"\n[{i}/{len(audio_files)}]")

            # Find stripes file
            stripes_file = None
            if manual_stripes_mapping and audio_file.name in manual_stripes_mapping:
                stripes_file = Path(manual_stripes_mapping[audio_file.name])
            else:
                stripes_file = self.find_stripes_file(audio_file)

            # Process track
            result = self.process_track(audio_file, stripes_file)
            self.results.append(result)

            if result['status'] == 'skipped':
                self.skipped += 1

        # Generate summary
        self.generate_summary()

    def generate_summary(self):
        """Generate and save batch processing summary."""
        summary = {
            'batch_info': {
                'music_directory': str(self.music_dir),
                'stripes_directory': str(self.stripes_dir),
                'output_directory': str(self.output_dir),
                'processed_at': datetime.now().isoformat(),
            },
            'statistics': {
                'total_files': len(self.results),
                'successful': self.successful,
                'failed': self.failed,
                'skipped': self.skipped,
                'success_rate': f"{(self.successful / len(self.results) * 100):.1f}%" if self.results else "0%",
            },
            'results': self.results,
            'errors': self.errors,
        }

        # Save summary
        summary_file = self.output_dir / "batch_summary.json"
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)

        # Print summary
        print(f"\n{'=' * 80}")
        print("BATCH PROCESSING COMPLETE")
        print(f"{'=' * 80}")
        print(f"Total files: {len(self.results)}")
        print(f"✅ Successful: {self.successful}")
        print(f"❌ Failed: {self.failed}")
        print(f"⏭️  Skipped: {self.skipped}")
        print(f"Success rate: {summary['statistics']['success_rate']}")
        print(f"\nSummary saved to: {summary_file}")
        print(f"{'=' * 80}\n")

        # Print errors if any
        if self.errors:
            print("\nErrors encountered:")
            for error in self.errors:
                print(f"  ❌ {Path(error['file']).name}: {error['error']}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Batch process audio files with hybrid Stripes + Librosa analysis"
    )
    parser.add_argument(
        "music_dir",
        help="Directory containing audio files to process"
    )
    parser.add_argument(
        "--stripes-dir",
        help="Traktor stripes directory (auto-detected if not specified)",
        default=None
    )
    parser.add_argument(
        "--output-dir",
        help="Output directory for analysis results (defaults to music_dir/analysis)",
        default=None
    )
    parser.add_argument(
        "--collection-nml",
        help="Path to Traktor collection.nml for track mapping",
        default=None
    )

    args = parser.parse_args()

    # Validate music directory
    music_dir = Path(args.music_dir)
    if not music_dir.exists():
        print(f"Error: Music directory not found: {music_dir}")
        return 1

    if not music_dir.is_dir():
        print(f"Error: Not a directory: {music_dir}")
        return 1

    try:
        # Create batch processor
        processor = BatchProcessor(
            music_dir=args.music_dir,
            stripes_dir=args.stripes_dir,
            output_dir=args.output_dir,
            collection_nml=args.collection_nml
        )

        # NOTE: For now, without NML integration, we need manual mapping
        print("\n⚠️  NOTE: NML integration not yet implemented")
        print("Without track-to-stripes mapping, analysis will be skipped")
        print("Coming soon: Automatic stripes file lookup via collection.nml\n")

        # Process all tracks
        processor.process_all()

        return 0

    except Exception as e:
        print(f"Error: {e}")
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
