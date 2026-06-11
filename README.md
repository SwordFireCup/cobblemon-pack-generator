# Cobblemon Pack Generator for Minecraft 1.21.1

Automates creation of custom Pokémon for Cobblemon with **full customization** support! Creates **separate** resource and behavior packs for easier distribution.

**Current version: 2.6** — verify your copy with:
```bash
python pack-generator.py --version
```
If this errors or shows an older number, your download is truncated or stale — re-download before doing anything else.

## Quick Start

### 1. Setup
Place your Blockbench files in: `Downloads/Mod-ResourceAndBehavior-Packs/`

Required files:
- **Model**: `.geo.json` (Blockbench Bedrock geometry)
- **Animations**: `.animation.json`
- **Textures**: `.png` or `.tga` (a filename containing `shiny` goes to the shiny slot; everything else is the default texture)

### 2. Run the Generator

```bash
# Basic Pokémon (minimal customization)
python pack-generator.py --name Flamebird --number 999

# With custom types and stats
python pack-generator.py --name Aquadragon --number 1000 --primary-type water --secondary-type dragon --hp 100 --attack 80 --defence 90 --special-attack 110

# With moves and abilities
python pack-generator.py --name Earthgolem --number 1001 --moves "1:tackle,7:rockthrow,20:earthquake,tm:stoneedge" --abilities "sturdy,h:sandforce"

# Flying/Swimming Pokémon
python pack-generator.py --name Skywhale --number 1002 --can-fly --can-swim --breathe-underwater --rarity rare --spawn-biomes "#minecraft:is_ocean"

# With evolution
python pack-generator.py --name Grayfix --number 1 --primary-type dark --secondary-type ground --evo-target brightfix --evo-method level_up --evo-level 28

# Evolution target (set pre-evolution back-link)
python pack-generator.py --name Brightfix --number 2 --primary-type normal --secondary-type ground --pre-evolution grayfix

# A cave-dwelling Pokémon with custom catch rate and drops
python pack-generator.py --name Gloomite --number 1003 --catch-rate 90 --can-see-sky false --spawn-biomes "#minecraft:is_dripstone_caves" --drops "minecraft:redstone:50,cobblemon:exp_candy_xs:10"
```

### 3. Result - Two Separate Packs

```
Downloads/Mod-ResourceAndBehavior-Packs/
├── resource_pack/
│   ├── pack.mcmeta (format 34)
│   └── assets/cobblemon/
│       ├── bedrock/pokemon/
│       │   ├── models/pokemonname/pokemonname.geo.json
│       │   ├── animations/pokemonname/pokemonname.animation.json
│       │   ├── posers/pokemonname.json
│       │   └── resolvers/0_pokemonname_base.json
│       ├── textures/pokemon/pokemonname/
│       │   ├── pokemonname.png
│       │   └── pokemonname_shiny.png
│       └── lang/en_us.json
│
└── behavior_pack/
    ├── pack.mcmeta (format 48)
    └── data/cobblemon/
        ├── species/custom/pokemonname.json
        └── spawn_pool_world/pokemonname.json
```

## Why Separate Packs?

- **Easier distribution**: Share resource or behavior pack independently
- **Server-friendly**: Servers only need behavior pack
- **Client flexibility**: Players can use just resources if server has data
- **Different pack formats**: Resource (34) vs Data (48) for 1.21.1
- **Can only combine if formats match** (change in script if needed)

## Full Customization Options

All of these work in **both create and edit modes**. Defaults listed apply on create; `--edit` only changes what you explicitly pass.

### Basic Info
| Argument | Description | Default on create |
|----------|-------------|-------------------|
| `--name` | Pokémon name | *required (create)* |
| `--number` | Pokédex number (edit warns on duplicates) | *required (create)* |
| `--primary-type` | Primary type | `normal` |
| `--secondary-type` | Secondary type (`none` in edit mode removes it) | none |

