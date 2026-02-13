#!/usr/bin/env python3
"""
Cobblemon Species Editor (v1.1)
Edit existing Pokémon through Species Additions
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Optional
import argparse


class CobblemonSpeciesEditor:
    """Edit existing Pokémon using Species Additions"""
    
    # Valid types
    TYPES = [
        "normal", "fire", "water", "electric", "grass", "ice", "fighting",
        "poison", "ground", "flying", "psychic", "bug", "rock", "ghost",
        "dragon", "dark", "steel", "fairy"
    ]
    
    def __init__(self, pack_path: str = None):
        """Initialize the species editor"""
        if pack_path is None:
            pack_path = str(Path.home() / "Downloads" / "Mod-ResourceAndBehavior-Packs")
        
        self.pack_path = Path(pack_path)
        self.species_additions_dir = self.pack_path / "behavior_pack" / "data" / "cobblemon" / "species_additions"
        
    def setup_directories(self):
        """Create necessary directories"""
        self.species_additions_dir.mkdir(parents=True, exist_ok=True)
    
    def create_species_addition(self, config: Dict) -> bool:
        """Create a Species Addition to modify an existing Pokémon"""
        print(f"\n{'='*70}")
        print(f"📝 CREATING SPECIES ADDITION FOR: {config['pokemon'].upper()}")
        print(f"{'='*70}\n")
        
        self.setup_directories()
        
        target = config['pokemon'].lower()
        
        # Use custom namespace to avoid conflicts
        namespace = config.get('namespace', 'custom')
        addition_file = self.species_additions_dir / f"{namespace}_{target}_addition.json"
        
        # Build the species addition JSON
        addition_data = {
            "target": f"cobblemon:{target}"
        }
        
        changes_made = []
        
        # Add moves if specified
        if config.get('add_moves'):
            moves_list = [m.strip() for m in config['add_moves'].split(',')]
            addition_data["moves"] = moves_list
            changes_made.append(f"Moves: {len(moves_list)} moves set")
            print(f"⚠️  WARNING: This will REPLACE all moves for {target}!")
            print(f"   The Pokémon will ONLY know these {len(moves_list)} moves.")
            print(f"   To keep existing moves, you must include them in the list.\n")
        
        # Add evolution if specified
        if config.get('add_evolution'):
            evo_target = config['add_evolution']
            evo_method = config.get('evo_method', 'level_up')
            
            evolution = {
                "id": f"{target}_{evo_target}",
                "variant": evo_method,
                "result": evo_target,
                "consumeHeldItem": False,
                "learnableMoves": [],
                "requirements": []
            }
            
            # Add requirements based on method
            if evo_method == 'level_up':
                evo_level = config.get('evo_level', 36)
                evolution["requirements"].append({
                    "variant": "level",
                    "minLevel": evo_level
                })
                changes_made.append(f"Evolution: {target} → {evo_target} at level {evo_level}")
                print(f"✅ Adding evolution: {target} → {evo_target} at level {evo_level}")
            
            elif evo_method == 'item_interact':
                evo_item = config.get('evo_item')
                if not evo_item:
                    print(f"⚠️  WARNING: item_interact requires --evo-item! Using default.")
                    evo_item = "minecraft:stone"
                evolution["requiredContext"] = evo_item
                changes_made.append(f"Evolution: {target} → {evo_target} with {evo_item}")
                print(f"✅ Adding evolution: {target} → {evo_target} with {evo_item}")
            
            elif evo_method == 'trade':
                changes_made.append(f"Evolution: {target} → {evo_target} by trading")
                print(f"✅ Adding evolution: {target} → {evo_target} by trading")
                if config.get('evo_item'):
                    evolution["requirements"].append({
                        "variant": "held_item",
                        "item": config['evo_item']
                    })
                    changes_made.append(f"  Requires holding: {config['evo_item']}")
                    print(f"   Requires holding: {config['evo_item']}")
            
            addition_data["evolutions"] = [evolution]
        
        # Change types if specified
        if config.get('primary_type'):
            ptype = config['primary_type'].lower()
            if ptype not in self.TYPES:
                print(f"⚠️  WARNING: '{ptype}' is not a valid type!")
                print(f"   Valid types: {', '.join(self.TYPES)}")
                print(f"   Continuing anyway (might work in newer versions)...\n")
            addition_data["primaryType"] = ptype
            changes_made.append(f"Primary Type: {ptype}")
            print(f"✅ Changing primary type to: {ptype}")
        
        if config.get('secondary_type'):
            stype = config['secondary_type'].lower()
            if stype not in self.TYPES:
                print(f"⚠️  WARNING: '{stype}' is not a valid type!")
                print(f"   Valid types: {', '.join(self.TYPES)}")
                print(f"   Continuing anyway (might work in newer versions)...\n")
            addition_data["secondaryType"] = stype
            changes_made.append(f"Secondary Type: {stype}")
            print(f"✅ Changing secondary type to: {stype}")
        
        # Change scale if specified
        if config.get('base_scale'):
            addition_data["baseScale"] = float(config['base_scale'])
            changes_made.append(f"Base Scale: {config['base_scale']}")
            print(f"✅ Setting base scale to: {config['base_scale']}")
        
        # Change hitbox if specified
        if config.get('hitbox'):
            if ',' not in config['hitbox']:
                print(f"❌ Error: Hitbox must be in format 'width,height' (e.g., '2,2')")
                return False
            try:
                width, height = config['hitbox'].split(',', 1)
                addition_data["hitbox"] = {
                    "width": float(width.strip()),
                    "height": float(height.strip()),
                    "fixed": False
                }
                changes_made.append(f"Hitbox: {width.strip()}x{height.strip()}")
                print(f"✅ Setting hitbox to: {width.strip()}x{height.strip()}")
            except ValueError as e:
                print(f"❌ Error parsing hitbox: {e}")
                print(f"   Format: 'width,height' (e.g., '2,2' or '1.5,2.3')")
                return False
        
        # Add abilities if specified
        if config.get('abilities'):
            abilities_list = [a.strip() for a in config['abilities'].split(',')]
            addition_data["abilities"] = abilities_list
            changes_made.append(f"Abilities: {', '.join(abilities_list)}")
            print(f"✅ Setting abilities to: {', '.join(abilities_list)}")
        
        # Add drops if specified
        if config.get('drops'):
            # Format: "item:percentage,item:percentage"
            drop_entries = []
            try:
                for drop in config['drops'].split(','):
                    if ':' not in drop:
                        print(f"⚠️  WARNING: Skipping invalid drop format: {drop}")
                        print(f"   Format should be: item:percentage")
                        continue
                    item, percentage = drop.split(':', 1)
                    drop_entries.append({
                        "item": item.strip(),
                        "percentage": float(percentage.strip())
                    })
            except ValueError as e:
                print(f"❌ Error parsing drops: {e}")
                print(f"   Format: 'item:percentage,item:percentage'")
                return False
            
            if drop_entries:
                addition_data["drops"] = {
                    "amount": "1-2",
                    "entries": drop_entries
                }
                changes_made.append(f"Drops: {len(drop_entries)} item(s)")
                print(f"✅ Adding {len(drop_entries)} drop(s)")
        
        # Add behavior changes if specified
        if config.get('can_fly') or config.get('can_swim'):
            behavior = {
                "moving": {}
            }
            
            if config.get('can_fly'):
                behavior["moving"]["fly"] = {"canFly": True}
                changes_made.append("Flight: enabled")
                print(f"✅ Enabling flight")
            
            if config.get('can_swim'):
                behavior["moving"]["swim"] = {
                    "canSwimInWater": True,
                    "canBreatheUnderwater": config.get('breathe_underwater', False)
                }
                swim_msg = "Swimming: enabled"
                if config.get('breathe_underwater'):
                    swim_msg += " (can breathe underwater)"
                changes_made.append(swim_msg)
                print(f"✅ Enabling swimming")
            
            addition_data["behaviour"] = behavior
        
        # Check if any changes were made
        if not changes_made:
            print(f"❌ No changes specified!")
            print(f"   Use flags like --add-moves, --add-evolution, --primary-type, etc.")
            print(f"\n💡 Run with --help to see all options")
            return False
        
        # Write the file
        try:
            with open(addition_file, 'w') as f:
                json.dump(addition_data, f, indent=2)
        except Exception as e:
            print(f"\n❌ ERROR: Failed to write file!")
            print(f"   {e}")
            print(f"   Check that the directory exists and you have write permissions.")
            return False
        
        print(f"\n{'='*70}")
        print("✨ SPECIES ADDITION CREATED SUCCESSFULLY! ✨")
        print(f"{'='*70}\n")
        print(f"📁 Addition file: {addition_file}")
        print(f"🎯 Target: cobblemon:{target}")
        print(f"\n📋 Changes applied:")
        for change in changes_made:
            print(f"   • {change}")
        print(f"\n💡 How Species Additions Work:")
        print(f"   • Multiple addons can modify the same Pokémon")
        print(f"   • Evolutions/forms are ADDED (stackable)")
        print(f"   • Other properties are REPLACED (last loaded wins)")
        print(f"\n⚠️  Remember: Move lists are REPLACED, not appended!")
        print(f"   If you added moves, the Pokémon will ONLY know those moves.\n")
        print(f"🔄 Reload in-game: /reload")
        print(f"{'='*70}\n")
        
        return True


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Cobblemon Species Editor (v1.1) - Modify existing Pokémon via Species Additions",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Add moves to Bulbasaur
  python cobblemon_species_editor.py --pokemon bulbasaur --add-moves "flamethrower,earthquake,thunderbolt"
  
  # Eevee → Dragvee with Dragon Scale
  python cobblemon_species_editor.py --pokemon eevee --add-evolution dragvee --evo-method item_interact --evo-item "cobblemon:dragon_scale"
  
  # Level-up evolution
  python cobblemon_species_editor.py --pokemon eevee --add-evolution charizard --evo-method level_up --evo-level 36
  
  # Change Pikachu's size
  python cobblemon_species_editor.py --pokemon pikachu --base-scale 2.0 --hitbox "2,2"
  
  # Change type
  python cobblemon_species_editor.py --pokemon bulbasaur --primary-type fire --secondary-type water
  
  # Multiple changes at once
  python cobblemon_species_editor.py --pokemon magikarp --primary-type dragon --base-scale 3.0 --can-fly --add-evolution gyarados --evo-level 20
        """
    )
    
    # Target Pokémon (required)
    parser.add_argument('--pokemon', type=str, required=True, help='Target Pokémon to modify')
    
    # Move modifications
    parser.add_argument('--add-moves', type=str, help='Comma-separated moves (WARNING: replaces ALL moves!)')
    
    # Evolution
    parser.add_argument('--add-evolution', type=str, help='Add evolution to this Pokémon')
    parser.add_argument('--evo-method', type=str, choices=['level_up', 'item_interact', 'trade'], 
                        default='level_up', help='Evolution method (default: level_up)')
    parser.add_argument('--evo-level', type=int, default=36, help='Evolution level (for level_up, default: 36)')
    parser.add_argument('--evo-item', type=str, help='Required item (for item_interact or trade with item)')
    
    # Type changes
    parser.add_argument('--primary-type', type=str, help='Change primary type')
    parser.add_argument('--secondary-type', type=str, help='Change secondary type')
    
    # Abilities
    parser.add_argument('--abilities', type=str, help='Set abilities (e.g., "blaze,h:solar_power")')
    
    # Model/hitbox
    parser.add_argument('--base-scale', type=float, help='Model scale multiplier')
    parser.add_argument('--hitbox', type=str, help='Hitbox size (format: "width,height")')
    
    # Drops
    parser.add_argument('--drops', type=str, help='Item drops (format: "item:percentage,item:percentage")')
    
    # Behavior
    parser.add_argument('--can-fly', action='store_true', help='Enable flight')
    parser.add_argument('--can-swim', action='store_true', help='Enable swimming')
    parser.add_argument('--breathe-underwater', action='store_true', help='Can breathe underwater (use with --can-swim)')
    
    # Advanced
    parser.add_argument('--namespace', type=str, default='custom', help='Custom namespace (default: custom)')
    parser.add_argument('--pack-path', type=str, help='Path to pack directory')
    
    args = parser.parse_args()
    
    # Build config
    config = {
        'pokemon': args.pokemon,
        'add_moves': args.add_moves,
        'add_evolution': args.add_evolution,
        'evo_method': args.evo_method,
        'evo_level': args.evo_level,
        'evo_item': args.evo_item,
        'primary_type': args.primary_type,
        'secondary_type': args.secondary_type,
        'abilities': args.abilities,
        'base_scale': args.base_scale,
        'hitbox': args.hitbox,
        'drops': args.drops,
        'can_fly': args.can_fly,
        'can_swim': args.can_swim,
        'breathe_underwater': args.breathe_underwater,
        'namespace': args.namespace,
    }
    
    # Create editor
    editor = CobblemonSpeciesEditor(pack_path=args.pack_path)
    
    # Create the species addition
    editor.create_species_addition(config)


if __name__ == "__main__":
    main()
