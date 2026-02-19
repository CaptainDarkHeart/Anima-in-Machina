<div align="center">
  <img src="assets/logo.png" alt="Anima-in-Machina">
</div>

# Anima-in-Machina

A knowledge base and automation system for deep space house DJing, created through collaboration between a human DJ and AI. Contains detailed track analysis, mixing techniques, label guides, technical workflows, and working Python automation for Traktor Pro 3.

> **[Read the full project context and background →](CONTEXT.md)**

---

## Repository Structure

```
Anima-in-Machina/
├── docs/                        # Knowledge base (music, labels, techniques)
├── ai-dj-mcp-server/            # MCP server — Claude reads/writes Traktor NML
├── traktor-automation/          # Python MIDI automation for live performance
├── track-selection-engine/      # Playlist generation tools and data
└── analysis/                    # Stripes/transient analysis outputs
```

---

## What's Inside

### Project Context
- **[CONTEXT.md](CONTEXT.md)** - Complete background on the project, Dan's 11,000+ track collection, workflow evolution, and human-AI collaboration model

### Music Library
- **[Best of Deep Dub Tech House - Complete Analysis](docs/dj-reference/Best_of_Deep_Dub_Tech_House_FINAL.md)** - Deep dive into a 30-track collection with BPM corrections, key relationships, mixing strategies, and pre-planned journey arcs
- **[Detailed Music List](docs/music-library/Detailed_Music_List.md)** - 11,000+ track collection organized by BPM and genre
- **[Music Library Clean](docs/music-library/Music_Library_Clean.md)** - Organized music collection management

### DJ Reference Guides
- **[Label Guide](docs/dj-reference/LABEL_GUIDE.md)** - Detailed profiles of core deep space house labels (Lucidflow, Echocord, Styrax, Plastic City, and more) with mixing compatibility matrices
- **[Artist Profiles](docs/dj-reference/ARTIST_PROFILES.md)** - In-depth artist information and signature sounds
- **[Texture Reference](docs/dj-reference/TEXTURE_REFERENCE.md)** - Sound design and textural elements guide
- **[Transition Techniques](docs/dj-reference/TRANSITION_TECHNIQUES.md)** - Detailed methods for smooth, atmospheric transitions
- **[Example Journey Arcs](docs/dj-reference/EXAMPLE_JOURNEY_ARCS.md)** - Sample set structures from ambient openings to peak moments

### Technical Documentation
- **[Traktor Setup Guide](docs/technical/TRAKTOR_SETUP_GUIDE.md)** - Complete Traktor Pro configuration optimized for extended blends, effect routing, cue point systems, and loop management
- **[Traktor Automation Analysis](docs/technical/TRAKTOR_AUTOMATION_ANALYSIS.md)** - Advanced workflow automation strategies
- **[AI DJ MCP Server Overview](docs/technical/AI_DJ_MCP_SERVER_OVERVIEW.md)** - Model Context Protocol integration for AI-powered DJ assistance
- **[Track Selection Engine](docs/technical/LAYER_3_COMPLETE.md)** - Intelligent playlist generation using deep space house philosophy

### Templates
- **[Tracklist Template](docs/templates/TRACKLIST_TEMPLATE.md)** - Standardized format for documenting DJ sets
- **[Loop Library Template](docs/templates/LOOP_LIBRARY_TEMPLATE.md)** - Framework for cataloging loop-worthy sections

---

## AI DJ MCP Server (`ai-dj-mcp-server/`)

An MCP server that lets Claude read Traktor's analysis and write cue points directly to `collection.nml`. Traktor's own beatgrid is the primary data source — no re-deriving BPM from audio.

**Five tools:**

| Tool | What it does |
|------|-------------|
| `get_track_info` | Read BPM, key, cues from NML — fast, no audio |
| `suggest_cue_points` | Calculate bar-snapped Beat/Groove/Breakdown/End cues and write to NML |
| `write_cue_points` | Write manually specified positions to NML |
| `suggest_transition` | BPM + Camelot key compatibility and EQ strategy |
| `analyze_library_track` | Full NML + librosa analysis (read-only) |

**Example:** "Suggest cue points for 'Stimming - Una Pena.m4a'" → Claude calculates positions from Traktor's beatgrid, writes to `collection.nml`, reminds you to restart Traktor.

See **[ai-dj-mcp-server/README.md](ai-dj-mcp-server/README.md)** for installation and full documentation.

---

## Traktor Automation (`traktor-automation/`)

Python automation for live performance via IAC Driver MIDI. Runs the full mix — crossfades, EQ bass swaps, track loading — with coexistence support for X1 mk2 and Z1 hardware controllers.

**Key files:**

| File | Purpose |
|------|---------|
| `traktor_ai_dj.py` | Main controller: MIDI automation, crossfader, EQ bass swap, soft-takeover |
| `intelligent_dj.py` | Subclass using structured mix plan data for intelligent transitions |
| `deep_house_cue_writer.py` | CLI cue writer — NML-only, no audio analysis required |
| `diagnose_nml.py` / `check_dir_entries.py` | NML inspection utilities |
| `strip_old_cues.py` | Remove stripes-generated cues that clutter waveforms |

