#!/usr/bin/env python3
"""
Cobblemon Pokémon Pack Generator for Minecraft 1.21.1
Creates SEPARATE resource and behavior packs for easier distribution
"""

import os
import json
import shutil
from pathlib import Path
from typing import Dict, List, Optional
import argparse


class CobblemonPackGenerator:
    """Generates separate Cobblemon resource and behavior packs"""
    
    # Pack formats for 1.21.1
    RESOURCE_PACK_FORMAT = 34  # Change to 40+ if needed for newer versions
    DATA_PACK_FORMAT = 48      # Data pack format for 1.21.1
    
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
        print(f"\n📁 Setting up directory structure for {pokemon_name}...")
        
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
        
        print("✅ Directory structure created!")
    
    def find_files_in_base_dir(self) -> Dict[str, List[Path]]:
        """Find all relevant files in the base directory (excludes Python scripts)"""
        files = {
            'animations': [],
            'models': [],
            'textures': [],
            'other': []
        }
        
        if not self.base_dir.exists():
            print(f"⚠️  Base directory not found: {self.base_dir}")
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
        
        # Parse types
        primary_type = config.get('primary_type', 'normal')
        secondary_type = config.get('secondary_type')
        
        return {
            "implemented": True,
            "name": pokemon_lower,
            "labels": ["custom"],
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
            "eggGroups": [config.get('egg_group', 'field')],
            "baseFriendship": config.get('friendship', 50),
            "evYield": {
                "hp": config.get('ev_hp', 1),
                "attack": config.get('ev_attack', 0),
                "defence": config.get('ev_defence', 0),
                "special_attack": config.get('ev_sp_attack', 0),
                "special_defence": config.get('ev_sp_defence', 0),
                "speed": config.get('ev_speed', 0)
            },
            "height": config.get('height', 10),
            "weight": config.get('weight', 100),
            "aspects": [],
            "cannotDynamax": False,
            "drops": {
                "amount": "1-2",
                "entries": []
            },
            "moves": moves,
            "abilities": abilities,
            "evolutions": [],
            "preEvolution": config.get('pre_evolution'),
            "behaviour": {
                "moving": {
                    # canLook must be false if no head bone, otherwise true by default
                    "canLook": False if (config.get('head_bone', 'head').lower() == 'none') else config.get('can_look', True),
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
    
    def create_poser_json(self, pokemon_name: str, config: Dict) -> Dict:
        """Create poser configuration"""
        pokemon_lower = pokemon_name.lower()
        
        # Build animations based on movement type
        poses = {
            "standing": {
                "poseName": "standing",
                "transformTicks": 10,
                "poseTypes": ["STAND", "NONE", "PORTRAIT", "PROFILE"],
                "animations": [
                    "look",
                    f"bedrock({pokemon_lower}, ground_idle)"
                ]
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
                    # Shiny variant with full path
                    "texture": f"cobblemon:textures/pokemon/{pokemon_lower}/{pokemon_lower}_shiny.png"
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
                        "biomes": config.get('spawn_biomes', ['#minecraft:is_overworld']).split(',') if isinstance(config.get('spawn_biomes', '#minecraft:is_overworld'), str) else config.get('spawn_biomes', ['#minecraft:is_overworld'])
                    }
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
                        "biomes": config.get('spawn_biomes', ['#minecraft:is_overworld']).split(',') if isinstance(config.get('spawn_biomes', '#minecraft:is_overworld'), str) else config.get('spawn_biomes', ['#minecraft:is_overworld'])
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
                print(f"\n⚠️  WARNING: Missing recommended animations: {', '.join(missing)}")
                print(f"   Your Pokémon may not animate properly!")
                print(f"   Add these animations in Blockbench:")
                for anim in missing:
                    print(f"   - animation.{pokemon_name}.{anim}")
            else:
                print(f"  ✓ Animation validation passed")
                
        except Exception as e:
            print(f"  ⚠️  Could not validate animations: {e}")
    
    def organize_files(self, pokemon_name: str, files: Dict[str, List[Path]]):
        """Organize files into resource pack"""
        print(f"\n📦 Organizing files for {pokemon_name}...")
        
        pokemon_lower = pokemon_name.lower()
        
        # Validate animation file if present
        if files['animations']:
            self.validate_animations(files['animations'][0], pokemon_lower)
        
        # Copy animations
        if files['animations']:
            dest_dir = self.resource_pack_dir / "assets" / "cobblemon" / "bedrock" / "pokemon" / "animations" / pokemon_lower
            for anim_file in files['animations']:
                dest_file = dest_dir / f"{pokemon_lower}_animation.json"
                shutil.copy2(anim_file, dest_file)
                print(f"  ✓ Animation: {anim_file.name} → {dest_file.relative_to(self.resource_pack_dir)}")
        
        # Copy models
        if files['models']:
            dest_dir = self.resource_pack_dir / "assets" / "cobblemon" / "bedrock" / "pokemon" / "models" / pokemon_lower
            for model_file in files['models']:
                dest_file = dest_dir / f"{pokemon_lower}_geo.json"
                shutil.copy2(model_file, dest_file)
                print(f"  ✓ Model: {model_file.name} → {dest_file.relative_to(self.resource_pack_dir)}")
        
        # Copy textures
        if files['textures']:
            dest_dir = self.resource_pack_dir / "assets" / "cobblemon" / "textures" / "pokemon" / pokemon_lower
            for idx, texture_file in enumerate(files['textures']):
                if idx == 0:
                    dest_file = dest_dir / f"{pokemon_lower}.png"
                elif idx == 1:
                    dest_file = dest_dir / f"{pokemon_lower}_shiny.png"
                else:
                    dest_file = dest_dir / texture_file.name
                shutil.copy2(texture_file, dest_file)
                print(f"  ✓ Texture: {texture_file.name} → {dest_file.relative_to(self.resource_pack_dir)}")
        
        print("✅ Files organized!")
    
    def generate_pack_files(self, pokemon_name: str, config: Dict):
        """Generate all pack configuration files"""
        print(f"\n⚙️  Generating configuration files for {pokemon_name}...")
        
        pokemon_lower = pokemon_name.lower()
        
        # Resource pack.mcmeta (create if doesn't exist)
        resource_mcmeta = self.resource_pack_dir / "pack.mcmeta"
        if not resource_mcmeta.exists():
            with open(resource_mcmeta, 'w') as f:
                json.dump(self.create_pack_mcmeta('resource'), f, indent=2)
            print(f"  ✓ Resource pack.mcmeta created (format {self.RESOURCE_PACK_FORMAT})")
        else:
            print(f"  ℹ️  Resource pack.mcmeta already exists (keeping existing)")
        
        # Behavior pack.mcmeta (create if doesn't exist)
        behavior_mcmeta = self.behavior_pack_dir / "pack.mcmeta"
        if not behavior_mcmeta.exists():
            with open(behavior_mcmeta, 'w') as f:
                json.dump(self.create_pack_mcmeta('behavior'), f, indent=2)
            print(f"  ✓ Behavior pack.mcmeta created (format {self.DATA_PACK_FORMAT})")
        else:
            print(f"  ℹ️  Behavior pack.mcmeta already exists (keeping existing)")
        
        # Species definition
        species_file = self.behavior_pack_dir / "data" / "cobblemon" / "species" / "custom" / f"{pokemon_lower}.json"
        with open(species_file, 'w') as f:
            json.dump(self.create_species_json(pokemon_name, config), f, indent=2)
        print(f"  ✓ Species definition")
        
        # Poser
        poser_file = self.resource_pack_dir / "assets" / "cobblemon" / "bedrock" / "pokemon" / "posers" / f"{pokemon_lower}.json"
        with open(poser_file, 'w') as f:
            json.dump(self.create_poser_json(pokemon_name, config), f, indent=2)
        print(f"  ✓ Poser configuration")
        
        # Resolver
        resolver_file = self.resource_pack_dir / "assets" / "cobblemon" / "bedrock" / "pokemon" / "resolvers" / f"0_{pokemon_lower}_base.json"
        with open(resolver_file, 'w') as f:
            json.dump(self.create_resolver_json(pokemon_name), f, indent=2)
        print(f"  ✓ Model resolver")
        
        # Spawn pool
        spawn_file = self.behavior_pack_dir / "data" / "cobblemon" / "spawn_pool_world" / f"{pokemon_lower}.json"
        with open(spawn_file, 'w') as f:
            json.dump(self.create_spawn_pool_json(pokemon_name, config), f, indent=2)
        print(f"  ✓ Spawn pool")
        
        # Language file - MERGE with existing if present
        lang_file = self.resource_pack_dir / "assets" / "cobblemon" / "lang" / "en_us.json"
        new_lang_data = {
            f"cobblemon.species.{pokemon_lower}.name": pokemon_name,
            f"cobblemon.species.{pokemon_lower}.desc1": config.get('desc1', f"A mysterious Pokémon known as {pokemon_name}."),
            f"cobblemon.species.{pokemon_lower}.desc2": config.get('desc2', "Customize this description in the language file!")
        }
        
        # Load existing language file and merge
        if lang_file.exists():
            with open(lang_file, 'r') as f:
                existing_lang = json.load(f)
            existing_lang.update(new_lang_data)
            with open(lang_file, 'w') as f:
                json.dump(existing_lang, f, indent=2, sort_keys=True)
            print(f"  ✓ Language file updated (merged with existing)")
        else:
            with open(lang_file, 'w') as f:
                json.dump(new_lang_data, f, indent=2)
            print(f"  ✓ Language file created")
        
        print("✅ Configuration files generated!")
    
    def cleanup_source_files(self, files: Dict[str, List[Path]]):
        """Remove source files after copying (NEVER deletes .py files or files outside base_dir)"""
        print("\n🧹 Cleaning up source files...")
        
        files_to_remove = []
        for file_list in files.values():
            files_to_remove.extend(file_list)
        
        for file in files_to_remove:
            # Safety checks - NEVER delete:
            # 1. Python files
            # 2. Files outside the base directory
            # 3. The script itself
            if file.suffix == '.py':
                print(f"  ⚠️  Skipped (Python file): {file.name}")
                continue
            
            if not str(file).startswith(str(self.base_dir)):
                print(f"  ⚠️  Skipped (outside base directory): {file.name}")
                continue
            
            if file.exists():
                file.unlink()
                print(f"  ✓ Removed: {file.name}")
        
        print("✅ Cleanup complete!")
    
    def generate_pokemon(self, pokemon_name: str, config: Dict, cleanup: bool = True):
        """Main function to generate Pokémon packs"""
        print(f"\n{'='*70}")
        print(f"🎮 Cobblemon Pack Generator - Creating {pokemon_name.upper()}")
        print(f"{'='*70}")
        
        # Important warning
        print(f"\n⚠️  IMPORTANT: Keep this Python script OUTSIDE of:")
        print(f"   {self.base_dir}")
        print(f"   (Only put your .geo.json, .animation.json, .png files there!)")
        
        # Find files
        print(f"\n🔍 Scanning {self.base_dir} for files...")
        files = self.find_files_in_base_dir()
        
        print(f"\nFound:")
        print(f"  • {len(files['animations'])} animation file(s)")
        print(f"  • {len(files['models'])} model file(s)")
        print(f"  • {len(files['textures'])} texture file(s)")
        
        if not any(files[key] for key in ['animations', 'models', 'textures']):
            print("\n⚠️  No valid files found! Please add files to:")
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
            print(f"\nℹ️  Note: No head bone specified")
            print(f"   - Poser will not include 'head' field")
            print(f"   - Species 'canLook' automatically set to false")
        
        # Cleanup if requested
        if cleanup:
            self.cleanup_source_files(files)
        
        print(f"\n{'='*70}")
        print("✨ PACK GENERATION COMPLETE! ✨")
        print(f"{'='*70}")
        print(f"\n📍 Your packs are at:")
        print(f"   Resource Pack: {self.resource_pack_dir}")
        print(f"   Behavior Pack: {self.behavior_pack_dir}")
        print(f"\n📝 Pack Formats:")
        print(f"   Resource: {self.RESOURCE_PACK_FORMAT} | Behavior: {self.DATA_PACK_FORMAT}")
        print(f"   ⚠️  Can only combine into one folder if formats match!")
        print(f"\n🔄 Adding More Pokémon:")
        print(f"   Just run the script again with new files and a new name!")
        print(f"   It will ADD to the existing packs (won't overwrite)")
        print(f"\n💡 Installation:")
        print(f"   1. Copy resource_pack/ to .minecraft/resourcepacks/")
        print(f"   2. Copy behavior_pack/ to .minecraft/saves/YourWorld/datapacks/")
        print(f"   3. In-game: Enable resource pack, /reload")
        print(f"   4. Test: /pokespawn {pokemon_name.lower()}")
        print(f"\n🐛 Texture Issue?")
        print(f"   If showing practice dummy, check:")
        print(f"   - Texture is .png format")
        print(f"   - Model identifier matches Pokémon name")
        print(f"   - Both packs are installed AND enabled")
        print(f"   - Run /reload after installing")
        print(f"\n{'='*70}\n")
        
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
    
    # Required arguments
    parser.add_argument('--name', type=str, required=True, help='Pokémon name')
    parser.add_argument('--number', type=int, required=True, help='Pokédex number')
    
    # Type arguments
    parser.add_argument('--primary-type', type=str, default='normal', help='Primary type (default: normal)')
    parser.add_argument('--secondary-type', type=str, help='Secondary type (optional)')
    
    # Stats
    parser.add_argument('--hp', type=int, default=50, help='HP stat (default: 50)')
    parser.add_argument('--attack', type=int, default=50, help='Attack stat (default: 50)')
    parser.add_argument('--defence', type=int, default=50, help='Defence stat (default: 50)')
    parser.add_argument('--special-attack', type=int, default=50, help='Special Attack (default: 50)')
    parser.add_argument('--special-defence', type=int, default=50, help='Special Defence (default: 50)')
    parser.add_argument('--speed', type=int, default=50, help='Speed stat (default: 50)')
    
    # Moves and abilities
    parser.add_argument('--moves', type=str, help='Comma-separated moves (e.g. "1:tackle,7:ember,tm:flamethrower")')
    parser.add_argument('--abilities', type=str, help='Comma-separated abilities (e.g. "blaze,h:solar_power")')
    
    # Physical properties
    parser.add_argument('--height', type=int, default=10, help='Height in decimeters (default: 10)')
    parser.add_argument('--weight', type=int, default=100, help='Weight in hectograms (default: 100)')
    
    # Movement abilities
    parser.add_argument('--can-fly', action='store_true', help='Pokémon can fly')
    parser.add_argument('--can-swim', action='store_true', help='Pokémon can swim')
    parser.add_argument('--breathe-underwater', action='store_true', help='Can breathe underwater')
    
    # Spawn configuration
    parser.add_argument('--rarity', type=str, default='common', choices=['common', 'uncommon', 'rare', 'ultra-rare'], help='Spawn rarity')
    parser.add_argument('--spawn-level', type=str, default='5-30', help='Spawn level range (e.g. "10-40")')
    parser.add_argument('--spawn-biomes', type=str, default='#minecraft:is_overworld', help='Spawn biomes (comma-separated)')
    
    # Descriptions
    parser.add_argument('--desc1', type=str, help='First Pokédex entry')
    parser.add_argument('--desc2', type=str, help='Second Pokédex entry')
    
    # Model customization
    parser.add_argument('--head-bone', type=str, default='head', help='Head bone name (use "none" if model has no head)')
    
    # Other options
    parser.add_argument('--downloads', type=str, help='Custom Downloads path')
    parser.add_argument('--no-cleanup', action='store_true', help='Keep source files')
    
    args = parser.parse_args()
    
    # Build configuration dictionary
    config = {
        'pokedex_number': args.number,
        'primary_type': args.primary_type,
        'secondary_type': args.secondary_type,
        'hp': args.hp,
        'attack': args.attack,
        'defence': args.defence,
        'special_attack': args.special_attack,
        'special_defence': args.special_defence,
        'speed': args.speed,
        'moves': args.moves,
        'abilities': args.abilities,
        'height': args.height,
        'weight': args.weight,
        'can_fly': args.can_fly,
        'can_swim': args.can_swim,
        'breathe_underwater': args.breathe_underwater,
        'can_look': not args.no_look,  # Inverted: --no-look sets canLook to false
        'rarity': args.rarity,
        'spawn_level': args.spawn_level,
        'spawn_biomes': args.spawn_biomes,
        'desc1': args.desc1,
        'desc2': args.desc2,
        'head_bone': args.head_bone,
    }
    
    # Create generator
    generator = CobblemonPackGenerator(downloads_path=args.downloads)
    
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
