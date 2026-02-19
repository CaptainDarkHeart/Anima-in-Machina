"""AI DJ MCP Server — Traktor-first DJ mixing tools via Model Context Protocol.

Data hierarchy:
  PRIMARY  — Traktor's analysis in collection.nml (BPM, beatgrid, key, gain, cues)
  SECONDARY — librosa on raw audio (energy envelope, BPM cross-check, breakdown detection)

Tools:
  get_track_info        — read Traktor analysis data for a track (fast, NML only)
  suggest_cue_points    — calculate + write 4 cue points using Traktor BPM/beatgrid
  write_cue_points      — manually write exact cue positions to NML
  suggest_transition    — BPM + key compatibility between two tracks
  analyze_library_track — full analysis: Traktor data + librosa cross-check
"""

import asyncio
import logging
from pathlib import Path

from mcp.server import Server
from mcp.types import Tool, TextContent

from .nml_reader import NMLReader, camelot_compatible
from .traktor_track import TraktorTrack, bars_to_ms

# ──────────────────────────────────────────────────────────────────────────── #
# Initialisation                                                                #
# ──────────────────────────────────────────────────────────────────────────── #

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ai-dj-mcp")

app = Server("ai-dj")

# Shared NMLReader — lazy-loaded once, cached
_nml_reader: NMLReader | None = None


def get_nml_reader() -> NMLReader:
    global _nml_reader
    if _nml_reader is None:
        _nml_reader = NMLReader()
    return _nml_reader


# ──────────────────────────────────────────────────────────────────────────── #
# Tool declarations                                                             #
# ──────────────────────────────────────────────────────────────────────────── #

@app.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="get_track_info",
            description=(
                "Read Traktor's analysis data for a track directly from collection.nml. "
                "Returns BPM, musical key (Camelot notation), duration, loudness/gain levels, "
                "beatgrid anchor position, and any existing cue points. Fast — no audio loading."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "filename": {
                        "type": "string",
                        "description": "Track filename, e.g. 'Dreams.m4a'. Must match exactly as stored in Traktor."
                    }
                },
                "required": ["filename"]
            }
        ),
        Tool(
            name="suggest_cue_points",
            description=(
                "Calculate and write four cue points for a track using Traktor's BPM and "
                "beatgrid anchor as the primary source. Cue positions are snapped to bar "
                "boundaries. If audio_path is provided, librosa analyses the energy envelope "
                "to detect the actual breakdown position rather than estimating at 65%. "
                "Writes directly to collection.nml with automatic backup. "
                "Slot layout: Slot 2=Beat (intro), Slot 3=Breakdown, Slot 4=Groove (32-bar loop), Slot 5=End (mix-out)."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "filename": {
                        "type": "string",
                        "description": "Track filename, e.g. 'Dreams.m4a'"
                    },
                    "audio_path": {
                        "type": "string",
                        "description": "Absolute path to audio file for librosa energy analysis (optional but recommended)"
                    },
                    "overwrite": {
                        "type": "boolean",
                        "description": "Replace existing cues in slots 2-5 (default: false — skips occupied slots)",
                        "default": False
                    }
                },
                "required": ["filename"]
            }
        ),
        Tool(
            name="write_cue_points",
            description=(
                "Manually write specific cue points to a track in collection.nml. "
                "Use this after reviewing suggestions to write exact positions, or to "
                "correct a specific cue. Slot 1 is always protected. "
                "Creates automatic NML backup before writing."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "filename": {
                        "type": "string",
                        "description": "Track filename, e.g. 'Dreams.m4a'"
                    },
                    "cue_points": {
                        "type": "array",
                        "description": "List of cue points to write",
                        "items": {
                            "type": "object",
                            "properties": {
                                "slot":     {"type": "integer", "description": "Hotcue slot (2-8; slot 1 always protected)"},
                                "name":     {"type": "string",  "description": "Cue label, e.g. 'Breakdown'"},
                                "time_ms":  {"type": "number",  "description": "Position in milliseconds"},
                                "type":     {"type": "integer", "description": "0=cue, 5=loop (default: 0)"},
                                "len_ms":   {"type": "number",  "description": "Loop length in ms (loops only, default: 0)"}
                            },
                            "required": ["slot", "name", "time_ms"]
                        }
                    },
                    "overwrite": {
                        "type": "boolean",
                        "description": "Replace existing cues in specified slots (default: false)",
                        "default": False
                    }
                },
                "required": ["filename", "cue_points"]
            }
        ),
        Tool(
            name="suggest_transition",
            description=(
                "Analyse two tracks and suggest how to mix them. Uses Traktor's BPM and key data "
                "from collection.nml. Returns BPM compatibility, Camelot wheel key compatibility, "
                "suggested mix-out time for the outgoing track, suggested mix-in time for the "
                "incoming track, and EQ swap strategy."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "filename1": {
                        "type": "string",
                        "description": "Outgoing track filename"
                    },
                    "filename2": {
                        "type": "string",
                        "description": "Incoming track filename"
                    },
                    "blend_bars": {
                        "type": "integer",
                        "description": "Desired blend length in bars (default: 32)",
                        "default": 32
                    }
                },
                "required": ["filename1", "filename2"]
            }
        ),
        Tool(
            name="analyze_library_track",
            description=(
                "Full analysis combining Traktor collection.nml data with librosa audio analysis. "
                "Returns all Traktor fields plus librosa BPM cross-check, energy envelope summary, "
                "detected breakdown position, and agreement flags. Slower than get_track_info "
                "because it loads and analyses the audio file."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "filename": {
                        "type": "string",
                        "description": "Track filename, e.g. 'Dreams.m4a'"
                    },
                    "audio_path": {
                        "type": "string",
                        "description": "Absolute path to audio file"
                    }
                },
                "required": ["filename", "audio_path"]
            }
        ),
    ]