**Z1 soft-takeover:** grabbing any Z1 EQ knob mid-transition pauses automation on that band only — everything else keeps moving.

See **[traktor-automation/README.md](traktor-automation/README.md)** for the full MIDI CC table, setup instructions, and hardware guide.

---

## Track Selection Engine (`track-selection-engine/`)

Playlist generation tools and data files for the Best of Deep Dub Tech House set.

- `best-of-deep-dub-tech-house-ai-ordered.json` — AI-ordered 30-track playlist with full metadata
- `best-of-deep-dub-tech-house-ai-ordered.m3u` — Traktor-importable playlist
- Python scripts for custom playlist generation from the full library

---

## Philosophy

This knowledge base treats DJing as a craft that combines:

- **Technical precision** — BPM management, harmonic mixing, and equipment mastery
- **Artistic vision** — Journey arc design and emotional flow
- **Deep musical understanding** — Label aesthetics, artist signatures, and genre evolution
- **Performance preparation** — Systematic cue points, effects routing, and backup strategies

The focus is on **deep space house**: patient, hypnotic electronic music that emphasises extended blends (60-90+ seconds), dub-influenced atmospheres, gradual energy development, and journey-focused set structures.

---

## Key Features

### BPM Corrections & Verification
Track analysis includes corrected BPM data verified against Beatport, fixing common half-time detection errors.

### Harmonic Mixing Strategies
Detailed key relationships with specific mixing chains for 90+ minute journeys.

### Effect Routing Systems
Three-bank effect setups in Traktor with specific use cases: atmospheric blending, textural enhancement, emergency utilities.

### Color-Coded Cue Points
Blue (load), green (mix-in), yellow (structure), orange (loops), red (mix-out), purple (creative).

### NML-First Cue Automation
Cue positions are bar-snapped to Traktor's own beatgrid — accurate to the millisecond, no guessing from audio waveforms. Available both via the MCP server (Claude) and the standalone `deep_house_cue_writer.py` CLI.

---

## How to Use This Repository

### For DJs
1. Start with the [Label Guide](docs/dj-reference/LABEL_GUIDE.md) to understand the deep space house ecosystem
2. Review the [Traktor Setup Guide](docs/technical/TRAKTOR_SETUP_GUIDE.md) to optimise your technical workflow
3. Study the [Best of Deep Dub Tech House Analysis](docs/dj-reference/Best_of_Deep_Dub_Tech_House_FINAL.md) for detailed track preparation
4. Use the [Transition Techniques](docs/dj-reference/TRANSITION_TECHNIQUES.md) to expand your mixing vocabulary

### For AI/ML Projects
This dataset represents:
- Systematic musical analysis (BPM, key, energy levels, textures)
- Relationship mapping (track compatibility, transition strategies)
- Domain knowledge codification (label aesthetics, artist signatures)
- Expert decision-making processes (set construction, track selection)
- Working MCP server + Python automation as reference implementations

---

## The Story Behind This Repository

The title "Anima-in-Machina" references the soul (anima) within the machine — where human artistry meets artificial intelligence.

This project emerged from Claude.ai sessions where Dan, a DJ with an 11,000+ track collection focused on deep house, tech house, progressive, and dub techno, collaborated with Claude to:
- Correct BPM detection errors in Traktor (half-time detection issues)
- Map out complex harmonic relationships and key-based mixing chains
- Document implicit mixing knowledge developed over years of performance
- Create systematic preparation workflows for 165-200 minute journey sets
- Build working automation: MIDI controller, cue writer, MCP server

---

## Collection Stats (Best of Deep Dub Tech House)

- **30 tracks** totalling 224 minutes (from an 11,000+ track library)
- **BPM range:** 83-131
- **Modal BPM:** 120 (6 tracks)
- **Dominant key:** A Minor (9 tracks — 30% of collection)
- **Average duration:** 7:28 per track
- **43% of tracks** exceed 8 minutes
- **Journey length**: Designed for 165-200 minute sets

---

## License

Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0).

---

## Acknowledgments

Created through collaboration between:
- **Dan Taylor** — DJ, curator, deep space house enthusiast with 11,000+ track collection
- **Claude (Anthropic)** — AI assistant for analysis, organisation, and knowledge synthesis

Core artists in the analysis: Riccicomoto (4 tracks), Klartraum (3 tracks), Nadja Lind, The Timewriter.
Core labels: Lucidflow Records, Echocord, Styrax, Plastic City, Smallville Records.

---

## Resources

- [Lucidflow Records](https://lucidflow.de)
- [Juno Download](https://www.junodownload.com)
- [Beatport](https://www.beatport.com)
- [Discogs](https://www.discogs.com)

---

*"The journey is the destination. The mix is the meditation. The beats are the breath."*

*Repository created February 2026*
