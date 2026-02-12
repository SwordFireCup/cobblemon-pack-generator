# Cobblemon Pack Generator - Troubleshooting Guide

## 🐛 Common Issues and Fixes

### Issue 1: Practice Dummy / Missing Texture

**Symptoms**: Pokémon spawns as a practice dummy or invisible instead of showing your model/texture.

**Causes & Fixes**:

#### Fix 1: Texture Path Issue (MOST COMMON)
The resolver JSON needs the correct texture path format.

**✅ Correct Format** (what the updated script uses):
```json
{
  "texture": "cobblemon:pokemon/pokemonname/pokemonname"
}
```

**❌ Wrong Format** (old versions):
```json
{
  "texture": "cobblemon:textures/pokemon/pokemonname/pokemonname.png"
}
```

**Solution**: Re-run the updated script - it now uses the correct path format!

#### Fix 2: Model Identifier Mismatch
Your Blockbench model's identifier must match your Pokémon name.

**Check**:
1. Open your `.geo.json` file
2. Look for: `"identifier": "geometry.yourpokemon"`
3. The name after `geometry.` should match your `--name` argument

**Example**:
- If you use `--name Flamebird`
- Model identifier should be: `geometry.flamebird` (lowercase!)

#### Fix 3: Both Packs Not Installed
You need BOTH resource and behavior packs installed!

**Checklist**:
```
✓ resource_pack/ copied to .minecraft/resourcepacks/
✓ behavior_pack/ copied to .minecraft/saves/YourWorld/datapacks/
✓ Resource pack ENABLED in Options → Resource Packs
✓ Ran /reload command after installing
```

#### Fix 4: Texture File Format
Make sure texture is `.png` (not `.jpg`, `.jpeg`, etc.)

**To Convert**:
- Open in image editor (GIMP, Photoshop, Paint.NET)
- Save As → PNG format

#### Fix 5: Case Sensitivity
All names should be lowercase!

**Example**:
```bash
# ❌ Wrong
--name FlAmEbIrD

# ✅ Correct  
--name flamebird
```

Files will be named: `flamebird.geo.json`, `flamebird.png`, etc.

---

### Issue 2: Script Gets Deleted When Running

**This shouldn't happen!** Possible causes:

#### Cause 1: Running with `--cleanup` Flag
The cleanup flag deletes SOURCE files (model, texture, animation) from the input folder, NOT the script itself.

**What gets deleted**: Files in `Downloads/Mod-ResourceAndBehavior-Packs/`
**What stays**: The Python script

**Solution**: Use `--no-cleanup` flag to keep source files:
```bash
python cobblemon_pack_generator.py --name Test --number 999 --no-cleanup
```

#### Cause 2: Antivirus/Security Software
Some antivirus programs quarantine Python scripts.

**Solution**:
1. Add exception for the script
2. Check antivirus quarantine/logs
3. Run from a different folder

#### Cause 3: File Permissions
The script might not have proper permissions.

**Solution** (Linux/Mac):
```bash
chmod +x cobblemon_pack_generator.py
```

**Solution** (Windows):
- Right-click script → Properties → Uncheck "Read-only"

---

### Issue 3: Adding Multiple Pokémon

**Good news**: The updated script now ADDS to existing packs!

#### How It Works:
1. First Pokémon: Creates new packs
2. Second Pokémon: Adds to existing packs (merges language files)
3. Third+ Pokémon: Keeps adding!

#### Workflow:
```bash
# First Pokémon
python cobblemon_pack_generator.py --name Flamebird --number 1001
# Creates: resource_pack/ and behavior_pack/

# Second Pokémon  
python cobblemon_pack_generator.py --name Aquadragon --number 1002
# Adds to existing packs!

# Third Pokémon
python cobblemon_pack_generator.py --name Leafgolem --number 1003
# Keeps adding!
```

#### What Gets Merged:
- ✅ Language file (`en_us.json`) - entries combined
- ✅ Species files - separate file per Pokémon
- ✅ Models/textures - separate folders per Pokémon
- ✅ pack.mcmeta - kept from first run

---

## 🔍 Advanced Debugging

### Check Your Pack Structure

**Resource Pack** should look like:
```
resource_pack/
├── pack.mcmeta
└── assets/cobblemon/
    ├── bedrock/pokemon/
    │   ├── models/pokemonname/pokemonname.geo.json
    │   ├── animations/pokemonname/pokemonname.animation.json
    │   ├── posers/pokemonname.json
    │   └── resolvers/0_pokemonname_base.json
    ├── textures/pokemon/pokemonname/
    │   ├── pokemonname.png
    │   └── pokemonname_shiny.png
    └── lang/en_us.json
```

