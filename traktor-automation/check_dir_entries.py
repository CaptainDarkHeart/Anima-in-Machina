#!/usr/bin/env python3
"""
Quick check: show all NML entries for a given directory substring.
Usage:
    python3 traktor-automation/check_dir_entries.py "Testing"
"""
import xml.etree.ElementTree as ET
import sys
from pathlib import Path

NML_PATH = Path.home() / "Documents/Native Instruments/Traktor 3.11.1/collection.nml"
target = sys.argv[1] if len(sys.argv) > 1 else "Testing"

tree = ET.parse(str(NML_PATH))
root = tree.getroot()
collection = root.find('.//COLLECTION')

matches = []
for entry in collection.findall('ENTRY'):
    loc = entry.find('LOCATION')
    if loc is not None and target in loc.get('DIR', ''):
        matches.append(entry)

print(f"Found {len(matches)} entries matching '{target}'\n")
for entry in matches:
    loc   = entry.find('LOCATION')
    tempo = entry.find('TEMPO')
    cues  = entry.findall('CUE_V2')
    has_grid = any(c.get('TYPE') == '4' for c in cues)
    bpm = tempo.get('BPM', 'n/a') if tempo is not None else 'n/a'
    print(f"  {'✅' if has_grid else '❌'}  {loc.get('FILE','?'):55s}  "
          f"BPM={float(bpm):.1f}  cues={len(cues)}  grid={'yes' if has_grid else 'NO'}")