# ──────────────────────────────────────────────────────────────────────────── #
# Tool dispatch                                                                 #
# ──────────────────────────────────────────────────────────────────────────── #

@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    try:
        if name == "get_track_info":
            return await _get_track_info(arguments["filename"])

        elif name == "suggest_cue_points":
            return await _suggest_cue_points(
                filename=arguments["filename"],
                audio_path=arguments.get("audio_path"),
                overwrite=arguments.get("overwrite", False),
            )

        elif name == "write_cue_points":
            return await _write_cue_points(
                filename=arguments["filename"],
                cue_points=arguments["cue_points"],
                overwrite=arguments.get("overwrite", False),
            )

        elif name == "suggest_transition":
            return await _suggest_transition(
                filename1=arguments["filename1"],
                filename2=arguments["filename2"],
                blend_bars=arguments.get("blend_bars", 32),
            )

        elif name == "analyze_library_track":
            return await _analyze_library_track(
                filename=arguments["filename"],
                audio_path=arguments["audio_path"],
            )

        else:
            raise ValueError(f"Unknown tool: {name}")

    except Exception as e:
        logger.error(f"Error in {name}: {e}", exc_info=True)
        return [TextContent(type="text", text=f"Error: {e}")]


# ──────────────────────────────────────────────────────────────────────────── #
# Tool implementations                                                          #
# ──────────────────────────────────────────────────────────────────────────── #

