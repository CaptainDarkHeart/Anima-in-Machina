#!/usr/bin/env python3
"""
Deep House Cue Point Writer
============================

Writes four specific cue points to Traktor's collection.nml using the
beatgrid data that Traktor has already computed for each track.

NO audio analysis required. NO stripes parsing. NO librosa.
Uses only the BPM and beatgrid anchor already stored in the NML.

Cue layout (hotcue slots 2-5, slot 1 is NEVER touched):
  Slot 2 — "Beat"      : Where the kick comes in (bar-boundary estimated)
  Slot 3 — "Groove"    : 32-bar loop in the sustained groove section
  Slot 4 — "Breakdown" : Where the breakdown begins (estimated)
  Slot 5 — "End"       : Mix-out marker, 32 bars from the end

Safety rules enforced:
  - HOTCUE 1 (TYPE=5, floating cue/saved loop) is NEVER touched
  - Script ONLY writes to hotcue slots 2, 3, 4, 5
  - If a slot already has a user cue, it is skipped unless --overwrite
  - Automatic backup created before any write
  - Dry-run mode available to preview without writing

NML format (confirmed from collection inspection):
  TEMPO BPM="124.999954"                        <- BPM source
  CUE_V2 NAME="AutoGrid" TYPE="4" HOTCUE="0"   <- beatgrid anchor (read only)
  CUE_V2 NAME="n.n."     TYPE="5" HOTCUE="1"   <- floating cue (NEVER touch)
  INFO PLAYTIME_FLOAT="459.105011"              <- duration in seconds

Usage:
    # Dry run — see what would be written, no changes made
    python3 traktor-automation/deep_house_cue_writer.py \\
        --playlist track-selection-engine/best-of-deep-dub-tech-house.json \\
        --dry-run

    # Process a single track
    python3 traktor-automation/deep_house_cue_writer.py \\
        --track "Nadja Lind - Spherical.m4a"

    # Process all tracks in a playlist JSON
    python3 traktor-automation/deep_house_cue_writer.py \\
        --playlist track-selection-engine/best-of-deep-dub-tech-house.json

    # Overwrite existing hotcues in slots 2-5 (slot 1 always protected)
    python3 traktor-automation/deep_house_cue_writer.py \\
        --playlist track-selection-engine/best-of-deep-dub-tech-house.json \\
        --overwrite
"""

import xml.etree.ElementTree as ET
import json
import shutil
import argparse
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional


# ─────────────────────────────────────────────────────────────────────────────
# CONSTANTS
# ─────────────────────────────────────────────────────────────────────────────

NML_DEFAULT = Path.home() / "Documents/Native Instruments/Traktor 3.11.1/collection.nml"

# Hotcue slots matching Dan's layout. Slot 1 is NEVER touched.
# Slot 1 = track start (Traktor places this, we never overwrite)
# Slot 2 = kick drum entry
# Slot 3 = breakdown
# Slot 4 = 32-beat loop (groove pocket)
# Slot 5 = 32 beats from end (mix-out marker)
SLOT_BEAT      = 2
SLOT_BREAKDOWN = 3
SLOT_GROOVE    = 4
SLOT_END       = 5

# Traktor CUE_V2 TYPE values (confirmed from NML inspection)
TYPE_CUE  = 0   # Regular cue point
TYPE_LOOP = 4   # Loop
# TYPE=4 HOTCUE=0  => AutoGrid beatgrid anchor  — read only, never written
# TYPE=5 HOTCUE=1  => Floating cue / saved loop — NEVER touched under any circumstances

# Loop length in bars for the Groove cue
GROOVE_LOOP_BARS = 32

# Flag short tracks where 32 bars exceeds this fraction of total duration
SHORT_TRACK_LOOP_RATIO = 0.40

# Fraction of track duration where each cue is estimated to fall
GROOVE_FRACTION    = 0.35   # ~35% in = sustained groove pocket
BREAKDOWN_FRACTION = 0.65   # ~65% in = breakdown zone


# ─────────────────────────────────────────────────────────────────────────────
# NML HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def load_nml(nml_path: Path) -> tuple:
    """Parse collection.nml and return (tree, root)."""
    if not nml_path.exists():
        raise FileNotFoundError(f"collection.nml not found: {nml_path}")
    tree = ET.parse(str(nml_path))
    return tree, tree.getroot()


