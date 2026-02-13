**This generator is a WIP.**

Therefore it might have **bugs** that have not been fixed.

Plus I can't make *textures* this good for moves so it is really just a W.

THIS IS ADVANCED STUFF!

Don't be sad if it dosn't work because my program is terrible.

Just a warning.

Good move creating!

# Cobblemon Move & Ability Creator

**Version 1.0 - Work in Progress**

A Python tool for creating and editing custom moves and abilities for Cobblemon through JavaScript datapacks.

---

## ⚠️ Work in Progress

This is version 1.0 and is actively being developed. Features may change, and some functionality may be incomplete or experimental. Use at your own risk and always back up your packs!

---

## 🎯 Features

### ✅ Currently Working

- **Create custom moves** with full property control
- **Create custom abilities** with stat boosts, immunities, and type boosts
- **Edit official Cobblemon moves** (creates datapack overrides)
- **Edit official Cobblemon abilities** (creates datapack overrides)
- **Edit your custom moves/abilities** in your pack
- **Automatic language file generation** for names and descriptions
- **Proper file structure** generation for Cobblemon datapacks

### 🚧 Planned Features (Future Versions)

- Interactive mode with guided prompts
- Template library for common move/ability patterns
- JavaScript syntax validation
- Import/export move/ability sets
- Batch creation from CSV/JSON
- Visual editor interface
- More complex ability effects (weather, terrain, etc.)
- Advanced move mechanics (charging moves, two-turn moves, etc.)

---

## 📦 Installation

### Requirements

- Python 3.7 or higher
- Cobblemon 1.7+ for Minecraft
- Basic understanding of Pokémon moves and abilities

### Setup

1. Download `cobblemon_move_ability_creator.py`
2. Place it in a convenient location (NOT inside your pack folders)
3. Ensure Python is installed: `python --version`
4. You're ready to go!

---

## 🚀 Quick Start

See [QUICKSTART.md](QUICKSTART.md) for a 5-minute tutorial!

---

## 📖 Usage

### Command Structure

```bash
python cobblemon_move_ability_creator.py [ACTION] [TYPE] --name [NAME] [OPTIONS]
```

**Actions:**
- `--create` - Create a new move or ability from scratch
- `--edit` - Edit an official Cobblemon move/ability (creates override)
- `--editpack` - Edit a move/ability you already created

**Types:**
- `move` - Work with moves
- `ability` - Work with abilities

---

## 🎮 Move Properties

### Basic Properties

| Flag | Description | Values | Default |
|------|-------------|--------|---------|
| `--name` | Move name (required) | Any string | - |
| `--type` | Move type | fire, water, grass, etc. | normal |
| `--category` | Move category | Physical, Special, Status | Physical |
| `--power` | Base power | 0-999 | 50 |
| `--accuracy` | Accuracy | 0-100 or "true" | 100 |
| `--max-uses` | PP/uses | 1-40 | 20 |
| `--priority` | Priority | -7 to 5 | 0 |
| `--target` | Target | normal, allAdjacent, etc. | normal |

### Advanced Properties

| Flag | Description | Example |
|------|-------------|---------|
| `--secondary-effect` | Status/stat change | `psn`, `boost:atk:1`, `flinch` |
| `--secondary-chance` | Effect chance % | `10`, `30`, `100` |
| `--recoil` | Recoil damage % | `25`, `33`, `50` |
| `--drain` | HP drain % | `50`, `75`, `100` |
| `--multihit` | Multi-hit | `2`, `5`, `"2,5"` (range) |
| `--crit-ratio` | Crit ratio | `0-4` |
| `--type-effectiveness` | Type changes | `Bug:1,Steel:-1` |

### Move Flags

- `--sound` - Sound-based move
- `--punch` - Punching move
- `--bullet` - Ballistic move

---

## ⚡ Ability Properties

| Flag | Description | Example |
|------|-------------|---------|
| `--name` | Ability name (required) | Any string |
| `--stat-boost` | Stats on switch-in | `atk:1,def:1` |
| `--immunity-type` | Type immunity | `fire`, `water` |
| `--type-boost` | Boost move type | `fire:1.5` |
| `--heal-amount` | Heal % per turn | `12`, `25` |

---

## 💡 Examples

### Create a Custom Ice Move
```bash
python cobblemon_move_ability_creator.py --create move \
  --name "ice-blast" \
  --type ice \
  --category Special \
  --power 90 \
  --accuracy 100 \
  --max-uses 15 \
  --secondary-effect frz \
  --secondary-chance 10
```

### Create a Custom Ability
```bash
python cobblemon_move_ability_creator.py --create ability \
  --name "flame-aura" \
  --stat-boost "atk:1,spa:1" \
  --type-boost "fire:1.3"
```