async def _get_track_info(filename: str) -> list[TextContent]:
    """Read all Traktor analysis data for a track from collection.nml."""
    reader = get_nml_reader()
    data = reader.get_track_data(filename)

    if data is None:
        return [TextContent(type="text", text=(
            f"Track not found in collection.nml: {filename!r}\n"
            "Make sure the filename matches exactly as stored in Traktor "
            "(e.g. 'Dreams.m4a', not a full path)."
        ))]

    dur_s = (data["duration_ms"] / 1000.0) if data["duration_ms"] else None
    anchor_s = (data["anchor_ms"] / 1000.0) if data["anchor_ms"] else None
    grid_status = "✓ beatgrid present" if data["has_grid"] else "✗ no beatgrid — analyse in Traktor first"

    cues_text = ""
    if data["existing_cues"]:
        cues_text = "\nExisting cue points:\n"
        for cue in sorted(data["existing_cues"], key=lambda c: c.get("hotcue", -1)):
            hc = cue["hotcue"]
            slot_str = f"Slot {hc}" if hc >= 0 else "(no hotcue)"
            t_s = cue["start_ms"] / 1000.0
            mins, secs = divmod(t_s, 60)
            loop_note = f"  [loop {cue['len_ms']/1000:.1f}s]" if cue.get("len_ms", 0) > 0 else ""
            cues_text += f"  {slot_str}: {int(mins)}:{secs:05.2f}  {cue['name']}{loop_note}\n"
    else:
        cues_text = "\nNo cue points set.\n"

    result = f"""Track Info: {filename}

Traktor Analysis (from collection.nml):
  BPM:         {data['bpm']:.3f if data['bpm'] else 'unknown'}
  Key:         {data['key_camelot'] or 'unknown'}  ({data['key_name'] or '—'})
  Duration:    {f"{int(dur_s//60)}:{dur_s%60:05.2f}" if dur_s else 'unknown'}
  Beatgrid:    {grid_status}
  Anchor:      {f"{anchor_s:.3f}s" if anchor_s else 'none'}

Loudness / Auto-gain:
  Peak:        {f"{data['peak_db']:.2f} dB" if data['peak_db'] is not None else 'unknown'}
  Perceived:   {f"{data['perceived_db']:.2f} dB" if data['perceived_db'] is not None else 'unknown'}
  Analyzed:    {f"{data['analyzed_db']:.2f} dB" if data['analyzed_db'] is not None else 'unknown'}
{cues_text}"""

    return [TextContent(type="text", text=result)]


async def _suggest_cue_points(
    filename: str,
    audio_path: str | None,
    overwrite: bool,
) -> list[TextContent]:
    """Calculate bar-snapped cue positions and write them to collection.nml."""
    reader = get_nml_reader()
    data = reader.get_track_data(filename)

    if data is None:
        return [TextContent(type="text", text=f"Track not found in collection.nml: {filename!r}")]

    if not data["has_grid"]:
        return [TextContent(type="text", text=(
            f"Track {filename!r} has no beatgrid in Traktor.\n"
            "Open Traktor, load the track, and analyse it first (tick the Analyse box)."
        ))]

    track = TraktorTrack.from_nml_data(data)

    # Optional librosa enhancement
    if audio_path:
        try:
            logger.info(f"Loading librosa analysis for {filename}")
            await asyncio.get_event_loop().run_in_executor(
                None, track.load_librosa_analysis, audio_path
            )
        except Exception as e:
            logger.warning(f"Librosa analysis failed, continuing NML-only: {e}")

    # Calculate positions
    positions = track.suggest_cue_positions()

    # Convert to cue specs (skip occupied unless overwrite)
    specs = track.to_cue_specs(positions, overwrite=overwrite)

    result_lines = [
        f"Cue Points: {filename}",
        f"Source: {positions['source']}",
        f"BPM: {track.bpm:.3f}  |  Anchor: {track.anchor_ms:.1f}ms  |  Duration: {track.duration_ms/1000:.1f}s",
        "",
        "Calculated positions (bar-snapped):",
        f"  Slot 2  Beat:      {positions['beat_ms']/1000:.2f}s  ({_ms_to_mmss(positions['beat_ms'])})",
        f"  Slot 3  Breakdown: {positions['breakdown_ms']/1000:.2f}s  ({_ms_to_mmss(positions['breakdown_ms'])})",
        f"  Slot 4  Groove:    {positions['groove_ms']/1000:.2f}s  ({_ms_to_mmss(positions['groove_ms'])})  [loop {positions['groove_len_ms']/1000:.1f}s]",
        f"  Slot 5  End:       {positions['end_ms']/1000:.2f}s  ({_ms_to_mmss(positions['end_ms'])})",
        "",
    ]

    for flag in positions["flags"]:
        result_lines.append(f"  📋 {flag}")

    if not specs:
        result_lines += [
            "",
            "⚠️  All slots already occupied — nothing written.",
            "Use overwrite=true to replace existing cues in slots 2-5.",
        ]
        return [TextContent(type="text", text="\n".join(result_lines))]

    # Write to NML
    try:
        write_result = reader.write_cues(filename, specs, overwrite=overwrite)
        result_lines += [
            "",
            f"✅ Written to collection.nml (backup: {write_result['backup'].name}):",
        ]
        for line in write_result["written"]:
            result_lines.append(f"   {line}")
        if write_result["skipped"]:
            result_lines.append("")
            for line in write_result["skipped"]:
                result_lines.append(f"   ⚠️  {line}")
        result_lines.append("")
        result_lines.append("⚠️  Restart Traktor to load the updated collection.")
    except Exception as e:
        result_lines += ["", f"❌ Failed to write to NML: {e}"]

    return [TextContent(type="text", text="\n".join(result_lines))]