def backup_nml(nml_path: Path) -> Path:
    """Create a timestamped backup before any write."""
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = nml_path.parent / f"collection_backup_{ts}.nml"
    shutil.copy2(nml_path, backup_path)
    return backup_path


def find_track_entry(root: ET.Element, filename: str,
                     dir_filter: Optional[str] = None) -> Optional[ET.Element]:
    """
    Find the best ENTRY for a given filename.

    Traktor creates duplicate entries when a file appears in multiple
    folders/playlists. We want the entry that Traktor has fully analysed —
    i.e. the one containing an AutoGrid cue (TYPE=4). If multiple gridded
    entries exist we pick the most recently modified. Falls back to most
    recently modified ungridded entry if no grid is found anywhere.
    """
    collection = root.find('.//COLLECTION')
    if collection is None:
        return None

    candidates = []
    for entry in collection.findall('ENTRY'):
        loc = entry.find('LOCATION')
        if loc is None:
            continue
        if loc.get('FILE') != filename:
            continue
        if dir_filter and dir_filter not in loc.get('DIR', ''):
            continue
        candidates.append(entry)

    if not candidates:
        return None
    if len(candidates) == 1:
        return candidates[0]

    def modified_sort_key(e):
        date = e.get('MODIFIED_DATE', '0000/0/0').replace('/', '')
        time = e.get('MODIFIED_TIME', '0').zfill(10)
        return (date, time)

    # Prefer entries that have an AutoGrid cue (TYPE=4)
    gridded = [e for e in candidates
               if any(c.get('TYPE') == '4' for c in e.findall('CUE_V2'))]

    pool = gridded if gridded else candidates
    return sorted(pool, key=modified_sort_key, reverse=True)[0]


def get_beatgrid_info(entry: ET.Element) -> tuple:
    """
    Return (bpm, anchor_ms) from a track ENTRY.

    BPM  comes from the TEMPO element.
    Anchor comes from the first CUE_V2 with TYPE=4 (the AutoGrid marker).
    Returns (None, None) if either is missing.
    """
    bpm = None
    anchor_ms = None

    tempo_el = entry.find('TEMPO')
    if tempo_el is not None:
        try:
            bpm = float(tempo_el.get('BPM', 0))
            if bpm <= 0:
                bpm = None
        except (ValueError, TypeError):
            pass

    for cue in entry.findall('CUE_V2'):
        if cue.get('TYPE') == '4':
            try:
                anchor_ms = float(cue.get('START', 0))
            except (ValueError, TypeError):
                pass
            break

    return bpm, anchor_ms


def get_duration_ms(entry: ET.Element) -> Optional[float]:
    """Return track duration in milliseconds from INFO element."""
    info = entry.find('INFO')
    if info is not None:
        for attr in ('PLAYTIME_FLOAT', 'PLAYTIME'):
            val = info.get(attr)
            if val:
                try:
                    return float(val) * 1000.0
                except (ValueError, TypeError):
                    pass
    return None


def occupied_hotcue_slots(entry: ET.Element) -> set:
    """
    Return the set of hotcue slot numbers already in use.
    Slot 1 is always included — it belongs to the floating cue and is
    off-limits regardless of what the NML actually contains.
    """
    slots = {1}  # slot 1 always protected
    for cue in entry.findall('CUE_V2'):
        try:
            slot = int(cue.get('HOTCUE', '0'))
            if slot > 0:
                slots.add(slot)
        except ValueError:
            pass
    return slots


# ─────────────────────────────────────────────────────────────────────────────
# CUE POINT ARITHMETIC
# ─────────────────────────────────────────────────────────────────────────────

def bars_to_ms(bars: float, bpm: float) -> float:
    """Convert bars (4/4) to milliseconds."""
    return bars * 4 * (60_000.0 / bpm)


def snap_to_bar(ms: float, bpm: float, anchor_ms: float) -> float:
    """Snap a millisecond position to the nearest bar boundary."""
    bar_ms = bars_to_ms(1, bpm)
    offset = ms - anchor_ms
    nearest_bar = round(offset / bar_ms)
    return anchor_ms + nearest_bar * bar_ms