### Edit Official Move (Override)
```bash
python cobblemon_move_ability_creator.py --edit move flamethrower \
  --power 100 \
  --accuracy 95
```

### Edit Your Custom Move
```bash
python cobblemon_move_ability_creator.py --editpack move ice-blast \
  --power 95 \
  --max-uses 20
```

---

## 📁 File Structure

The tool creates files in this structure:

```
Mod-ResourceAndBehavior-Packs/
├── behavior_pack/
│   └── data/cobblemon/
│       ├── moves/
│       │   └── your-move.js
│       └── abilities/
│           └── your-ability.js
└── resource_pack/
    └── assets/cobblemon/lang/
        └── en_us.json
```

---

## 🔧 How It Works

### Moves

The tool generates JavaScript files that Cobblemon's battle engine (based on Pokémon Showdown) reads. Each move is a `.js` file containing a JavaScript object with the move's properties and effects.

**Example output (`ice-blast.js`):**
```javascript
{
  accuracy: 100,
  basePower: 90,
  category: "Special",
  name: "Ice Blast",
  pp: 15,
  priority: 0,
  flags: {"protect": 1, "mirror": 1},
  secondary: {
    chance: 10,
    status: "frz"
  },
  target: "normal",
  type: "Ice"
}
```

### Abilities

Similar to moves, abilities are JavaScript objects that define when and how they activate.

**Example output (`flame-aura.js`):**
```javascript
{
  onStart(pokemon) {
    this.add("-ability", pokemon, "Flame Aura");
    this.boost({"atk": 1, "spa": 1}, pokemon);
  },
  onBasePower(basePower, pokemon, target, move) {
    if (move.type === "Fire") {
      return this.chainModify(1.3);
    }
  },
  flags: {},
  name: "Flame Aura",
  rating: 3
}
```

---

##  Advanced Usage

### Custom Pack Path

By default, the tool looks for packs in `~/Downloads/Mod-ResourceAndBehavior-Packs`. To use a different location:

```bash
python cobblemon_move_ability_creator.py --create move \
  --name "my-move" \
  --pack-path "/path/to/your/packs"
```

### Adding Descriptions

Use `--description` to set the language file entry:

```bash
python cobblemon_move_ability_creator.py --create move \
  --name "ice-blast" \
  --description "A powerful ice attack that may freeze the target."
```

---

##  Known Limitations

### Version 1.0 Limitations

1. **JavaScript Generation** - Complex custom logic must be manually edited
2. **Edit Functionality** - Editing rebuilds files; custom JS code will be lost
3. **No Validation** - JavaScript syntax is not validated (yet)
4. **Limited Ability Effects** - Only basic effects supported
5. **No Templates** - No pre-built templates for common patterns (yet)
6. **Single Language** - Only English (`en_us.json`) supported

### Workarounds

- **Complex Logic** - Manually edit the `.js` files after generation
- **Preserve Custom Code** - Back up files before using `--editpack`
- **Syntax Errors** - Test in-game and check logs for JS errors
- **Advanced Abilities** - Reference Pokémon Showdown documentation

---

##  Resources

### Official Documentation

- [Cobblemon Wiki - Custom Pokemon](https://wiki.cobblemon.com/creating-a-custom-pokemon)
- [Cobblemon Wiki - Move Effects](https://wiki.cobblemon.com/datapackable-move-effects)
- [Pokémon Showdown Repository](https://github.com/smogon/pokemon-showdown)

### Helpful Links

- [Cobblemon Discord](https://discord.gg/cobblemon)
- [Blockbench](https://www.blockbench.net) - For creating models
- [JavaScript Tutorial](https://javascript.info) - If you want to write custom logic

---

##  Contributing

This is a work-in-progress tool! Contributions, bug reports, and feature requests are welcome.

### How to Contribute

1. Test the tool and report bugs
2. Suggest new features or improvements
3. Share templates for common move/ability patterns
4. Improve documentation

---

##  Roadmap
The Future Of The Ability Generator
- [ ] JavaScript syntax validation
- [ ] Better error messages
- [ ] Template library
- [ ] Batch operations
- [ ] Advanced ability effects (weather, terrain)
- [ ] Troubleshooting pack

---

##  License

This tool is provided as-is for use with Cobblemon. Use freely and modify as needed!

---

##  Credits

Created for the Cobblemon community. Special thanks to:
- Cobblemon development team
- Pokémon Showdown contributors
- Community members who tested and provided feedback

---

**Version 1.0** - Initial WIP Release

---

## Need Help?

- Check [QUICKSTART.md](QUICKSTART.md) for tutorials
- Visit the [Cobblemon Discord](https://discord.gg/cobblemon)
- Read the [Cobblemon Wiki](https://wiki.cobblemon.com)

**Remember:** This is an advanced tool for experienced users. No troubleshooting section is provided - you're expected to figure things out!
