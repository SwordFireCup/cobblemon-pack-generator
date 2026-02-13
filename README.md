**This generator is a WIP.**

Therefore it might have **bugs** that have not been fixed.

SO use at your OWN RISK.

THIS IS ADVANCED STUFF!

Don't be sad if it dosn't work because my program is terrible.

Just a warning.

Good pokemon changing!

**Remember:** This is an advanced tool for experienced users. No troubleshooting section is provided - you're expected to figure things out!


# 🧬 Cobblemon Species Editor v1.1

**Modify existing Pokémon in Cobblemon using Species Additions!**

This tool creates Species Addition files that override and modify existing Pokémon behavior, stats, evolutions, and more - all through datapacks, no mods required!

---

## 📋 Table of Contents

- [What It Does](#what-it-does)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Evolution Guide](#evolution-guide)
- [All Features](#all-features)
- [Examples](#examples)
- [Troubleshooting](#troubleshooting)

---

## 🎯 What It Does

The Species Editor creates **Species Addition** files that modify existing Pokémon in Cobblemon. You can:

- ✅ Add new evolutions to any Pokémon (e.g., make Eevee evolve into your custom Drageon)
- ✅ Change types, abilities, stats
- ✅ Modify behavior (can fly, can swim, etc.)
- ✅ Update model size and hitbox
- ✅ Change item drops
- ✅ Replace move pools

**All changes use datapacks - no client-side mods needed!**

---

## 📦 Installation

### Requirements
- Python 3.7 or higher
- A Cobblemon server or world (1.4+)

### Setup
1. Download `cobblemon_species_editor.py`
2. Place it in your pack directory (same folder as your `behavior_pack/` folder)
3. Run from command line!

**No Python libraries needed** - uses only built-in modules!

---

## 🚀 Quick Start

### Basic Usage

```bash
python cobblemon_species_editor.py --pokemon <pokemon_name> [options]
```

**The `--pokemon` argument is REQUIRED** - this is the Pokémon you want to modify.

### Simplest Example: Add Evolution

```bash
python cobblemon_species_editor.py --pokemon eevee --add-evolution drageon --evo-method item_interact --evo-item "cobblemon:dragon_scale"
```

This makes Eevee evolve into Drageon when you use a Dragon Scale on it!

---

## 🐉 Evolution Guide

### Evolution Methods

There are 3 evolution methods available:

#### 1. **Level Up Evolution** (`level_up`)
Pokémon evolves when it reaches a certain level.

```bash
python cobblemon_species_editor.py --pokemon pikachu --add-evolution raichu --evo-method level_up --evo-level 30
```

**Required:**
- `--evo-level` - The level needed (e.g., 30)

---

#### 2. **Item Interaction Evolution** (`item_interact`)
Pokémon evolves when you use a specific item on it.

```bash
python cobblemon_species_editor.py --pokemon eevee --add-evolution vaporeon --evo-method item_interact --evo-item "cobblemon:water_stone"
```

**Required:**
- `--evo-item` - The item needed (e.g., "cobblemon:water_stone", "cobblemon:dragon_scale")

**Common Evolution Items:**
- `cobblemon:fire_stone`
- `cobblemon:water_stone`
- `cobblemon:thunder_stone`
- `cobblemon:leaf_stone`
- `cobblemon:moon_stone`
- `cobblemon:sun_stone`
- `cobblemon:shiny_stone`
- `cobblemon:dusk_stone`
- `cobblemon:dawn_stone`
- `cobblemon:ice_stone`
- `cobblemon:dragon_scale`
- `cobblemon:kings_rock`
- `cobblemon:metal_coat`
- `cobblemon:upgrade`

---

#### 3. **Trade Evolution** (`trade`)
Pokémon evolves when traded to another player.

```bash
python cobblemon_species_editor.py --pokemon haunter --add-evolution gengar --evo-method trade
```

**Optional:**
- `--evo-item` - Item the Pokémon must hold during trade

```bash
python cobblemon_species_editor.py --pokemon onix --add-evolution steelix --evo-method trade --evo-item "cobblemon:metal_coat"
```

---

### Evolution Examples

#### Make Eevee evolve into custom Drageon
```bash
python cobblemon_species_editor.py --pokemon eevee --add-evolution drageon --evo-method item_interact --evo-item "cobblemon:dragon_scale"
```

#### Make Pikachu evolve at level 30
```bash
python cobblemon_species_editor.py --pokemon pikachu --add-evolution raichu --evo-method level_up --evo-level 30
```

#### Make Haunter evolve when traded
```bash
python cobblemon_species_editor.py --pokemon haunter --add-evolution gengar --evo-method trade
```

#### Make Onix evolve when traded holding Metal Coat
```bash
python cobblemon_species_editor.py --pokemon onix --add-evolution steelix --evo-method trade --evo-item "cobblemon:metal_coat"
```

---

## 🎨 All Features

### Change Types

```bash
python cobblemon_species_editor.py --pokemon pikachu --primary-type fire --secondary-type dragon
```

**Result:** Pikachu becomes Fire/Dragon type

---

### Change Abilities

```bash
python cobblemon_species_editor.py --pokemon charizard --abilities "blaze,h:solar_power"
```

**Format:** `ability1,ability2,h:hidden_ability`
- Regular abilities: Just the name (e.g., `blaze`)
- Hidden ability: Prefix with `h:` (e.g., `h:solar_power`)

---

### Modify Model Size

```bash
python cobblemon_species_editor.py --pokemon wailord --base-scale 3.0 --hitbox "5.0,8.0,5.0"
```

**Parameters:**
- `--base-scale` - Overall size multiplier (1.0 = normal, 2.0 = double size)
- `--hitbox` - Collision box as `width,height,width` (all in blocks)

---

### Add Item Drops

```bash
python cobblemon_species_editor.py --pokemon pikachu --drops "cobblemon:thunder_stone:5,minecraft:redstone:50"
```

**Format:** `item:percentage,item:percentage`
- `cobblemon:thunder_stone:5` = 5% chance to drop Thunder Stone
- `minecraft:redstone:50` = 50% chance to drop Redstone

---

### Enable Flight/Swimming

```bash
python cobblemon_species_editor.py --pokemon charizard --can-fly
python cobblemon_species_editor.py --pokemon gyarados --can-swim --breathe-underwater
```

**Flags:**
- `--can-fly` - Pokémon can fly
- `--can-swim` - Pokémon can swim
- `--breathe-underwater` - Pokémon can breathe underwater

---

### Replace Move Pool

```bash
python cobblemon_species_editor.py --pokemon pikachu --add-moves "1:tackle,5:thundershock,10:quick_attack,15:thunderbolt"
```

**⚠️ WARNING:** This **REPLACES ALL MOVES** the Pokémon knows! Use carefully!

**Format:** `level:move,level:move`
- `1:tackle` = Learns Tackle at level 1
- `tm:thunderbolt` = Learns via TM
- `egg:volt_tackle` = Learns as egg move

---

### Custom Namespace

```bash
python cobblemon_species_editor.py --pokemon eevee --add-evolution drageon --evo-method item_interact --evo-item "cobblemon:dragon_scale" --namespace mypack
```

**Result:** Creates file at `behavior_pack/data/mypack/species_additions/eevee.json`

Default namespace is `custom`.

---

## 📚 Examples

### Example 1: Create Dragon Eeveelution

```bash
python cobblemon_species_editor.py --pokemon eevee --add-evolution drageon --evo-method item_interact --evo-item "cobblemon:dragon_scale"
```

Now Eevee can evolve into a Drageon to add an Eeeveelution!

---

### Example 2: Make Magikarp Evolve Earlier

```bash
python cobblemon_species_editor.py --pokemon magikarp --add-evolution gyarados --evo-method level_up --evo-level 15
```

Magikarp now evolves at level 15 instead of 20!

---

### Example 3: Change Charizard to Fire/Dragon

```bash
python cobblemon_species_editor.py --pokemon charizard --primary-type fire --secondary-type dragon
```

Charizard is now Fire/Dragon type (like it should be!)

---

### Example 4: Make Pikachu Drop Thunder Stones

```bash
python cobblemon_species_editor.py --pokemon pikachu --drops "cobblemon:thunder_stone:10"
```

Pikachu now has a 10% chance to drop a Thunder Stone when defeated.

---

### Example 5: Make Pidgey Flyable

```bash
python cobblemon_species_editor.py --pokemon pidgey --can-fly
```

Now you can fly on Pidgey!

---

### Example 6: Buff Rattata

```bash
python cobblemon_species_editor.py --pokemon rattata --primary-type normal --secondary-type dark --abilities "guts,hustle,h:adaptability"
```

Rattata is now Normal/Dark with better abilities!

---

## 🔧 Troubleshooting

### "Evolution not working in-game"

**Check:**
1. Did you `/reload` the server/world?
2. Is the evolution target Pokémon actually in your pack? (Evolution won't work if Drageon doesn't exist)
3. Is the item spelled correctly? (Use quotes: `"cobblemon:dragon_scale"`)

---

### "File not found error"

**Solution:** Make sure you run the script from your pack's root directory:

```
your-pack/
├── behavior_pack/
├── resource_pack/
└── cobblemon_species_editor.py  ← Run from here!
```

---

### "Pokémon still has original moves"

The `--add-moves` flag **REPLACES** the entire move pool. Make sure you include all the moves you want!

---

### "Changes not appearing"

1. Check the file was created: `behavior_pack/data/custom/species_additions/<pokemon>.json`
2. Run `/reload` in-game
3. Verify JSON syntax is valid (use a JSON validator)

---

## 📁 Output Location

Species Addition files are saved to:
```
behavior_pack/data/<namespace>/species_additions/<pokemon>.json
```

**Default namespace:** `custom`
**Custom namespace:** Use `--namespace <name>`

---

## 🎯 Use Cases

### Perfect For:
- ✅ Adding evolutions to custom Pokémon
- ✅ Creating regional variants (Alolan/Galarian style)
- ✅ Balancing/buffing weak Pokémon
- ✅ Custom evolution items
- ✅ Making Pokémon rideable (can-fly)
- ✅ Custom drop tables

### NOT For:
- ❌ Creating new Pokémon from scratch (use Pack Generator for that)
- ❌ Creating new moves (requires Showdown modding)
- ❌ Creating new abilities (requires Showdown modding)

---

## ⚠️ Important Notes

1. **Species Additions are ADDITIVE** - Multiple mods can modify the same Pokémon
2. **Evolutions must point to EXISTING Pokémon** - Create your custom Pokémon first!
3. **Use `/reload` after changes** - Required for changes to take effect
4. **Datapack format** - Works on both client and server, just needs to be in the world folder

---

## 🆘 Getting Help

**Having issues?**
1. Run the Pack Checker tool to validate your files
2. Check Cobblemon Discord #support channel
3. Verify your Cobblemon version (1.4+)
4. Make sure your pack structure is correct

---

## 📜 License

Free to use and modify! Created by the Cobblemon community.

---

## 🎉 Credits

Created to make Cobblemon pack creation easier for everyone!

Special thanks to the Cobblemon development team for the Species Additions system!

---

Happy modding!