def calculate_positions(bpm: float, anchor_ms: float, duration_ms: float) -> dict:
    """
    Calculate the four cue positions using bar-boundary arithmetic.

    BEAT      — bar boundary nearest to 10% of track duration.
                Deep house intros are typically 8–32 bars; 10% lands
                reliably in the early groove zone. Flag for review.

    GROOVE    — 32-bar loop starting at ~35% of track duration.
                This reliably lands in the sustained groove pocket for
                typical 6–10 minute deep house arrangements.

    BREAKDOWN — bar boundary nearest to 65% of track duration.
                Deep house breakdowns typically fall 60–70% in.
                Flag for review.

    END       — bar boundary 32 bars before end of track.
                Gives a full 32-bar mix-out runway.
    """
    flags = []
    bar_ms   = bars_to_ms(1, bpm)
    loop_ms  = bars_to_ms(GROOVE_LOOP_BARS, bpm)

    # BEAT
    beat_ms = snap_to_bar(duration_ms * 0.10, bpm, anchor_ms)
    if beat_ms < anchor_ms:
        beat_ms = snap_to_bar(anchor_ms + bar_ms, bpm, anchor_ms)
    flags.append("BEAT: estimated at ~10% of track — verify kick entry in Traktor")

    # GROOVE (32-bar loop)
    groove_ms = snap_to_bar(duration_ms * GROOVE_FRACTION, bpm, anchor_ms)
    end_zone  = duration_ms - loop_ms - bar_ms
    if groove_ms + loop_ms > end_zone:
        groove_ms = snap_to_bar(end_zone - loop_ms, bpm, anchor_ms)
        flags.append("GROOVE: loop shifted earlier to avoid overlap with end zone")
    if loop_ms > duration_ms * SHORT_TRACK_LOOP_RATIO:
        flags.append(
            f"SHORT TRACK: 32-bar loop ({loop_ms/1000:.0f}s) is "
            f"{loop_ms/duration_ms*100:.0f}% of total duration — "
            "consider a shorter loop"
        )

    # BREAKDOWN
    breakdown_ms = snap_to_bar(duration_ms * BREAKDOWN_FRACTION, bpm, anchor_ms)
    flags.append("BREAKDOWN: estimated at ~65% of track — verify in Traktor")

    # END (mix-out marker)
    end_ms = snap_to_bar(duration_ms - loop_ms, bpm, anchor_ms)
    if end_ms <= breakdown_ms + bar_ms:
        end_ms = snap_to_bar(breakdown_ms + bars_to_ms(8, bpm), bpm, anchor_ms)
        flags.append("END: pushed forward — very short outro detected")

    return {
        'beat_ms':       beat_ms,
        'groove_ms':     groove_ms,
        'groove_len_ms': loop_ms,
        'breakdown_ms':  breakdown_ms,
        'end_ms':        end_ms,
        'flags':         flags,
        'bpm':           bpm,
        'duration_ms':   duration_ms,
        'anchor_ms':     anchor_ms,
    }


# ─────────────────────────────────────────────────────────────────────────────
# NML WRITING
# ─────────────────────────────────────────────────────────────────────────────

def make_cue_element(name: str, start_ms: float, hotcue: int,
                     displ_order: int, cue_type: int = TYPE_CUE,
                     len_ms: float = 0.0) -> ET.Element:
    el = ET.Element('CUE_V2')
    el.set('NAME',        name)
    el.set('DISPL_ORDER', str(displ_order))
    el.set('TYPE',        str(cue_type))
    el.set('START',       f"{start_ms:.6f}")
    el.set('LEN',         f"{len_ms:.6f}")
    el.set('REPEATS',     '-1')
    el.set('HOTCUE',      str(hotcue))
    return el


def remove_slot(entry: ET.Element, slot: int):
    """Remove a hotcue from an entry. Slot 1 is hardcoded immovable."""
    if slot == 1:
        return
    for cue in list(entry.findall('CUE_V2')):
        if cue.get('HOTCUE') == str(slot):
            entry.remove(cue)


def write_cues(entry: ET.Element, pos: dict, overwrite: bool = False) -> dict:
    """
    Write the four cue points into an ENTRY element.
    Returns {'written': [...], 'skipped': [...]}.
    """
    occupied = occupied_hotcue_slots(entry)
    written  = []
    skipped  = []

    cues = [
        (SLOT_BEAT,      'Beat',      pos['beat_ms'],      TYPE_CUE,  0.0),
        (SLOT_BREAKDOWN, 'Breakdown', pos['breakdown_ms'], TYPE_CUE,  0.0),
        (SLOT_GROOVE,    'Groove',    pos['groove_ms'],    TYPE_LOOP, pos['groove_len_ms']),
        (SLOT_END,       'End',       pos['end_ms'],       TYPE_CUE,  0.0),
    ]

    for slot, name, start_ms, cue_type, len_ms in cues:
        if slot in occupied and not overwrite:
            skipped.append(f"Slot {slot} ({name}) already occupied — skipped (use --overwrite)")
            continue
        if slot in occupied:
            remove_slot(entry, slot)

        entry.append(make_cue_element(
            name=name, start_ms=start_ms, hotcue=slot,
            displ_order=slot - 1, cue_type=cue_type, len_ms=len_ms,
        ))
        loop_note = f"  [loop {len_ms/1000:.1f}s]" if len_ms > 0 else ""
        written.append(f"Slot {slot} ({name}): {start_ms/1000:.2f}s{loop_note}")

    return {'written': written, 'skipped': skipped}


