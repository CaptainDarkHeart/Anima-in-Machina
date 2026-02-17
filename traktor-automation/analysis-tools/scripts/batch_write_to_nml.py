#!/usr/bin/env python3
"""
Batch Write Cue Points to Traktor NML
=====================================

Writes all intelligent cue points from analysis files to Traktor's collection.nml.

Usage:
    python batch_write_to_nml.py <analysis_directory>

Example:
    python batch_write_to_nml.py "/Volumes/TRAKTOR/.../analysis"
"""

import sys
from pathlib import Path
from nml_writer import NMLWriter


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python batch_write_to_nml.py <analysis_directory>")
        print("\nExample:")
        print('  python batch_write_to_nml.py "/Volumes/TRAKTOR/.../analysis"')
        return 1

    analysis_dir = Path(sys.argv[1])

    if not analysis_dir.exists():
        print(f"Error: Analysis directory not found: {analysis_dir}")
        return 1

    # Find all analysis JSON files (exclude batch_summary.json)
    analysis_files = [
        f for f in analysis_dir.glob("*_analysis.json")
        if f.name != "batch_summary.json"
    ]

    if not analysis_files:
        print(f"No analysis files found in {analysis_dir}")
        return 1

    print(f"={'=' * 60}")
    print(f"BATCH WRITE TO TRAKTOR NML")
    print(f"={'=' * 60}")
    print(f"Analysis directory: {analysis_dir}")
    print(f"Found {len(analysis_files)} analysis files")
    print(f"={'=' * 60}\n")

    # Create NML writer
    writer = NMLWriter()
    writer.load()

    # Process all files
    # IMPORTANT: replace_existing=False to preserve user's manual cue points!
    successful, failed = writer.batch_add_cue_points(
        analysis_files,
        replace_existing=False  # DO NOT DELETE existing cue points!
    )

    # Save
    if successful > 0:
        writer.save()
        print(f"\n🎉 Success! {successful} tracks updated in Traktor")
    else:
        print("\n❌ No tracks were updated")
        return 1

    if failed > 0:
        print(f"⚠️  {failed} tracks failed")

    return 0


if __name__ == '__main__':
    sys.exit(main())