### Stats (All default to 50 on create)
```bash
--hp 78 --attack 84 --defence 78 --special-attack 109 --special-defence 85 --speed 100
```

### Species Fields
| Argument | Description | Default on create |
|----------|-------------|-------------------|
| `--catch-rate` (or `--catchrate`) | 3 (legendary-hard) to 255 (trivial) | `45` |
| `--male-ratio` | -1 = genderless, 0 = all female, 1 = all male | `0.5` |
| `--exp-group` | slow, medium_slow, medium_fast, fast, erratic, fluctuating | `medium_fast` |
| `--egg-cycles` | Hatch time | `20` |
| `--egg-groups` | Comma-separated, e.g. `"mineral,amorphous"` | `field` |
| `--base-exp` | Base experience yield | `100` |
| `--friendship` | Base friendship | `50` |
| `--ev-yield` | e.g. `"speed:2"` or `"attack:1,hp:1"` (vanilla total max 3) | `hp:1` |
| `--drops` | `item:percentage` list, e.g. `"minecraft:redstone:50"` | none |
| `--base-scale` | Model scale multiplier | model default |
| `--hitbox` | `"width,height"`, e.g. `"1.5,2"` | model default |

### Moves & Abilities
```bash
# Moves format: level:move OR category:move
--moves "1:tackle,1:growl,7:ember,tm:flamethrower,egg:roost,tutor:airslash"

# Abilities format: ability OR h:hiddenability
--abilities "blaze,h:solar_power"
```

**Move categories**: `0:` or `1:` (level), `egg:`, `tm:`, `tutor:`

**Note**: Level `0` is valid — it means the move is learned at evolution or from the start.

**Warning**: `--moves` REPLACES the whole list (in create and edit alike). In edit mode, use `--add-moves` to append instead (see Editing below).

### Evolution
```bash
# Basic level-up evolution
--evo-target brightfix --evo-method level_up --evo-level 28

# Item interaction evolution
--evo-target brightfix --evo-method item_interact --evo-item "cobblemon:dragon_scale"

# Trade evolution (optional held item)
--evo-target brightfix --evo-method trade --evo-item "cobblemon:metal_coat"

# Mark the evolution target's pre-evolution
--pre-evolution grayfix
```

| Argument | Description | Default |
|----------|-------------|---------|
| `--evo-target` | Pokémon this evolves into | none |
| `--evo-method` | `level_up`, `item_interact`, or `trade` | `level_up` |
| `--evo-level` | Level to evolve at | `36` |
| `--evo-item` | Item required for item/trade evolution | none |
| `--pre-evolution` | Pokémon this evolves from | none |

