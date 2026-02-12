# QUICK START GUIDE - Read This First!

## ⚠️ CRITICAL: File Locations

### ✅ WHERE TO PUT THE PYTHON SCRIPT:
```
Downloads/cobblemon_pack_generator.py    ← Script goes HERE!
```

### ✅ WHERE TO PUT YOUR BLOCKBENCH FILES:
```
Downloads/Mod-ResourceAndBehavior-Packs/
├── yourpokemon.geo.json          ← Model
├── yourpokemon.animation.json    ← Animations
├── yourpokemon.png               ← Texture (default)
└── yourpokemon_shiny.png         ← Texture (shiny, optional)
```

### ❌ DO NOT PUT THE SCRIPT IN THE SAME FOLDER AS YOUR FILES!
If you put `cobblemon_pack_generator.py` inside `Mod-ResourceAndBehavior-Packs/`, it might get deleted by the cleanup function!

---

## 📁 Correct Folder Structure

```
Downloads/
├── cobblemon_pack_generator.py              ← SCRIPT HERE
└── Mod-ResourceAndBehavior-Packs/
    ├── yourpokemon.geo.json                 ← FILES HERE
    ├── yourpokemon.animation.json           ← FILES HERE
    ├── yourpokemon.png                      ← FILES HERE
    └── yourpokemon_shiny.png                ← FILES HERE (optional)
```

---

## 🚀 Running the Script

### Step 1: Open Terminal/Command Prompt
- **Windows**: Press Win+R, type `cmd`, press Enter
- **Mac**: Press Cmd+Space, type `terminal`, press Enter
- **Linux**: Ctrl+Alt+T

### Step 2: Navigate to Downloads
```bash
cd Downloads
```

### Step 3: Run the Script
```bash
# Basic example
python cobblemon_pack_generator.py --name Flamebird --number 999

# With customization
python cobblemon_pack_generator.py --name Aquadragon --number 1000 \
  --primary-type water --secondary-type dragon \
  --hp 100 --attack 80 --defence 90 \
  --moves "1:tackle,7:watergun,20:surf,tm:icebeam" \
  --abilities "torrent,h:swiftswim"
```

### Step 4: Check Output
The script creates TWO folders in `Downloads/Mod-ResourceAndBehavior-Packs/`:
- `resource_pack/` - Contains models, textures, animations
- `behavior_pack/` - Contains species data, spawn info

---

## 🔄 Adding Multiple Pokémon

Just run the script again with different files and name:

```bash
# First Pokémon
python cobblemon_pack_generator.py --name Flamebird --number 1001

# Replace files in Mod-ResourceAndBehavior-Packs/ with new Pokémon's files

# Second Pokémon
python cobblemon_pack_generator.py --name Aquadragon --number 1002

# The script ADDS to existing packs automatically!
```

---

## 📦 Installing Your Packs

### Step 1: Copy Resource Pack
```
FROM: Downloads/Mod-ResourceAndBehavior-Packs/resource_pack/
TO:   .minecraft/resourcepacks/my_cobblemon_pack/
```

### Step 2: Copy Behavior Pack
```
FROM: Downloads/Mod-ResourceAndBehavior-Packs/behavior_pack/
TO:   .minecraft/saves/YourWorldName/datapacks/my_cobblemon_pack/
```

### Step 3: Enable in Minecraft
1. Start Minecraft
2. Options → Resource Packs
3. Find your pack and move it to "Selected"
4. Load your world
5. Run command: `/reload`

### Step 4: Test
```
/pokespawn yourpokemon
```

---

## 🐛 Practice Dummy Issue?

If your Pokémon shows as a practice dummy, check these:

### ✅ Checklist:
- [ ] Both resource_pack AND behavior_pack are installed
- [ ] Resource pack is ENABLED in Options → Resource Packs
- [ ] You ran `/reload` after installing packs
- [ ] Texture file is `.png` format (not .jpg)
- [ ] Model identifier in Blockbench matches Pokémon name (lowercase)

### 🔧 Model Identifier Check:
1. Open your `.geo.json` file in a text editor
2. Look for: `"identifier": "geometry.yourpokemon"`
3. The name after `geometry.` should match your `--name` argument (in lowercase)

Example:
```json
{
  "format_version": "1.12.0",
  "minecraft:geometry": [
    {
      "description": {
        "identifier": "geometry.flamebird",  ← Must match --name flamebird
        "texture_width": 64,
        "texture_height": 64
      }
    }
  ]
}
```

---

## 🛡️ Script Keeps Disappearing?

### Reason:
You probably put the script INSIDE `Mod-ResourceAndBehavior-Packs/` folder!

### Solution:
1. Move script to `Downloads/` (parent folder)
2. Keep your Blockbench files in `Downloads/Mod-ResourceAndBehavior-Packs/`
3. Run script from `Downloads/` folder

### Alternative - Use --no-cleanup Flag:
```bash
python cobblemon_pack_generator.py --name Test --number 999 --no-cleanup
```
This prevents ANY file deletion (keeps source files too).

---

## 📋 File Extensions Guide

### What Gets Picked Up:
- ✅ `.geo.json` - Model file
- ✅ `.animation.json` - Animation file
- ✅ `.png` - Texture file
- ✅ `.tga` - Texture file (alternative)

### What Gets Ignored:
- ❌ `.py` - Python scripts (protected!)
- ❌ `.txt` - Text files
- ❌ `.md` - Markdown files
- ❌ Folders/directories
- ❌ Hidden files (starting with `.`)

---

## 💡 Pro Tips

1. **Always use --no-cleanup while testing**:
   ```bash
   python cobblemon_pack_generator.py --name Test --number 999 --no-cleanup
   ```

2. **Keep original Blockbench files backed up** somewhere safe

3. **Test one Pokémon first** before making a whole pack

4. **Check Minecraft logs** if something goes wrong:
   - Location: `.minecraft/logs/latest.log`
   - Search for your Pokémon name or "cobblemon"

5. **Use the MOVES_AND_ABILITIES_REFERENCE.md** file for move/ability ideas

---

## 🆘 Still Having Issues?

1. Make sure you have the **latest version** of the script
2. Check that **Cobblemon mod is installed** and working
3. Test with vanilla Pokémon first: `/pokespawn bulbasaur`
4. Join **Cobblemon Discord** for help

---

## ✅ Quick Verification

Run this to check your setup:

```bash
# Check script location
ls Downloads/cobblemon_pack_generator.py

# Check files location
ls Downloads/Mod-ResourceAndBehavior-Packs/
```

You should see:
- Script in Downloads/
- Model, animation, texture files in Mod-ResourceAndBehavior-Packs/

**NOT BOTH IN THE SAME FOLDER!**
