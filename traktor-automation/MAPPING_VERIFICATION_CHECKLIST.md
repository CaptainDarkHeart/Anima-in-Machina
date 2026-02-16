# TRAKTOR AI DJ - MIDI MAPPING VERIFICATION CHECKLIST

Use this checklist to verify your Traktor MIDI mappings are correct.

---

## ✅ REQUIRED MAPPINGS (14 Inputs)

Open Traktor → Preferences → Controller Manager → Generic MIDI (IAC Driver Bus 1)

Check that you have these **INPUT** mappings:

### Deck A Controls (5 mappings)
- [ ] **Play/Pause** - Ch01.CC.001 → Deck A → Play/Pause (Toggle)
- [ ] **Cue** - Ch01.CC.003 → Deck A → Cue (Toggle)
- [ ] **Sync** - Ch01.CC.005 → Deck A → Master Tempo (Toggle)
- [ ] **Load** - Ch01.CC.007 → Deck A → Load Selected (Toggle)
- [ ] **Tempo Reset** - Ch01.CC.030 → Deck A → Tempo Reset (Toggle)

### Deck B Controls (5 mappings)
- [ ] **Play/Pause** - Ch01.CC.002 → Deck B → Play/Pause (Toggle)
- [ ] **Cue** - Ch01.CC.004 → Deck B → Cue (Toggle)
- [ ] **Sync** - Ch01.CC.006 → Deck B → Master Tempo (Toggle)
- [ ] **Load** - Ch01.CC.008 → Deck B → Load Selected (Toggle)
- [ ] **Tempo Reset** - Ch01.CC.031 → Deck B → Tempo Reset (Toggle)

### Mixer Controls (1 mapping)
- [ ] **Crossfader** - Ch01.CC.010 → Mixer → X-Fader (Fader/Knob, Direct)

### Browser Controls (2 mappings)
- [ ] **Track Up** - Ch01.CC.020 → Browser → Select Up/Down (Button, Direct/Increment)
- [ ] **Track Down** - Ch01.CC.021 → Browser → Select Up/Down (Button, Direct/Decrement)

### Reserved for Future (1 mapping - optional)
- [ ] **Deck A Tempo Reset** - Ch01.CC.030 (if not already mapped)
- [ ] **Deck B Tempo Reset** - Ch01.CC.031 (if not already mapped)

---

## 📤 OPTIONAL OUTPUT MAPPINGS (4 outputs)

These are **nice to have** but not required for basic functionality:

- [ ] **Deck A Position** - Ch01.CC.040 ← Deck A → Playback Position (OUT)
- [ ] **Deck B Position** - Ch01.CC.041 ← Deck B → Playback Position (OUT)
- [ ] **Deck A Playing** - Ch01.CC.042 ← Deck A → Is Playing (OUT)
- [ ] **Deck B Playing** - Ch01.CC.043 ← Deck B → Is Playing (OUT)

**Note:** If you can't find output mappings, skip them. The AI DJ will work using time-based calculations instead.

---

## 🔍 COMMON ISSUES TO CHECK

### Issue 1: Wrong MIDI Channel
- ✅ **Correct:** All mappings use **Ch01** (MIDI Channel 1)
- ❌ **Wrong:** Mappings on Ch02, Ch03, etc.

**How to fix:** Edit each mapping and set channel to Ch01

### Issue 2: Wrong CC Numbers
Double-check the CC numbers match exactly:
- Deck A Play = CC 1 (not CC 01 or CC 001, just the number 1)
- Deck A Cue = CC 3
- Deck A Sync = CC 5
- etc.

### Issue 3: Wrong Interaction Mode
- **Buttons** (Play, Cue, Sync, Load): Use **Toggle** or **Direct**
- **Crossfader**: Use **Direct** (NOT Toggle!)
- **Crossfader Type**: Must be **Fader/Knob** (NOT Button!)

### Issue 4: Wrong Assignment
- Make sure **Deck A** controls are assigned to Deck A (not Deck Common or Deck B)
- Make sure **Deck B** controls are assigned to Deck B
- **Sync** should be assigned to **"Master Tempo"** (not just "Sync")
- **Load** should be **"Load Selected"** (from browser)

### Issue 5: IAC Driver Not Selected
- In Traktor Controller Manager
- Device must be **Generic MIDI**
- **In-Port:** IAC Driver Bus 1
- **Out-Port:** IAC Driver Bus 1

---

## 🧪 TESTING YOUR MAPPINGS

### Test 1: Manual MIDI Test
Run this in Terminal:
```bash
cd "/Users/dantaylor/Claude/Last Night an AI Saved My Life/traktor-automation"
python3 << 'EOF'
import mido
import time

output = mido.open_output("IAC Driver Bus 1")

print("Testing MIDI mappings...")
print("Watch Traktor - Deck A should start playing")

# Send Play command to Deck A (CC 1, value 127)
output.send(mido.Message('control_change', control=1, value=127, channel=0))
time.sleep(0.5)

print("If Deck A started playing, mappings are working!")
output.close()
EOF
```

**Expected:** Deck A in Traktor should start playing

### Test 2: Crossfader Test
```bash
python3 << 'EOF'
import mido
import time

output = mido.open_output("IAC Driver Bus 1")

print("Testing crossfader...")
print("Watch Traktor - crossfader should move from left to right")

# Move crossfader left to right
for i in range(0, 128, 10):
    output.send(mido.Message('control_change', control=10, value=i, channel=0))
    time.sleep(0.1)

print("Crossfader test complete!")
output.close()
EOF
```

**Expected:** Traktor's crossfader should smoothly move from left to right

---

## 📋 QUICK REFERENCE

| What | Channel | CC | Assignment | Type | Mode |
|------|---------|----|-----------|----- |------|
| Deck A Play | Ch01 | 1 | Deck A Play/Pause | Button | Toggle |
| Deck A Cue | Ch01 | 3 | Deck A Cue | Button | Toggle |
| Deck A Sync | Ch01 | 5 | Deck A Master Tempo | Button | Toggle |
| Deck A Load | Ch01 | 7 | Deck A Load Selected | Button | Toggle |
| Deck B Play | Ch01 | 2 | Deck B Play/Pause | Button | Toggle |
| Deck B Cue | Ch01 | 4 | Deck B Cue | Button | Toggle |
| Deck B Sync | Ch01 | 6 | Deck B Master Tempo | Button | Toggle |
| Deck B Load | Ch01 | 8 | Deck B Load Selected | Button | Toggle |
| Crossfader | Ch01 | 10 | Mixer X-Fader | Fader | Direct |
| Track Up | Ch01 | 20 | Browser Select Up/Down | Button | Direct |
| Track Down | Ch01 | 21 | Browser Select Up/Down | Button | Direct |
| Deck A Tempo | Ch01 | 30 | Deck A Tempo Reset | Button | Toggle |
| Deck B Tempo | Ch01 | 31 | Deck B Tempo Reset | Button | Toggle |

---

## ✅ VERIFICATION COMPLETE?

If all checkboxes are checked and tests pass, your mappings are correct!

**Next step:** Run the AI DJ
```bash
cd "/Users/dantaylor/Claude/Last Night an AI Saved My Life/traktor-automation"
python3 traktor_ai_dj.py
```

---

**Need help?** Check `TRAKTOR_MIDI_MAPPING_GUIDE.md` for detailed instructions.
