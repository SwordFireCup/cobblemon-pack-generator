# cobblemon-pack-generator
Generates Cobblemon packs without all that fuss of the folders!
# Cobblemon Pack Generator for Minecraft 1.21.1

Automates creation of custom Pokémon for Cobblemon with **full customization** support! Creates **separate** resource and behavior packs for easier distribution.

## Quick Start

### 1. Setup
Place your Blockbench files in: `Downloads/Mod-ResourceAndBehavior-Packs/`

Required files:
- **Model**: `.geo.json` (Blockbench Bedrock geometry)
- **Animations**: `.animation.json`  
- **Textures**: `.png` or `.tga` (first = default, second = shiny)

### 2. Run the Generator

```bash
# Basic Pokémon (minimal customization)
python cobblemon_pack_generator.py --name Flamebird --number 999

# With custom types and stats
python cobblemon_pack_generator.py --name Aquadragon --number 1000 \
  --primary-type water --secondary-type dragon \
  --hp 100 --attack 80 --defence 90 --special-attack 110

# With moves and abilities
python cobblemon_pack_generator.py --name Earthgolem --number 1001 \
  --moves "1:tackle,7:rockthrow,20:earthquake,tm:stoneedge" \
  --abilities "sturdy,h:sandforce"

# Flying/Swimming Pokémon
python cobblemon_pack_generator.py --name Skywhale --number 1002 \
  --can-fly --can-swim --breathe-underwater \
  --rarity rare --spawn-biomes "#minecraft:is_ocean"
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
- ** Can combine ONLY if formats match** (change in script if needed)

##  Full Customization Options

### Basic Info
| Argument | Description | Default |
|----------|-------------|---------|
| `--name` | Pokémon name | *required* |
| `--number` | Pokédex number | *required* |
| `--primary-type` | Primary type | `normal` |
| `--secondary-type` | Secondary type | `None` |

### Stats (All default to 50)
```bash
--hp 78 --attack 84 --defence 78 \
--special-attack 109 --special-defence 85 --speed 100
```

### Moves & Abilities
```bash
# Moves format: level:move OR category:move
--moves "1:tackle,1:growl,7:ember,tm:flamethrower,egg:roost,tutor:airslash"

# Abilities format: ability OR h:hiddenability  
--abilities "blaze,h:solar_power"
```

**Move categories**: `1:` (level), `egg:`, `tm:`, `tutor:`

### Physical Properties
```bash
--height 17      # In decimeters (1.7m = 17)
--weight 905     # In hectograms (90.5kg = 905)
--head-bone none # Meaning No head bone, exclude if you have a head bone
```

### Movement & Behavior
```bash
--can-fly                # Enables flying
--can-swim               # Enables swimming  
--breathe-underwater     # Can breathe underwater
```

**Note**: Poser automatically adds water/air animations when flags are set!

### Spawn Configuration
```bash
--rarity rare                           # common|uncommon|rare|ultra-rare
--spawn-level "10-40"                   # Level range
--spawn-biomes "#minecraft:is_forest"  # Biome tags (comma-separated)
--legendary
```

### Descriptions
```bash
--desc1 "A fiery bird Pokémon that soars through the sky."
--desc2 "Its flames grow hotter when angered."
```

### Separate Utilities
Note that these must be preformed ALONE, like this: --show-current-pokemon
They also must have the file name and stuff before.
--show-current-pokemon
--edit Pokemon-Name new-pokemon-stats

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

## Complete Example

```bash
python cobblemon_pack_generator.py \
  --name Volcanodon \
  --number 2500 \
  --primary-type fire \
  --secondary-type rock \
  --hp 105 \
  --attack 130 \
  --defence 120 \
  --special-attack 80 \
  --special-defence 90 \
  --speed 75 \
  --moves "1:tackle,1:leer,7:ember,15:rockthrow,25:flameburst,35:rocktomb,45:lavaplume,tm:flamethrower,tm:stoneedge,egg:ancientpower" \
  --abilities "solid_rock,h:flame_body" \
  --height 22 \
  --weight 2500 \
  --can-swim \
  --breathe-underwater \
  --rarity ultra-rare \
  --spawn-level "40-60" \
  --spawn-biomes "#minecraft:is_nether" \
  --desc1 "An ancient Pokémon from volcanic regions." \
  --desc2 "Its body temperature can melt steel."