async def _write_cue_points(
    filename: str,
    cue_points: list[dict],
    overwrite: bool,
) -> list[TextContent]:
    """Write manually specified cue positions to collection.nml."""
    reader = get_nml_reader()

    # Validate track exists
    if reader.get_track_data(filename) is None:
        return [TextContent(type="text", text=f"Track not found in collection.nml: {filename!r}")]

    # Map input to internal spec format
    specs = []
    for cp in cue_points:
        specs.append({
            "slot":     cp["slot"],
            "name":     cp.get("name", "n.n."),
            "start_ms": float(cp["time_ms"]),
            "type":     int(cp.get("type", 0)),
            "len_ms":   float(cp.get("len_ms", 0.0)),
        })

    try:
        result = reader.write_cues(filename, specs, overwrite=overwrite)
    except Exception as e:
        return [TextContent(type="text", text=f"❌ Failed to write cues: {e}")]

    lines = [f"Write Cue Points: {filename}", ""]
    if result["written"]:
        lines.append(f"✅ Written (backup: {result['backup'].name}):")
        for line in result["written"]:
            lines.append(f"   {line}")
    if result["skipped"]:
        lines.append("")
        for line in result["skipped"]:
            lines.append(f"   ⚠️  {line}")
    if result["written"]:
        lines += ["", "⚠️  Restart Traktor to load the updated collection."]

    return [TextContent(type="text", text="\n".join(lines))]


