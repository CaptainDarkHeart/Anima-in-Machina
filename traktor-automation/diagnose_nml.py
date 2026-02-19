#!/usr/bin/env python3
"""
NML Diagnostic Tool
====================
Prints the raw XML of a track entry from collection.nml.

Usage:
    python3 traktor-automation/diagnose_nml.py "Prof. Fee 2009 (Dub Taylor D. Mark Remix).m4a"
"""

import xml.etree.ElementTree as ET
import xml.dom.minidom
import sys
from pathlib import Path

NML_PATH = Path.home() / "Documents/Native Instruments/Traktor 3.11.1/collection.nml"


def modified_sort_key(e):
    date = e.get('MODIFIED_DATE', '0000/0/0').replace('/', '')
    time = e.get('MODIFIED_TIME', '0').zfill(10)
    return (date, time)


def main():
    filename = sys.argv[1] if len(sys.argv) > 1 else "Prof. Fee 2009 (Dub Taylor D. Mark Remix).m4a"

    print(f"NML  : {NML_PATH}")
    print(f"Track: {filename}\n")

    tree = ET.parse(str(NML_PATH))
    root = tree.getroot()
    collection = root.find('.//COLLECTION')

    candidates = []
    for entry in collection.findall('ENTRY'):
        loc = entry.find('LOCATION')
        if loc is not None and loc.get('FILE') == filename:
            candidates.append(entry)

    print(f"Entries found: {len(candidates)}")

    for i, entry in enumerate(candidates):
        cues = entry.findall('CUE_V2')
        has_grid = any(c.get('TYPE') == '4' for c in cues)
        print(f"\n{'='*70}")
        print(f"ENTRY {i+1}  modified={entry.get('MODIFIED_DATE')} {entry.get('MODIFIED_TIME')}  "
              f"has_autogrid={has_grid}")
        print(f"DIR: {entry.find('LOCATION').get('DIR')}")
        print(f"{'='*70}")

        tempo = entry.find('TEMPO')
        info  = entry.find('INFO')
        if tempo is not None:
            print(f"BPM      : {tempo.get('BPM')}")
        if info is not None:
            print(f"Duration : {info.get('PLAYTIME_FLOAT')}s")

        print(f"\nCUE_V2 elements ({len(cues)} total):")
        print(f"  {'HOTCUE':>6}  {'TYPE':>4}  {'DISPL_ORDER':>11}  {'START':>14}  {'LEN':>12}  NAME")
        print(f"  {'-'*6}  {'-'*4}  {'-'*11}  {'-'*14}  {'-'*12}  ----")
        for c in sorted(cues, key=lambda x: float(x.get('START', 0))):
            print(f"  {c.get('HOTCUE','?'):>6}  {c.get('TYPE','?'):>4}  "
                  f"{c.get('DISPL_ORDER','?'):>11}  "
                  f"{float(c.get('START','0'))/1000:>13.3f}s  "
                  f"{float(c.get('LEN','0'))/1000:>11.3f}s  "
                  f"{c.get('NAME','')}")

    # Show which entry the writer would pick
    gridded = [e for e in candidates
               if any(c.get('TYPE') == '4' for c in e.findall('CUE_V2'))]
    pool = gridded if gridded else candidates
    best = sorted(pool, key=modified_sort_key, reverse=True)[0] if pool else None
    if best is not None:
        idx = candidates.index(best) + 1
        print(f"\n→ Writer would select Entry {idx} (most recent gridded entry)")


if __name__ == '__main__':
    main()
