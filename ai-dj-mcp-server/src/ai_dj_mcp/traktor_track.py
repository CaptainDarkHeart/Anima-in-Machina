"""TraktorTrack — track model with Traktor-first analysis + optional librosa enhancement.

Data hierarchy:
  PRIMARY  — Traktor's own analysis via collection.nml (BPM, key, beatgrid, gain)
  SECONDARY — librosa analysis of raw audio (energy envelope, breakdown detection, BPM cross-check)

Cue position logic ported from traktor-automation/deep_house_cue_writer.py.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

# ──────────────────────────────────────────────────────────────────────────── #
# Constants                                                                     #
# ──────────────────────────────────────────────────────────────────────────── #

# Default cue layout (hotcue slots; slot 1 always protected by Traktor)
SLOT_BEAT      = 2   # First kick / bar boundary near intro
SLOT_BREAKDOWN = 3   # Breakdown start
SLOT_GROOVE    = 4   # Sustained groove pocket (32-bar loop)
SLOT_END       = 5   # Mix-out marker

GROOVE_LOOP_BARS        = 32
SHORT_TRACK_LOOP_RATIO  = 0.40  # Warn if 32-bar loop > 40% of track duration
GROOVE_FRACTION         = 0.35  # ~35% into track
BREAKDOWN_FRACTION      = 0.65  # ~65% into track


# ──────────────────────────────────────────────────────────────────────────── #
# Bar arithmetic (ported from deep_house_cue_writer.py)                        #
# ──────────────────────────────────────────────────────────────────────────── #

def bars_to_ms(bars: float, bpm: float) -> float:
    """Convert bars (4/4 time) to milliseconds."""
    return bars * 4 * (60_000.0 / bpm)


def snap_to_bar(ms: float, bpm: float, anchor_ms: float) -> float:
    """Snap a millisecond position to the nearest bar boundary."""
    bar_ms = bars_to_ms(1, bpm)
    offset = ms - anchor_ms
    nearest_bar = round(offset / bar_ms)
    return anchor_ms + nearest_bar * bar_ms


# ──────────────────────────────────────────────────────────────────────────── #
# TraktorTrack                                                                  #
# ──────────────────────────────────────────────────────────────────────────── #

@dataclass
class TraktorTrack:
    """
    Represents a track with Traktor analysis as the primary data source.

    Instantiate via TraktorTrack.from_nml_data(data) where `data` is a dict
    from NMLReader.get_track_data().

    Optionally call load_librosa_analysis(audio_path) to enrich with energy
    envelope and a more accurate breakdown position.
    """

    # ── NML fields (primary) ──────────────────────────────────────────────── #
    filename:     str
    bpm:          Optional[float]
    anchor_ms:    Optional[float]
    duration_ms:  Optional[float]
    key_camelot:  Optional[str]
    key_name:     Optional[str]
    peak_db:      Optional[float]
    perceived_db: Optional[float]
    analyzed_db:  Optional[float]
    has_grid:     bool
    existing_cues: list[dict] = field(default_factory=list)

    # ── Librosa fields (secondary, populated on demand) ──────────────────── #
    librosa_bpm:       Optional[float] = None
    beat_times:        Optional[list[float]] = None  # seconds
    energy_envelope:   Optional[list[float]] = None  # RMS per frame
    energy_times:      Optional[list[float]] = None  # time axis for envelope
    breakdown_ms:      Optional[float] = None        # detected from energy dip
    librosa_loaded:    bool = False

    # ──────────────────────────────────────────────────────────────────────── #
    # Construction                                                              #
    # ──────────────────────────────────────────────────────────────────────── #

    @classmethod
    def from_nml_data(cls, data: dict) -> "TraktorTrack":
        """Build a TraktorTrack from the dict returned by NMLReader.get_track_data()."""
        return cls(
            filename=data["filename"],
            bpm=data.get("bpm"),
            anchor_ms=data.get("anchor_ms"),
            duration_ms=data.get("duration_ms"),
            key_camelot=data.get("key_camelot"),
            key_name=data.get("key_name"),
            peak_db=data.get("peak_db"),
            perceived_db=data.get("perceived_db"),
            analyzed_db=data.get("analyzed_db"),
            has_grid=data.get("has_grid", False),
            existing_cues=data.get("existing_cues", []),
        )

    # ──────────────────────────────────────────────────────────────────────── #
    # Properties                                                                #
    # ──────────────────────────────────────────────────────────────────────── #

    @property
    def duration_s(self) -> Optional[float]:
        return self.duration_ms / 1000.0 if self.duration_ms else None

    @property
    def bar_ms(self) -> Optional[float]:
        return bars_to_ms(1, self.bpm) if self.bpm else None

    def bpm_verified(self) -> bool:
        """True if librosa BPM agrees with Traktor BPM within 3%."""
        if self.bpm is None or self.librosa_bpm is None:
            return False
        return abs(self.librosa_bpm - self.bpm) / self.bpm < 0.03

    def occupied_hotcue_slots(self) -> set[int]:
        """Return set of hotcue slot numbers already in use (slot 1 always included)."""
        slots = {1}
        for cue in self.existing_cues:
            hc = cue.get("hotcue", -1)
            if hc is not None and hc > 0:
                slots.add(hc)
        return slots

    # ──────────────────────────────────────────────────────────────────────── #
    # Librosa analysis                                                          #
    # ──────────────────────────────────────────────────────────────────────── #

    def load_librosa_analysis(self, audio_path: str) -> None:
        """
        Run librosa analysis on the raw audio file.

        Populates: librosa_bpm, beat_times, energy_envelope, energy_times,
                   breakdown_ms (lowest-energy window in the 40-80% zone).
        """
        try:
            import librosa
            import numpy as np
        except ImportError as e:
            raise ImportError(f"librosa is required for audio analysis: {e}")

        audio_path = str(audio_path)
        if not Path(audio_path).exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        # Load at 22050 Hz (sufficient for structural analysis, much faster than 44.1k)
        y, sr = librosa.load(audio_path, sr=22050, mono=True)

        # Beat tracking
        tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr)
        self.librosa_bpm = float(tempo) if hasattr(tempo, "__len__") else float(tempo)
        self.beat_times = librosa.frames_to_time(beat_frames, sr=sr).tolist()

        # Energy envelope (RMS, hop_length=512 ≈ 23ms per frame at 22050Hz)
        hop = 512
        rms = librosa.feature.rms(y=y, hop_length=hop)[0]
        times = librosa.frames_to_time(range(len(rms)), sr=sr, hop_length=hop)
        self.energy_envelope = rms.tolist()
        self.energy_times = times.tolist()

        # Locate breakdown: lowest-energy 30s window in the 40–80% zone
        if self.duration_ms:
            self.breakdown_ms = self._detect_breakdown_ms(rms, times, self.duration_ms / 1000.0)

        self.librosa_loaded = True

    def _detect_breakdown_ms(
        self,
        rms: "np.ndarray",
        times: "np.ndarray",
        duration_s: float,
        window_s: float = 30.0,
        zone_start_frac: float = 0.40,
        zone_end_frac: float = 0.80,
    ) -> Optional[float]:
        """
        Find the start of the lowest-energy 30s window in the 40-80% zone.
        Returns position in milliseconds, or None if detection fails.
        """
        try:
            import numpy as np
            zone_start = duration_s * zone_start_frac
            zone_end   = duration_s * zone_end_frac

            # Indices within the zone
            mask = (times >= zone_start) & (times <= zone_end - window_s)
            if not mask.any():
                return None

            zone_times = times[mask]
            zone_rms   = rms[mask]

            # Convert window_s to number of frames
            frame_rate   = len(times) / duration_s
            window_frames = max(1, int(window_s * frame_rate))

            # Rolling mean energy over window
            if len(zone_rms) < window_frames:
                return None

            windows = np.convolve(zone_rms, np.ones(window_frames) / window_frames, mode="valid")
            best_idx = int(np.argmin(windows))
            return float(zone_times[best_idx]) * 1000.0

        except Exception:
            return None

    # ──────────────────────────────────────────────────────────────────────── #
    # Cue position calculation                                                  #
    # ──────────────────────────────────────────────────────────────────────── #

    def suggest_cue_positions(self) -> dict:
        """
        Calculate the four cue positions.

        Primary source: Traktor BPM + beatgrid anchor (bar arithmetic).
        Enhanced: if librosa analysis was loaded, the Breakdown position uses
                  the actual detected low-energy section instead of 65% estimate.

        Returns dict with keys:
            beat_ms, groove_ms, groove_len_ms, breakdown_ms, end_ms,
            flags (list of review notes), source ('nml' or 'nml+librosa')
        """
        if not self.bpm or not self.anchor_ms or not self.duration_ms:
            raise ValueError(
                f"Track {self.filename!r} is missing BPM, beatgrid anchor, or duration. "
                "Has it been analysed in Traktor?"
            )

        bpm        = self.bpm
        anchor_ms  = self.anchor_ms
        duration_ms = self.duration_ms
        flags: list[str] = []

        bar_ms  = bars_to_ms(1, bpm)
        loop_ms = bars_to_ms(GROOVE_LOOP_BARS, bpm)

        # ── BEAT: bar boundary near 10% of track ─────────────────────────── #
        beat_ms = snap_to_bar(duration_ms * 0.10, bpm, anchor_ms)
        if beat_ms < anchor_ms:
            beat_ms = snap_to_bar(anchor_ms + bar_ms, bpm, anchor_ms)
        flags.append("Beat: estimated at ~10% — verify kick entry in Traktor")

        # ── GROOVE: 32-bar loop at ~35% ───────────────────────────────────── #
        groove_ms = snap_to_bar(duration_ms * GROOVE_FRACTION, bpm, anchor_ms)
        end_zone  = duration_ms - loop_ms - bar_ms
        if groove_ms + loop_ms > end_zone:
            groove_ms = snap_to_bar(end_zone - loop_ms, bpm, anchor_ms)
            flags.append("Groove: loop shifted earlier to avoid overlap with end zone")
        if loop_ms > duration_ms * SHORT_TRACK_LOOP_RATIO:
            flags.append(
                f"Short track: 32-bar loop ({loop_ms/1000:.0f}s) is "
                f"{loop_ms/duration_ms*100:.0f}% of total — consider shorter loop"
            )

        # ── BREAKDOWN ─────────────────────────────────────────────────────── #
        if self.librosa_loaded and self.breakdown_ms is not None:
            # Snap the librosa-detected position to the nearest bar
            breakdown_ms = snap_to_bar(self.breakdown_ms, bpm, anchor_ms)
            source = "nml+librosa"

            # Sanity: breakdown must be after groove and before end zone
            min_breakdown = groove_ms + bars_to_ms(8, bpm)
            max_breakdown = duration_ms * 0.85
            if not (min_breakdown <= breakdown_ms <= max_breakdown):
                # Fall back to arithmetic estimate
                breakdown_ms = snap_to_bar(duration_ms * BREAKDOWN_FRACTION, bpm, anchor_ms)
                flags.append(
                    "Breakdown: librosa detection out of range — fell back to ~65% estimate"
                )
            else:
                flags.append(
                    f"Breakdown: detected at {breakdown_ms/1000:.1f}s by energy analysis"
                )
        else:
            breakdown_ms = snap_to_bar(duration_ms * BREAKDOWN_FRACTION, bpm, anchor_ms)
            source = "nml"
            flags.append("Breakdown: estimated at ~65% — verify in Traktor")

        # ── END: 32 bars before end ───────────────────────────────────────── #
        end_ms = snap_to_bar(duration_ms - loop_ms, bpm, anchor_ms)
        if end_ms <= breakdown_ms + bar_ms:
            end_ms = snap_to_bar(breakdown_ms + bars_to_ms(8, bpm), bpm, anchor_ms)
            flags.append("End: pushed forward — very short outro detected")

        # ── BPM cross-check ──────────────────────────────────────────────── #
        if self.librosa_loaded:
            if self.bpm_verified():
                flags.append(
                    f"BPM verified: Traktor {bpm:.2f} ≈ librosa {self.librosa_bpm:.2f} ✓"
                )
            elif self.librosa_bpm:
                flags.append(
                    f"BPM mismatch: Traktor {bpm:.2f} vs librosa {self.librosa_bpm:.2f} — "
                    "check beatgrid in Traktor"
                )

        return {
            "beat_ms":       beat_ms,
            "groove_ms":     groove_ms,
            "groove_len_ms": loop_ms,
            "breakdown_ms":  breakdown_ms,
            "end_ms":        end_ms,
            "flags":         flags,
            "source":        source if self.librosa_loaded else "nml",
        }

    def to_cue_specs(self, positions: dict, overwrite: bool = False) -> list[dict]:
        """
        Convert suggested positions dict to a list of cue_specs ready for NMLReader.write_cues().

        Skips slots already occupied (unless overwrite=True).
        """
        from .nml_reader import TYPE_CUE, TYPE_LOOP

        occupied = self.occupied_hotcue_slots()

        specs = [
            {
                "slot":     SLOT_BEAT,
                "name":     "Beat",
                "start_ms": positions["beat_ms"],
                "type":     TYPE_CUE,
                "len_ms":   0.0,
            },
            {
                "slot":     SLOT_BREAKDOWN,
                "name":     "Breakdown",
                "start_ms": positions["breakdown_ms"],
                "type":     TYPE_CUE,
                "len_ms":   0.0,
            },
            {
                "slot":     SLOT_GROOVE,
                "name":     "Groove",
                "start_ms": positions["groove_ms"],
                "type":     TYPE_LOOP,
                "len_ms":   positions["groove_len_ms"],
            },
            {
                "slot":     SLOT_END,
                "name":     "End",
                "start_ms": positions["end_ms"],
                "type":     TYPE_CUE,
                "len_ms":   0.0,
            },
        ]

        if not overwrite:
            specs = [s for s in specs if s["slot"] not in occupied]

        return specs