async def _suggest_transition(
    filename1: str,
    filename2: str,
    blend_bars: int,
) -> list[TextContent]:
    """Suggest a transition between two tracks using Traktor NML data."""
    reader = get_nml_reader()

    data1 = reader.get_track_data(filename1)
    data2 = reader.get_track_data(filename2)

    missing = []
    if data1 is None: missing.append(filename1)
    if data2 is None: missing.append(filename2)
    if missing:
        return [TextContent(type="text", text=f"Not found in collection.nml: {', '.join(missing)}")]

    bpm1 = data1.get("bpm")
    bpm2 = data2.get("bpm")
    key1 = data1.get("key_camelot")
    key2 = data2.get("key_camelot")
    dur1 = data1.get("duration_ms")
    dur2 = data2.get("duration_ms")

    lines = [
        "Transition Analysis",
        "=" * 50,
        "",
        f"Outgoing: {filename1}",
        f"  BPM: {bpm1:.3f if bpm1 else 'unknown'}  |  Key: {key1 or 'unknown'} ({data1.get('key_name') or '—'})  |  Duration: {_ms_to_mmss(dur1) if dur1 else 'unknown'}",
        "",
        f"Incoming: {filename2}",
        f"  BPM: {bpm2:.3f if bpm2 else 'unknown'}  |  Key: {key2 or 'unknown'} ({data2.get('key_name') or '—'})  |  Duration: {_ms_to_mmss(dur2) if dur2 else 'unknown'}",
        "",
    ]

    # BPM compatibility
    if bpm1 and bpm2:
        ratio = bpm1 / bpm2
        if 0.97 <= ratio <= 1.03:
            bpm_verdict = f"✓ Direct beatmatch  (ratio {ratio:.3f})"
            bpm_adj = f"Adjust by {abs(bpm1 - bpm2):.1f} BPM"
        elif 1.94 <= ratio <= 2.06:
            bpm_verdict = f"✓ 2:1 halftime mix  (ratio {ratio:.3f})"
            bpm_adj = "Play incoming at double time"
        elif 0.47 <= ratio <= 0.53:
            bpm_verdict = f"✓ 1:2 double-time mix  (ratio {ratio:.3f})"
            bpm_adj = "Play incoming at half time"
        else:
            bpm_verdict = f"✗ BPM mismatch  (ratio {ratio:.3f})"
            bpm_adj = f"Pitch track 2 to {bpm1:.1f} BPM for 1:1 mix"
        lines += [f"BPM:  {bpm_verdict}", f"      {bpm_adj}", ""]
    else:
        lines += ["BPM:  unknown — check Traktor analysis", ""]

    # Key compatibility
    key_compat, key_desc = camelot_compatible(key1 or "", key2 or "")
    key_icon = "✓" if key_compat else "✗"
    lines += [f"Key:  {key_icon} {key_desc}", ""]

    # Transition timing
    if bpm1 and dur1 and bpm2:
        blend_ms = bars_to_ms(blend_bars, bpm1)
        mixout_ms = dur1 - blend_ms
        mixout_s = mixout_ms / 1000.0
        blend_s = blend_ms / 1000.0

        lines += [
            f"Timing ({blend_bars}-bar blend at {bpm1:.1f} BPM = {blend_s:.0f}s):",
            f"  Start blend at:   {_ms_to_mmss(mixout_ms)} into outgoing track",
            f"  Incoming starts:  from beginning",
            "",
            "Suggested technique:",
        ]

        if key_compat and bpm1 and bpm2 and 0.97 <= bpm1/bpm2 <= 1.03:
            lines += [
                "  1. At blend start, bring incoming up under the outgoing bass",
                f"  2. Over {blend_s/2:.0f}s: cut bass on outgoing, add bass on incoming",
                "  3. Use mid-EQ swell to mask the transition",
                "  4. Trim outgoing highs as incoming establishes",
            ]
        elif not key_compat:
            lines += [
                "  ⚠️  Keys are incompatible — consider a short blend or effects mask",
                "  1. Use reverb/delay throw on outgoing before cut",
                "  2. Drop to drums-only then bring in incoming",
                "  3. Keep blend under 16 bars to reduce key clash",
            ]
        else:
            lines += [
                "  1. Match energy levels before blend (check gain/perceived dB)",
                f"  2. Blend over {blend_s:.0f}s with gradual EQ swap",
                "  3. Layer atmospheric elements during crossover",
            ]

        # Gain match advisory
        p1 = data1.get("perceived_db")
        p2 = data2.get("perceived_db")
        if p1 is not None and p2 is not None:
            gain_diff = abs(p1 - p2)
            lines.append("")
            if gain_diff > 3.0:
                lines.append(f"  ⚠️  Loudness difference: {gain_diff:.1f} dB — adjust trim before blend")
            else:
                lines.append(f"  ✓ Loudness match: {gain_diff:.1f} dB difference (acceptable)")
    else:
        lines.append("Timing: BPM/duration missing — analyse tracks in Traktor first")

    return [TextContent(type="text", text="\n".join(lines))]


