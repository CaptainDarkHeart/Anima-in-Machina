#!/usr/bin/env python3
"""
Batch Process "Best of Deep Dub Tech House" Collection
======================================================

Automatically processes all 30 tracks in the collection by:
1. Finding all audio files in the music directory
2. Finding corresponding stripes files by matching hashes
3. Running hybrid analysis on each track
4. Generating summary report

Usage:
    python batch_process_best_of.py
"""

import sys
from pathlib import Path
from typing import Dict, List, Optional
import json
from datetime import datetime
import traceback

# Import hybrid analyzer
sys.path.insert(0, str(Path(__file__).parent))
from hybrid_analyzer import HybridAnalyzer


class BestOfProcessor:
    """Process the Best of Deep Dub Tech House collection."""

    def __init__(self):
        """Initialize processor with default paths."""
        self.music_dir = Path("/Volumes/TRAKTOR/Traktor/Music/2026/Best of Deep Dub Tech House")
        self.stripes_dir = Path.home() / "Documents" / "Native Instruments" / "Traktor 3.11.1" / "Stripes"
        self.transients_dir = Path.home() / "Documents" / "Native Instruments" / "Traktor 3.11.1" / "Transients"
        self.output_dir = self.music_dir / "analysis"

        # Results tracking
        self.results = []
        self.errors = []
        self.successful = 0
        self.failed = 0
        self.skipped = 0

    def find_audio_files(self) -> List[Path]:
        """Find all audio files in the music directory."""
        audio_extensions = {'.mp3', '.m4a', '.flac', '.wav', '.aiff', '.aif'}
        audio_files = []

        for ext in audio_extensions:
            audio_files.extend(self.music_dir.glob(f"*{ext}"))

        return sorted(audio_files)

    def find_stripes_files(self) -> Dict[str, Path]:
        """
        Find all stripes files and index them by hash.

        Returns:
            Dictionary mapping hash -> stripes_file_path
        """
        stripes_index = {}

        # Search all subdirectories
        for subdir in self.stripes_dir.iterdir():
            if not subdir.is_dir():
                continue

            for stripes_file in subdir.iterdir():
                if stripes_file.name.startswith('.'):
                    continue

                # Hash is the filename
                hash_id = stripes_file.name
                stripes_index[hash_id] = stripes_file

        return stripes_index

    def get_recently_analyzed_hashes(self, minutes: int = 120) -> List[str]:
        """
        Get hashes of recently analyzed tracks by checking Transients directory.

        Since Transients files are updated when tracks are analyzed,
        we can use them to find which tracks were just analyzed.

        Args:
            minutes: How many minutes back to look

        Returns:
            List of hash IDs for recently analyzed tracks
        """
        import time
        cutoff_time = time.time() - (minutes * 60)
        hashes = []

        for subdir in self.transients_dir.iterdir():
            if not subdir.is_dir():
                continue

            for transients_file in subdir.iterdir():
                if transients_file.name.startswith('.'):
                    continue

                # Check if modified recently
                if transients_file.stat().st_mtime > cutoff_time:
                    hashes.append(transients_file.name)

        return hashes

    def find_stripes_for_audio(self, audio_file: Path, stripes_index: Dict[str, Path], recent_hashes: List[str]) -> Optional[Path]:
        """
        Find the stripes file for an audio file.

        Strategy: Use recently analyzed hashes from Transients directory.
        The same hash is used for both Stripes and Transients files.
        """
        # For each recently analyzed hash, check if it has a corresponding stripes file
        for hash_id in recent_hashes:
            if hash_id in stripes_index:
                # This is a candidate - we'll return the first one we find
                # TODO: Better matching by duration or other metadata
                recent_hashes.remove(hash_id)  # Remove so we don't reuse
                return stripes_index[hash_id]

        return None

    def process_track(self, audio_file: Path, stripes_file: Path) -> Dict:
        """Process a single track with hybrid analysis."""
        try:
            print(f"\n{'=' * 80}")
            print(f"Processing: {audio_file.name}")
            print(f"Stripes: {stripes_file.parent.name}/{stripes_file.name}")
            print(f"{'=' * 80}")

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

    def process_all(self):
        """Process all tracks in the collection."""
        print(f"\n{'=' * 80}")
        print("BATCH PROCESSING: Best of Deep Dub Tech House")
        print(f"{'=' * 80}")
        print(f"Music directory: {self.music_dir}")
        print(f"Stripes directory: {self.stripes_dir}")
        print(f"Output directory: {self.output_dir}")
        print(f"{'=' * 80}\n")

        # Create output directory
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Find all audio files
        audio_files = self.find_audio_files()
        print(f"Found {len(audio_files)} audio files")

        # Index all stripes files
        print("Indexing stripes files...")
        stripes_index = self.find_stripes_files()
        print(f"Found {len(stripes_index)} stripes files")

        # Get recently analyzed hashes
        print("Finding recently analyzed tracks...")
        recent_hashes = self.get_recently_analyzed_hashes(minutes=120)
        print(f"Found {len(recent_hashes)} recently analyzed tracks")

        if len(audio_files) == 0:
            print("No audio files found. Exiting.")
            return

        # Process each file
        for i, audio_file in enumerate(audio_files, 1):
            print(f"\n[{i}/{len(audio_files)}]")

            # Find stripes file
            stripes_file = self.find_stripes_for_audio(audio_file, stripes_index, recent_hashes)

            if not stripes_file:
                print(f"⏭️  Skipping {audio_file.name} - no stripes file found")
                self.skipped += 1
                self.results.append({
                    'file': str(audio_file),
                    'status': 'skipped',
                    'reason': 'No stripes file found',
                })
                continue

            # Process track
            result = self.process_track(audio_file, stripes_file)
            self.results.append(result)

        # Generate summary
        self.generate_summary()

    def generate_summary(self):
        """Generate and save batch processing summary."""
        summary = {
            'batch_info': {
                'collection': 'Best of Deep Dub Tech House',
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

        # Print successful tracks
        if self.successful > 0:
            print(f"\n✅ Successfully processed {self.successful} tracks:")
            for result in self.results:
                if result.get('status') == 'success':
                    cue_count = len(result.get('cue_points', []))
                    print(f"  • {Path(result['file']).name} - {cue_count} cue points")


def main():
    """Main entry point."""
    try:
        processor = BestOfProcessor()
        processor.process_all()
        return 0

    except Exception as e:
        print(f"Error: {e}")
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