In **edit mode**, evolutions are smart: same target replaces that evolution in place (re-running won't stack duplicates), a different target adds a second branch (Eevee-style), and `--remove-evolutions` clears them all.

### Physical Properties
```bash
--height 17      # In decimeters (1.7m = 17)
--weight 905     # In hectograms (90.5kg = 905)
--head-bone none # No head bone — omit this flag if your model has a head
```

In edit mode, `--head-bone none` does the full three-part fix (deletes the poser's `head` field, strips `look` animations, sets `canLook: false`), and `--head-bone <bone>` reverses it.

### Movement & Behavior
```bash
--can-fly                # Enables flying
--can-swim               # Enables swimming
--breathe-underwater     # Can breathe underwater
--no-look                # Disables head look tracking (canLook=false)
```

**Note**: Poser automatically adds water/air animation poses when flags are set.

### Spawn Configuration
```bash
--rarity rare                           # common|uncommon|rare|ultra-rare (edit: applies to ALL entries)
--spawn-level "10-40"                   # Level range (edit: applies to ALL entries)
--spawn-biomes "#minecraft:is_forest"   # Biome tags, comma-separated (edit: ALL entries)
--spawn-weight 4.5                      # Spawn weight (default 10; explicit value overrides legendary 0.05)
--can-see-sky false                     # false = underground/cave spawner
--legendary                             # Auto-sets catch rate, exp, rarity, weight 0.05
```

### Multiple Spawn Entries (edit mode only)

Give one Pokémon several spawn configurations — e.g. common on the surface, rare in caves:

```bash
# Append an entry: key=value pairs, ';' between items inside lists
python pack-generator.py --edit gloomite --append "bucket=rare,level=30-50,weight=3,biomes=#minecraft:is_dripstone_caves;#minecraft:is_deep_dark,canSeeSky=false"

# Raw JSON also works
python pack-generator.py --edit gloomite --append "{\"bucket\":\"uncommon\",\"level\":\"10-20\"}"

# Remove by 1-based index (same numbering the pack checker reports), or the last one
python pack-generator.py --edit gloomite --removespawn 2
python pack-generator.py --edit gloomite --removelastspawn

# Replace the WHOLE spawns array: entries separated by '|', requires --confirmset
python pack-generator.py --edit gloomite --spawnset "bucket=common,level=5-30|bucket=ultra-rare,level=45-60,weight=0.5" --confirmset
```

- `--spawnset` **without** `--confirmset` prints a preview of what would be written and changes nothing.
- Appended entries get the same defaults as creation, and ids auto-number (`gloomite-2`, `gloomite-3`, ...).
- Valid keys: `bucket, level, weight, biomes, canSeeSky, context, presets, id, pokemon`. Invalid buckets are rejected before anything is written.
- `--spawnset` can't be combined with `--append`/`--removespawn`/`--removelastspawn` in one command.

### Descriptions
```bash
--desc1 "A fiery bird Pokémon that soars through the sky."
--desc2 "Its flames grow hotter when angered."
```

## Editing Pokémon

```bash
python pack-generator.py --edit Grayfix --hp 60 --attack 70
python pack-generator.py --edit Grayfix --primary-type dark --rarity uncommon
python pack-generator.py --edit Grayfix --number 1102 --catch-rate 60
python pack-generator.py --edit Grayfix --evo-target brightfix --evo-level 25
```

**Everything you can generate, you can edit!** `--edit` only updates what you specify; all other existing data is preserved.

### Edit-only extras

| Argument | Description |
|----------|-------------|
| `--add-moves "7:spark,15:discharge"` | APPENDS moves (with dedupe) instead of replacing the list |
| `--remove-evolutions` | Remove all evolutions |
| `--not-legendary` | Remove legendary status (reminds you about spawn weight) |
| `--secondary-type none` | Make the Pokémon mono-type |
| `--rename <newname>` | Full rename across every file (see below) |
| `--append` / `--removespawn` / `--removelastspawn` / `--spawnset` | Spawn entry management (see above) |

### Renaming

```bash
python pack-generator.py --edit grayfix --rename shadowfix
```

Updates **every** site in one shot: species file (name, pokedex keys, evolution ids, filename), spawn file (pokemon fields, ids, filename), model geometry identifier + file + folder, animation key prefixes + file + folder, poser `bedrock()` refs + filename, resolver refs + filename, texture files + folder, lang keys and display name, **other species'** evolutions and preEvolution pointing at it, and species_additions targets. Rejects invalid names and collisions. If your Pokédex description text mentions the old name, it warns (prose isn't auto-rewritten — use `--desc1`/`--desc2`).

Run the pack checker afterward to verify — its cross-reference checks cover exactly the sites a rename touches.

### Swapping Asset Files (--editfiles)

Replace a Pokémon's model, animations, or textures without touching its data:

```bash
# 1. Drop the new files in Downloads/Mod-ResourceAndBehavior-Packs/
# 2. Swap them in:
python pack-generator.py --editfiles grayfix
```

Whichever of model / animation / base texture / shiny texture are present get installed (shiny detected by `shiny` in the filename). The **old** files are moved out into the pack folder — so running `--editfiles grayfix` again swaps them back. One-command undo.

Notes:
- The backup is one level deep: swapping in a second new model overwrites the saved original (it warns when this happens).
- Incoming files are sanity-checked (geometry identifier, animation key prefixes) with immediate warnings if they'd break rendering.

### Other utilities

```bash
# Show all Pokémon currently in the pack (dex, types, BST, legendary, catch rate)
python pack-generator.py --show-current-pokemon

# Which version is on disk?
python pack-generator.py --version
```

## Installation

Since packs are **separate**, install both:

### Step 1: Install Resource Pack
```
Copy: resource_pack/
To:   .minecraft/resourcepacks/cobblemon_custom_resource_pack/
```

### Step 2: Install Behavior Pack
```
Copy: behavior_pack/
To:   .minecraft/saves/YourWorld/datapacks/cobblemon_custom_behavior_pack/
```

### Step 3: Enable & Test
1. Start Minecraft
2. Options → Resource Packs → Enable your pack
3. Load world (datapack auto-loads)
4. Run `/reload` to refresh data
5. Test: `/pokespawn yourpokemon`

## Importing Your Packs (Detailed)

1. Open Minecraft with Cobblemon installed. This pack does not include Cobblemon assets — check CurseForge for the latest version.
2. Enter **Settings → Resource Packs**.
3. Drag the resource pack into the window and move it to the **Active** section.
4. Click **Done** and create a new world.
5. On the world creation screen go to the third tab and click **Data Packs**.
6. Drag your behavior pack in and click it to move it to **Active**.
7. Click **Done** and finish creating the world.
8. Once in-game, use `/pokespawn pokemon-name` to spawn your Pokémon, or `/pokegive pokemon-name` to add it to your party.
9. Your Pokémon will also spawn naturally based on its spawn pool configuration.

## Complete Example

```bash
python pack-generator.py --name Volcanodon --number 2500 --primary-type fire --secondary-type rock --hp 105 --attack 130 --defence 120 --special-attack 80 --special-defence 90 --speed 75 --moves "0:tackle,0:leer,7:ember,15:rockthrow,25:flameburst,35:rocktomb,45:lavaplume,tm:flamethrower,tm:stoneedge,egg:ancientpower" --abilities "solidrock,h:flamebody" --height 22 --weight 2500 --catch-rate 30 --ev-yield "attack:2,defence:1" --drops "minecraft:magma_block:33" --rarity ultra-rare --spawn-level "40-60" --spawn-biomes "#minecraft:is_nether" --desc1 "An ancient Pokémon from volcanic regions." --desc2 "Its body temperature can melt steel."
```

## Pack Formats

```python
# In the script (top of CobblemonPackGenerator class):
RESOURCE_PACK_FORMAT = 34  # Change to 40+ if needed
DATA_PACK_FORMAT = 48      # For 1.21.1
```

**Combining packs**: Only possible if BOTH formats are the same. Since resource=34 and data=48 for 1.21.1, they must stay separate. If your version uses matching formats you can merge `assets/` and `data/` into one folder with a single `pack.mcmeta`.

## Blockbench Export Guide

### 1. Create Bedrock Entity
File → New → Bedrock Entity
- File Name: `yourpokemon`
- Model Identifier: `yourpokemon` (lowercase)

### 2. Required Animations
**All Pokémon**:
- `ground_idle`
- `ground_walk`
- `sleep`
- `faint`

**Recommended** (Cobblemon falls back to `ground_idle` without it, but battles look better):
- `battle_idle`

**Water Pokémon** (if using `--can-swim`):
- `water_idle`
- `water_swim`

**Flying Pokémon** (if using `--can-fly`):
- `air_idle`
- `air_fly`

**Animation ID format**: `animation.yourpokemon.ground_idle`

**Tip**: If you want the head to look around freely, do NOT include a `rotation` key on the head bone in your idle/walk animations — even `[0, 0, 0]` will lock it. Only use `position` for bobs and sways.

### 3. Export Files
- **Model**: File → Export → Export Bedrock Geometry → `yourpokemon.geo.json`
- **Animations**: Click export in Animations panel → `yourpokemon.animation.json`
- **Texture**: Export texture → `yourpokemon.png`
- **Shiny** (optional): Create variant → `yourpokemon_shiny.png`

The generator will rename files correctly on copy — you can export with underscores (`yourpokemon_geo.json`) and it will fix them.

## Pro Tips

- **Stats**: Total BST should be 300–600 for balanced gameplay
- **Moves**: Use level `0` for moves learned at evolution or from the start
- **Hidden ability**: Always prefix with `h:` (e.g., `h:solar_power`)
- **Biomes**: Use tags like `#minecraft:is_forest` or specific like `minecraft:plains`
- **Catch rates**: 3 = legendary-hard, 45 = starter-ish, 255 = trivially easy
- **Testing**: Use `--no-cleanup` to keep original files while testing
- **Evolution chains**: Run the generator once per Pokémon in the chain, using `--evo-target` on the pre-evolution and `--pre-evolution` on the evolved form. Both also work in `--edit` after the fact.
- **Validate often**: run the companion **Pack Checker** (separate tool/branch) after generating, editing, renaming, or swapping files — it cross-checks every reference between your files
- **After downloading a new script version**: run `--version` first. A truncated download throws an error instead of printing the version.

## Troubleshooting

**"No valid files found!"**
→ Check files are in `Downloads/Mod-ResourceAndBehavior-Packs/`
→ Verify extensions: `.geo.json`, `.animation.json`, `.png`

**Pack not loading**
→ Check pack formats match your Minecraft version
→ Validate JSON with a linter (or run the Pack Checker)
→ Ensure Cobblemon mod is installed

**Pokémon not spawning**
→ Check abilities are set — an empty abilities list prevents spawning
→ Check spawn weight isn't 0 (and wasn't left at the legendary 0.05 after `--not-legendary`)
→ Use `--edit name --append ...` / `--spawnset ...` to fix spawn entries from the CLI
→ Use `/reload` after changes