async def _analyze_library_track(filename: str, audio_path: str) -> list[TextContent]:
    """Full analysis: Traktor NML data + librosa cross-check."""
    reader = get_nml_reader()
    data = reader.get_track_data(filename)

    if data is None:
        return [TextContent(type="text", text=f"Track not found in collection.nml: {filename!r}")]

    track = TraktorTrack.from_nml_data(data)

    # Run librosa
    librosa_error = None
    try:
        await asyncio.get_event_loop().run_in_executor(
            None, track.load_librosa_analysis, audio_path
        )
    except Exception as e:
        librosa_error = str(e)

    dur_s = track.duration_s or 0.0
    lines = [
        f"Full Analysis: {filename}",
        "=" * 60,
        "",
        "── Traktor (collection.nml) ──────────────────────────────",
        f"  BPM:       {track.bpm:.3f if track.bpm else 'unknown'}",
        f"  Key:       {track.key_camelot or 'unknown'}  ({track.key_name or '—'})",
        f"  Duration:  {int(dur_s//60)}:{dur_s%60:05.2f}",
        f"  Beatgrid:  {'✓ present' if track.has_grid else '✗ missing'}",
        f"  Anchor:    {f'{track.anchor_ms:.1f}ms' if track.anchor_ms else 'none'}",
        f"  Peak dB:   {f'{track.peak_db:.2f}' if track.peak_db is not None else 'unknown'}",
        f"  Perceived: {f'{track.perceived_db:.2f} dB' if track.perceived_db is not None else 'unknown'}",
        "",
    ]

    if librosa_error:
        lines += [
            "── librosa ──────────────────────────────────────────────",
            f"  ❌ Analysis failed: {librosa_error}",
            "",
        ]
    else:
        bpm_check = "✓ agree" if track.bpm_verified() else f"⚠️  mismatch (librosa: {track.librosa_bpm:.1f})"
        lines += [
            "── librosa ──────────────────────────────────────────────",
            f"  BPM:       {track.librosa_bpm:.1f if track.librosa_bpm else 'unknown'}  {bpm_check}",
            f"  Beats:     {len(track.beat_times) if track.beat_times else 0} detected",
            f"  Breakdown: {f'{track.breakdown_ms/1000:.1f}s detected by energy analysis' if track.breakdown_ms else 'not detected'}",
            "",
        ]

    if track.has_grid and track.bpm and track.librosa_loaded:
        try:
            positions = track.suggest_cue_positions()
            lines += [
                "── Suggested cue positions ───────────────────────────────",
                f"  Slot 2  Beat:      {_ms_to_mmss(positions['beat_ms'])}",
                f"  Slot 3  Breakdown: {_ms_to_mmss(positions['breakdown_ms'])}",
                f"  Slot 4  Groove:    {_ms_to_mmss(positions['groove_ms'])}  [loop {positions['groove_len_ms']/1000:.0f}s]",
                f"  Slot 5  End:       {_ms_to_mmss(positions['end_ms'])}",
                f"  Source: {positions['source']}",
                "",
            ]
            for flag in positions["flags"]:
                lines.append(f"  📋 {flag}")
        except Exception as e:
            lines.append(f"  Cue calculation failed: {e}")

    return [TextContent(type="text", text="\n".join(lines))]


# ──────────────────────────────────────────────────────────────────────────── #
# Utilities                                                                     #
# ──────────────────────────────────────────────────────────────────────────── #

def _ms_to_mmss(ms: float | None) -> str:
    if ms is None:
        return "unknown"
    s = ms / 1000.0
    mins = int(s // 60)
    secs = s % 60
    return f"{mins}:{secs:05.2f}"


# ──────────────────────────────────────────────────────────────────────────── #
# Entry point                                                                   #
# ──────────────────────────────────────────────────────────────────────────── #

async def main():
    logger.info("Starting AI DJ MCP Server v0.2.0 (Traktor-first)")
    from mcp.server.stdio import stdio_server
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
