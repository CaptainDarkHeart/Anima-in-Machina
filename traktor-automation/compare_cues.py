#!/usr/bin/env python3
"""Compare cue points across two NML entries for the same track."""
import xml.etree.ElementTree as ET
from pathlib import Path

NML_PATH = Path.home() / "Documents/Native Instruments/Traktor 3.11.1/collection.nml"
FILENAME = "Amazonas Santiago (Riccicomoto Para Dub).m4a"
DIRS = ["/:Traktor/:Music/:2026/:Best of Deep Dub Tech House/:", "Testing"]

tree = ET.parse(str(NML_PATH))
collection = tree.getroot().find('.//COLLECTION')

for target_dir in DIRS:
    for entry in collection.findall('ENTRY'):
        loc = entry.find('LOCATION')
        if loc is None: continue
        if loc.get('FILE') != FILENAME: continue
        if target_dir not in loc.get('DIR', ''): continue

        tempo = entry.find('TEMPO')
        info  = entry.find('INFO')
        bpm   = float(tempo.get('BPM', 0)) if tempo is not None else 0
        dur   = float(info.get('PLAYTIME_FLOAT', 0)) if info is not None else 0
        cues  = entry.findall('CUE_V2')

        print(f"\n{'='*65}")
        print(f"DIR : {loc.get('DIR')}")
        print(f"BPM : {bpm:.2f}   Duration: {dur:.1f}s")
        print(f"{'='*65}")
        print(f"  {'HOTCUE':>6}  {'TYPE':>4}  {'START':>10}  {'LEN':>10}  NAME")
        print(f"  {'-'*6}  {'-'*4}  {'-'*10}  {'-'*10}  ----")
        for c in sorted(cues, key=lambda x: float(x.get('HOTCUE','0'))):
            start_s = float(c.get('START', 0)) / 1000
            len_s   = float(c.get('LEN', 0)) / 1000
            pct     = start_s / dur * 100 if dur else 0
            print(f"  {c.get('HOTCUE','?'):>6}  {c.get('TYPE','?'):>4}  "
                  f"{start_s:>8.2f}s  {len_s:>8.2f}s  "
                  f"{c.get('NAME',''):<20}  ({pct:.0f}% through)")
        break
