# TRAKTOR AI DJ - MIDI MAPPING GUIDE

This guide will help you set up the MIDI mapping in Traktor Pro 3 so the Python AI DJ controller can communicate with Traktor.

---

## STEP 1: Configure IAC Driver in Traktor

1. **Open Traktor Pro 3**
2. **Go to Preferences** (⌘+,)
3. **Controller Manager** tab
4. **Add Generic MIDI**:
   - Click **"Add..."** → **"Generic MIDI"**
   - **Device:** Select **"IAC Driver Bus 1"**
   - **In-Port:** IAC Driver Bus 1
   - **Out-Port:** IAC Driver Bus 1
   - Click **OK**

---

## STEP 2: Create MIDI Mappings

### DECK A CONTROLS

| Function | Type | MIDI Channel | CC# | Assignment |
|----------|------|--------------|-----|------------|
| **Play/Pause** | In | Ch1 | 1 | Deck A > Play/Pause |
| **Cue** | In | Ch1 | 3 | Deck A > Cue |
| **Sync** | In | Ch1 | 5 | Deck A > Sync (On) |
| **Load Selected** | In | Ch1 | 7 | Deck A > Load Selected |
| **Tempo Reset** | In | Ch1 | 30 | Deck A > Tempo Reset |

### DECK B CONTROLS

| Function | Type | MIDI Channel | CC# | Assignment |
|----------|------|--------------|-----|------------|
| **Play/Pause** | In | Ch1 | 2 | Deck B > Play/Pause |
| **Cue** | In | Ch1 | 4 | Deck B > Cue |
| **Sync** | In | Ch1 | 6 | Deck B > Sync (On) |
| **Load Selected** | In | Ch1 | 8 | Deck B > Load Selected |
| **Tempo Reset** | In | Ch1 | 31 | Deck B > Tempo Reset |

### MIXER CONTROLS

| Function | Type | MIDI Channel | CC# | Assignment |
|----------|------|--------------|-----|------------|
| **Crossfader** | In | Ch1 | 10 | Mixer > Crossfader |

### BROWSER NAVIGATION

| Function | Type | MIDI Channel | CC# | Assignment |
|----------|------|--------------|-----|------------|
| **Track Up** | In | Ch1 | 20 | Browser > List > Select Up |
| **Track Down** | In | Ch1 | 21 | Browser > List > Select Down |

### FEEDBACK (Traktor → Python)

| Function | Type | MIDI Channel | CC# | Assignment |
|----------|------|--------------|-----|------------|
| **Deck A Position** | Out | Ch1 | 40 | Deck A > Deck Playing Position |
| **Deck B Position** | Out | Ch1 | 41 | Deck B > Deck Playing Position |
| **Deck A Is Playing** | Out | Ch1 | 42 | Deck A > Is Deck Playing |
| **Deck B Is Playing** | Out | Ch1 | 43 | Deck B > Is Deck Playing |

---

## STEP 3: How to Add Each Mapping

For **each row** in the tables above:

1. **Click "Add In..."** (for In) or **"Add Out..."** (for Out)
2. **Device:** IAC Driver Bus 1
3. **Control:** Control Change
4. **Ch:** Set to the MIDI Channel (Ch1 = channel 0 in Traktor)
5. **No:** Set to the CC# number
6. **Assignment:**
   - Click on the right dropdown
   - Navigate to the assignment (e.g., "Deck A > Play/Pause")
   - Select it
7. **Interaction Mode:**
   - For buttons (Play, Cue, Sync, Load): **"Toggle"** or **"Direct"**
   - For continuous (Crossfader, Position): **"Relative"** or **"Direct"**
8. **Click "OK"**

---

## STEP 4: Configure Mapping Details

### For Play/Pause, Cue, Sync, Load Selected:
- **Type of Controller:** Button
- **Interaction Mode:** Toggle
- **Set to Value:** ON

### For Crossfader:
- **Type of Controller:** Fader/Knob
- **Interaction Mode:** Direct
- **Soft Takeover:** OFF
- **Invert:** OFF
- **Rotate:** OFF
- **Resolution:** Fine (256)

### For Track Up/Down:
- **Type of Controller:** Button
- **Interaction Mode:** Direct
- **Set to Value:** ON

### For Feedback (OUT mappings):
- **Type of Controller:** LED/Output
- **Controller Range:** 0 - 127
- **Blend:** Use Traktor setting

---

## STEP 5: Save the Mapping

1. **Give it a name:** "AI DJ Controller"
2. **Click "OK"** in Controller Manager
3. **Save Traktor preferences**

---

## STEP 6: Export Mapping (Optional)

To save your mapping for future use:

1. **Controller Manager**
2. **Select "AI DJ Controller"**
3. **Export** button
4. **Save as:** `Traktor_AI_DJ_Mapping.tsi`

---

## TROUBLESHOOTING

### MIDI Not Working?
1. Check IAC Driver is online in **Audio MIDI Setup**
2. Verify **"IAC Driver Bus 1"** appears in Traktor's MIDI device list
3. Restart Traktor if needed

### Crossfader Not Smooth?
1. Set **Resolution** to **Fine (256)**
2. Disable **Soft Takeover**
3. Check **Interaction Mode** is **Direct**

### Feedback Not Received?
1. Verify **Out-Port** is set to **IAC Driver Bus 1**
2. Check Python script is listening on correct MIDI channel
3. Enable MIDI feedback in Traktor preferences

---

## QUICK START AFTER MAPPING

Once mapping is complete:

1. **Load playlist in Traktor:**
   - Import M3U or manually add tracks from:
   `/Volumes/TRAKTOR/Traktor/Music/2026/Best of Deep Dub Tech House`

2. **Run Python AI DJ:**
   ```bash
   cd "/Users/dantaylor/Claude/Last Night an AI Saved My Life/traktor-automation"
   python3 traktor_ai_dj.py
   ```

3. **Watch the automation!** 🎧

---

**Total Mappings:** 14 In + 4 Out = 18 total

**Estimated Setup Time:** 15-20 minutes

**Difficulty:** ⭐⭐☆☆☆ (Moderate)
