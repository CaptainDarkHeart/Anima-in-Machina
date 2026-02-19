# AI DJ MCP Server — Quick Reference

## Tool summary

| Tool | When to use | Required params |
|------|-------------|-----------------|
| `get_track_info` | Check BPM, key, cues for a track | `filename` |
| `suggest_cue_points` | Auto-calculate and write 4 cues | `filename` |
| `suggest_cue_points` + audio | Same but with librosa breakdown detection | `filename`, `audio_path` |
| `write_cue_points` | Write specific positions manually | `filename`, `cue_points[]` |
| `suggest_transition` | Plan mix between two tracks | `filename1`, `filename2` |
| `analyze_library_track` | Full NML + librosa analysis | `filename`, `audio_path` |

---

## Common prompts

### Get track info (fast)
```
Get track info for "Stimming - Una Pena.m4a"
```

### Write cue points (NML only)
```
Suggest cue points for "Stimming - Una Pena.m4a"
```

### Write cue points (with librosa breakdown detection)
```
Suggest cue points for "Stimming - Una Pena.m4a" using
/Users/dantaylor/Music/Stimming - Una Pena.m4a
```

### Overwrite existing cues
```
Suggest cue points for "Stimming - Una Pena.m4a" and overwrite existing
```

### Plan a transition
```
Suggest transition from "Track A.m4a" to "Track B.m4a"
```

### Full deep analysis
```
Analyze "Stimming - Una Pena.m4a" at
/Users/dantaylor/Music/Stimming - Una Pena.m4a
```

### Manually set a specific cue
```
Write a cue point for "Stimming - Una Pena.m4a":
  slot 3, name "Breakdown", time 245100ms
```

---

## Cue slots

| Slot | Name | Position | Type |
|------|------|----------|------|
| 1 | (protected) | — | — |
| 2 | Beat | ~10% | Hot cue |
| 3 | Breakdown | ~65% (or detected) | Hot cue |
| 4 | Groove | ~35% | 32-bar loop |
| 5 | End | ~32 bars before end | Hot cue |

---

## Filename format

Always use the bare filename as stored in Traktor, not a full path or display title:

```
"Dreams.m4a"                        ✓
"02 Dreams.m4a"                     ✓ (if that's how it's stored)
"/Users/dantaylor/Music/Dreams.m4a" ✗ (full path — won't match)
"Dreams"                            ✗ (no extension)
```

---

## After writing cues

**Restart Traktor** — it only reads collection.nml at startup.

A backup is saved automatically at:
```
~/Documents/Native Instruments/Traktor 3.11.1/collection_backup_YYYYMMDD_HHMMSS.nml
```

---

## Camelot key compatibility

`suggest_transition` reports key compatibility using the Camelot wheel:
- **Same key** — perfect match
- **Same number, m↔d** — relative key (e.g. 8m ↔ 8d)
- **Adjacent ±1 same mode** — energy shift mix
- **Anything else** — incompatible (consider short blend or effects mask)

---

## BPM compatibility

| Ratio | Result |
|-------|--------|
| 0.97–1.03 | Direct beatmatch |
| 1.94–2.06 | 2:1 halftime |
| 0.47–0.53 | 1:2 double-time |
| Outside above | BPM mismatch |

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| Track not found | Check exact filename (grep collection.nml) |
| No beatgrid | Analyse track in Traktor first |
| Cues not showing in Traktor | Restart Traktor |
| All slots occupied | Use `overwrite=true` |
| librosa fails | Pass absolute audio path; check file exists |
