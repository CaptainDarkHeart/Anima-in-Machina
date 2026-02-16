# QUICK FIX: Browser Navigation

✅ **Good news:** All other MIDI commands work (Play, Cue, Sync, Load, Crossfader)
❌ **Issue:** Browser up/down (CC 20/21) not working

This is a **5-minute fix** in Traktor.

---

## Step-by-Step Fix

### 1. Open Traktor Preferences
- **⌘+,** (Command + Comma)
- Go to **Controller Manager** tab

### 2. Select Generic MIDI Device
- In the device list, find **"Generic MIDI"** (IAC Driver Bus 1)
- Click on it to select it

### 3. Find Browser Mappings
- Scroll through the mapping list
- Look for entries with CC 20 or CC 21
- You should see two entries (or they might be missing)

### 4. Delete Existing Browser Mappings (if any)
- If you see CC 20 or CC 21 mappings, select them and click **"Delete"**
- We'll recreate them with the correct settings

### 5. Add Track Up (CC 20)

Click **"Add In..."**

Fill in:
- **Device:** IAC Driver Bus 1
- **Control:** Control Change
- **Ch:** Ch01
- **No:** 20

Click **"Assignment"** dropdown and navigate to:
- **Browser** → **List** → **Select Up/Down**

Set these options:
- **Interaction Mode:** **Inc** (or Increment)
- **Type of Controller:** **Button**
- **Set to value:** **ON**

Click **"OK"** or **"Add"**

### 6. Add Track Down (CC 21)

Click **"Add In..."**

Fill in:
- **Device:** IAC Driver Bus 1
- **Control:** Control Change
- **Ch:** Ch01
- **No:** 21

Click **"Assignment"** dropdown and navigate to:
- **Browser** → **List** → **Select Up/Down**

Set these options:
- **Interaction Mode:** **Dec** (or Decrement)
- **Type of Controller:** **Button**
- **Set to value:** **ON**

Click **"OK"** or **"Add"**

### 7. Save
- Click **"OK"** in Controller Manager
- Traktor will save the settings

---

## Test It

Run the browser test:

```bash
cd "/Users/dantaylor/Claude/Last Night an AI Saved My Life/traktor-automation"
python3 test_browser.py
```

You should now see the browser selection moving up and down!

---

## If It Still Doesn't Work

### Alternative Assignment Names

If you can't find **"Browser > List > Select Up/Down"**, try:

**For CC 20 (Up):**
- Look for: **"Browser > List > Select Next Track"**
- Or: **"Browser > List > Selector"**
- Use **Direct** mode instead of Inc

**For CC 21 (Down):**
- Look for: **"Browser > List > Select Previous Track"**
- Or: **"Browser > List > Selector"**
- Use **Direct** mode instead of Dec

### Check Browser Focus

Browser navigation only works when:
- ✅ Browser panel is visible in Traktor
- ✅ Browser has focus (click in it first)
- ✅ A playlist/folder is selected
- ✅ Tracks are visible in the list

---

## Visual Reference

Your mapping should look like this in Traktor:

```
┌─────────────────────────────────────────────────────────┐
│ Generic MIDI (IAC Driver Bus 1)                         │
├─────────────────────────────────────────────────────────┤
│ ...                                                     │
│ Ch01.CC.020 → Browser.List.Select Up/Down (Inc)        │
│ Ch01.CC.021 → Browser.List.Select Up/Down (Dec)        │
│ ...                                                     │
└─────────────────────────────────────────────────────────┘
```

---

## Why This Happens

Browser navigation is different from other controls because:
- It uses **Inc/Dec** mode instead of **Toggle**
- The same assignment (**Select Up/Down**) is used for both, but with different modes
- Some Traktor versions have different assignment names
- It requires the browser to have focus

Other controls (Play, Load, Crossfader) use **Toggle** or **Direct** mode, which is why they worked fine.

---

**That's it!** Once you add these two mappings with Inc/Dec mode, browser navigation will work perfectly. 🎧
