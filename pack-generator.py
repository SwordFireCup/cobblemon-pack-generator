#!/usr/bin/env python3
"""
Cobblemon Pokémon Pack Generator for Minecraft 1.21.1
Creates SEPARATE resource and behavior packs for easier distribution

v2.2 changelog (2026-06-10):
  - FIX: --show-current-pokemon / --edit crashed with NameError
  - FIX: --edit silently reset base stats to 50 (argparse default leak)
  - FIX: --edit silently reset primary type to 'normal' and rarity to 'common'
         (same default leak; all edit-mode flags now audited, default=None)
  - FIX: shiny texture assignment no longer depends on directory order
  - NEW: --edit supports --number (with duplicate-dex warning)
  - NEW: --edit supports evolutions (--evo-target/-method/-level/-item,
         dedupes by id, supports branches, --remove-evolutions)
  - NEW: --edit supports --head-bone none / --head-bone <bone> / --no-look
         (updates poser head field, look animations, and species canLook)
  - NEW: --version flag to verify which build is on disk
v2.3 changelog (2026-06-11):
  - NEW: --edit parity with creation: --height, --weight, --can-fly,
         --can-swim, --breathe-underwater, --spawn-level, --spawn-biomes
         (all spawn entries), --desc1/--desc2, --pre-evolution
  - NEW: --editfiles <pokemon>: swap in new model/animation/texture files
         from the pack folder; old files moved out for one-command undo
  - NEW: --edit <old> --rename <new>: renames across ALL sites (species,
         spawn, model id, animation keys, poser refs, resolver, textures,
         lang, other species evolutions/preEvolution, species_additions)
v2.4 changelog (2026-06-11):
  - CHANGE: emoji-free console output (ASCII labels: [OK], ERROR:, WARNING:,
            NOTE:, TIP:) for Windows terminal compatibility
v2.5 changelog (2026-06-11):
  - NEW: species fields in BOTH create and edit: --catch-rate (alias
         --catchrate), --male-ratio, --exp-group, --egg-cycles, --egg-groups,
         --base-exp, --friendship, --ev-yield, --drops, --base-scale, --hitbox
  - NEW: spawn fields in both modes: --spawn-weight, --can-see-sky
         (false = cave spawner; explicit --spawn-weight overrides the
         legendary 0.05 auto-weight)
  - NEW: --not-legendary (edit) removes legendary status
  - NEW: --secondary-type none (edit) removes secondary type (mono-type)
  - NEW: --add-moves (edit) APPENDS moves instead of replacing
  - CHANGE: --rarity edit now applies to ALL spawn entries (was first only)
"""

GENERATOR_VERSION = "2.5"

import os
import json
import shutil
from pathlib import Path
from typing import Dict, List, Optional
import argparse


VALID_EXP_GROUPS = {"slow", "medium_slow", "medium_fast", "fast", "erratic", "fluctuating"}
VALID_EGG_GROUPS = {"monster", "water1", "bug", "flying", "field", "fairy", "grass", "humanlike",
                    "water3", "mineral", "amorphous", "water2", "ditto", "dragon", "undiscovered"}
EV_STATS = ("hp", "attack", "defence", "special_attack", "special_defence", "speed")


def parse_ev_yield(spec: str):
    """Parse "speed:2,attack:1" into a full six-stat dict (unspecified -> 0)."""
    result = {s: 0 for s in EV_STATS}
    aliases = {"spatk": "special_attack", "spdef": "special_defence", "spa": "special_attack",
               "spd": "special_defence", "def": "defence", "atk": "attack", "spe": "speed"}
    for part in spec.split(','):
        if ':' not in part:
            raise ValueError(f"'{part}' is not stat:amount")
        stat, amount = part.rsplit(':', 1)
        stat = aliases.get(stat.strip().lower(), stat.strip().lower())
        if stat not in result:
            raise ValueError(f"unknown stat '{stat}' (valid: {', '.join(EV_STATS)})")
        result[stat] = int(amount)
    return result


def parse_drops(spec: str):
    """Parse "minecraft:redstone:50,cobblemon:exp_candy_xs:10" into drop entries.
    The LAST colon-separated field is the percentage; the rest is the item id."""
    entries = []
    for part in spec.split(','):
        if ':' not in part:
            raise ValueError(f"'{part}' is not item:percentage")
        item, pct = part.rsplit(':', 1)
        entries.append({"item": item.strip(), "percentage": float(pct.strip())})
    return entries


def parse_hitbox(spec: str):
    """Parse "width,height" into a hitbox dict."""
    w, h = spec.split(',', 1)
    return {"width": float(w.strip()), "height": float(h.strip()), "fixed": False}