# ─────────────────────────────────────────────────────────────────────────────
# TRACK PROCESSING
# ─────────────────────────────────────────────────────────────────────────────

def process_track(root: ET.Element, filename: str,
                  overwrite: bool = False, dry_run: bool = False,
                  dir_filter: Optional[str] = None) -> dict:
    result = {
        'ok': False, 'filename': filename,
        'written': [], 'skipped': [], 'flags': [], 'error': None,
    }

    entry = find_track_entry(root, filename, dir_filter=dir_filter)
    if entry is None:
        result['error'] = "Not found in collection.nml"
        return result

    bpm, anchor_ms = get_beatgrid_info(entry)
    if bpm is None:
        result['error'] = "No BPM data — has this track been analysed in Traktor?"
        return result
    if anchor_ms is None:
        result['error'] = "No beatgrid anchor (AutoGrid) found — re-analyse in Traktor"
        return result

    duration_ms = get_duration_ms(entry)
    if not duration_ms:
        result['error'] = "Could not read track duration from NML"
        return result

    pos = calculate_positions(bpm, anchor_ms, duration_ms)
    result['flags'] = pos['flags']

    if dry_run:
        result['ok'] = True
        result['written'] = [
            f"[DRY RUN] BPM={bpm:.2f}  anchor={anchor_ms/1000:.3f}s  duration={duration_ms/1000:.1f}s",
            f"[DRY RUN] Slot {SLOT_BEAT}  Beat:      {pos['beat_ms']/1000:.2f}s",
            f"[DRY RUN] Slot {SLOT_BREAKDOWN}  Breakdown: {pos['breakdown_ms']/1000:.2f}s",
            f"[DRY RUN] Slot {SLOT_GROOVE}  Groove:    {pos['groove_ms']/1000:.2f}s"
            f"  [loop {pos['groove_len_ms']/1000:.1f}s]",
            f"[DRY RUN] Slot {SLOT_END}  End:       {pos['end_ms']/1000:.2f}s",
        ]
    else:
        wr = write_cues(entry, pos, overwrite=overwrite)
        result['written'] = wr['written']
        result['skipped'] = wr['skipped']
        result['ok'] = True

    return result


def print_result(result: dict, verbose: bool = True):
    status = "✅" if result['ok'] else "❌"
    print(f"\n{status}  {result['filename']}")
    if result['error']:
        print(f"   ERROR: {result['error']}")
        return
    for line in result['written']:
        print(f"   {line}")
    for line in result['skipped']:
        print(f"   ⚠️  {line}")
    if verbose:
        for flag in result['flags']:
            print(f"   📋 {flag}")


# ─────────────────────────────────────────────────────────────────────────────
# ENTRY POINTS
# ─────────────────────────────────────────────────────────────────────────────

def run_single(args, root, tree, nml_path):
    filename = Path(args.track).name
    result = process_track(root, filename, overwrite=args.overwrite,
                           dry_run=args.dry_run, dir_filter=args.dir)
    print_result(result)
    if result['ok'] and not args.dry_run and result['written']:
        bp = backup_nml(nml_path)
        print(f"\n💾 Backup: {bp}")
        tree.write(str(nml_path), encoding='UTF-8', xml_declaration=True)
        print(f"✅ Saved: {nml_path}")
        print("\n⚠️  Restart Traktor to load the updated collection.")


