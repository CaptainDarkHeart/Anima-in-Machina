"""NML Reader — reads Traktor's collection.nml and exposes per-track analysis data.

Traktor stores all its analysis results in collection.nml:
  - BPM (TEMPO element)
  - Beatgrid anchor — bar 1, beat 1 position in ms (CUE_V2 TYPE=4)
  - Musical key in Camelot notation (INFO KEY)
  - Loudness / auto-gain levels (LOUDNESS element)
  - Duration (INFO PLAYTIME_FLOAT)
  - Existing cue points and loops (CUE_V2 elements)

This module is the single source of truth for all Traktor data in the MCP server.
Logic is ported from traktor-automation/deep_house_cue_writer.py.
"""

import shutil
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path
from typing import Optional

NML_DEFAULT = Path.home() / "Documents/Native Instruments/Traktor 3.11.1/collection.nml"

# Traktor CUE_V2 TYPE values
TYPE_CUE      = 0   # Regular hot cue
TYPE_FADE_IN  = 1
TYPE_FADE_OUT = 2
TYPE_LOAD     = 3
TYPE_GRID     = 4   # AutoGrid beatgrid anchor — read-only, never written
TYPE_LOOP     = 5   # Saved loop / floating cue

# Camelot wheel: key string → wheel position (1-12, minor=m, major=d)
# Used for harmonic compatibility scoring.
CAMELOT_POSITIONS = {
    "1m": 1,  "2m": 2,  "3m": 3,  "4m": 4,  "5m": 5,  "6m": 6,
    "7m": 7,  "8m": 8,  "9m": 9,  "10m": 10, "11m": 11, "12m": 12,
    "1d": 13, "2d": 14, "3d": 15, "4d": 16,  "5d": 17, "6d": 18,
    "7d": 19, "8d": 20, "9d": 21, "10d": 22, "11d": 23, "12d": 24,
}

# Human-readable key names for display
KEY_NAMES = {
    "1m": "A min",  "2m": "E min",  "3m": "B min",  "4m": "F# min",
    "5m": "C# min", "6m": "G# min", "7m": "Eb min", "8m": "Bb min",
    "9m": "F min",  "10m": "C min", "11m": "G min", "12m": "D min",
    "1d": "C maj",  "2d": "G maj",  "3d": "D maj",  "4d": "A maj",
    "5d": "E maj",  "6d": "B maj",  "7d": "F# maj", "8d": "Db maj",
    "9d": "Ab maj", "10d": "Eb maj","11d": "Bb maj","12d": "F maj",
}


def camelot_compatible(key1: str, key2: str) -> tuple[bool, str]:
    """
    Determine Camelot wheel compatibility between two keys.

    Returns (is_compatible, description).
    Compatible = same key, adjacent number same mode, or same number relative (m↔d).
    """
    if not key1 or not key2:
        return False, "unknown key"

    p1 = CAMELOT_POSITIONS.get(key1)
    p2 = CAMELOT_POSITIONS.get(key2)
    if p1 is None or p2 is None:
        return False, f"unrecognised key ({key1!r} or {key2!r})"

    if key1 == key2:
        return True, "same key — perfect match"

    # Extract number and mode from each key
    mode1 = "m" if key1.endswith("m") else "d"
    mode2 = "m" if key2.endswith("m") else "d"
    num1 = int(key1[:-1])
    num2 = int(key2[:-1])

    # Relative key: same number, different mode (e.g. 8m ↔ 8d)
    if num1 == num2 and mode1 != mode2:
        return True, f"relative key ({KEY_NAMES.get(key1, key1)} ↔ {KEY_NAMES.get(key2, key2)})"

    # Adjacent on same mode ring (±1, wrapping 12→1)
    if mode1 == mode2:
        diff = abs(num1 - num2)
        if diff == 1 or diff == 11:
            return True, "adjacent key — energy shift mix"

    return False, f"incompatible keys (Camelot {key1} vs {key2})"