class CobblemonPackGenerator:
    """Generates separate Cobblemon resource and behavior packs"""

    # Pack formats for 1.21.1
    RESOURCE_PACK_FORMAT = 34  # Change to 40+ if needed for newer versions
    DATA_PACK_FORMAT = 48  # Data pack format for 1.21.1

    def __init__(self, downloads_path: str = None):
        """Initialize the pack generator"""
        if downloads_path is None:
            downloads_path = str(Path.home() / "Downloads")

        self.base_dir = Path(downloads_path) / "Mod-ResourceAndBehavior-Packs"

        # Separate packs for easier distribution
        self.resource_pack_dir = self.base_dir / "resource_pack"
        self.behavior_pack_dir = self.base_dir / "behavior_pack"

        # Expected file types
        self.animation_extensions = ['.animation.json', '.animations.json']
        self.model_extensions = ['.geo.json', '.json']
        self.texture_extensions = ['.png', '.tga']

    def create_pack_mcmeta(self, pack_type: str) -> Dict:
        """Create pack.mcmeta for resource or behavior pack

        Note: Packs can only be combined into one folder if both formats match!
        For 1.21.1: Resource = 34 (or 40+), Data = 48
        """
        if pack_type == 'resource':
            return {
                "pack": {
                    "pack_format": self.RESOURCE_PACK_FORMAT,
                    "description": "Cobblemon Custom Pokémon - Resource Pack"
                }
            }
        else:  # behavior/data pack
            return {
                "pack": {
                    "pack_format": self.DATA_PACK_FORMAT,
                    "description": "Cobblemon Custom Pokémon - Data Pack"
                }
            }

    def setup_directories(self, pokemon_name: str):
        """Create directory structure for both packs"""
        print(f"\nSetting up directory structure for {pokemon_name}...")

        pokemon_lower = pokemon_name.lower()

        # Resource pack directories
        resource_dirs = [
            self.resource_pack_dir / "assets" / "cobblemon" / "bedrock" / "pokemon" / "models" / pokemon_lower,
            self.resource_pack_dir / "assets" / "cobblemon" / "bedrock" / "pokemon" / "animations" / pokemon_lower,
            self.resource_pack_dir / "assets" / "cobblemon" / "bedrock" / "pokemon" / "posers",
            self.resource_pack_dir / "assets" / "cobblemon" / "bedrock" / "pokemon" / "resolvers",
            self.resource_pack_dir / "assets" / "cobblemon" / "textures" / "pokemon" / pokemon_lower,
            self.resource_pack_dir / "assets" / "cobblemon" / "lang",
        ]

        # Behavior pack (data pack) directories
        behavior_dirs = [
            self.behavior_pack_dir / "data" / "cobblemon" / "species" / "custom",
            self.behavior_pack_dir / "data" / "cobblemon" / "species_features",
            self.behavior_pack_dir / "data" / "cobblemon" / "spawn_pool_world",
        ]

        for directory in resource_dirs + behavior_dirs:
            directory.mkdir(parents=True, exist_ok=True)

        print("[OK] Directory structure created!")

    def find_files_in_base_dir(self) -> Dict[str, List[Path]]:
        """Find all relevant files in the base directory (excludes Python scripts)"""
        files = {
            'animations': [],
            'models': [],
            'textures': [],
            'other': []
        }

        if not self.base_dir.exists():
            print(f"WARNING: Base directory not found: {self.base_dir}")
            return files

        for file in self.base_dir.iterdir():
            # Skip directories, Python files, and hidden files
            if not file.is_file():
                continue
            if file.suffix == '.py':
                continue
            if file.name.startswith('.'):
                continue

            # Check animations
            if any(file.name.endswith(ext) for ext in self.animation_extensions):
                files['animations'].append(file)
            # Check models
            elif any(file.name.endswith(ext) for ext in self.model_extensions):
                if 'geo' in file.name.lower() or 'model' in file.name.lower():
                    files['models'].append(file)
                else:
                    files['other'].append(file)
            # Check textures
            elif any(file.name.endswith(ext) for ext in self.texture_extensions):
                files['textures'].append(file)
            else:
                files['other'].append(file)

        return files

    def create_species_json(self, pokemon_name: str, config: Dict) -> Dict:
        """Create species definition with customization options"""
        pokemon_lower = pokemon_name.lower()

        # Parse moves if provided
        moves = []
        if config.get('moves'):
            moves = [m.strip() for m in config['moves'].split(',')]

        # Parse abilities if provided
        abilities = []
        if config.get('abilities'):
            abilities = [a.strip() for a in config['abilities'].split(',')]
            print(f"  NOTE: Abilities configured: {abilities}")
        else:
            print(f"  WARNING: No abilities specified! Pokémon will fail to spawn!")
            print(f"     Use --abilities to add abilities (e.g., --abilities \"blaze,h:solar_power\")")

        # Parse types
        primary_type = config.get('primary_type', 'normal')
        secondary_type = config.get('secondary_type')

        # Get labels - add legendary if flagged
        labels = config.get('labels', ['custom'])
        if config.get('legendary') and 'legendary' not in labels:
            labels.append('legendary')

        return {
            "implemented": True,
            "name": pokemon_lower,
            "labels": labels,
            "pokedex": [
                f"cobblemon.species.{pokemon_lower}.desc1",
                f"cobblemon.species.{pokemon_lower}.desc2"
            ],
            "nationalPokedexNumber": config['pokedex_number'],
            "primaryType": primary_type,
            "secondaryType": secondary_type,
            "baseStats": {
                "hp": config.get('hp', 50),
                "attack": config.get('attack', 50),
                "defence": config.get('defence', 50),
                "special_attack": config.get('special_attack', 50),
                "special_defence": config.get('special_defence', 50),
                "speed": config.get('speed', 50)
            },
            "catchRate": config.get('catch_rate', 45),
            "maleRatio": config.get('male_ratio', 0.5),
            "baseExperienceYield": config.get('base_exp', 100),
            "experienceGroup": config.get('exp_group', 'medium_fast'),
            "eggCycles": config.get('egg_cycles', 20),
            "eggGroups": config.get('egg_groups', ['field']),
            "baseFriendship": config.get('friendship', 50),
            "evYield": (parse_ev_yield(config['ev_yield_spec'])
                        if config.get('ev_yield_spec') else
                        {"hp": 1, "attack": 0, "defence": 0,
                         "special_attack": 0, "special_defence": 0, "speed": 0}),
            "height": config.get('height', 10),
            "weight": config.get('weight', 100),
            "aspects": [],
            "cannotDynamax": False,
            "drops": {
                "amount": "1-2",
                "entries": parse_drops(config['drops_spec']) if config.get('drops_spec') else []
            },
            **({"baseScale": float(config['base_scale'])} if config.get('base_scale') else {}),
            **({"hitbox": parse_hitbox(config['hitbox_spec'])} if config.get('hitbox_spec') else {}),
            "moves": moves,
            "abilities": abilities,
            "evolutions": self._build_evolutions(pokemon_lower, config),
            "preEvolution": config.get('pre_evolution'),
            "behaviour": {
                "moving": {
                    # canLook must be false if no head bone, otherwise true by default
                    "canLook": False if (config.get('head_bone', 'head').lower() == 'none') else config.get('can_look',
                                                                                                            True),
                    "fly": {
                        "canFly": config.get('can_fly', False)
                    },
                    "swim": {
                        "swimSpeed": 0.3,
                        "canSwimInWater": config.get('can_swim', False),
                        "canBreatheUnderwater": config.get('breathe_underwater', False)
                    }
                }
            }
        }

    def _build_evolutions(self, pokemon_lower: str, config: Dict) -> list:
        """Build evolutions list from config"""
        if not config.get('evo_target'):
            return []

        evo_target = config['evo_target'].lower()
        evo_method = config.get('evo_method', 'level_up')

        evolution = {
            "id": f"{pokemon_lower}_{evo_target}",
            "variant": evo_method,
            "result": evo_target,
            "consumeHeldItem": False,
            "learnableMoves": [],
            "requirements": []
        }

        if evo_method == 'level_up':
            evolution["requirements"].append({
                "variant": "level",
                "minLevel": config.get('evo_level', 36)
            })
        elif evo_method == 'item_interact':
            evo_item = config.get('evo_item', 'minecraft:stone')
            evolution["requiredContext"] = evo_item
        elif evo_method == 'trade':
            if config.get('evo_item'):
                evolution["requirements"].append({
                    "variant": "held_item",
                    "item": config['evo_item']
                })

        return [evolution]

    def create_poser_json(self, pokemon_name: str, config: Dict) -> Dict:
        """Create poser configuration"""
        pokemon_lower = pokemon_name.lower()

        # Check if head bone exists
        has_head_bone = config.get('head_bone', 'head').lower() != 'none'

        # Build base animations for standing pose
        standing_animations = []
        if has_head_bone:
            standing_animations.append("look")
        standing_animations.append(f"bedrock({pokemon_lower}, ground_idle)")

        # Build poses based on movement type
        poses = {
            "standing": {
                "poseName": "standing",
                "transformTicks": 10,
                "poseTypes": ["STAND", "NONE", "PORTRAIT", "PROFILE"],
                "animations": standing_animations
            },
            "walking": {
                "poseName": "walking",
                "transformTicks": 10,
                "poseTypes": ["WALK"],
                "animations": [f"bedrock({pokemon_lower}, ground_walk)"]
            },
            "sleep": {
                "poseName": "sleep",
                "transformTicks": 10,
                "poseTypes": ["SLEEP"],
                "animations": [f"bedrock({pokemon_lower}, sleep)"]
            }
        }

        # Add water poses if it can swim
        if config.get('can_swim', False):
            poses["floating"] = {
                "poseName": "floating",
                "transformTicks": 10,
                "poseTypes": ["FLOAT"],
                "animations": [f"bedrock({pokemon_lower}, water_idle)"]
            }
            poses["swimming"] = {
                "poseName": "swimming",
                "transformTicks": 10,
                "poseTypes": ["SWIM"],
                "animations": [f"bedrock({pokemon_lower}, water_swim)"]
            }

        # Add flying poses if it can fly
        if config.get('can_fly', False):
            poses["flying"] = {
                "poseName": "flying",
                "transformTicks": 10,
                "poseTypes": ["FLY"],
                "animations": [f"bedrock({pokemon_lower}, air_fly)"]
            }
            poses["hovering"] = {
                "poseName": "hovering",
                "transformTicks": 10,
                "poseTypes": ["HOVER"],
                "animations": [f"bedrock({pokemon_lower}, air_idle)"]
            }

        result = {
            "portraitScale": config.get('portrait_scale', 1.25),
            "portraitTranslation": [0, 0.5, 0],
            "profileScale": config.get('profile_scale', 0.8),
            "profileTranslation": [0, 0.4, 0],
            "faint": f"bedrock({pokemon_lower}, faint)",
            "poses": poses
        }

        # Only add head bone if specified (some models don't have a head)
        head_bone = config.get('head_bone', 'head')
        if head_bone and head_bone.lower() != 'none':
            result["head"] = head_bone
        else:
            # No head bone - canLook will be automatically set to false in species JSON
            pass

        return result

    def create_resolver_json(self, pokemon_name: str) -> Dict:
        """Create model resolver with correct texture paths"""
        pokemon_lower = pokemon_name.lower()
        return {
            "species": f"cobblemon:{pokemon_lower}",
            "order": 0,
            "variations": [
                {
                    "aspects": [],
                    "poser": f"cobblemon:{pokemon_lower}",
                    "model": f"cobblemon:{pokemon_lower}.geo",
                    # Correct path format that ACTUALLY works
                    "texture": f"cobblemon:textures/pokemon/{pokemon_lower}/{pokemon_lower}.png",
                    "layers": []
                },
                {
                    "aspects": ["shiny"],
                    "poser": f"cobblemon:{pokemon_lower}",
                    "model": f"cobblemon:{pokemon_lower}.geo",
                    # Shiny variant with full path
                    "texture": f"cobblemon:textures/pokemon/{pokemon_lower}/{pokemon_lower}_shiny.png",
                    "layers": []
                }
            ]
        }

    def create_spawn_pool_json(self, pokemon_name: str, config: Dict) -> Dict:
        """Create spawn pool configuration"""
        pokemon_lower = pokemon_name.lower()

        # Determine spawn context based on abilities
        context = "grounded"
        presets = ["natural"]

        if config.get('can_swim', False):
            context = "submerged"
            presets = ["underwater"]
        elif config.get('can_fly', False):
            context = "grounded"  # Still spawns on ground but can fly
            presets = ["natural"]

        return {
            "enabled": True,
            "neededInstalledMods": [],
            "neededUninstalledMods": [],
            "spawns": [
                {
                    "id": f"{pokemon_lower}-1",
                    "pokemon": pokemon_lower,
                    "presets": presets,
                    "type": "pokemon",
                    "context": context,
                    "bucket": config.get('rarity', 'common'),
                    "level": config.get('spawn_level', '5-30'),
                    "weight": config.get('spawn_weight', 10.0),
                    "condition": {
                        "canSeeSky": config.get('spawn_surface', True),
                        "biomes": config.get('spawn_biomes', ['#minecraft:is_overworld']).split(',') if isinstance(
                            config.get('spawn_biomes', '#minecraft:is_overworld'), str) else config.get('spawn_biomes',
                                                                                                        ['#minecraft:is_overworld'])
                    }
                }
            ]
        }

    def validate_animations(self, anim_file: Path, pokemon_name: str):
        """Validate animation file has required animations"""
        try:
            with open(anim_file, 'r') as f:
                anim_data = json.load(f)

            required_anims = ['ground_idle', 'ground_walk']
            found_anims = []

            if 'animations' in anim_data:
                for anim_key in anim_data['animations'].keys():
                    # Extract animation name from key like "animation.pokemon.ground_idle"
                    if '.' in anim_key:
                        anim_name = anim_key.split('.')[-1]
                        found_anims.append(anim_name)

            missing = [anim for anim in required_anims if anim not in found_anims]

            if missing:
                print(f"\nWARNING: Missing recommended animations: {', '.join(missing)}")
                print(f"   Your Pokémon may not animate properly!")
                print(f"   Add these animations in Blockbench:")
                for anim in missing:
                    print(f"   - animation.{pokemon_name}.{anim}")
            else:
                print(f"  [OK] Animation validation passed")

        except Exception as e:
            print(f"  WARNING: Could not validate animations: {e}")

    def organize_files(self, pokemon_name: str, files: Dict[str, List[Path]]):
        """Organize files into resource pack"""
        print(f"\nOrganizing files for {pokemon_name}...")

        pokemon_lower = pokemon_name.lower()

        # Validate animation file if present
        if files['animations']:
            self.validate_animations(files['animations'][0], pokemon_lower)

        # Copy animations
        if files['animations']:
            dest_dir = self.resource_pack_dir / "assets" / "cobblemon" / "bedrock" / "pokemon" / "animations" / pokemon_lower
            for anim_file in files['animations']:
                dest_file = dest_dir / f"{pokemon_lower}.animation.json"  # Use .animation.json NOT _animation.json
                shutil.copy2(anim_file, dest_file)
                print(f"  [OK] Animation: {anim_file.name} → {dest_file.relative_to(self.resource_pack_dir)}")

        # Copy models and fix identifier
        if files['models']:
            dest_dir = self.resource_pack_dir / "assets" / "cobblemon" / "bedrock" / "pokemon" / "models" / pokemon_lower
            for model_file in files['models']:
                dest_file = dest_dir / f"{pokemon_lower}.geo.json"  # Use .geo.json NOT _geo.json

                # Read model and fix identifier if needed
                with open(model_file, 'r') as f:
                    model_data = json.load(f)

                # Fix the identifier to match Cobblemon's requirements
                if 'minecraft:geometry' in model_data:
                    for geom in model_data['minecraft:geometry']:
                        if 'description' in geom and 'identifier' in geom['description']:
                            old_id = geom['description']['identifier']
                            new_id = f"geometry.{pokemon_lower}"
                            geom['description']['identifier'] = new_id
                            if old_id != new_id:
                                print(f"  NOTE: Fixed model identifier: {old_id} → {new_id}")

                # Write fixed model
                with open(dest_file, 'w') as f:
                    json.dump(model_data, f, indent=2)

                print(f"  [OK] Model: {model_file.name} → {dest_file.relative_to(self.resource_pack_dir)}")

        # Copy textures (detect shiny by filename rather than by directory order)
        if files['textures']:
            dest_dir = self.resource_pack_dir / "assets" / "cobblemon" / "textures" / "pokemon" / pokemon_lower
            shiny_files = [t for t in files['textures'] if 'shiny' in t.name.lower()]
            normal_files = [t for t in files['textures'] if 'shiny' not in t.name.lower()]

            # Fallback so the Pokémon always gets a base texture
            if not normal_files:
                normal_files = shiny_files

            copied = set()

            # Base (non-shiny) texture
            base_src = normal_files[0]
            base_dest = dest_dir / f"{pokemon_lower}.png"
            shutil.copy2(base_src, base_dest)
            copied.add(base_src)
            print(f"  [OK] Texture: {base_src.name} → {base_dest.relative_to(self.resource_pack_dir)}")

            # Shiny texture (only if a distinct shiny file exists)
            if shiny_files and shiny_files[0] not in copied:
                shiny_dest = dest_dir / f"{pokemon_lower}_shiny.png"
                shutil.copy2(shiny_files[0], shiny_dest)
                copied.add(shiny_files[0])
                print(f"  [OK] Texture: {shiny_files[0].name} → {shiny_dest.relative_to(self.resource_pack_dir)}")

            # Any remaining textures keep their original names
            for texture_file in files['textures']:
                if texture_file in copied:
                    continue
                dest_file = dest_dir / texture_file.name
                shutil.copy2(texture_file, dest_file)
                print(f"  [OK] Texture: {texture_file.name} → {dest_file.relative_to(self.resource_pack_dir)}")

        print("[OK] Files organized!")

    def generate_pack_files(self, pokemon_name: str, config: Dict):
        """Generate all pack configuration files"""
        print(f"\n  Generating configuration files for {pokemon_name}...")

        pokemon_lower = pokemon_name.lower()

        # Resource pack.mcmeta (create if doesn't exist)
        resource_mcmeta = self.resource_pack_dir / "pack.mcmeta"
        if not resource_mcmeta.exists():
            with open(resource_mcmeta, 'w') as f:
                json.dump(self.create_pack_mcmeta('resource'), f, indent=2)
            print(f"  [OK] Resource pack.mcmeta created (format {self.RESOURCE_PACK_FORMAT})")
        else:
            print(f"  NOTE: Resource pack.mcmeta already exists (keeping existing)")

        # Behavior pack.mcmeta (create if doesn't exist)
        behavior_mcmeta = self.behavior_pack_dir / "pack.mcmeta"
        if not behavior_mcmeta.exists():
            with open(behavior_mcmeta, 'w') as f:
                json.dump(self.create_pack_mcmeta('behavior'), f, indent=2)
            print(f"  [OK] Behavior pack.mcmeta created (format {self.DATA_PACK_FORMAT})")
        else:
            print(f"  NOTE: Behavior pack.mcmeta already exists (keeping existing)")

        # Species definition
        species_file = self.behavior_pack_dir / "data" / "cobblemon" / "species" / "custom" / f"{pokemon_lower}.json"
        with open(species_file, 'w') as f:
            json.dump(self.create_species_json(pokemon_name, config), f, indent=2)
        print(f"  [OK] Species definition")

        # Poser
        poser_file = self.resource_pack_dir / "assets" / "cobblemon" / "bedrock" / "pokemon" / "posers" / f"{pokemon_lower}.json"
        with open(poser_file, 'w') as f:
            json.dump(self.create_poser_json(pokemon_name, config), f, indent=2)
        print(f"  [OK] Poser configuration")

        # Resolver
        resolver_file = self.resource_pack_dir / "assets" / "cobblemon" / "bedrock" / "pokemon" / "resolvers" / f"0_{pokemon_lower}_base.json"
        with open(resolver_file, 'w') as f:
            json.dump(self.create_resolver_json(pokemon_name), f, indent=2)
        print(f"  [OK] Model resolver")

        # Spawn pool
        spawn_file = self.behavior_pack_dir / "data" / "cobblemon" / "spawn_pool_world" / f"{pokemon_lower}.json"
        with open(spawn_file, 'w') as f:
            json.dump(self.create_spawn_pool_json(pokemon_name, config), f, indent=2)
        print(f"  [OK] Spawn pool")

        # Language file - MERGE with existing if present
        lang_file = self.resource_pack_dir / "assets" / "cobblemon" / "lang" / "en_us.json"
        new_lang_data = {
            f"cobblemon.species.{pokemon_lower}.name": pokemon_name,
            f"cobblemon.species.{pokemon_lower}.desc1": config.get('desc1',
                                                                   f"A mysterious Pokémon known as {pokemon_name}."),
            f"cobblemon.species.{pokemon_lower}.desc2": config.get('desc2',
                                                                   "Customize this description in the language file!")
        }

        # Load existing language file and merge
        if lang_file.exists():
            with open(lang_file, 'r') as f:
                existing_lang = json.load(f)
            existing_lang.update(new_lang_data)
            with open(lang_file, 'w') as f:
                json.dump(existing_lang, f, indent=2, sort_keys=True)
            print(f"  [OK] Language file updated (merged with existing)")
        else:
            with open(lang_file, 'w') as f:
                json.dump(new_lang_data, f, indent=2)
            print(f"  [OK] Language file created")

        print("[OK] Configuration files generated!")

    def cleanup_source_files(self, files: Dict[str, List[Path]]):
        """Remove source files after copying (NEVER deletes .py files or files outside base_dir)"""
        print("\nCleaning up source files...")

        files_to_remove = []
        for file_list in files.values():
            files_to_remove.extend(file_list)

        for file in files_to_remove:
            # Safety checks - NEVER delete:
            # 1. Python files
            # 2. Files outside the base directory
            # 3. The script itself
            if file.suffix == '.py':
                print(f"  WARNING: Skipped (Python file): {file.name}")
                continue

            if not str(file).startswith(str(self.base_dir)):
                print(f"  WARNING: Skipped (outside base directory): {file.name}")
                continue

            if file.exists():
                file.unlink()
                print(f"  [OK] Removed: {file.name}")

        print("[OK] Cleanup complete!")

    def show_current_pokemon(self):
        """Display all Pokémon currently in the packs"""
        print(f"\n{'=' * 70}")
        print("CURRENT POKÉMON IN PACKS")
        print(f"{'=' * 70}\n")

        # Check if packs exist
        species_dir = self.behavior_pack_dir / "data" / "cobblemon" / "species" / "custom"

        if not species_dir.exists():
            print("ERROR: No packs found!")
            print(f"   Location checked: {species_dir}")
            print("\nTIP: Generate your first Pokémon to create the packs!")
            return

        # Find all species files
        species_files = list(species_dir.glob("*.json"))

        if not species_files:
            print("ERROR: No Pokémon found in packs!")
            print(f"   Location: {species_dir}")
            return

        print(f"Found {len(species_files)} Pokémon:\n")

        # Parse and display each Pokémon
        pokemon_list = []
        for species_file in sorted(species_files):
            try:
                with open(species_file, 'r') as f:
                    data = json.load(f)

                name = data.get('name', species_file.stem).capitalize()
                pokedex_num = data.get('nationalPokedexNumber', '???')
                primary_type = data.get('primaryType', '???').upper()
                secondary_type = data.get('secondaryType', '')

                # Get stats
                stats = data.get('baseStats', {})
                hp = stats.get('hp', 0)
                atk = stats.get('attack', 0)
                defe = stats.get('defence', 0)
                spatk = stats.get('special_attack', 0)
                spdef = stats.get('special_defence', 0)
                speed = stats.get('speed', 0)
                total = hp + atk + defe + spatk + spdef + speed

                # Check if legendary
                labels = data.get('labels', [])
                is_legendary = 'legendary' in labels

                # Get catch rate
                catch_rate = data.get('catchRate', 45)

                pokemon_list.append({
                    'name': name,
                    'number': pokedex_num,
                    'primary_type': primary_type,
                    'secondary_type': secondary_type,
                    'total': total,
                    'hp': hp,
                    'atk': atk,
                    'def': defe,
                    'spatk': spatk,
                    'spdef': spdef,
                    'speed': speed,
                    'legendary': is_legendary,
                    'catch_rate': catch_rate
                })

            except Exception as e:
                print(f"WARNING: Error reading {species_file.name}: {e}")

        # Display in table format
        print(f"{'#':<6} {'Name':<15} {'Type':<20} {'BST':<6} {'Legendary':<10} {'Catch':<6}")
        print("-" * 70)

        for p in sorted(pokemon_list, key=lambda x: x['number']):
            type_str = p['primary_type']
            if p['secondary_type']:
                type_str += f"/{p['secondary_type'].upper()}"

            legendary_mark = "YES" if p['legendary'] else "No"

            print(
                f"#{p['number']:<5} {p['name']:<15} {type_str:<20} {p['total']:<6} {legendary_mark:<10} {p['catch_rate']:<6}")

        # Summary stats
        print("\n" + "=" * 70)
        print(f"SUMMARY:")
        print(f"   Total Pokémon: {len(pokemon_list)}")
        legendary_count = sum(1 for p in pokemon_list if p['legendary'])
        print(f"   Legendary: {legendary_count}")
        print(f"   Regular: {len(pokemon_list) - legendary_count}")

        # Average BST
        avg_bst = sum(p['total'] for p in pokemon_list) // len(pokemon_list) if pokemon_list else 0
        print(f"   Average BST: {avg_bst}")

        # Type distribution
        type_counts = {}
        for p in pokemon_list:
            primary = p['primary_type']
            type_counts[primary] = type_counts.get(primary, 0) + 1
            if p['secondary_type']:
                secondary = p['secondary_type'].upper()
                type_counts[secondary] = type_counts.get(secondary, 0) + 1

        print(f"\n   Type Distribution:")
        for ptype, count in sorted(type_counts.items(), key=lambda x: x[1], reverse=True):
            print(f"      {ptype}: {count}")

        print(f"\n{'=' * 70}")
        print(f"Pack Locations:")
        print(f"   Resource: {self.resource_pack_dir}")
        print(f"   Behavior: {self.behavior_pack_dir}")
        print(f"{'=' * 70}\n")

    def edit_pokemon(self, pokemon_name: str, args):
        """Edit an existing Pokémon's stats and properties"""
        print(f"\n{'=' * 70}")
        print(f"EDITING POKÉMON: {pokemon_name.upper()}")
        print(f"{'=' * 70}\n")

        pokemon_lower = pokemon_name.lower()
        species_file = self.behavior_pack_dir / "data" / "cobblemon" / "species" / "custom" / f"{pokemon_lower}.json"

        # Check if Pokémon exists
        if not species_file.exists():
            print(f"ERROR: Pokémon '{pokemon_name}' not found!")
            print(f"   Looked for: {species_file}")
            print(f"\nTIP: Use --show-current-pokemon to see all Pokémon")
            return

        # Load existing data
        try:
            with open(species_file, 'r') as f:
                data = json.load(f)
        except Exception as e:
            print(f"ERROR: reading {pokemon_name}: {e}")
            return

        print(f"Current Stats for {pokemon_name.capitalize()}:")
        current_stats = data.get('baseStats', {})
        current_hp = current_stats.get('hp', 0)
        current_atk = current_stats.get('attack', 0)
        current_def = current_stats.get('defence', 0)
        current_spatk = current_stats.get('special_attack', 0)
        current_spdef = current_stats.get('special_defence', 0)
        current_speed = current_stats.get('speed', 0)
        current_total = current_hp + current_atk + current_def + current_spatk + current_spdef + current_speed

        print(f"   HP: {current_hp}")
        print(f"   Attack: {current_atk}")
        print(f"   Defence: {current_def}")
        print(f"   Sp. Attack: {current_spatk}")
        print(f"   Sp. Defence: {current_spdef}")
        print(f"   Speed: {current_speed}")
        print(f"   TOTAL BST: {current_total}")
        print(
            f"   Type: {data.get('primaryType', 'normal').upper()}/{data.get('secondaryType', '').upper() if data.get('secondaryType') else 'None'}")
        print(f"   Catch Rate: {data.get('catchRate', 45)}")
        print(f"   Legendary: {'YES' if 'legendary' in data.get('labels', []) else 'No'}")

        # Track what was changed
        changes_made = []

        # Update stats if provided (compare against current value so setting to 50 works)
        if args.hp is not None and args.hp != current_hp:
            data['baseStats']['hp'] = args.hp
            changes_made.append(f"HP: {current_hp} → {args.hp}")

        if args.attack is not None and args.attack != current_atk:
            data['baseStats']['attack'] = args.attack
            changes_made.append(f"Attack: {current_atk} → {args.attack}")

        if args.defence is not None and args.defence != current_def:
            data['baseStats']['defence'] = args.defence
            changes_made.append(f"Defence: {current_def} → {args.defence}")

        if args.special_attack is not None and args.special_attack != current_spatk:
            data['baseStats']['special_attack'] = args.special_attack
            changes_made.append(f"Sp. Attack: {current_spatk} → {args.special_attack}")

        if args.special_defence is not None and args.special_defence != current_spdef:
            data['baseStats']['special_defence'] = args.special_defence
            changes_made.append(f"Sp. Defence: {current_spdef} → {args.special_defence}")

        if args.speed is not None and args.speed != current_speed:
            data['baseStats']['speed'] = args.speed
            changes_made.append(f"Speed: {current_speed} → {args.speed}")

        # Update types if provided
        if args.primary_type and args.primary_type != data.get('primaryType', 'normal'):
            old_type = data.get('primaryType', 'normal')
            data['primaryType'] = args.primary_type
            changes_made.append(f"Primary Type: {old_type} → {args.primary_type}")

        if args.secondary_type:
            old_type = data.get('secondaryType', 'None')
            data['secondaryType'] = args.secondary_type
            changes_made.append(f"Secondary Type: {old_type} → {args.secondary_type}")

        # Update rarity
        if args.rarity:
            # Update spawn file
            spawn_file = self.behavior_pack_dir / "data" / "cobblemon" / "spawn_pool_world" / f"{pokemon_lower}.json"
            if spawn_file.exists():
                try:
                    with open(spawn_file, 'r') as f:
                        spawn_data = json.load(f)
                    old_rarity = spawn_data['spawns'][0].get('bucket', 'common')
                    for _entry in spawn_data['spawns']:
                        if isinstance(_entry, dict):
                            _entry['bucket'] = args.rarity
                    with open(spawn_file, 'w') as f:
                        json.dump(spawn_data, f, indent=2)
                    changes_made.append(f"Rarity: {old_rarity} → {args.rarity}")
                except Exception as e:
                    print(f"WARNING: Could not update spawn rarity: {e}")

        # Update legendary status
        if args.legendary:
            if 'legendary' not in data.get('labels', []):
                data['labels'].append('legendary')
                data['catchRate'] = 3
                data['baseExperienceYield'] = 290
                data['baseFriendship'] = 0
                changes_made.append("Made legendary (catchRate=3, baseExp=290)")

        # Update pokedex number if provided
        if args.number is not None and args.number != data.get('nationalPokedexNumber'):
            old_num = data.get('nationalPokedexNumber', '???')

            # Warn if another species already uses this number
            for other_file in species_file.parent.glob("*.json"):
                if other_file == species_file:
                    continue
                try:
                    with open(other_file, 'r') as f:
                        other_data = json.load(f)
                    if other_data.get('nationalPokedexNumber') == args.number:
                        print(f"WARNING: Dex #{args.number} is already used by "
                              f"'{other_data.get('name', other_file.stem)}'!")
                except Exception:
                    pass

            data['nationalPokedexNumber'] = args.number
            changes_made.append(f"Pokédex Number: #{old_num} → #{args.number}")

        # Add/replace an evolution if provided
        if args.evo_target:
            evo_config = {
                'evo_target': args.evo_target,
                'evo_method': args.evo_method,
                'evo_level': args.evo_level,
                'evo_item': args.evo_item,
            }
            new_evos = self._build_evolutions(pokemon_lower, evo_config)

            existing_evos = data.get('evolutions', []) or []
            new_ids = {e['id'] for e in new_evos}
            # Replace same-id evolution if present, keep other branches
            kept = [e for e in existing_evos if e.get('id') not in new_ids]
            replaced = len(existing_evos) - len(kept)
            data['evolutions'] = kept + new_evos

            evo_desc = f"{pokemon_lower} → {args.evo_target.lower()}"
            if args.evo_method == 'level_up':
                evo_desc += f" at level {args.evo_level}"
            elif args.evo_method == 'item_interact':
                evo_desc += f" with {args.evo_item or 'minecraft:stone'}"
            elif args.evo_method == 'trade':
                evo_desc += " by trading"
                if args.evo_item:
                    evo_desc += f" (holding {args.evo_item})"
            action = "Replaced evolution" if replaced else "Added evolution"
            changes_made.append(f"{action}: {evo_desc}")
            if kept:
                changes_made.append(f"  (kept {len(kept)} other evolution branch(es))")

        # Remove all evolutions if requested
        if getattr(args, 'remove_evolutions', False):
            old_count = len(data.get('evolutions', []) or [])
            if old_count:
                data['evolutions'] = []
                changes_made.append(f"Removed all evolutions ({old_count} removed)")
            else:
                print(f"NOTE: No evolutions to remove.")

        # Edit head bone (updates BOTH species canLook and the poser file)
        head_bone = getattr(args, 'head_bone', None)
        if head_bone is not None:
            no_head = head_bone.lower() == 'none'

            # 1) Species: behaviour.moving.canLook
            behaviour = data.setdefault('behaviour', {})
            moving = behaviour.setdefault('moving', {})
            moving['canLook'] = (not no_head) and (not getattr(args, 'no_look', False))

            # 2) Poser: head field + look animation
            poser_file = (self.resource_pack_dir / "assets" / "cobblemon" / "bedrock" /
                          "pokemon" / "posers" / f"{pokemon_lower}.json")
            if poser_file.exists():
                try:
                    with open(poser_file, 'r') as f:
                        poser_data = json.load(f)

                    if no_head:
                        # Delete head field entirely (never set to null!)
                        poser_data.pop('head', None)
                        # Strip "look" from every pose's animations
                        for pose in poser_data.get('poses', {}).values():
                            if isinstance(pose, dict) and isinstance(pose.get('animations'), list):
                                pose['animations'] = [a for a in pose['animations']
                                                      if str(a).strip().lower() != 'look']
                        changes_made.append("Head bone: REMOVED (poser 'head' deleted, "
                                            "'look' animations stripped, canLook=false)")
                    else:
                        poser_data['head'] = head_bone
                        # Ensure standing pose has "look" so the head actually tracks
                        standing = poser_data.get('poses', {}).get('standing')
                        if isinstance(standing, dict) and isinstance(standing.get('animations'), list):
                            if not any(str(a).strip().lower() == 'look' for a in standing['animations']):
                                standing['animations'].insert(0, 'look')
                        changes_made.append(f"Head bone: set to '{head_bone}' "
                                            f"(canLook={moving['canLook']})")

                    with open(poser_file, 'w') as f:
                        json.dump(poser_data, f, indent=2)
                except Exception as e:
                    print(f"WARNING: Could not update poser file: {e}")
                    changes_made.append(f"canLook: {moving['canLook']} (species only — poser update FAILED)")
            else:
                print(f"WARNING: Poser file not found: {poser_file}")
                print(f"   Updated species canLook only — fix the poser manually!")
                changes_made.append(f"canLook: {moving['canLook']} (species only — no poser file found)")

        # --no-look on its own: force canLook=false without touching the head bone
        elif getattr(args, 'no_look', False):
            behaviour = data.setdefault('behaviour', {})
            moving = behaviour.setdefault('moving', {})
            if moving.get('canLook') is not False:
                moving['canLook'] = False
                changes_made.append("canLook: false (head bone unchanged)")

        # Edit height/weight if provided
        if getattr(args, 'height', None) is not None and args.height != data.get('height'):
            changes_made.append(f"Height: {data.get('height', '?')} → {args.height} decimeters")
            data['height'] = args.height
        if getattr(args, 'weight', None) is not None and args.weight != data.get('weight'):
            changes_made.append(f"Weight: {data.get('weight', '?')} → {args.weight} hectograms")
            data['weight'] = args.weight

        # Edit movement behaviors if flagged
        if getattr(args, 'can_fly', False):
            moving = data.setdefault('behaviour', {}).setdefault('moving', {})
            if not moving.setdefault('fly', {}).get('canFly'):
                moving['fly']['canFly'] = True
                changes_made.append("Flight: enabled")
        if getattr(args, 'can_swim', False) or getattr(args, 'breathe_underwater', False):
            moving = data.setdefault('behaviour', {}).setdefault('moving', {})
            swim = moving.setdefault('swim', {})
            swim.setdefault('swimSpeed', 0.3)
            if getattr(args, 'can_swim', False) and not swim.get('canSwimInWater'):
                swim['canSwimInWater'] = True
                changes_made.append("Swimming: enabled")
            if getattr(args, 'breathe_underwater', False) and not swim.get('canBreatheUnderwater'):
                swim['canBreatheUnderwater'] = True
                changes_made.append("Underwater breathing: enabled")

        # Edit spawn level / biomes if provided (applies to ALL spawn entries)
        spawn_level = getattr(args, 'spawn_level', None)
        spawn_biomes = getattr(args, 'spawn_biomes', None)
        if spawn_level is not None or spawn_biomes is not None:
            spawn_file = (self.behavior_pack_dir / "data" / "cobblemon" /
                          "spawn_pool_world" / f"{pokemon_lower}.json")
            if spawn_file.exists():
                try:
                    with open(spawn_file, 'r') as f:
                        spawn_data = json.load(f)
                    entries = spawn_data.get('spawns', [])
                    for entry in entries:
                        if not isinstance(entry, dict):
                            continue
                        if spawn_level is not None:
                            entry['level'] = spawn_level
                        if spawn_biomes is not None:
                            entry.setdefault('condition', {})['biomes'] = [
                                b.strip() for b in spawn_biomes.split(',')]
                    with open(spawn_file, 'w') as f:
                        json.dump(spawn_data, f, indent=2)
                    n = len(entries)
                    if spawn_level is not None:
                        changes_made.append(f"Spawn level: {spawn_level} ({n} entr{'y' if n == 1 else 'ies'})")
                    if spawn_biomes is not None:
                        changes_made.append(f"Spawn biomes: {spawn_biomes} ({n} entr{'y' if n == 1 else 'ies'})")
                except Exception as e:
                    print(f"WARNING: Could not update spawn file: {e}")
            else:
                print(f"WARNING: Spawn file not found: {spawn_file}")

        # Edit Pokédex descriptions if provided (lang file)
        desc1 = getattr(args, 'desc1', None)
        desc2 = getattr(args, 'desc2', None)
        if desc1 is not None or desc2 is not None:
            lang_file = (self.resource_pack_dir / "assets" / "cobblemon" /
                         "lang" / "en_us.json")
            try:
                lang_data = {}
                if lang_file.exists():
                    with open(lang_file, 'r', encoding='utf-8') as f:
                        lang_data = json.load(f)
                else:
                    lang_file.parent.mkdir(parents=True, exist_ok=True)
                if desc1 is not None:
                    lang_data[f"cobblemon.species.{pokemon_lower}.desc1"] = desc1
                    changes_made.append(f"Pokédex desc1 updated")
                if desc2 is not None:
                    lang_data[f"cobblemon.species.{pokemon_lower}.desc2"] = desc2
                    changes_made.append(f"Pokédex desc2 updated")
                with open(lang_file, 'w', encoding='utf-8') as f:
                    json.dump(lang_data, f, indent=2, ensure_ascii=False)
            except Exception as e:
                print(f"WARNING: Could not update lang file: {e}")

        # Edit preEvolution field if provided
        pre_evo = getattr(args, 'pre_evolution', None)
        if pre_evo is not None and data.get('preEvolution') != pre_evo.lower():
            changes_made.append(f"Pre-evolution: {data.get('preEvolution', 'none')} → {pre_evo.lower()}")
            data['preEvolution'] = pre_evo.lower()
            print(f"NOTE: preEvolution is informational. For {pre_evo} to actually evolve")
            print(f"   into {pokemon_lower}, also run:")
            print(f"   --edit {pre_evo.lower()} --evo-target {pokemon_lower} --evo-level <level>")

        # --- Simple species fields (v2.5) ---
        catch_rate = getattr(args, 'catch_rate', None)
        if catch_rate is not None and catch_rate != data.get('catchRate'):
            if not (3 <= catch_rate <= 255):
                print(f"WARNING: Catch rate {catch_rate} outside vanilla range 3-255")
            changes_made.append(f"Catch rate: {data.get('catchRate', '?')} → {catch_rate}")
            data['catchRate'] = catch_rate

        male_ratio = getattr(args, 'male_ratio', None)
        if male_ratio is not None and male_ratio != data.get('maleRatio'):
            if not (-1 <= male_ratio <= 1):
                print(f"WARNING: maleRatio {male_ratio} outside range -1 to 1")
            changes_made.append(f"Male ratio: {data.get('maleRatio', '?')} → {male_ratio}")
            data['maleRatio'] = male_ratio

        exp_group = getattr(args, 'exp_group', None)
        if exp_group is not None and exp_group != data.get('experienceGroup'):
            if exp_group not in VALID_EXP_GROUPS:
                print(f"WARNING: '{exp_group}' is not a known experience group")
                print(f"   Valid: {', '.join(sorted(VALID_EXP_GROUPS))}")
            changes_made.append(f"Experience group: {data.get('experienceGroup', '?')} → {exp_group}")
            data['experienceGroup'] = exp_group

        egg_cycles = getattr(args, 'egg_cycles', None)
        if egg_cycles is not None and egg_cycles != data.get('eggCycles'):
            changes_made.append(f"Egg cycles: {data.get('eggCycles', '?')} → {egg_cycles}")
            data['eggCycles'] = egg_cycles

        egg_groups = getattr(args, 'egg_groups', None)
        if egg_groups is not None:
            groups = [g.strip().lower() for g in egg_groups.split(',')]
            unknown = [g for g in groups if g not in VALID_EGG_GROUPS]
            if unknown:
                print(f"WARNING: Unknown egg group(s): {', '.join(unknown)}")
                print(f"   Valid: {', '.join(sorted(VALID_EGG_GROUPS))}")
            if groups != data.get('eggGroups'):
                changes_made.append(f"Egg groups: {data.get('eggGroups', '?')} → {groups}")
                data['eggGroups'] = groups

        base_exp = getattr(args, 'base_exp', None)
        if base_exp is not None and base_exp != data.get('baseExperienceYield'):
            changes_made.append(f"Base exp yield: {data.get('baseExperienceYield', '?')} → {base_exp}")
            data['baseExperienceYield'] = base_exp

        friendship = getattr(args, 'friendship', None)
        if friendship is not None and friendship != data.get('baseFriendship'):
            changes_made.append(f"Base friendship: {data.get('baseFriendship', '?')} → {friendship}")
            data['baseFriendship'] = friendship

        ev_spec = getattr(args, 'ev_yield', None)
        if ev_spec is not None:
            try:
                new_evs = parse_ev_yield(ev_spec)
                if sum(new_evs.values()) > 3:
                    print(f"WARNING: Total EV yield {sum(new_evs.values())} exceeds vanilla max of 3")
                if new_evs != data.get('evYield'):
                    nonzero = ', '.join(f"{k}:{v}" for k, v in new_evs.items() if v)
                    changes_made.append(f"EV yield: {nonzero or 'none'}")
                    data['evYield'] = new_evs
            except ValueError as e:
                print(f"ERROR: Bad --ev-yield: {e}")

        drops_spec = getattr(args, 'drops', None)
        if drops_spec is not None:
            try:
                entries = parse_drops(drops_spec)
                data['drops'] = {"amount": data.get('drops', {}).get('amount', '1-2'),
                                 "entries": entries}
                changes_made.append(f"Drops: {len(entries)} entr{'y' if len(entries) == 1 else 'ies'} "
                                    f"({', '.join(e['item'] for e in entries)})")
            except ValueError as e:
                print(f"ERROR: Bad --drops: {e}")

        base_scale = getattr(args, 'base_scale', None)
        if base_scale is not None and base_scale != data.get('baseScale'):
            changes_made.append(f"Base scale: {data.get('baseScale', 'default')} → {base_scale}")
            data['baseScale'] = float(base_scale)

        hitbox_spec = getattr(args, 'hitbox', None)
        if hitbox_spec is not None:
            try:
                hb = parse_hitbox(hitbox_spec)
                if hb != data.get('hitbox'):
                    changes_made.append(f"Hitbox: {hb['width']}x{hb['height']}")
                    data['hitbox'] = hb
            except ValueError as e:
                print(f"ERROR: Bad --hitbox (format: \"width,height\"): {e}")

        # Un-set legendary status
        if getattr(args, 'not_legendary', False):
            labels = data.get('labels', [])
            if 'legendary' in labels:
                labels.remove('legendary')
                data['labels'] = labels
                changes_made.append("Legendary: REMOVED")
                print(f"NOTE: Spawn weight unchanged — if it was set to 0.05 for legendary,")
                print(f"   consider also: --spawn-weight 10")
            else:
                print(f"NOTE: {pokemon_lower} wasn't legendary.")

        # Remove secondary type with --secondary-type none
        # (handled here as a pre-check so the normal type-edit code below sees None)
        if getattr(args, 'secondary_type', None) and args.secondary_type.lower() == 'none':
            if 'secondaryType' in data:
                changes_made.append(f"Secondary type: {data['secondaryType']} → REMOVED (mono-type)")
                del data['secondaryType']
            else:
                print(f"NOTE: {pokemon_lower} has no secondary type.")
            args.secondary_type = None  # prevent the regular type editor from re-adding it

        # --- Spawn-file fields (v2.5): weight and canSeeSky, all entries ---
        spawn_weight = getattr(args, 'spawn_weight', None)
        can_see_sky = getattr(args, 'can_see_sky', None)
        if spawn_weight is not None or can_see_sky is not None:
            spawn_file = (self.behavior_pack_dir / "data" / "cobblemon" /
                          "spawn_pool_world" / f"{pokemon_lower}.json")
            if spawn_file.exists():
                try:
                    with open(spawn_file, 'r') as f:
                        spawn_data = json.load(f)
                    entries = spawn_data.get('spawns', [])
                    for entry in entries:
                        if not isinstance(entry, dict):
                            continue
                        if spawn_weight is not None:
                            entry['weight'] = spawn_weight
                        if can_see_sky is not None:
                            entry.setdefault('condition', {})['canSeeSky'] = (can_see_sky == 'true')
                    with open(spawn_file, 'w') as f:
                        json.dump(spawn_data, f, indent=2)
                    n = len(entries)
                    if spawn_weight is not None:
                        if spawn_weight <= 0:
                            print(f"WARNING: Weight {spawn_weight} means it will NEVER spawn!")
                        changes_made.append(f"Spawn weight: {spawn_weight} ({n} entr{'y' if n == 1 else 'ies'})")
                    if can_see_sky is not None:
                        where = "surface only" if can_see_sky == 'true' else "underground/caves allowed"
                        changes_made.append(f"canSeeSky: {can_see_sky} ({where}, {n} entr{'y' if n == 1 else 'ies'})")
                except Exception as e:
                    print(f"WARNING: Could not update spawn file: {e}")
            else:
                print(f"WARNING: Spawn file not found: {spawn_file}")

        # Append moves (unlike --moves which replaces)
        add_moves = getattr(args, 'add_moves', None)
        if add_moves is not None:
            if getattr(args, 'moves', None):
                print(f"WARNING: Both --moves and --add-moves given; --moves (replace) runs below,")
                print(f"   so --add-moves is appending to the REPLACED list.")
            existing = data.get('moves', []) or []
            new_moves = [m.strip() for m in add_moves.split(',') if m.strip()]
            appended = [m for m in new_moves if m not in existing]
            skipped = len(new_moves) - len(appended)
            if appended:
                data['moves'] = existing + appended
                changes_made.append(f"Moves appended: {len(appended)} "
                                    f"({len(existing)} kept{f', {skipped} duplicates skipped' if skipped else ''})")
            else:
                print(f"NOTE: All {len(new_moves)} moves already known — nothing appended.")

        # Update moves if provided
        if args.moves:
            new_moves = [m.strip() for m in args.moves.split(',')]
            old_moves = data.get('moves', [])
            data['moves'] = new_moves
            changes_made.append(f"Moves: {len(old_moves)} move(s) → {len(new_moves)} move(s)")

        # Update abilities if provided
        if args.abilities:
            new_abilities = [a.strip() for a in args.abilities.split(',')]
            old_abilities = data.get('abilities', [])
            data['abilities'] = new_abilities
            changes_made.append(f"Abilities: {old_abilities} → {new_abilities}")

        # Save if changes were made
        if changes_made:
            print(f"\nChanges to apply:")
            for change in changes_made:
                print(f"   • {change}")

            # Calculate new BST
            new_stats = data.get('baseStats', {})
            new_total = (new_stats.get('hp', 0) + new_stats.get('attack', 0) +
                         new_stats.get('defence', 0) + new_stats.get('special_attack', 0) +
                         new_stats.get('special_defence', 0) + new_stats.get('speed', 0))

            if new_total != current_total:
                print(f"\n   BST Change: {current_total} → {new_total}")

            # Save the file
            try:
                with open(species_file, 'w') as f:
                    json.dump(data, f, indent=2)
                print(f"\n[OK] Successfully updated {pokemon_name.capitalize()}!")
                print(f"   File: {species_file}")
            except Exception as e:
                print(f"\nERROR: saving changes: {e}")
        else:
            print(f"\nWARNING: No changes specified!")
            print(f"   Use --hp, --attack, --number, --evo-target, --moves, etc. to make changes")
            print(f"\nTIP: Examples:")
            print(f"   python script.py --edit {pokemon_name} --hp 80 --attack 70 --rarity rare")
            print(f"   python script.py --edit {pokemon_name} --number 1102")
            print(f"   python script.py --edit {pokemon_name} --evo-target newmon --evo-level 25")
            print(f"   python script.py --edit {pokemon_name} --remove-evolutions")

        print(f"\n{'=' * 70}\n")

    def edit_files(self, pokemon_name: str) -> bool:
        """Swap in new asset files (model/animation/textures) for an existing Pokémon.
        New files are taken from the base pack folder; displaced files are moved OUT
        to that same folder, so running --editfiles again swaps back (one-level undo)."""
        pokemon_lower = pokemon_name.lower()

        print(f"\n{'=' * 70}")
        print(f"SWAPPING ASSET FILES FOR: {pokemon_lower.upper()}")
        print(f"{'=' * 70}\n")

        species_file = (self.behavior_pack_dir / "data" / "cobblemon" /
                        "species" / "custom" / f"{pokemon_lower}.json")
        if not species_file.exists():
            print(f"ERROR: Pokémon '{pokemon_lower}' not found!")
            return False

        files = self.find_files_in_base_dir()
        bedrock = self.resource_pack_dir / "assets" / "cobblemon" / "bedrock" / "pokemon"
        tex_dir = (self.resource_pack_dir / "assets" / "cobblemon" /
                   "textures" / "pokemon" / pokemon_lower)

        def swap(source: Path, installed: Path, label: str) -> bool:
            """Collision-safe swap: source -> installed; old installed -> base dir."""
            try:
                temp = self.base_dir / f".swap_tmp_{installed.name}"
                shutil.move(str(source), str(temp))
                if installed.exists():
                    out_path = self.base_dir / installed.name
                    if out_path.exists():
                        print(f"WARNING: Overwriting previous backup: {out_path.name}")
                        out_path.unlink()
                    shutil.move(str(installed), str(out_path))
                    print(f"  Old {label} → {out_path.name} (in pack folder, run --editfiles again to restore)")
                else:
                    installed.parent.mkdir(parents=True, exist_ok=True)
                    print(f"  NOTE: No previous {label} — nothing to back up")
                shutil.move(str(temp), str(installed))
                print(f"  New {label}: {source.name} → installed")
                return True
            except Exception as e:
                print(f"  ERROR: Failed to swap {label}: {e}")
                return False

        swapped = []

        # Model
        if files['models']:
            if len(files['models']) > 1:
                print(f"WARNING: Multiple model files found, using: {files['models'][0].name}")
            installed = bedrock / "models" / pokemon_lower / f"{pokemon_lower}.geo.json"
            if swap(files['models'][0], installed, "model"):
                swapped.append("model")
                # Sanity-check the new model's identifier
                try:
                    with open(installed, 'r') as f:
                        geo = json.load(f)
                    ident = geo.get("minecraft:geometry", [{}])[0].get(
                        "description", {}).get("identifier", "")
                    if ident != f"geometry.{pokemon_lower}":
                        print(f"  WARNING: New model identifier is '{ident}' — expected "
                              f"'geometry.{pokemon_lower}'. Fix in Blockbench or it won't render!")
                except Exception:
                    print(f"  WARNING: Could not validate new model JSON — run the pack checker!")

        # Animation
        if files['animations']:
            if len(files['animations']) > 1:
                print(f"WARNING: Multiple animation files found, using: {files['animations'][0].name}")
            installed = bedrock / "animations" / pokemon_lower / f"{pokemon_lower}.animation.json"
            if swap(files['animations'][0], installed, "animation"):
                swapped.append("animation")
                try:
                    with open(installed, 'r') as f:
                        anims = json.load(f).get("animations", {})
                    bad = [k for k in anims if not k.startswith(f"animation.{pokemon_lower}.")]
                    if bad:
                        print(f"  WARNING: {len(bad)} animation key(s) don't start with "
                              f"'animation.{pokemon_lower}.' — posers won't find them!")
                except Exception:
                    print(f"  WARNING: Could not validate new animation JSON — run the pack checker!")

        # Textures (classify by filename: 'shiny' -> shiny slot)
        shiny_sources = [t for t in files['textures'] if 'shiny' in t.name.lower()]
        normal_sources = [t for t in files['textures'] if 'shiny' not in t.name.lower()]
        if normal_sources:
            if len(normal_sources) > 1:
                print(f"WARNING: Multiple base textures found, using: {normal_sources[0].name}")
            if swap(normal_sources[0], tex_dir / f"{pokemon_lower}.png", "texture"):
                swapped.append("texture")
        if shiny_sources:
            if len(shiny_sources) > 1:
                print(f"WARNING: Multiple shiny textures found, using: {shiny_sources[0].name}")
            if swap(shiny_sources[0], tex_dir / f"{pokemon_lower}_shiny.png", "shiny texture"):
                swapped.append("shiny texture")

        if not swapped:
            print(f"ERROR: No asset files found in: {self.base_dir}")
            print(f"   Drop the new files there first. Recognized:")
            print(f"   • Model:     *.geo.json (or containing 'geo'/'model')")
            print(f"   • Animation: *.animation.json")
            print(f"   • Textures:  *.png ('shiny' in name → shiny slot)")
            return False

        print(f"\n{'=' * 70}")
        print(f"SWAPPED: {', '.join(swapped)}")
        print(f"{'=' * 70}")
        print(f"  Undo: run --editfiles {pokemon_lower} again (old files are in the pack folder)")
        print(f"Recommended: run pack_checker.py to validate the new files")
        print(f"Reload in-game: /reload\n")
        return True

    def rename_pokemon(self, old_name: str, new_name: str) -> bool:
        """Rename a Pokémon across EVERY site: species, spawn, model, animation,
        poser, resolver, textures, lang, other species' evolutions/preEvolution,
        and species_additions."""
        old = old_name.lower()
        new = new_name.lower()

        print(f"\n{'=' * 70}")
        print(f"  RENAMING: {old.upper()} → {new.upper()}")
        print(f"{'=' * 70}\n")

        import re
        if not re.fullmatch(r'[a-z0-9_]+', new):
            print(f"ERROR: Invalid name '{new}': use lowercase letters, numbers, underscores only")
            return False

        species_dir = self.behavior_pack_dir / "data" / "cobblemon" / "species" / "custom"
        old_species = species_dir / f"{old}.json"
        if not old_species.exists():
            print(f"ERROR: Pokémon '{old}' not found!")
            return False
        if (species_dir / f"{new}.json").exists():
            print(f"ERROR: A Pokémon named '{new}' already exists!")
            return False

        bedrock = self.resource_pack_dir / "assets" / "cobblemon" / "bedrock" / "pokemon"
        changes = []

        # 1. Species file: name, pokedex keys, evolution ids, then rename file
        with open(old_species, 'r') as f:
            data = json.load(f)
        data['name'] = new
        if isinstance(data.get('pokedex'), list):
            data['pokedex'] = [k.replace(f"cobblemon.species.{old}.", f"cobblemon.species.{new}.")
                               for k in data['pokedex']]
        for evo in data.get('evolutions', []) or []:
            if isinstance(evo, dict) and str(evo.get('id', '')).startswith(f"{old}_"):
                evo['id'] = new + evo['id'][len(old):]
        with open(species_dir / f"{new}.json", 'w') as f:
            json.dump(data, f, indent=2)
        old_species.unlink()
        changes.append("species file (name, pokedex keys, evolution ids, filename)")

        # 2. Spawn file: pokemon field, ids, filename
        spawn_dir = self.behavior_pack_dir / "data" / "cobblemon" / "spawn_pool_world"
        old_spawn = spawn_dir / f"{old}.json"
        if old_spawn.exists():
            with open(old_spawn, 'r') as f:
                spawn = json.load(f)
            for entry in spawn.get('spawns', []) or []:
                if not isinstance(entry, dict):
                    continue
                base = str(entry.get('pokemon', '')).split(' ')
                if base and base[0] == old:
                    entry['pokemon'] = ' '.join([new] + base[1:]).strip()
                if str(entry.get('id', '')).startswith(f"{old}-"):
                    entry['id'] = new + entry['id'][len(old):]
            with open(spawn_dir / f"{new}.json", 'w') as f:
                json.dump(spawn, f, indent=2)
            old_spawn.unlink()
            changes.append("spawn file (pokemon, ids, filename)")

        # 3. Model: identifier, file, folder
        old_model_dir = bedrock / "models" / old
        if old_model_dir.exists():
            model_file = old_model_dir / f"{old}.geo.json"
            if model_file.exists():
                with open(model_file, 'r') as f:
                    geo = json.load(f)
                for g in geo.get("minecraft:geometry", []):
                    desc = g.get("description", {})
                    if desc.get("identifier") == f"geometry.{old}":
                        desc["identifier"] = f"geometry.{new}"
                with open(model_file, 'w') as f:
                    json.dump(geo, f, indent=2)
                model_file.rename(old_model_dir / f"{new}.geo.json")
            old_model_dir.rename(bedrock / "models" / new)
            changes.append("model (geometry identifier, file, folder)")

        # 4. Animation: keys, file, folder
        old_anim_dir = bedrock / "animations" / old
        if old_anim_dir.exists():
            anim_file = old_anim_dir / f"{old}.animation.json"
            if anim_file.exists():
                with open(anim_file, 'r') as f:
                    anim = json.load(f)
                anim['animations'] = {
                    (f"animation.{new}." + k[len(f"animation.{old}."):]
                     if k.startswith(f"animation.{old}.") else k): v
                    for k, v in anim.get('animations', {}).items()}
                with open(anim_file, 'w') as f:
                    json.dump(anim, f, indent=2)
                anim_file.rename(old_anim_dir / f"{new}.animation.json")
            old_anim_dir.rename(bedrock / "animations" / new)
            changes.append("animation (keys, file, folder)")

        # 5. Poser: bedrock() refs, filename
        old_poser = bedrock / "posers" / f"{old}.json"
        if old_poser.exists():
            text = old_poser.read_text(encoding='utf-8')
            text = text.replace(f"bedrock({old},", f"bedrock({new},")
            (bedrock / "posers" / f"{new}.json").write_text(text, encoding='utf-8')
            old_poser.unlink()
            changes.append("poser (bedrock() refs, filename)")

        # 6. Resolver: species/model/poser/texture refs, filename
        resolvers_dir = bedrock / "resolvers"
        if resolvers_dir.exists():
            for res_file in list(resolvers_dir.glob(f"*_{old}_base.json")):
                with open(res_file, 'r') as f:
                    res = json.load(f)
                if res.get('species') == f"cobblemon:{old}":
                    res['species'] = f"cobblemon:{new}"
                for var in res.get('variations', []) or []:
                    if not isinstance(var, dict):
                        continue
                    if var.get('model') == f"cobblemon:{old}.geo":
                        var['model'] = f"cobblemon:{new}.geo"
                    if var.get('poser') == f"cobblemon:{old}":
                        var['poser'] = f"cobblemon:{new}"
                    if 'texture' in var:
                        var['texture'] = (str(var['texture'])
                                          .replace(f"pokemon/{old}/", f"pokemon/{new}/")
                                          .replace(f"/{old}_shiny.png", f"/{new}_shiny.png")
                                          .replace(f"/{old}.png", f"/{new}.png"))
                new_res_name = res_file.name.replace(f"_{old}_base.json", f"_{new}_base.json")
                with open(resolvers_dir / new_res_name, 'w') as f:
                    json.dump(res, f, indent=2)
                res_file.unlink()
            changes.append("resolver (species/model/poser/texture refs, filename)")

        # 7. Textures: files, folder
        old_tex_dir = (self.resource_pack_dir / "assets" / "cobblemon" /
                       "textures" / "pokemon" / old)
        if old_tex_dir.exists():
            for tex in list(old_tex_dir.iterdir()):
                if tex.name.startswith(old):
                    tex.rename(old_tex_dir / (new + tex.name[len(old):]))
            old_tex_dir.rename(old_tex_dir.parent / new)
            changes.append("textures (files, folder)")

        # 8. Lang: all cobblemon.species.{old}.* keys
        lang_file = (self.resource_pack_dir / "assets" / "cobblemon" /
                     "lang" / "en_us.json")
        if lang_file.exists():
            with open(lang_file, 'r', encoding='utf-8') as f:
                lang = json.load(f)
            prefix = f"cobblemon.species.{old}."
            renamed = {}
            for k, v in lang.items():
                renamed[f"cobblemon.species.{new}." + k[len(prefix):] if k.startswith(prefix) else k] = v
            # Update the display name VALUE too (if it was the auto-generated default)
            name_key = f"cobblemon.species.{new}.name"
            if name_key in renamed:
                if str(renamed[name_key]).lower() == old:
                    renamed[name_key] = new.title()
                else:
                    print(f"WARNING: Display name '{renamed[name_key]}' looks custom — kept as-is.")
                    print(f"   Update it manually in en_us.json if it should change.")
            # Warn if desc prose still mentions the old name (can't safely auto-rewrite)
            stale = [k for k, v in renamed.items()
                     if k.startswith(f"cobblemon.species.{new}.desc") and old in str(v).lower()]
            if stale:
                print(f"WARNING: Pokédex text still mentions '{old}' in: {', '.join(stale)}")
                print(f"   Update with: --edit {new} --desc1 \"...\" --desc2 \"...\"")
            if renamed != lang:
                with open(lang_file, 'w', encoding='utf-8') as f:
                    json.dump(renamed, f, indent=2, ensure_ascii=False)
                changes.append("lang file (name/desc keys)")

        # 9. Other species: evolutions results/ids and preEvolution references
        touched_others = []
        for other_file in species_dir.glob("*.json"):
            try:
                with open(other_file, 'r') as f:
                    other = json.load(f)
            except Exception:
                continue
            dirty = False
            for evo in other.get('evolutions', []) or []:
                if not isinstance(evo, dict):
                    continue
                parts = str(evo.get('result', '')).split(' ')
                if parts and parts[0].split(':')[-1] == old:
                    ns = parts[0][:-len(old)]
                    evo['result'] = ' '.join([ns + new] + parts[1:]).strip()
                    dirty = True
                if str(evo.get('id', '')).endswith(f"_{old}"):
                    evo['id'] = evo['id'][:-len(old)] + new
                    dirty = True
            if other.get('preEvolution') == old:
                other['preEvolution'] = new
                dirty = True
            if dirty:
                with open(other_file, 'w') as f:
                    json.dump(other, f, indent=2)
                touched_others.append(other_file.stem)
        if touched_others:
            changes.append(f"other species referencing it: {', '.join(touched_others)}")

        # 10. Species additions: targets, evolution results, filenames
        additions_dir = (self.behavior_pack_dir / "data" / "cobblemon" /
                         "species_additions")
        if additions_dir.exists():
            touched_adds = []
            for add_file in list(additions_dir.glob("*.json")):
                try:
                    with open(add_file, 'r') as f:
                        add = json.load(f)
                except Exception:
                    continue
                dirty = False
                if add.get('target') == f"cobblemon:{old}":
                    add['target'] = f"cobblemon:{new}"
                    dirty = True
                for evo in add.get('evolutions', []) or []:
                    if isinstance(evo, dict):
                        parts = str(evo.get('result', '')).split(' ')
                        if parts and parts[0].split(':')[-1] == old:
                            ns = parts[0][:-len(old)]
                            evo['result'] = ' '.join([ns + new] + parts[1:]).strip()
                            dirty = True
                        if str(evo.get('id', '')).endswith(f"_{old}"):
                            evo['id'] = evo['id'][:-len(old)] + new
                            dirty = True
                if dirty:
                    new_add_name = add_file.name.replace(f"_{old}_", f"_{new}_")
                    with open(additions_dir / new_add_name, 'w') as f:
                        json.dump(add, f, indent=2)
                    if new_add_name != add_file.name:
                        add_file.unlink()
                    touched_adds.append(new_add_name)
            if touched_adds:
                changes.append(f"species_additions: {', '.join(touched_adds)}")

        print(f"RENAME COMPLETE — sites updated:")
        for c in changes:
            print(f"   • {c}")
        print(f"\nSTRONGLY recommended: run pack_checker.py now to verify all references")
        print(f"Reload in-game: /reload")
        print(f"{'=' * 70}\n")
        return True

    def generate_pokemon(self, pokemon_name: str, config: Dict, cleanup: bool = True):
        """Main function to generate Pokémon packs"""
        print(f"\n{'=' * 70}")
        print(f"Cobblemon Pack Generator - Creating {pokemon_name.upper()}")
        print(f"{'=' * 70}")

        # Important warning
        print(f"\nWARNING: IMPORTANT: Keep this Python script OUTSIDE of:")
        print(f"   {self.base_dir}")
        print(f"   (Only put your .geo.json, .animation.json, .png files there!)")

        # Find files
        print(f"\nScanning {self.base_dir} for files...")
        files = self.find_files_in_base_dir()

        print(f"\nFound:")
        print(f"  • {len(files['animations'])} animation file(s)")
        print(f"  • {len(files['models'])} model file(s)")
        print(f"  • {len(files['textures'])} texture file(s)")

        if not any(files[key] for key in ['animations', 'models', 'textures']):
            print("\nWARNING: No valid files found! Please add files to:")
            print(f"    {self.base_dir}")
            return False

        # Setup directories
        self.setup_directories(pokemon_name)

        # Organize files
        self.organize_files(pokemon_name, files)

        # Generate configuration files
        self.generate_pack_files(pokemon_name, config)

        # Info message about head bone
        if config.get('head_bone', 'head').lower() == 'none':
            print(f"\nNOTE: Note: No head bone specified")
            print(f"   - Poser will not include 'head' field")
            print(f"   - Species 'canLook' automatically set to false")

        # Cleanup if requested
        if cleanup:
            self.cleanup_source_files(files)

        print(f"\n{'=' * 70}")
        print("PACK GENERATION COMPLETE! ")
        print(f"{'=' * 70}")
        print(f"\nYour packs are at:")
        print(f"   Resource Pack: {self.resource_pack_dir}")
        print(f"   Behavior Pack: {self.behavior_pack_dir}")
        print(f"\nPack Formats:")
        print(f"   Resource: {self.RESOURCE_PACK_FORMAT} | Behavior: {self.DATA_PACK_FORMAT}")
        print(f"   WARNING: Can only combine into one folder if formats match!")
        print(f"\nAdding More Pokémon:")
        print(f"   Just run the script again with new files and a new name!")
        print(f"   It will ADD to the existing packs (won't overwrite)")
        print(f"\nTIP: Installation:")
        print(f"   1. Copy resource_pack/ to .minecraft/resourcepacks/")
        print(f"   2. Copy behavior_pack/ to .minecraft/saves/YourWorld/datapacks/")
        print(f"   3. In-game: Enable resource pack, /reload")
        print(f"   4. Test: /pokespawn {pokemon_name.lower()}")
        print(f"\nTexture Issue?")
        print(f"   If showing practice dummy, check:")
        print(f"   - Texture is .png format")
        print(f"   - Model identifier matches Pokémon name")
        print(f"   - Both packs are installed AND enabled")
        print(f"   - Run /reload after installing")
        print(f"\n{'=' * 70}\n")

        return True