def run_playlist(args, root, tree, nml_path):
    playlist_path = Path(args.playlist)
    if not playlist_path.exists():
        print(f"❌ Playlist not found: {playlist_path}")
        sys.exit(1)

    with open(playlist_path) as f:
        playlist = json.load(f)

    tracks = playlist.get('tracks', [])
    if not tracks:
        print("❌ No tracks found in playlist JSON")
        sys.exit(1)

    print(f"\n🎵 Processing {len(tracks)} tracks from {playlist_path.name}")
    if args.dry_run:
        print("   (DRY RUN — no changes will be written)\n")

    results = []
    for track in tracks:
        filename = Path(track.get('file_path', '')).name
        result = process_track(root, filename, overwrite=args.overwrite,
                               dry_run=args.dry_run, dir_filter=args.dir)
        print_result(result, verbose=args.verbose)
        results.append(result)

    ok      = [r for r in results if r['ok'] and r['written']]
    skipped = [r for r in results if r['ok'] and not r['written'] and not r['error']]
    errors  = [r for r in results if r['error']]
    flagged = [r for r in results if r['flags']]

    print(f"\n{'─'*60}")
    print(f"  Processed : {len(results)}")
    print(f"  Written   : {len(ok)}")
    print(f"  Skipped   : {len(skipped)}")
    print(f"  Errors    : {len(errors)}")
    print(f"  Flagged   : {len(flagged)}  (need manual review in Traktor)")
    print(f"{'─'*60}")

    if errors:
        print("\nErrors:")
        for r in errors:
            print(f"  {r['filename']}: {r['error']}")

    if any(r['written'] for r in results) and not args.dry_run:
        bp = backup_nml(nml_path)
        print(f"\n💾 Backup: {bp}")
        tree.write(str(nml_path), encoding='UTF-8', xml_declaration=True)
        print(f"✅ Saved: {nml_path}")
        print("\n⚠️  Restart Traktor to load the updated collection.")
    elif args.dry_run:
        print("\n(Dry run complete — nothing written)")
    else:
        print("\nNothing to write.")


# ─────────────────────────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description='Write deep house cue points to Traktor collection.nml',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Dry run — preview without writing
  python3 traktor-automation/deep_house_cue_writer.py \\
      --playlist track-selection-engine/best-of-deep-dub-tech-house.json \\
      --dry-run

  # Single track
  python3 traktor-automation/deep_house_cue_writer.py \\
      --track "Prof. Fee 2009 (Dub Taylor D. Mark Remix).m4a"

  # Full playlist
  python3 traktor-automation/deep_house_cue_writer.py \\
      --playlist track-selection-engine/best-of-deep-dub-tech-house.json

  # Overwrite existing slots 2-5 (slot 1 always protected)
  python3 traktor-automation/deep_house_cue_writer.py \\
      --playlist track-selection-engine/best-of-deep-dub-tech-house.json \\
      --overwrite

  # Override NML path
  python3 traktor-automation/deep_house_cue_writer.py \\
      --playlist track-selection-engine/best-of-deep-dub-tech-house.json \\
      --nml "/Users/dantaylor/Documents/Native Instruments/Traktor 3.11.1/collection.nml"
        """
    )

    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--track',    metavar='FILENAME',
                      help='Filename of a single track to process')
    mode.add_argument('--playlist', metavar='JSON_FILE',
                      help='Path to playlist JSON file')

    parser.add_argument('--nml', metavar='PATH',
                        default=str(NML_DEFAULT),
                        help=f'Path to collection.nml (default: {NML_DEFAULT})')
    parser.add_argument('--dir', metavar='SUBSTR', default=None,
                        help='Only write to entries whose DIR contains this substring '
                             '(e.g. "Testing"). Useful when duplicate entries exist.')
    parser.add_argument('--dry-run',   action='store_true',
                        help='Preview without writing')
    parser.add_argument('--overwrite', action='store_true',
                        help='Replace existing cues in slots 2-5')
    parser.add_argument('--verbose',   action='store_true', default=True,
                        help='Show flags and review notes (default: on)')

    args = parser.parse_args()
    nml_path = Path(args.nml)

    print(f"\n{'═'*60}")
    print(f"  Deep House Cue Point Writer")
    print(f"  NML: {nml_path}")
    if args.dry_run:
        print(f"  Mode: DRY RUN (no changes)")
    elif args.overwrite:
        print(f"  Mode: OVERWRITE (slots 2-5 replaced)")
    else:
        print(f"  Mode: SAFE (existing slots preserved)")
    print(f"{'═'*60}")

    try:
        tree, root = load_nml(nml_path)
    except FileNotFoundError as e:
        print(f"\n❌ {e}")
        sys.exit(1)

    if args.track:
        run_single(args, root, tree, nml_path)
    else:
        run_playlist(args, root, tree, nml_path)


if __name__ == '__main__':
    main()
