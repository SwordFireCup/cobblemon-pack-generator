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

### Basic Info
| Argument | Description | Default |
|----------|-------------|---------|
| `--name` | Pokémon name | *required* |
| `--number` | Pokédex number | *required* |
| `--primary-type` | Primary type | `normal` |
| `--secondary-type` | Secondary type | `None` |

### Stats (All default to 50)
```bash
--hp 78 --attack 84 --defence 78 --special-attack 109 --special-defence 85 --speed 100
```

### Moves & Abilities
```bash
# Moves format: level:move OR category:move
--moves "1:tackle,1:growl,7:ember,tm:flamethrower,egg:roost,tutor:airslash"

# Abilities format: ability OR h:hiddenability
--abilities "blaze,h:solar_power"
```

**Move categories**: `0:` or `1:` (level), `egg:`, `tm:`, `tutor:`

**Note**: Level `0` is valid — it means the move is learned at evolution or from the start.

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
| `--evo-target` | Pokémon this evolves into | `None` |
| `--evo-method` | `level_up`, `item_interact`, or `trade` | `level_up` |
| `--evo-level` | Level to evolve at | `36` |
| `--evo-item` | Item required for item/trade evolution | `None` |
| `--pre-evolution` | Pokémon this evolves from | `None` |

### Physical Properties
```bash
--height 17      # In decimeters (1.7m = 17)
--weight 905     # In hectograms (90.5kg = 905)
--head-bone none # No head bone — omit this flag if your model has a head
```

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
--rarity rare                           # common|uncommon|rare|ultra-rare
--spawn-level "10-40"                   # Level range
--spawn-biomes "#minecraft:is_forest"   # Biome tags (comma-separated)
--legendary                             # Auto-sets catch rate, exp, rarity
```

### Descriptions
```bash
--desc1 "A fiery bird Pokémon that soars through the sky."
--desc2 "Its flames grow hotter when angered."
```

### Utilities
These must be used alone (not combined with `--name`/`--number`):

```bash
# Show all Pokémon currently in the pack
python pack-generator.py --show-current-pokemon

# Edit an existing Pokémon's stats, type, moves, abilities, or rarity
python pack-generator.py --edit Grayfix --hp 60 --attack 70
python pack-generator.py --edit Grayfix --moves "0:tackle,5:bite,tm:crunch" --abilities "intimidate,h:sand_rush"
python pack-generator.py --edit Grayfix --primary-type dark --rarity uncommon
```

**Warning**: `--edit` only updates what you specify. All other existing data is preserved.

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
python pack-generator.py --name Volcanodon --number 2500 --primary-type fire --secondary-type rock --hp 105 --attack 130 --defence 120 --special-attack 80 --special-defence 90 --speed 75 --moves "0:tackle,0:leer,7:ember,15:rockthrow,25:flameburst,35:rocktomb,45:lavaplume,tm:flamethrower,tm:stoneedge,egg:ancientpower" --abilities "solidrock,h:flamebody" --height 22 --weight 2500 --rarity ultra-rare --spawn-level "40-60" --spawn-biomes "#minecraft:is_nether" --desc1 "An ancient Pokémon from volcanic regions." --desc2 "Its body temperature can melt steel."
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
- **Testing**: Use `--no-cleanup` to keep original files while testing
- **Evolution chains**: Run the generator once per Pokémon in the chain, using `--evo-target` on the pre-evolution and `--pre-evolution` on the evolved form

## Troubleshooting

**"No valid files found!"**
→ Check files are in `Downloads/Mod-ResourceAndBehavior-Packs/`
→ Verify extensions: `.geo.json`, `.animation.json`, `.png`

**Pack not loading**
→ Check pack formats match your Minecraft version
→ Validate JSON with a linter
→ Ensure Cobblemon mod is installed

**Pokémon not spawning**
→ Check abilities are set — an empty abilities list prevents spawning
→ Edit spawn pool JSON in behavior pack
→ Use `/reload` after changes

**Pokémon frozen / not animating**
→ Check animation file has `animation_length` set
→ Make sure animations have actual keyframes, not just `[0, 0, 0]` placeholders

**Head not looking around**
→ Remove `rotation` entirely from the head bone in idle/walk animations
→ Make sure the poser has a `head` field matching your model's head bone name

**Wrong animations playing**
→ Check animation names: must be `animation.pokemonname.ground_idle` etc.
→ Verify poser references correct animations

## Additional Resources

- [Cobblemon Wiki](https://wiki.cobblemon.com/)
- [Blockbench](https://www.blockbench.net/)
- [Minecraft Pack Formats](https://minecraft.wiki/w/Pack_format)
- [Cobblemon Discord](https://discord.gg/cobblemon)

---
Happy Pokémon creating!
