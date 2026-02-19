#!/usr/bin/env python3
"""
Strip old auto-generated cues from NML entries.

Removes CUE_V2 elements where HOTCUE="0" and TYPE="0" from entries
in a specified directory path. These are the stripes-generated cues
(Load, Drop 1, Build 1 etc.) that clutter the waveform display.

Preserves:
  - TYPE=4 HOTCUE=0  (AutoGrid — beatgrid anchor)
  - TYPE=5 HOTCUE=1  (Floating cue — never touched)
  - Any HOTCUE > 0   (User hotcues)

Usage:
    # Dry run — see what would be removed
    python3 traktor-automation/strip_old_cues.py --dry-run

    # Run for real
    python3 traktor-automation/strip_old_cues.py

    # Target a specific directory substring
    python3 traktor-automation/strip_old_cues.py --dir "Album – Best of Deep Dub Tech House"
"""

import xml.etree.ElementTree as ET
import shutil
import argparse
import sys
from pathlib import Path
from datetime import datetime

NML_DEFAULT = Path.home() / "Documents/Native Instruments/Traktor 3.11.1/collection.nml"
DEFAULT_DIR = "Album – Best of Deep Dub Tech House"


def is_stripes_cue(cue: ET.Element) -> bool:
    """
    Return True if this cue is a stripes-generated non-hotcue regular cue.
    These have HOTCUE=0 and TYPE=0 — plain cue points with no slot assignment.
    AutoGrid (TYPE=4 HOTCUE=0) is explicitly excluded.
    """
    hotcue = cue.get('HOTCUE', '0')
    ctype  = cue.get('TYPE', '0')
    return hotcue == '0' and ctype == '0'


def main():
    parser = argparse.ArgumentParser(
        description='Strip old auto-generated cues from Traktor NML entries',
    )
    parser.add_argument('--nml', metavar='PATH', default=str(NML_DEFAULT),
                        help=f'Path to collection.nml (default: {NML_DEFAULT})')
    parser.add_argument('--dir', metavar='SUBSTR', default=DEFAULT_DIR,
                        help=f'Directory substring to target (default: "{DEFAULT_DIR}")')
    parser.add_argument('--dry-run', action='store_true',
                        help='Preview without writing')
    args = parser.parse_args()

    nml_path = Path(args.nml)
    if not nml_path.exists():
        print(f"❌ NML not found: {nml_path}")
        sys.exit(1)

    tree = ET.parse(str(nml_path))
    root = tree.getroot()
    collection = root.find('.//COLLECTION')

    print(f"\n{'═'*60}")
    print(f"  Strip Old Cues")
    print(f"  NML: {nml_path}")
    print(f"  Target dir: {args.dir!r}")
    print(f"  Mode: {'DRY RUN' if args.dry_run else 'LIVE'}")
    print(f"{'═'*60}\n")

    total_entries  = 0
    total_stripped = 0

    for entry in collection.findall('ENTRY'):
        loc = entry.find('LOCATION')
        if loc is None:
            continue
        entry_dir = loc.get('DIR', '')
        if args.dir not in entry_dir:
            continue

        filename = loc.get('FILE', 'unknown')
        stripes_cues = [c for c in entry.findall('CUE_V2') if is_stripes_cue(c)]

        if not stripes_cues:
            continue

        total_entries  += 1
        total_stripped += len(stripes_cues)

        names = [c.get('NAME', '?') for c in stripes_cues]
        action = '[DRY RUN] Would remove' if args.dry_run else 'Removed'
        print(f"  {filename}")
        print(f"    {action} {len(stripes_cues)} cues: {', '.join(names)}")

        if not args.dry_run:
            for cue in stripes_cues:
                entry.remove(cue)

    print(f"\n{'─'*60}")
    print(f"  Entries affected : {total_entries}")
    print(f"  Cues {'to remove' if args.dry_run else 'removed'}   : {total_stripped}")
    print(f"{'─'*60}")

    if total_stripped == 0:
        print("\nNothing to do.")
        return

    if args.dry_run:
        print("\n(Dry run — nothing written)")
        return

    # Backup and save
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = nml_path.parent / f"collection_backup_{ts}.nml"
    shutil.copy2(nml_path, backup)
    print(f"\n💾 Backup: {backup}")

    tree.write(str(nml_path), encoding='UTF-8', xml_declaration=True)
    print(f"✅ Saved: {nml_path}")
    print("\n⚠️  Restart Traktor to load the updated collection.")


if __name__ == '__main__':
    main()
