# Using Super Xtreme Mapper for Custom Traktor Mappings

[Super Xtreme Mapper](https://github.com/SuperXtremeMapper/super-xtreme-mapper) is a modern macOS app for editing Traktor TSI mapping files visually. This is much easier than using Traktor's built-in Controller Manager!

## Why Use Super Xtreme Mapper?

### For Your AI DJ Setup:

✅ **Visual editing** - See all mappings in a sortable table instead of Traktor's clunky interface
✅ **Bulk editing** - Change CC numbers quickly for all commands
✅ **Copy/paste** - Drag mappings between TSI files
✅ **Fix browser navigation** - Easier to verify Inc/Dec settings
✅ **Export/backup** - Save your IAC Driver mapping as a TSI file
✅ **Version control** - Track changes to your mapping over time

### Current Use Cases:

1. **Fix the browser navigation issue** - Visually verify CC 20/21 settings
2. **Create a clean IAC Driver mapping** from scratch
3. **Backup your working mapping** for future use
4. **Document your MIDI CC assignments** for the Python code
5. **Merge** X1 mk2 manual controls with IAC automation mappings

---

## Installation

### 1. Download
- Go to: https://github.com/SuperXtremeMapper/super-xtreme-mapper/releases
- Download the latest `.dmg` file

### 2. Install
- Open the `.dmg`
- Drag app to Applications folder

### 3. First Run (macOS Security)
The app isn't code-signed, so macOS will block it:

**Method A: Right-click → Open**
- Right-click the app → **Open**
- Click **Open** in the warning dialog

**Method B: System Settings**
- Try to open the app normally (it will be blocked)
- Go to **System Settings** → **Privacy & Security**
- Scroll down to "Security" section
- Click **"Open Anyway"** next to Super Xtreme Mapper
- Click **Open** in the confirmation dialog

---

## How to Use for Your AI DJ Setup

### Export Your Current Mapping from Traktor

1. **Open Traktor → Preferences → Controller Manager**
2. **Select "Generic MIDI" (IAC Driver Bus 1)**
3. **Click "Export"**
4. **Save as:** `AI_DJ_IAC_Mapping_v1.tsi`
5. **Location:** `/Users/dantaylor/Claude/Last Night an AI Saved My Life/traktor-automation/mappings/`

### Open in Super Xtreme Mapper

1. **Launch Super Xtreme Mapper**
2. **File → Open** (or drag TSI file into window)
3. **Select:** `AI_DJ_IAC_Mapping_v1.tsi`

You'll see a table of all your mappings!

### Fix Browser Navigation

1. **Search/Filter** for CC 20 and CC 21
2. **Check the settings:**
   - Assignment: Browser > List > Select Up/Down
   - Interaction Mode: Inc (for CC 20) or Dec (for CC 21)
   - Type: Button
3. **Edit if needed** by clicking on the row
4. **Save** the TSI file
5. **Import back into Traktor**

### Create a Complete Mapping from Scratch

Instead of manually clicking in Traktor, you can:

1. **Create a new TSI** in Super Xtreme Mapper
2. **Add all 18 mappings** from your MIDI_CC table
3. **Set proper modes** (Toggle, Direct, Inc/Dec)
4. **Save and import** into Traktor

This ensures consistency and is faster than clicking through Traktor's interface.

---

## Recommended Workflow

### 1. Export Current Mapping
```bash
# Create mappings directory
mkdir -p "/Users/dantaylor/Claude/Last Night an AI Saved My Life/traktor-automation/mappings"
```

Export from Traktor to this folder.

### 2. Edit in Super Xtreme Mapper
- Fix browser navigation
- Verify all CC numbers match your Python code
- Add comments/notes if supported
- Check modifier settings (if using)

### 3. Version Control
```bash
cd "/Users/dantaylor/Claude/Last Night an AI Saved My Life/traktor-automation/mappings"
git add AI_DJ_IAC_Mapping_v1.tsi
git commit -m "Working IAC Driver mapping with browser fix"
```

### 4. Import Back to Traktor
- Traktor → Controller Manager
- Delete old "Generic MIDI" device
- Import → Select your edited TSI file
- Test with `test_midi_auto.py`

---

## Advanced: Create Template Mappings

You could create different TSI files for different scenarios:

### `AI_DJ_Full_Auto.tsi`
All automation mappings enabled

### `AI_DJ_Track_Selection_Only.tsi`
Only browser and load commands (manual mixing)

### `AI_DJ_Monitoring_Only.tsi`
Only feedback/output mappings (for monitoring Traktor state)

Then switch between them in Traktor depending on your performance style.

---

## Backup Your X1 mk2 / Z1 Mappings Too

Even though you're keeping them in Native mode, you can:

1. **Export X1 mk2 mapping** from Traktor
2. **Open in Super Xtreme Mapper**
3. **See all the default NI mappings**
4. **Copy useful mappings** to your IAC Driver mapping

This is helpful if you want to:
- Understand how NI maps certain controls
- Copy their modifier logic
- Create hybrid mappings

---

## TSI File Naming Convention

Use clear naming:
```
AI_DJ_IAC_v1.0_working.tsi          # Working version
AI_DJ_IAC_v1.1_browser_fix.tsi      # After fixing browser
AI_DJ_IAC_v2.0_z1_hybrid.tsi        # Hybrid with Z1 controls
X1_mk2_native_backup.tsi             # Backup of X1 native mapping
Z1_native_backup.tsi                 # Backup of Z1 native mapping
```

Keep them in `/traktor-automation/mappings/` and version control them.

---

## Creating Your Mapping Programmatically

Since TSI files are XML-based, you could even generate them from your Python MIDI_CC dictionary:

```python
# Future enhancement idea
from traktor_ai_dj import TraktorAIDJ

dj = TraktorAIDJ()
dj.export_tsi_mapping("AI_DJ_IAC_Generated.tsi")
```

This would ensure your Python code and Traktor mapping are always in sync!

---

## Key Benefits for Your Setup

### 1. **Visual Verification**
See all mappings in one table - easier to spot the browser navigation issue

### 2. **Documentation**
Export your working mapping and commit it to git - now your setup is reproducible

### 3. **Experimentation**
Try different interaction modes visually before importing to Traktor

### 4. **Backup**
If Traktor corrupts settings, restore from TSI file

### 5. **Sharing**
If you publish your AI DJ system, include the TSI file so others can import it instantly

---

## Quick Fix: Browser Navigation with SXM

1. **Export** your Generic MIDI mapping from Traktor
2. **Open** in Super Xtreme Mapper
3. **Find** CC 20 and CC 21 rows
4. **Edit Interaction Mode:**
   - CC 20 → **Inc**
   - CC 21 → **Dec**
5. **Save** TSI file
6. **Import** back to Traktor
7. **Test** with `python3 test_browser.py`

This is probably **faster** than clicking through Traktor's interface!

---

## Download Link

https://github.com/SuperXtremeMapper/super-xtreme-mapper/releases

⚠️ **Requirements:**
- macOS 14.0+ (Sonoma or later)
- Apple Silicon or Intel Mac

---

## Next Steps

1. Install Super Xtreme Mapper
2. Export your current Generic MIDI mapping from Traktor
3. Open it in SXM and fix the browser navigation
4. Save and reimport
5. Test with the browser test script

This should be faster than manual Traktor editing! 🎚️