**Behavior Pack** should look like:
```
behavior_pack/
├── pack.mcmeta
└── data/cobblemon/
    ├── species/custom/pokemonname.json
    └── spawn_pool_world/pokemonname.json
```

### Validate JSON Files

Use a JSON validator to check for syntax errors:
- Online: https://jsonlint.com
- VS Code: Install "JSON Validate" extension

**Common JSON Errors**:
- Missing comma between entries
- Extra comma at end of list
- Unmatched brackets `{}` or `[]`
- Unescaped quotes in strings

### Check Minecraft Logs

Look for errors in `latest.log`:
- Location: `.minecraft/logs/latest.log`
- Search for: "cobblemon" or your Pokémon name
- Look for: "Failed to load" or "Exception"

### Test in Creative Mode

```
/gamemode creative
/pokespawn yourpokemon
```

If it works in creative but not survival, it's likely a spawn configuration issue (not texture).

---

## 🎮 Installation Checklist

Use this checklist to ensure everything is set up correctly:

### Before Running Script:
- [ ] Downloaded and installed Minecraft with Cobblemon mod
- [ ] Created `Downloads/Mod-ResourceAndBehavior-Packs/` folder
- [ ] Exported files from Blockbench:
  - [ ] Model: `pokemon.geo.json`
  - [ ] Animation: `pokemon.animation.json`
  - [ ] Texture: `pokemon.png`
- [ ] Verified model identifier matches Pokémon name (lowercase)

### After Running Script:
- [ ] Script completed without errors
- [ ] `resource_pack/` folder created
- [ ] `behavior_pack/` folder created
- [ ] Files exist in correct locations (check structure above)

### Installing Packs:
- [ ] Copied `resource_pack/` to `.minecraft/resourcepacks/`
- [ ] Copied `behavior_pack/` to `.minecraft/saves/YourWorld/datapacks/`
- [ ] Started Minecraft
- [ ] Enabled resource pack in Options → Resource Packs
- [ ] Loaded world with datapack
- [ ] Ran `/reload` command

### Testing:
- [ ] Ran `/pokespawn yourpokemon`
- [ ] Pokémon appears with correct model
- [ ] Pokémon has correct texture
- [ ] Animations work (walking, idle, etc.)

---

## 💡 Quick Fixes Summary

| Problem | Quick Fix |
|---------|-----------|
| Practice dummy appears | Re-run updated script (fixes texture path) |
| Invisible Pokémon | Check both packs installed, run /reload |
| Script disappears | Use --no-cleanup flag |
| Can't add multiple Pokémon | Use updated script - it merges automatically |
| Texture not showing | Check .png format, model identifier match |
| Pokémon name is weird text | Edit language file (en_us.json) |
| No spawn in wild | Edit spawn_pool_world JSON |
| Wrong animations | Check animation IDs in Blockbench |

---

## 🆘 Still Having Issues?

1. **Re-download the script** - Make sure you have the latest version
2. **Check Cobblemon version** - Make sure mod is up to date
3. **Test with vanilla Pokémon** - Verify Cobblemon works: `/pokespawn bulbasaur`
4. **Ask for help** - Join Cobblemon Discord with:
   - Your Minecraft version
   - Cobblemon version
   - Error messages from logs
   - Screenshots of issue

---

## ✅ Verification Script

Run this in your pack directory to verify structure:

```bash
# Linux/Mac
find resource_pack behavior_pack -type f

# Windows PowerShell
Get-ChildItem -Recurse resource_pack, behavior_pack | Select-Object FullName
```

Should output all files - check that paths match the structure above!

---

## 🔧 Manual Fixes

### If Texture Still Doesn't Work:

1. Open `resolvers/0_yourpokemon_base.json`
2. Find the texture line
3. Change from:
   ```json
   "texture": "cobblemon:textures/pokemon/yourpokemon/yourpokemon.png"
   ```
   To:
   ```json
   "texture": "cobblemon:pokemon/yourpokemon/yourpokemon"
   ```
4. Save and run `/reload` in game

### If Model Doesn't Load:

1. Open `yourpokemon.geo.json`
2. Check `"identifier"` field
3. Should be: `"geometry.yourpokemon"` (all lowercase)
4. If different, either:
   - Re-export from Blockbench with correct name, OR
   - Change `"model"` in resolver to match

---

**Remember**: Always run `/reload` after making changes to packs!
