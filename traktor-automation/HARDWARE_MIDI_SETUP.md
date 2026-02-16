# HARDWARE MIDI SETUP - X1 MK2 + Z1 INTEGRATION

This guide configures the Traktor AI DJ to work with your hardware controllers:
- **Kontrol X1 mk2** - Deck control, transport, loop, FX
- **Kontrol Z1** - Mixer, crossfader, EQ, filters

## Architecture

```
Python AI DJ ──MIDI──> IAC Driver ──> Traktor Pro 3
                                         ↑ ↓
                        ┌────────────────┴─┴────────────────┐
                        │                                    │
                   X1 mk2 (USB)                         Z1 (USB)
                   - Deck control                       - Crossfader
                   - Transport                          - EQ/Filters
                   - Loop/FX                            - Cue Mix
                   - Manual override                    - Manual mix
```

## Why This Approach?

1. **IAC Driver** - Python automation sends commands
2. **X1 mk2 Native Mode** - Manual override, visual feedback via LEDs
3. **Z1 Native Mode** - Manual mixing control, audio interface
4. **All three can control Traktor simultaneously**

## STEP 1: Understanding Controller Modes

### X1 mk2 Button Combination

**To switch X1 mk2 to/from MIDI mode:**
- Press and hold **SHIFT + both left and right LOAD buttons** (the arrow buttons)
- LEDs will dim to indicate MIDI mode is active
- Press the same combination again to return to Native mode

### Z1 Button Combination (Original Z1)

**To switch Z1 to/from MIDI mode:**
- Press and hold **MODE + both left and right CUE buttons** (A and B)
- Display will show MIDI indicator
- Press the same combination again to return to Native mode

### Z1 mk2 Button Combination

**To switch Z1 mk2 to/from MIDI mode:**
- Press **--- button + ☰ button** together
- Center display will show "MIDI MODE"
- Press the same combination again to return to Native mode

---

## RECOMMENDED CONFIGURATION

⚠️ **Keep both controllers in NATIVE MODE** for best results!

### Native Mode Benefits:
- ✅ LED feedback (track position, loop status, FX status)
- ✅ Button lights that respond to Traktor state
- ✅ Pre-mapped controls that "just work"
- ✅ Can coexist with IAC Driver automation
- ✅ Z1 acts as audio interface
- ✅ X1 mk2 displays show track info

### MIDI Mode Use Cases:
- Only needed if controlling non-Traktor software
- Or if you need completely custom mappings
- **Not recommended for this AI DJ setup**

**Recommendation: Keep X1 mk2 AND Z1 in Native Mode**

## STEP 2: Traktor Controller Setup

### In Traktor Preferences → Controller Manager:

You should have **THREE** devices:

#### Device 1: Traktor Kontrol X1 mk2 (Native)
- **Device Type:** Traktor Kontrol X1 mk2
- **In-Port:** Traktor Kontrol X1 Mk2 Input
- **Out-Port:** Traktor Kontrol X1 Mk2 Output
- **Deck Assignment:**
  - Left side → Deck A
  - Right side → Deck B
- ✅ **Active**

#### Device 2: Traktor Kontrol Z1 (Native)
- **Device Type:** Traktor Kontrol Z1
- **In-Port:** Traktor Kontrol Z1 Input
- **Out-Port:** Traktor Kontrol Z1 Output
- **Deck Assignment:** A+B
- ✅ **Active**

#### Device 3: Generic MIDI (AI DJ Automation)
- **Device Type:** Generic MIDI
- **In-Port:** IAC Driver Bus 1
- **Out-Port:** IAC Driver Bus 1
- **Custom Mapping:** See TRAKTOR_MIDI_MAPPING_GUIDE.md
- ✅ **Active**

## STEP 3: Audio Routing with Z1

The Z1 can act as your audio interface:

1. **Traktor Preferences → Audio Setup**
2. **Audio Device:** Traktor Kontrol Z1
3. **Output Routing:**
   - Master: Traktor Kontrol Z1 (Main Out)
   - Monitor: Traktor Kontrol Z1 (Cue Out)
4. **Channel Setup:** Dual (Stereo)

## STEP 4: Control Priority

With all three devices active, control priority is:

1. **Manual controls override automation**
   - If you move Z1 crossfader manually → your position wins
   - If Python sends crossfader command → it moves unless you're touching it

2. **X1 mk2 transport controls**
   - You can manually Play/Pause/Cue
   - AI DJ automation respects manual state

3. **Soft takeover** (optional)
   - Enable in Traktor to prevent jumps when automation takes over

## STEP 5: Hybrid Control Modes

### Mode 1: Full Automation
- Python AI DJ handles everything
- X1 mk2 shows status via LEDs
- Z1 available for manual tweaks