```
non-bashes don't need the \ after each line, just put it as a space separated string, don't forget the -- before each key
Pack Formats (Important)

```python
# In the script (top of CobblemonPackGenerator class):
RESOURCE_PACK_FORMAT = 34  # Change to 40+ if needed
DATA_PACK_FORMAT = 48      # For 1.21.1
```

**Combining packs**: Only possible if BOTH formats are the same. Since resource=34 and data=48, they **must stay separate** for 1.21.1.

If your version uses matching formats, you can:
1. Change both to same number
2. Merge `assets/` and `data/` into one folder
3. Use single `pack.mcmeta`

## File Organization

The script:
- Renames files to match Pokémon name
- Places files in correct Cobblemon directories
- Creates proper pack.mcmeta for each pack
- Generates all JSON configs (species, poser, resolver, spawn)
- Creates language file with name + descriptions
- Names shiny texture automatically (2nd texture file)

##  Blockbench Export Guide

### 1. Create Bedrock Entity
File → New → Bedrock Entity
- File Name: `yourpokemon`
- Model Identifier: `yourpokemon` (lowercase)

### 2. Required Animations
**Land Pokémon** (always needed):
- `ground_idle`
- `ground_walk`
- `sleep`
- `faint`

**Water Pokémon** (if using `--can-swim`):
- `water_idle`
- `water_swim`

**Flying Pokémon** (if using `--can-fly`):
- `air_idle`
- `air_fly`

**Animation ID format**: `animation.yourpokemon.ground_idle`

### 3. Export Files
- **Model**: File → Export → Export Bedrock Geometry → `yourpokemon.geo.json`
- **Animations**: Click export button in Animations panel → `yourpokemon.animation.json`
- **Texture**: Export texture → `yourpokemon.png`
- **Shiny** (optional): Create variant → `yourpokemon_shiny.png`

## Pro Tips

- **Stats**: Total should be 300-600 for balanced gameplay
- **Moves format**: Use proper prefixes (`1:`, `tm:`, `egg:`, `tutor:`)
- **Hidden ability**: Always prefix with `h:` (e.g., `h:solar_power`)
- **Biomes**: Use tags like `#minecraft:is_forest` or specific like `minecraft:plains`
- **Testing**: Use `--no-cleanup` to keep original files while testing
- **Combining**: Only combine packs if formats match (edit script constants)

## Troubleshooting

**"No valid files found!"**
→ Check files are in `Downloads/Mod-ResourceAndBehavior-Packs/`
→ Verify extensions: `.geo.json`, `.animation.json`, `.png`

**Pack not loading**
→ Check pack formats match your Minecraft version
→ Validate JSON with a linter
→ Ensure Cobblemon mod is installed

**Pokémon not spawning**
→ Edit spawn pool JSON in behavior pack
→ Check biome conditions
→ Use `/reload` after changes

**Wrong animations playing**
→ Check animation names in `.animation.json`
→ Must match: `animation.pokemonname.ground_idle` etc.
→ Verify poser references correct animations

## Additional Resources

- [Cobblemon Wiki](https://wiki.cobblemon.com/)
- [Blockbench](https://www.blockbench.net/)
- [Minecraft Pack Formats](https://minecraft.wiki/w/Pack_format)
- [Cobblemon Discord](https://discord.gg/cobblemon)

---
Legendary sets up the rarity if you forgot to set it.
Happy Pokémon creating!

README SECTION 2:
Importing your packs in more detail
1. Open minecraft with Cobblemon installed, this pack does not have Cobblemon assets. Check CurseForge for Cobblemon recent versions.
2. Enter Settings, Resource Packs
3. Drag the Resource Pack into the screen and put it in the ACTIVE section.
4. Click the done button and create a new world. This world will contain a data pack that allows you to interact with your pokemon.
5. Go to the third tab and click Data Packs.
6. Now drag your behavior pack into the thing and click it to put it in ACTIVE.
7. Click Done.
8. Create the rest of the world in any way you want.
9. With pokemon-name being your pokemon name, type /pokespawn pokemon-name or /pokegive pokemon-name
10. Pokespawn will spawn your pokemon while pokegive will put that pokemon in your inventory.
11. You can also find it naturally.

Happy testing!
