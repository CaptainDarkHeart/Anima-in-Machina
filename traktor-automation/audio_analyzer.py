#!/usr/bin/env python3
"""
Audio Analysis Engine for Traktor AI DJ
========================================

Real-time audio analysis using Librosa to "hear" what's being played.

Features:
- Beat detection and tempo analysis
- Energy level measurement
- Harmonic/key detection
- Cue point detection (intro, outro, breakdown, build, drop)
- Spectral analysis for mix compatibility
"""

import librosa
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import json


class AudioAnalyzer:
    """Analyzes audio files to extract DJ-relevant features."""

    def __init__(self, sample_rate: int = 22050):
        """
        Initialize the audio analyzer.

        Args:
            sample_rate: Sample rate for analysis (22050 Hz is good for most music)
        """
        self.sample_rate = sample_rate
        self.cache_dir = Path.home() / ".cache" / "traktor_ai_dj"
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _get_cache_path(self, audio_path: str) -> Path:
        """Get cache file path for analyzed audio."""
        audio_file = Path(audio_path)
        cache_name = f"{audio_file.stem}_{audio_file.stat().st_mtime}.json"
        return self.cache_dir / cache_name

    def analyze_track(self, audio_path: str, use_cache: bool = True) -> Dict:
        """
        Analyze an audio track and extract all DJ-relevant features.

        Args:
            audio_path: Path to audio file
            use_cache: Whether to use cached analysis if available

        Returns:
            Dictionary containing analysis results
        """
        # Check cache first
        cache_path = self._get_cache_path(audio_path)
        if use_cache and cache_path.exists():
            with open(cache_path, 'r') as f:
                return json.load(f)

        print(f"Analyzing: {Path(audio_path).name}")

        # Load audio
        y, sr = librosa.load(audio_path, sr=self.sample_rate)
        duration = librosa.get_duration(y=y, sr=sr)

        # Perform all analyses
        analysis = {
            'file_path': str(audio_path),
            'duration': duration,
            'tempo': self._analyze_tempo(y, sr),
            'beats': self._detect_beats(y, sr),
            'energy': self._analyze_energy(y, sr),
            'harmony': self._analyze_harmony(y, sr),
            'cue_points': self._detect_cue_points(y, sr),
            'spectral': self._analyze_spectral(y, sr),
        }

        # Save to cache
        with open(cache_path, 'w') as f:
            json.dump(analysis, f, indent=2)

        return analysis

    def _analyze_tempo(self, y: np.ndarray, sr: int) -> Dict:
        """Analyze tempo and beat information."""
        # Get tempo and beat frames
        tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr)
        beat_times = librosa.frames_to_time(beat_frames, sr=sr)

        # Calculate tempo confidence by checking beat consistency
        beat_intervals = np.diff(beat_times)
        tempo_stability = 1.0 - np.std(beat_intervals) / np.mean(beat_intervals) if len(beat_intervals) > 0 else 0.0

        return {
            'bpm': float(tempo),
            'confidence': float(tempo_stability),
            'beat_count': len(beat_times),
            'first_beat_time': float(beat_times[0]) if len(beat_times) > 0 else 0.0,
        }

    def _detect_beats(self, y: np.ndarray, sr: int) -> List[float]:
        """Detect all beat timestamps in the track."""
        _, beat_frames = librosa.beat.beat_track(y=y, sr=sr)
        beat_times = librosa.frames_to_time(beat_frames, sr=sr)
        return [float(t) for t in beat_times]

    def _analyze_energy(self, y: np.ndarray, sr: int) -> Dict:
        """Analyze energy levels throughout the track."""
        # Calculate RMS energy in segments
        hop_length = 512
        rms = librosa.feature.rms(y=y, hop_length=hop_length)[0]
        times = librosa.frames_to_time(np.arange(len(rms)), sr=sr, hop_length=hop_length)

        # Segment into 8-second windows
        segment_duration = 8.0
        num_segments = int(len(times) / (segment_duration * sr / hop_length))

        segments = []
        for i in range(num_segments):
            start_idx = int(i * segment_duration * sr / hop_length)
            end_idx = int((i + 1) * segment_duration * sr / hop_length)

            if end_idx > len(rms):
                end_idx = len(rms)

            segment_rms = rms[start_idx:end_idx]
            segments.append({
                'start_time': float(times[start_idx]),
                'end_time': float(times[end_idx - 1]) if end_idx > 0 else 0.0,
                'energy': float(np.mean(segment_rms)),
                'peak': float(np.max(segment_rms)),
            })

        return {
            'overall': float(np.mean(rms)),
            'peak': float(np.max(rms)),
            'segments': segments,
        }

    def _analyze_harmony(self, y: np.ndarray, sr: int) -> Dict:
        """Analyze harmonic content and estimate musical key."""
        # Compute chromagram
        chromagram = librosa.feature.chroma_cqt(y=y, sr=sr)

        # Estimate key by finding dominant pitch class
        chroma_mean = np.mean(chromagram, axis=1)
        key_index = np.argmax(chroma_mean)

        # Map to key names (C, C#, D, etc.)
        key_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        estimated_key = key_names[key_index]

        # Determine if major or minor by analyzing the 3rd
        major_third = chroma_mean[(key_index + 4) % 12]
        minor_third = chroma_mean[(key_index + 3) % 12]
        mode = 'major' if major_third > minor_third else 'minor'

        # Calculate key confidence
        confidence = float(chroma_mean[key_index] / np.sum(chroma_mean))

        return {
            'key': estimated_key,
            'mode': mode,
            'confidence': confidence,
            'full_key': f"{estimated_key} {mode}",
        }

    def _detect_cue_points(self, y: np.ndarray, sr: int) -> Dict:
        """
        Detect important cue points for DJ mixing.

        - Intro: First 16-32 bars
        - Outro: Last 16-32 bars
        - Breakdown: Low energy sections
        - Build: Rising energy sections
        - Drop: Sudden energy increases
        """
        duration = librosa.get_duration(y=y, sr=sr)

        # Get beats and energy
        _, beat_frames = librosa.beat.beat_track(y=y, sr=sr)
        beat_times = librosa.frames_to_time(beat_frames, sr=sr)

        # Calculate energy
        hop_length = 512
        rms = librosa.feature.rms(y=y, hop_length=hop_length)[0]
        times = librosa.frames_to_time(np.arange(len(rms)), sr=sr, hop_length=hop_length)

        # Smooth energy for trend detection
        window_size = int(sr / hop_length * 2)  # 2 second window
        energy_smooth = np.convolve(rms, np.ones(window_size)/window_size, mode='same')

        cue_points = {}

        # INTRO: First 16 bars (or first beat if less than 16 bars)
        if len(beat_times) >= 16:
            cue_points['intro_start'] = 0.0
            cue_points['intro_end'] = float(beat_times[16])
        else:
            cue_points['intro_start'] = 0.0
            cue_points['intro_end'] = float(beat_times[-1]) if len(beat_times) > 0 else 0.0

        # OUTRO: Last 16 bars
        if len(beat_times) >= 16:
            cue_points['outro_start'] = float(beat_times[-16])
            cue_points['outro_end'] = duration
        else:
            cue_points['outro_start'] = float(beat_times[0]) if len(beat_times) > 0 else 0.0
            cue_points['outro_end'] = duration

        # BREAKDOWN: Find sections with lowest energy (good for mixing in)
        breakdowns = self._find_low_energy_sections(energy_smooth, times, beat_times)
        if breakdowns:
            cue_points['breakdown'] = breakdowns[0]  # Take the strongest breakdown

        # BUILD: Find sections with rising energy
        builds = self._find_energy_builds(energy_smooth, times, beat_times)
        if builds:
            cue_points['build'] = builds[0]  # Take the first major build

        # DROP: Find sudden energy increases (good for dramatic transitions)
        drops = self._find_energy_drops(energy_smooth, times, beat_times)
        if drops:
            cue_points['drop'] = drops[0]  # Take the first major drop

        return cue_points

    def _find_low_energy_sections(self, energy: np.ndarray, times: np.ndarray, beat_times: np.ndarray) -> List[Dict]:
        """Find breakdown sections with low energy."""
        threshold = np.percentile(energy, 25)  # Bottom 25% energy
        low_energy_mask = energy < threshold

        # Find continuous low-energy regions
        regions = []
        in_region = False
        start_idx = 0

        for i, is_low in enumerate(low_energy_mask):
            if is_low and not in_region:
                start_idx = i
                in_region = True
            elif not is_low and in_region:
                # Region ended, record it if it's long enough (>4 seconds)
                if times[i] - times[start_idx] > 4.0:
                    # Snap to nearest beat
                    start_time = self._snap_to_beat(times[start_idx], beat_times)
                    end_time = self._snap_to_beat(times[i], beat_times)

                    regions.append({
                        'start': float(start_time),
                        'end': float(end_time),
                        'duration': float(end_time - start_time),
                    })
                in_region = False

        # Sort by duration (longest first)
        regions.sort(key=lambda x: x['duration'], reverse=True)
        return regions[:3]  # Return top 3 breakdowns

    def _find_energy_builds(self, energy: np.ndarray, times: np.ndarray, beat_times: np.ndarray) -> List[Dict]:
        """Find sections with rising energy (builds)."""
        # Calculate energy gradient
        gradient = np.gradient(energy)

        # Find sustained positive gradients
        builds = []
        in_build = False
        start_idx = 0

        # Threshold for sustained rise
        rise_threshold = np.percentile(gradient, 70)

        for i, grad in enumerate(gradient):
            if grad > rise_threshold and not in_build:
                start_idx = i
                in_build = True
            elif grad <= 0 and in_build:
                # Build ended, record if significant (>4 seconds)
                if times[i] - times[start_idx] > 4.0:
                    start_time = self._snap_to_beat(times[start_idx], beat_times)
                    end_time = self._snap_to_beat(times[i], beat_times)

                    builds.append({
                        'start': float(start_time),
                        'end': float(end_time),
                        'duration': float(end_time - start_time),
                    })
                in_build = False

        # Sort by duration
        builds.sort(key=lambda x: x['duration'], reverse=True)
        return builds[:3]

    def _find_energy_drops(self, energy: np.ndarray, times: np.ndarray, beat_times: np.ndarray) -> List[Dict]:
        """Find sudden energy increases (drops/peaks)."""
        # Calculate second derivative to find sharp changes
        gradient = np.gradient(energy)
        second_derivative = np.gradient(gradient)

        # Find peaks in second derivative (sudden increases)
        from scipy.signal import find_peaks
        peaks, properties = find_peaks(second_derivative, prominence=np.std(second_derivative))

        drops = []
        for peak_idx in peaks:
            drop_time = self._snap_to_beat(times[peak_idx], beat_times)
            drops.append({
                'time': float(drop_time),
                'intensity': float(second_derivative[peak_idx]),
            })

        # Sort by intensity
        drops.sort(key=lambda x: x['intensity'], reverse=True)
        return drops[:5]  # Return top 5 drops

    def _snap_to_beat(self, time: float, beat_times: np.ndarray) -> float:
        """Snap a time to the nearest beat."""
        if len(beat_times) == 0:
            return time
        idx = np.argmin(np.abs(beat_times - time))
        return beat_times[idx]

    def _analyze_spectral(self, y: np.ndarray, sr: int) -> Dict:
        """Analyze spectral characteristics for mix compatibility."""
        # Spectral centroid (brightness)
        spectral_centroids = librosa.feature.spectral_centroid(y=y, sr=sr)[0]

        # Spectral rolloff (frequency below which 85% of energy is contained)
        spectral_rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)[0]

        # Zero crossing rate (percussiveness indicator)
        zcr = librosa.feature.zero_crossing_rate(y)[0]

        return {
            'brightness': float(np.mean(spectral_centroids)),
            'rolloff': float(np.mean(spectral_rolloff)),
            'percussiveness': float(np.mean(zcr)),
        }

    def get_mix_in_point(self, analysis: Dict) -> float:
        """
        Get the optimal time to mix into this track.

        Returns time in seconds.
        """
        cue_points = analysis['cue_points']

        # Prefer breakdown if available (low energy = easy to mix in)
        if 'breakdown' in cue_points:
            return cue_points['breakdown']['start']

        # Otherwise use intro end
        return cue_points.get('intro_end', 0.0)

    def get_mix_out_point(self, analysis: Dict) -> float:
        """
        Get the optimal time to start mixing out of this track.

        Returns time in seconds.
        """
        cue_points = analysis['cue_points']
        duration = analysis['duration']

        # Start mixing out at outro start
        outro_start = cue_points.get('outro_start', duration - 32.0)

        # But not too late (leave at least 45 seconds for blend)
        min_time = duration - 45.0

        return max(outro_start, min_time)

    def are_tracks_compatible(self, analysis1: Dict, analysis2: Dict) -> Dict:
        """
        Check if two tracks are compatible for mixing.

        Returns compatibility score and reasons.
        """
        score = 100.0
        reasons = []

        # Tempo compatibility (within 6% is mixable with pitch adjustment)
        tempo1 = analysis1['tempo']['bpm']
        tempo2 = analysis2['tempo']['bpm']
        tempo_diff = abs(tempo1 - tempo2) / tempo1

        if tempo_diff > 0.06:
            score -= 30
            reasons.append(f"Tempo mismatch: {tempo1:.1f} vs {tempo2:.1f} BPM")
        elif tempo_diff > 0.03:
            score -= 10
            reasons.append(f"Minor tempo difference: {tempo1:.1f} vs {tempo2:.1f} BPM")

        # Harmonic compatibility (key matching)
        key1 = analysis1['harmony']['key']
        key2 = analysis2['harmony']['key']

        if not self._keys_compatible(key1, key2):
            score -= 20
            reasons.append(f"Key clash: {key1} vs {key2}")

        # Energy compatibility (smooth transition)
        energy1 = analysis1['energy']['overall']
        energy2 = analysis2['energy']['overall']
        energy_diff = abs(energy1 - energy2) / max(energy1, energy2)

        if energy_diff > 0.3:
            score -= 15
            reasons.append(f"Large energy change: {energy_diff:.1%}")

        return {
            'score': max(0, score),
            'compatible': score > 50,
            'reasons': reasons,
        }

    def _keys_compatible(self, key1: str, key2: str) -> bool:
        """Check if two keys are harmonically compatible."""
        # Simplified harmonic mixing rules (Camelot wheel)
        # Compatible keys: same key, +/-1 semitone, +7 semitones (perfect 5th)
        key_map = {'C': 0, 'C#': 1, 'D': 2, 'D#': 3, 'E': 4, 'F': 5,
                   'F#': 6, 'G': 7, 'G#': 8, 'A': 9, 'A#': 10, 'B': 11}

        if key1 not in key_map or key2 not in key_map:
            return True  # Can't determine, assume compatible

        interval = abs(key_map[key1] - key_map[key2])
        interval = min(interval, 12 - interval)  # Handle wraparound

        return interval in [0, 1, 2, 5, 7]  # Compatible intervals
