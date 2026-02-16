# BROWSER NAVIGATION FIX

Browser up/down commands not working? This is a common Traktor MIDI mapping issue.

## The Problem

Browser navigation in Traktor has **three different mapping types**:

1. **List > Select Up/Down** - Single step navigation
2. **List > Select Next/Previous** - Alternative names for same thing
3. **Selector** - Continuous/encoder style control

## Solution 1: Use "Direct" Mode with Value Triggers

### In Traktor Controller Manager:

#### Track Up (CC 20):
```
Device: Generic MIDI (IAC Driver Bus 1)
Type: In
Control: Control Change
Channel: Ch01
Control No: 20
Assignment: Browser > List > Select Up/Down
Interaction Mode: Direct
Type of Controller: Button
Set to value: ON (value when pressed > 64)
```

**Important Settings:**
- ✅ **Interaction Mode: Direct** (NOT Toggle, NOT Increment)
- ✅ **Type: Button**
- ✅ **Set to value: ON**
- ✅ Make sure the dropdown says "Select **Up**/Down" not just "Select"

#### Track Down (CC 21):
```
Device: Generic MIDI (IAC Driver Bus 1)
Type: In
Control: Control Change
Channel: Ch01
Control No: 21
Assignment: Browser > List > Select Up/Down
Interaction Mode: Direct
Type of Controller: Button
Set to value: OFF (value when pressed < 64)
```

**Important Settings:**
- ✅ **Interaction Mode: Direct** (NOT Toggle, NOT Decrement)
- ✅ **Type: Button**
- ✅ **Set to value: OFF**
- ✅ Same assignment as Track Up, but value is OFF

## Solution 2: Use Two Separate Mappings (Simpler)

This is the **RECOMMENDED** approach:

### Track Up (CC 20):

1. **Add In... → Generic MIDI**
2. **Control:** Control Change
3. **Ch:** Ch01
4. **No:** 20
5. **Assignment:** Click dropdown → **Browser** → **List** → **Select Next Track**
6. **Interaction Mode:** Direct
7. **Type of Controller:** Button
8. **Set to value:** ON

### Track Down (CC 21):

1. **Add In... → Generic MIDI**
2. **Control:** Control Change
3. **Ch:** Ch01
4. **No:** 21
5. **Assignment:** Click dropdown → **Browser** → **List** → **Select Previous Track**
6. **Interaction Mode:** Direct
7. **Type of Controller:** Button
8. **Set to value:** ON

## Solution 3: Use Increment/Decrement Mode

### Track Up (CC 20):
```
Assignment: Browser > List > Select Up/Down
Interaction Mode: Inc
Type of Controller: Button
```

### Track Down (CC 21):
```
Assignment: Browser > List > Select Up/Down
Interaction Mode: Dec
Type of Controller: Button
```

## Testing After Fix

Run this test:

```bash
cd "/Users/dantaylor/Claude/Last Night an AI Saved My Life/traktor-automation"
python3 << 'EOF'
import mido
import time

output = mido.open_output("IAC Driver Bus 1")

print("Testing browser navigation...")
print("Watch Traktor browser - should move DOWN 5 times")

for i in range(5):
    output.send(mido.Message('control_change', control=21, value=127, channel=0))
    print(f"  Down {i+1}")
    time.sleep(0.5)

print("\nNow moving UP 5 times")
for i in range(5):
    output.send(mido.Message('control_change', control=20, value=127, channel=0))
    print(f"  Up {i+1}")
    time.sleep(0.5)

output.close()
print("\nDone! Did the browser selection move?")
EOF
```

## Common Issues

### Issue 1: Assignment Not Found
**Problem:** Can't find "Select Up/Down" in dropdown

**Fix:** Look for:
- `Browser > List > Select Up/Down`
- `Browser > List > Select Next Track` / `Select Previous Track`
- `Browser > List > Selector`

The exact wording varies by Traktor version.

### Issue 2: Only Works Once
**Problem:** First command works, then stops

**Fix:** Change from **Toggle** to **Direct** mode

### Issue 3: Works But Wrong Direction
**Problem:** Up goes down, down goes up

**Fix:** Swap the CC numbers (20 ↔ 21) or swap ON/OFF values

### Issue 4: Nothing Happens
**Problem:** No browser movement at all

**Fix:**
1. ✅ Browser must be **visible** in Traktor
2. ✅ Browser must have **focus** (click in browser first)
3. ✅ Playlist/folder must be **selected**
4. ✅ Some tracks must be **visible**

## Alternative: Use Note Messages Instead

If CC messages don't work, try **Note On/Off**:

```python
# Instead of:
output.send(mido.Message('control_change', control=20, value=127, channel=0))

# Use:
output.send(mido.Message('note_on', note=20, velocity=127, channel=0))
time.sleep(0.05)
output.send(mido.Message('note_off', note=20, velocity=0, channel=0))
```

Then in Traktor, map:
- **Control:** Note
- **Note:** 20 (for up) or 21 (for down)

## Recommended Final Configuration

**For best results, use Solution 2** with these exact settings:

| Function | Type | Ch | CC/Note | Assignment | Mode | Controller | Value |
|----------|------|----|---------|-----------|------|------------|-------|
| Track Up | In | 01 | CC 20 | Browser > List > Select Next Track | Direct | Button | ON |
| Track Down | In | 01 | CC 21 | Browser > List > Select Previous Track | Direct | Button | ON |

Or if those assignments don't exist in your Traktor:

| Function | Type | Ch | CC/Note | Assignment | Mode | Controller | Value |
|----------|------|----|---------|-----------|------|------------|-------|
| Track Up | In | 01 | CC 20 | Browser > List > Select Up/Down | Inc | Button | ON |
| Track Down | In | 01 | CC 21 | Browser > List > Select Up/Down | Dec | Button | ON |

## Update the Napkin

Once fixed, note which solution worked for your Traktor version!