class NMLReader:
    """Read-only interface to Traktor's collection.nml."""

    def __init__(self, nml_path: Path = NML_DEFAULT):
        self.nml_path = Path(nml_path)
        self._tree: Optional[ET.ElementTree] = None
        self._root: Optional[ET.Element] = None

    def _load(self) -> ET.Element:
        """Parse NML lazily; cache the result."""
        if self._root is None:
            if not self.nml_path.exists():
                raise FileNotFoundError(f"collection.nml not found: {self.nml_path}")
            self._tree = ET.parse(str(self.nml_path))
            self._root = self._tree.getroot()
        return self._root

    def reload(self) -> None:
        """Force re-parse of NML (call after external writes)."""
        self._tree = None
        self._root = None

    # ------------------------------------------------------------------ #
    # Entry lookup                                                         #
    # ------------------------------------------------------------------ #

    def find_entry(self, filename: str) -> Optional[ET.Element]:
        """
        Find the best ENTRY element for a given filename.

        When duplicate entries exist (track in multiple playlists), prefer:
        1. Entries that have an AutoGrid cue (TYPE=4) — fully analysed
        2. Most recently modified among those

        Ported from deep_house_cue_writer.find_track_entry().
        """
        root = self._load()
        collection = root.find(".//COLLECTION")
        if collection is None:
            return None

        candidates = [
            e for e in collection.findall("ENTRY")
            if (loc := e.find("LOCATION")) is not None
            and loc.get("FILE") == filename
        ]

        if not candidates:
            return None
        if len(candidates) == 1:
            return candidates[0]

        def modified_key(e: ET.Element) -> tuple:
            date = e.get("MODIFIED_DATE", "0000/0/0").replace("/", "")
            time = e.get("MODIFIED_TIME", "0").zfill(10)
            return date, time

        gridded = [
            e for e in candidates
            if any(c.get("TYPE") == "4" for c in e.findall("CUE_V2"))
        ]
        pool = gridded if gridded else candidates
        return sorted(pool, key=modified_key, reverse=True)[0]

    # ------------------------------------------------------------------ #
    # Data extraction                                                      #
    # ------------------------------------------------------------------ #

    def get_track_data(self, filename: str) -> Optional[dict]:
        """
        Return all Traktor analysis data for a track.

        Returns None if the track is not in the collection or has not been analysed.

        Keys in the returned dict:
            filename        str
            bpm             float | None
            anchor_ms       float | None   — beatgrid bar-1-beat-1 position
            duration_ms     float | None
            key_camelot     str | None     — e.g. "8m"
            key_name        str | None     — e.g. "Bb min"
            peak_db         float | None
            perceived_db    float | None
            analyzed_db     float | None
            has_grid        bool
            existing_cues   list[dict]     — each: {name, start_ms, hotcue, type, len_ms}
        """
        entry = self.find_entry(filename)
        if entry is None:
            return None

        data: dict = {"filename": filename}

        # BPM
        tempo_el = entry.find("TEMPO")
        if tempo_el is not None:
            try:
                bpm = float(tempo_el.get("BPM", 0))
                data["bpm"] = bpm if bpm > 0 else None
            except (ValueError, TypeError):
                data["bpm"] = None
        else:
            data["bpm"] = None

        # Beatgrid anchor
        data["anchor_ms"] = None
        data["has_grid"] = False
        for cue in entry.findall("CUE_V2"):
            if cue.get("TYPE") == "4":
                try:
                    data["anchor_ms"] = float(cue.get("START", 0))
                    data["has_grid"] = True
                except (ValueError, TypeError):
                    pass
                break

        # Duration
        info = entry.find("INFO")
        data["duration_ms"] = None
        if info is not None:
            for attr in ("PLAYTIME_FLOAT", "PLAYTIME"):
                val = info.get(attr)
                if val:
                    try:
                        data["duration_ms"] = float(val) * 1000.0
                        break
                    except (ValueError, TypeError):
                        pass

        # Key
        data["key_camelot"] = None
        data["key_name"] = None
        if info is not None:
            key_str = info.get("KEY", "")
            if key_str:
                data["key_camelot"] = key_str
                data["key_name"] = KEY_NAMES.get(key_str, key_str)

        # Loudness
        loudness = entry.find("LOUDNESS")
        data["peak_db"] = None
        data["perceived_db"] = None
        data["analyzed_db"] = None
        if loudness is not None:
            for attr in ("PEAK_DB", "PERCEIVED_DB", "ANALYZED_DB"):
                try:
                    data[attr.lower()] = float(loudness.get(attr, 0))
                except (ValueError, TypeError):
                    pass

        # Existing cues (hotcues only — hotcue >= 0, excluding grid anchor)
        existing: list[dict] = []
        for cue in entry.findall("CUE_V2"):
            cue_type = cue.get("TYPE", "0")
            if cue_type == "4":
                continue  # beatgrid anchor — skip
            try:
                hotcue = int(cue.get("HOTCUE", "-1"))
            except ValueError:
                hotcue = -1
            existing.append({
                "name":     cue.get("NAME", ""),
                "start_ms": float(cue.get("START", 0)),
                "hotcue":   hotcue,
                "type":     int(cue_type),
                "len_ms":   float(cue.get("LEN", 0)),
            })
        data["existing_cues"] = existing

        return data

    # ------------------------------------------------------------------ #
    # Writing                                                              #
    # ------------------------------------------------------------------ #

    def backup(self) -> Path:
        """Create a timestamped backup of collection.nml. Returns backup path."""
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = self.nml_path.parent / f"collection_backup_{ts}.nml"
        shutil.copy2(self.nml_path, backup_path)
        return backup_path

    def write_cues(
        self,
        filename: str,
        cue_specs: list[dict],
        overwrite: bool = False,
    ) -> dict:
        """
        Write cue points into a track's ENTRY.

        cue_specs: list of dicts with keys:
            slot      int     — hotcue slot number (2-8; slot 1 always protected)
            name      str
            start_ms  float
            type      int     — 0=cue, 5=loop
            len_ms    float   — loop length (0 for cues)

        Returns {'written': [...labels], 'skipped': [...labels], 'backup': Path}.
        Automatically backs up NML before any write.
        """
        root = self._load()
        entry = self.find_entry(filename)
        if entry is None:
            raise ValueError(f"Track not found in collection: {filename!r}")

        # Protected slots: slot 1 always, plus any occupied slots if not overwriting
        protected = {1}
        occupied: set[int] = set()
        for cue in entry.findall("CUE_V2"):
            try:
                slot = int(cue.get("HOTCUE", "-1"))
                if slot > 0:
                    occupied.add(slot)
            except ValueError:
                pass

        written = []
        skipped = []

        # Collect which slots we're actually going to touch, then do one backup
        to_write = []
        for spec in cue_specs:
            slot = spec["slot"]
            if slot in protected:
                skipped.append(f"Slot {slot} ({spec.get('name', '')}) — slot 1 always protected")
                continue
            if slot in occupied and not overwrite:
                skipped.append(f"Slot {slot} ({spec.get('name', '')}) — already occupied (use overwrite=true)")
                continue
            to_write.append(spec)

        if not to_write:
            return {"written": written, "skipped": skipped, "backup": None}

        backup_path = self.backup()

        for spec in to_write:
            slot = spec["slot"]
            # Remove existing cue in this slot
            for existing_cue in list(entry.findall("CUE_V2")):
                try:
                    if int(existing_cue.get("HOTCUE", "-1")) == slot:
                        entry.remove(existing_cue)
                except ValueError:
                    pass

            cue_el = ET.Element("CUE_V2")
            cue_el.set("NAME",        spec.get("name", "n.n."))
            cue_el.set("DISPL_ORDER", str(slot - 1))
            cue_el.set("TYPE",        str(spec.get("type", TYPE_CUE)))
            cue_el.set("START",       f"{spec['start_ms']:.6f}")
            cue_el.set("LEN",         f"{spec.get('len_ms', 0.0):.6f}")
            cue_el.set("REPEATS",     "-1")
            cue_el.set("HOTCUE",      str(slot))
            entry.append(cue_el)

            loop_note = f"  [loop {spec['len_ms']/1000:.1f}s]" if spec.get("len_ms", 0) > 0 else ""
            written.append(f"Slot {slot} ({spec.get('name', '')}): {spec['start_ms']/1000:.2f}s{loop_note}")

        assert self._tree is not None
        self._tree.write(str(self.nml_path), encoding="UTF-8", xml_declaration=True)
        self.reload()

        return {"written": written, "skipped": skipped, "backup": backup_path}