def main():
    """Main entry point with customization options"""
    parser = argparse.ArgumentParser(
        description='Generate Cobblemon packs with full customization',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic Pokémon
  python cobblemon_pack_generator.py --name Flamebird --number 999

  # With custom stats and type
  python cobblemon_pack_generator.py --name Aquadragon --number 1000 \\
    --primary-type water --secondary-type dragon \\
    --hp 100 --attack 80 --defence 90

  # With moves and abilities
  python cobblemon_pack_generator.py --name Earthgolem --number 1001 \\
    --moves "1:tackle,7:rockthrow,20:earthquake,tm:stoneedge" \\
    --abilities "sturdy,h:sandforce"

  # Flying/Swimming Pokémon
  python cobblemon_pack_generator.py --name Skywhale --number 1002 \\
    --can-fly --can-swim --breathe-underwater
        """
    )

    # Required arguments (unless using --show-current-pokemon)
    parser.add_argument('--name', type=str, help='Pokémon name')
    parser.add_argument('--number', type=int, help='Pokédex number')

    # Type arguments
    parser.add_argument('--primary-type', type=str, default=None, help='Primary type (default: normal on create)')
    parser.add_argument('--secondary-type', type=str, help='Secondary type (optional)')

    # Stats
    parser.add_argument('--hp', type=int, default=None, help='HP stat (default: 50 on create)')
    parser.add_argument('--attack', type=int, default=None, help='Attack stat (default: 50 on create)')
    parser.add_argument('--defence', type=int, default=None, help='Defence stat (default: 50 on create)')
    parser.add_argument('--special-attack', type=int, default=None, help='Special Attack (default: 50 on create)')
    parser.add_argument('--special-defence', type=int, default=None, help='Special Defence (default: 50 on create)')
    parser.add_argument('--speed', type=int, default=None, help='Speed stat (default: 50 on create)')

    # Moves and abilities
    parser.add_argument('--moves', type=str, help='Comma-separated moves (e.g. "1:tackle,7:ember,tm:flamethrower")')
    parser.add_argument('--abilities', type=str, help='Comma-separated abilities (e.g. "blaze,h:solar_power")')

    # Physical properties
    parser.add_argument('--height', type=int, default=None, help='Height in decimeters (default: 10 on create)')
    parser.add_argument('--weight', type=int, default=None, help='Weight in hectograms (default: 100 on create)')

    # Movement abilities
    parser.add_argument('--can-fly', action='store_true', help='Pokémon can fly')
    parser.add_argument('--can-swim', action='store_true', help='Pokémon can swim')
    parser.add_argument('--breathe-underwater', action='store_true', help='Can breathe underwater')
    parser.add_argument('--no-look', action='store_true', help='Pokémon cannot look around (canLook=false)')

    # Spawn configuration
    parser.add_argument('--rarity', type=str, default=None, choices=['common', 'uncommon', 'rare', 'ultra-rare'],
                        help='Spawn rarity (default: common on create)')
    parser.add_argument('--spawn-level', type=str, default=None, help='Spawn level range (e.g. "10-40"; default: 5-30 on create)')
    parser.add_argument('--spawn-biomes', type=str, default=None,
                        help='Comma-separated biome tags (default: #minecraft:is_overworld on create)')

    # Descriptions
    parser.add_argument('--desc1', type=str, help='First Pokédex entry')
    parser.add_argument('--desc2', type=str, help='Second Pokédex entry')

    # Legendary/Mythical
    parser.add_argument('--legendary', action='store_true',
                        help='Make this a legendary Pokémon (sets catchRate=3, baseExp=290, adds legendary label)')

    # Evolution
    parser.add_argument('--evo-target', type=str, help='Pokémon this evolves into (e.g. "brightfix")')
    parser.add_argument('--evo-method', type=str, choices=['level_up', 'item_interact', 'trade'],
                        default='level_up', help='Evolution method (default: level_up)')
    parser.add_argument('--evo-level', type=int, default=36, help='Level to evolve at (default: 36)')
    parser.add_argument('--evo-item', type=str, help='Item required for item_interact or trade evolution')
    parser.add_argument('--pre-evolution', type=str, help='Pokémon this evolves from (e.g. "grayfix")')
    parser.add_argument('--remove-evolutions', action='store_true',
                        help='(edit mode) Remove ALL evolutions from the Pokémon')

    # Species fields (work in BOTH create and edit modes)
    parser.add_argument('--catch-rate', '--catchrate', type=int, default=None, dest='catch_rate',
                        help='Catch rate 3-255 (default: 45 on create; 3=legendary-hard, 255=trivial)')
    parser.add_argument('--male-ratio', type=float, default=None,
                        help='Male ratio -1 to 1 (-1=genderless, 0=all female, 1=all male; default: 0.5 on create)')
    parser.add_argument('--exp-group', type=str, default=None,
                        help='Experience group (default: medium_fast on create)')
    parser.add_argument('--egg-cycles', type=int, default=None,
                        help='Egg cycles (default: 20 on create)')
    parser.add_argument('--egg-groups', type=str, default=None,
                        help='Comma-separated egg groups (default: field on create)')
    parser.add_argument('--base-exp', type=int, default=None,
                        help='Base experience yield (default: 100 on create)')
    parser.add_argument('--friendship', type=int, default=None,
                        help='Base friendship (default: 50 on create)')
    parser.add_argument('--ev-yield', type=str, default=None,
                        help='EV yield, e.g. "speed:2" or "attack:1,hp:1" (default: hp:1 on create)')
    parser.add_argument('--drops', type=str, default=None,
                        help='Item drops, e.g. "minecraft:redstone:50,cobblemon:exp_candy_xs:10" (item:percentage)')
    parser.add_argument('--base-scale', type=float, default=None,
                        help='Model scale multiplier')
    parser.add_argument('--hitbox', type=str, default=None,
                        help='Hitbox "width,height" (e.g. "1.5,2")')
    parser.add_argument('--spawn-weight', type=float, default=None,
                        help='Spawn weight (default: 10 on create, 0.05 for legendary)')
    parser.add_argument('--can-see-sky', type=str, default=None, choices=['true', 'false'],
                        help='Spawn condition: false = underground/cave spawner')
    parser.add_argument('--not-legendary', action='store_true',
                        help='(edit mode) Remove legendary status')
    parser.add_argument('--add-moves', type=str, default=None,
                        help='(edit mode) APPEND moves to the existing list (unlike --moves which replaces)')

    # Model customization
    parser.add_argument('--version', action='version',
                        version=f'Cobblemon Pack Generator v{GENERATOR_VERSION}')
    parser.add_argument('--head-bone', type=str, default=None,
                        help='Head bone name (use "none" if model has no head; default: "head" on create)')

    # Other options
    parser.add_argument('--downloads', type=str, help='Custom Downloads path')
    parser.add_argument('--no-cleanup', action='store_true', help='Keep source files')
    parser.add_argument('--show-current-pokemon', action='store_true', help='Show all Pokémon currently in the packs')
    parser.add_argument('--edit', type=str, help='Edit an existing Pokémon (use Pokémon name)')
    parser.add_argument('--rename', type=str,
                        help='(with --edit) Rename the Pokémon across ALL files/references')
    parser.add_argument('--editfiles', type=str, metavar='POKEMON',
                        help='Swap in new model/animation/texture files from the pack folder '
                             '(old files are moved out; run again to undo)')

    args = parser.parse_args()

    # Create generator (needed by --show-current-pokemon, --edit, and creation)
    generator = CobblemonPackGenerator(downloads_path=args.downloads)

    # Handle --editfiles command
    if args.editfiles:
        generator.edit_files(args.editfiles)
        return

    # Handle --rename (requires --edit)
    if args.rename:
        if not args.edit:
            parser.error('--rename requires --edit <current-name>')
        generator.rename_pokemon(args.edit, args.rename)
        return

    # Handle --show-current-pokemon command
    if args.show_current_pokemon:
        generator.show_current_pokemon()
        return

    # Handle --edit command
    if args.edit:
        generator.edit_pokemon(args.edit, args)
        return

    # Validate required arguments when creating a Pokémon
    if not args.name or not args.number:
        parser.error("--name and --number are required when creating a Pokémon")

    # Build configuration dictionary
    config = {
        'pokedex_number': args.number,
        'primary_type': args.primary_type if args.primary_type is not None else 'normal',
        'secondary_type': args.secondary_type,
        'hp': args.hp if args.hp is not None else 50,
        'attack': args.attack if args.attack is not None else 50,
        'defence': args.defence if args.defence is not None else 50,
        'special_attack': args.special_attack if args.special_attack is not None else 50,
        'special_defence': args.special_defence if args.special_defence is not None else 50,
        'speed': args.speed if args.speed is not None else 50,
        'moves': args.moves,
        'abilities': args.abilities,
        'height': args.height if args.height is not None else 10,
        'weight': args.weight if args.weight is not None else 100,
        'can_fly': args.can_fly,
        'can_swim': args.can_swim,
        'breathe_underwater': args.breathe_underwater,
        'can_look': not args.no_look,  # Inverted: --no-look sets canLook to false
        'rarity': args.rarity if args.rarity is not None else 'common',
        'spawn_level': args.spawn_level if args.spawn_level is not None else '5-30',
        'spawn_biomes': args.spawn_biomes if args.spawn_biomes is not None else '#minecraft:is_overworld',
        'desc1': args.desc1,
        'desc2': args.desc2,
        'head_bone': args.head_bone if args.head_bone is not None else 'head',
        'legendary': args.legendary,
        'evo_target': args.evo_target,
        'evo_method': args.evo_method,
        'evo_level': args.evo_level,
        'evo_item': args.evo_item,
        'pre_evolution': args.pre_evolution,
        'catch_rate': args.catch_rate if args.catch_rate is not None else 45,
        'male_ratio': args.male_ratio if args.male_ratio is not None else 0.5,
        'exp_group': args.exp_group if args.exp_group is not None else 'medium_fast',
        'egg_cycles': args.egg_cycles if args.egg_cycles is not None else 20,
        'egg_groups': ([g.strip() for g in args.egg_groups.split(',')]
                       if args.egg_groups is not None else ['field']),
        'base_exp': args.base_exp if args.base_exp is not None else 100,
        'friendship': args.friendship if args.friendship is not None else 50,
        'ev_yield_spec': args.ev_yield,
        'drops_spec': args.drops,
        'base_scale': args.base_scale,
        'hitbox_spec': args.hitbox,
        'spawn_surface': (args.can_see_sky != 'false') if args.can_see_sky is not None else True,
        'spawn_weight': args.spawn_weight if args.spawn_weight is not None else 10.0,
    }

    # Apply legendary settings if --legendary flag is used
    if args.legendary:
        config['catch_rate'] = 3  # Hard to catch (like Mewtwo)
        config['base_exp'] = 290  # High experience yield
        config['labels'] = ['custom', 'legendary']
        config['friendship'] = 0  # Starts unfriendly
        if args.spawn_weight is None:
            config['spawn_weight'] = 0.05  # Extremely rare spawn

        # Auto-set ultra-rare if not specified
        if args.rarity == 'common':  # Default value
            config['rarity'] = 'ultra-rare'

        print("\nLegendary mode activated!")
        print("   - Catch rate: 3 (very hard)")
        print("   - Base EXP: 290 (legendary level)")
        print("   - Spawn weight: 0.05 (extremely rare)")
        print("   - Labels: custom, legendary")

    # Generate the packs
    success = generator.generate_pokemon(
        pokemon_name=args.name,
        config=config,
        cleanup=not args.no_cleanup
    )

    if not success:
        exit(1)


if __name__ == "__main__":
    main()