### Mode 2: Semi-Automatic
- Python AI DJ selects and loads tracks
- You manually control crossfader on Z1
- X1 mk2 for manual cue/loop/FX

### Mode 3: Manual Override
- Touch any control to override AI
- AI resumes when you release
- Perfect for live tweaking

## STEP 6: Python Code Modifications

Your current code should work as-is, but you can add Z1 awareness:

### Monitor Z1 Crossfader Position

Add to `traktor_ai_dj.py`:

```python
# MIDI CC for Z1 crossfader feedback
self.MIDI_CC['z1_crossfader_position'] = 50  # Check actual Z1 CC#

def _handle_midi_input(self, message: Message):
    """Handle incoming MIDI messages."""
    if message.type == 'control_change':
        cc = message.control
        value = message.value

        # Detect manual Z1 crossfader override
        if cc == self.MIDI_CC.get('z1_crossfader_position'):
            self.manual_override_active = True
            self.log(f"🎚️ Manual crossfader override: {value}")
```

### Disable Automation During Manual Control

```python
def execute_crossfade(self, duration: float, from_deck: int, to_deck: int):
    """Execute automated crossfade (respects manual override)."""
    if self.manual_override_active:
        self.log("⏸️ Manual override active - skipping auto crossfade")
        return

    # ... existing crossfade code ...
```

## STEP 7: Testing

### Test 1: Hardware + Automation Coexistence

1. **Start Python AI DJ:**
   ```bash
   python3 traktor_ai_dj.py
   ```

2. **Watch X1 mk2:**
   - LEDs should respond to playback
   - Deck A/B buttons should light up

3. **Move Z1 crossfader:**
   - Should move smoothly
   - Python should detect override (if implemented)

4. **Press X1 mk2 Play:**
   - Should start/stop playback
   - Overrides Python play command

### Test 2: Verify All Three MIDI Sources

Run MIDI monitor to see all three devices:
```bash
python3 << 'EOF'
import mido

print("Available MIDI Inputs:")
for port_name in mido.get_input_names():
    print(f"  - {port_name}")

print("\nListening to all MIDI inputs (move X1/Z1 controls)...")
print("Press Ctrl+C to stop\n")

ports = [mido.open_input(name) for name in mido.get_input_names()]

for msg in mido.ports.MultiPort(ports):
    print(msg)
EOF
```

**Expected output when you:**
- Move Z1 crossfader → See CC message from Z1
- Press X1 button → See message from X1
- Python sends command → See message from IAC Driver

## TROUBLESHOOTING

### X1 mk2 LEDs Not Working
- ✅ Make sure X1 is in **Native Mode** (not MIDI mode)
- ✅ Out-Port must be set to X1 mk2 Output
- ✅ Check USB cable is firmly connected

### Z1 Crossfader Not Responding
- ✅ Check Z1 is in **Internal** mode (not MIDI mode)
- ✅ Audio interface is set to Z1
- ✅ Z1 driver is up to date

### Automation Conflicts with Manual Control
- ✅ Implement manual override detection (see Step 6)
- ✅ Enable soft takeover in Traktor preferences
- ✅ Reduce Python command frequency during manual use

### Some Commands Work, Others Don't

This is likely a **mapping issue** in Generic MIDI device:

1. **Open Traktor → Preferences → Controller Manager**
2. **Select "Generic MIDI" (IAC Driver)**
3. **Verify each mapping:**
   - ✅ Correct CC numbers
   - ✅ Correct channel (Ch01)
   - ✅ Correct interaction mode (Toggle vs Direct)
   - ✅ Correct assignment (Deck A vs Deck B)

**Run the mapping verification tests:**
```bash
cd "/Users/dantaylor/Claude/Last Night an AI Saved My Life/traktor-automation"
# See MAPPING_VERIFICATION_CHECKLIST.md for test commands
```

## RECOMMENDED WORKFLOW

1. **Let AI DJ handle track selection and loading**
2. **Let AI DJ handle basic timing and transitions**
3. **Manually control Z1 crossfader for feel**
4. **Use X1 mk2 for:**
   - Manual cue points
   - Loop controls
   - FX on/off
   - Emergency play/pause

This gives you **automation + human feel** 🎧

---

## Quick Reference: What Controls What

| Task | Controlled By |
|------|---------------|
| Track Selection | Python AI DJ |
| Track Loading | Python AI DJ |
| Play/Pause | Python AI DJ (can override with X1) |
| Beatmatching | Traktor Sync (triggered by Python) |
| Crossfading | Python AI DJ or Z1 manual |
| EQ/Filters | Z1 manual |
| Loops/Cues | X1 mk2 manual |
| FX | X1 mk2 manual |
| Monitoring | Z1 cue mix |

---

**Next Steps:**
1. Verify all three devices show up in Controller Manager
2. Run mapping verification tests
3. Test hybrid control (automation + manual)