**Pokémon frozen / not animating**
→ Check animation file has `animation_length` set
→ Make sure animations have actual keyframes, not just `[0, 0, 0]` placeholders

**Head not looking around**
→ Remove `rotation` entirely from the head bone in idle/walk animations
→ Make sure the poser has a `head` field matching your model's head bone name
→ Model has no head at all? `--edit name --head-bone none` fixes poser + species in one command

**Wrong animations playing**
→ Check animation names: must be `animation.pokemonname.ground_idle` etc.
→ Verify poser references correct animations (the Pack Checker validates every `bedrock()` reference)

**`IndentationError` / `SyntaxError` when running the script**
→ Your copy is truncated (usually from copy-paste instead of downloading). Re-download; the file should end with `if __name__ == "__main__":` followed by `    main()`, and `--version` should print cleanly.

## Version History

| Version | Highlights |
|---------|-----------|
| 2.6 | Multi-spawn-entry management (`--append`, `--removespawn`, `--removelastspawn`, `--spawnset --confirmset`) |
| 2.5 | Catch rate, gender ratio, exp group, egg groups/cycles, EV yield, drops, base scale, hitbox, friendship, spawn weight, `--can-see-sky`, `--not-legendary`, `--secondary-type none`, `--add-moves` |
| 2.4 | Emoji-free console output (Windows terminal safe) |
| 2.3 | Full `--edit` parity with creation; `--editfiles` asset swap with undo; `--rename` across all files |
| 2.2 | `--edit` supports number, evolutions, head bone; `--version` flag; shiny detection by filename; major edit-mode bug fixes |

## Additional Resources

- [Cobblemon Wiki](https://wiki.cobblemon.com/)
- [Blockbench](https://www.blockbench.net/)
- [Minecraft Pack Formats](https://minecraft.wiki/w/Pack_format)
- [Cobblemon Discord](https://discord.gg/cobblemon)

---
Happy Pokémon creating!
