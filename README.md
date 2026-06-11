# Cobblemon Pack Error Checker

Validates a Cobblemon custom Pokémon pack (separate resource + behavior packs for Minecraft 1.21.1) and finds the errors that cause practice-dummy models, invisible textures, broken evolutions, and silent spawn failures — before you waste time debugging them in-game.

**Current version: 2.4** — verify your copy with:
```bash
python pack_checker.py --version
```
If this errors or shows an older number, your download is truncated or stale.

## Usage

```bash
# Default pack location (Downloads/Mod-ResourceAndBehavior-Packs)
python pack_checker.py

# Explicit path
python pack_checker.py --pack-path "C:\path\to\Mod-ResourceAndBehavior-Packs"
```

Run it after every generate, edit, rename, or file swap. It's the safety net.

## Reading the Output

Issues are grouped: each problem is one bullet, with its details indented underneath. The counts in the summary count *problems*, not lines.

```
ERRORS (2):
   • molecul: ERROR: Head bone 'skull' doesn't exist in model!
        `- Model bones are: body, tail, leftarm
   • molecul: ERROR: Resolver variation #1 points at missing texture!
        `- 'cobblemon:textures/pokemon/molecul/TYPO.png' → <full path shown>
        `- This causes invisible/missing textures in-game (check spelling & case)

WARNINGS (1):
   • molecul: Missing recommended animation 'battle_idle'
        `- Cobblemon will fall back to ground_idle, but battles look better with it

======================================================================
Summary: 2 errors, 1 warnings
======================================================================
```

- **Errors** = will break in-game (won't load, won't render, won't fire).
- **Warnings** = suspicious or suboptimal, but the pack works.
- Spawn entries are numbered **1-based** — the same indices the generator's `--removespawn` uses.

## What It Checks

### Per-Pokémon file checks
- **Species** (`species/custom/*.json`): valid JSON, name matches filename and is lowercase, dex number present and unique across the pack, stat sanity (per-stat bounds and total BST), height/weight bounds, valid egg groups, `experienceGroup` against the valid set, `maleRatio` in range, evolution structure (`result`/`variant` present, `level_up` evolutions actually have a level requirement, `item_interact` has a `requiredContext`)
- **Model** (`models/<name>/<name>.geo.json`): valid JSON, geometry identifier matches `geometry.<name>`, bones present, `texture_width`/`texture_height` declared
- **Animations**: keys follow `animation.<name>.<anim>`, required animations present (`ground_idle`, `ground_walk` — errors), recommended ones flagged (`battle_idle` — warning, Cobblemon falls back gracefully), every animated bone exists in the model
- **Poser**: valid JSON, the `head: null` practice-dummy bug, head bone exists in the model, `look` animation without a head bone, every `bedrock(name, anim)` reference points at the right Pokémon and an animation that actually exists
- **Resolver**: species/model/poser references correct, poser reference resolves to a real file, **every variation's texture path resolves to a real file** (base and shiny)
- **Textures**: PNG magic-byte validation (base and shiny), suspicious file sizes, and **actual dimensions vs the model's declared UV size** (proportional scaling passes; aspect-ratio mismatches that garble in-game are errors)
- **Spawn file**: valid JSON, `pokemon` field matches the filename (copy-paste catcher), bucket validity, zero/negative weight (never spawns), level range sanity
- **Filenames**: underscore-vs-dot traps (`name_geo.json` vs `name.geo.json`), case sensitivity

### Pack-level cross-checks
- **Evolution targets**: every evolution `result` (in species files *and* species_additions) must exist in the pack, or you're warned to verify it's vanilla — otherwise the evolution silently never fires
- **Lang completeness**: `en_us.json` exists, has each Pokémon's `.name` key, and contains every Pokédex key the species file declares
- **species_additions**: valid JSON, `target` present and namespaced, evolution structure, and a warning that `moves` REPLACES the target's entire move list
- **Orphan detection**: posers, resolvers, model/animation/texture folders, and spawn files whose Pokémon has no species file (leftovers from renames/deletions)
- **pack.mcmeta**: exists in both packs, valid JSON, correct `pack_format` (34 resource / 48 data for 1.21.1)

## Typical Workflow

```bash
python pack-generator.py --name Newmon --number 1300 --abilities "static" --moves "1:tackle"
python pack_checker.py          # zero errors expected on a fresh generate
# ... edit, rename, swap files ...
python pack_checker.py          # re-verify after every change
```

A pack straight from the generator (v2.5+) passes with zero errors; the only expected warning is the `battle_idle` recommendation if you didn't make one.

## Notes & Limitations

- Vanilla Pokémon can't be verified locally, so evolution targets and addition targets that aren't in your pack produce a "verify the spelling" warning rather than an error.
- The checker reads `species/custom/` to enumerate Pokémon; species defined elsewhere won't be scanned (their additions still are).
- Output is plain ASCII (plus `é`, `→`, `•`) — safe for Windows terminals.
- The checker never modifies your pack. It only reads.

## Version History

| Version | Highlights |
|---------|-----------|
| 2.4 | `battle_idle` demoted from required (error) to recommended (warning) |
| 2.3 | Grouped results UI (details indent under their issue); counts count issues, not lines |
| 2.2 | Emoji-free console output; `--version` flag |
| 2.1 | Cross-file checks: resolver texture/poser paths, poser→animation refs, texture dims vs UV size, evolution targets, lang completeness, species_additions, orphan files, spawn deep checks, pack.mcmeta |
| 2.0 | Filename validation, bone matching, poser `head: null` detection, case checks, PNG validation |
