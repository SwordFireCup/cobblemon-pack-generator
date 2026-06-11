#!/usr/bin/env python3
"""
Cobblemon Pack Error Checker
Validates all files in your Cobblemon pack for common errors

v2.1 changelog (2026-06-10):
  - FIX: missing comma merged 'splishysplash'/'spore' in COMMON_MOVES
  - NEW: resolver texture/poser paths verified against real files
  - NEW: poser bedrock(name, anim) refs cross-checked (wrong name, missing anim)
  - NEW: texture dimensions vs model UV size (IHDR parse, no PIL needed)
  - NEW: evolution structure + target validation (incl. missing level reqs)
  - NEW: lang file completeness (.name + declared pokedex keys)
  - NEW: species_additions validation (JSON, target, evolutions, moves footgun)
  - NEW: orphan file detection (posers/resolvers/models/anims/textures/spawns)
  - NEW: spawn deep checks (pokemon-matches-filename, bucket, weight, level range)
  - NEW: pack.mcmeta validation (formats 34/48 for 1.21.1)
  - NEW: experienceGroup + maleRatio field validation
  - NEW: --version flag
v2.2 changelog (2026-06-11):
  - CHANGE: emoji-free console output for Windows terminal compatibility
v2.3 changelog (2026-06-11):
  - CHANGE: results UI groups detail lines as indented children of their
            parent issue; error/warning counts now count issues, not lines
v2.4 changelog (2026-06-11):
  - CHANGE: battle_idle demoted from required (error) to recommended (warning)
            — Cobblemon falls back to ground_idle, and the generator doesn't
            create it, so packs straight from the generator now pass clean
"""

CHECKER_VERSION = "2.4"

import json
import os
from pathlib import Path
from typing import Dict, List, Tuple


class CobblemonPackChecker:
    """Checks Cobblemon packs for errors"""

    VALID_TYPES = [
        "normal", "fire", "water", "electric", "grass", "ice", "fighting",
        "poison", "ground", "flying", "psychic", "bug", "rock", "ghost",
        "dragon", "dark", "steel", "fairy"
    ]

    REQUIRED_ANIMATIONS = [
        "ground_idle", "ground_walk"
    ]

    # Cobblemon falls back gracefully if these are missing, so they're warnings
    RECOMMENDED_ANIMATIONS = [
        "battle_idle"
    ]

    OPTIONAL_ANIMATIONS = [
        "sleep", "faint", "cry", "air_idle", "air_fly", "water_idle", "water_swim"
    ]

    # Common Cobblemon moves (not exhaustive, but catches most typos)
    COMMON_MOVES = {
            # A
    "10000000voltthunderbolt", "absorb", "accelerock", "acid", "acidarmor", "aciddownpour", "acidspray",
    "acrobatics", "acupressure", "aerialace", "aeroblast", "afteryou",
    "agility", "airslash", "aircutter", "alloutpummeling",
    "allyswitch", "amnesia", "anchorshot", "ancientpower",
    "appleacid", "aquacutter", "aquajet", "aquaring", "aquastep", "aquatail",
    "armorcannon", "armthrust", "aromatherapy", "aromaticmist",
    "assist", "assurance", "astonish", "astralbarrage",
    "attackorder", "attract", "aurasphere", "aurorabeam", "auroraveil",
    "autotomize", "avalanche", "axekick",

    # B
    "babydolleyes", "baddybad", "banefulbunker", "barbbarrage",
    "barrage", "barrier", "batonpass", "beakblast", "beatup",
    "belch", "bellydrum", "bestow", "bide", "bind", "bite",
    "bitterblade", "bittermalice", "blackholeeclipse",
    "blastburn", "blazekick", "bleakwindstorm", "blizzard",
    "block", "bloomdoom", "blueflare", "bodypress", "bodyslam",
    "boltbeak", "boltstrike", "boneclub", "bonemerang", "bonerush",
    "boomburst", "bounce", "bouncybubble", "branchpoke",
    "bravebird", "breakingswipe", "breakneckblitz", "brickbreak",
    "brine", "brutalswing", "bubble", "bubblebeam",
    "bugbite", "bugbuzz", "bulkup", "bulldoze",
    "bulletpunch", "bulletseed", "burningjealousy", "burnup",
    "buzzybuzz",

    # C
    "calmmind", "camouflage", "captivate", "catastropika",
    "ceaselessedge", "celebrate", "charge", "chargebeam",
    "charm", "chatter", "chillingwater", "chillyreception",
    "chipaway", "chloroblast", "circlethrow", "clamp",
    "clangoroussoul", "clangoroussoulblaze", "clearsmog",
    "closecombat", "coaching", "coil", "collisioncourse",
    "cometpunch", "comeuppance", "confide", "confuseray",
    "confusion", "constrict", "continentalcrush", "conversion",
    "conversion2", "copycat", "coreenforcer", "corkscrewcrash",
    "corrosivegas", "cosmicpower", "cottonguard", "cottonspore",
    "counter", "courtchange", "covet", "crabhammer",
    "craftyshield", "crosschop", "crosspoison", "crunch",
    "crushclaw", "crushgrip", "curse", "cut",

    # D
    "darkestlariat", "darkpulse", "darkvoid", "dazzlinggleam",
    "decorate", "defendorder", "defensecurl", "defog",
    "destinybond", "detect", "devastatingdrake", "diamondstorm",
    "dig", "disable", "disarmingvoice", "discharge",
    "dive", "dizzypunch", "doodle", "doomdesire",
    "doubleedge", "doubleironbash", "doublekick", "doubleshock",
    "doubleslap", "doubleteam", "dracometeor", "dragonascent",
    "dragonbreath", "dragonclaw", "dragondance", "dragondarts",
    "dragonenergy", "dragonhammer", "dragonpulse", "dragonrage",
    "dragonrush", "dragontail", "drainingkiss", "drainpunch",
    "dreameater", "drillpeck", "drillrun", "drumbeating",
    "dualchop", "dualwingbeat", "dynamaxcannon",

    # E
    "earthpower", "earthquake", "echoedvoice", "eerieimpulse",
    "eeriespell", "eggbomb", "electricterrain", "electrify",
    "electroball", "electrodrift", "electroweb", "embargo",
    "ember", "encore", "endeavor", "endure",
    "energyball", "entrainment", "eruption", "esperwing",
    "eternabeam", "expandingforce", "explosion", "extrasensory",
    "extremeevoboost", "extremespeed",

    # F
    "facade", "faintattack", "fairylock", "fairywind",
    "fakeout", "faketears", "falsesurrender", "falseswipe",
    "featherdance", "feint", "feintattack", "fellstinger",
    "fierydance", "fierywrath", "filletaway", "finalgambit",
    "fireblast", "firefang", "firelash", "firepledge",
    "firepunch", "firespin", "firstimpression", "fishiousrend",
    "fissure", "flail", "flameburst", "flamecharge",
    "flamewheel", "flamethrower", "flareblitz", "flash",
    "flashcannon", "flatter", "fleurcannon", "fling",
    "flipturn", "floatyfall", "floralhealing", "flowershield",
    "flowertrick", "fly", "flyingpress", "focusblast",
    "focusenergy", "focuspunch", "followme", "forcepalm",
    "foresight", "forestscurse", "foulplay", "freezedry",
    "freezeshock", "freezingglare", "freezyfrost", "frenzyplant",
    "frostbreath", "frustration", "furyattack", "furycutter",
    "furyswipes", "fusionbolt", "fusionflare", "futuresight",

    # G
    "gastroacid", "geargrind", "gearup", "genesissupernova",
    "geomancy", "gigadrain", "gigaimpact", "gigatonhammer",
    "gigavolthavoc", "glaciallance", "glaciate", "glaiverush",
    "glare", "glitzyglow", "gmaxbefuddle", "gmaxcannonade",
    "gmaxcentiferno", "gmaxchistrike", "gmaxcuddle",
    "gmaxdepletion", "gmaxdrumsolo", "gmaxfinale", "gmaxfireball",
    "gmaxfoamburst", "gmaxgoldrush", "gmaxgravitas",
    "gmaxhydrosnipe", "gmaxmalodor", "gmaxmeltdown",
    "gmaxoneblow", "gmaxrapidflow", "gmaxreplenish",
    "gmaxresonance", "gmaxsandblast", "gmaxsmite", "gmaxsnooze",
    "gmaxsteelsurge", "gmaxstonesurge", "gmaxstunshock",
    "gmaxsweetness", "gmaxtartness", "gmaxterror", "gmaxvinelash",
    "gmaxvolcalith", "gmaxvoltcrash", "gmaxwildfire", "gmaxwindrage",
    "grassknot", "grasspledge", "grasswhistle", "grassyglide",
    "grassyterrain", "gravapple", "gravity", "growl",
    "growth", "grudge", "guardianofalola", "guardsplit",
    "guardswap", "guillotine", "gunkshot", "gust",

    # H
    "hail", "hammerarm", "happyhour", "harden",
    "haze", "headbutt", "headcharge", "headlongrush",
    "headsmash", "healbell", "healblock", "healingwish",
    "healorder", "healpulse", "heartstamp",
    "heartswap", "heatcrash", "heatwave", "heavyslam",
    "helpinghand", "hex", "hiddenpower", "hiddenpowerbug",
    "hiddenpowerdark", "hiddenpowerdragon", "hiddenpowerelectric",
    "hiddenpowerfighting", "hiddenpowerfire", "hiddenpowerflying",
    "hiddenpowerghost", "hiddenpowergrass", "hiddenpowerground",
    "hiddenpowerice", "hiddenpowerpoison", "hiddenpowerpsychic",
    "hiddenpowerrock", "hiddenpowersteel", "hiddenpowerwater",
    "highhorsepower", "highjumpkick", "holdback", "holdhands",
    "honeclaws", "hornattack", "horndrill", "hornleech",
    "howl", "hurricane", "hydrocannon", "hydropump",
    "hydrosteam", "hydrovortex", "hyperbeam", "hyperdrill",
    "hyperfang", "hyperspacefury", "hyperspacehole", "hypervoice",
    "hypnosis",

    # I
    "iceball", "icebeam", "iceburn", "icefang",
    "icehammer", "icepunch", "iceshard", "icespinner",
    "iciclecrash", "iciclespear", "icywind",
    "imprison", "incinerate", "infernalparade", "inferno",
    "infernooverdrive", "infestation", "ingrain", "instruct",
    "iondeluge", "irondefense", "ironhead", "irontail",

    # J
    "jawlock", "jetpunch", "judgment", "jumpkick",
    "junglehealing",

    # K
    "karatechop", "kinesis", "kingsshield", "knockoff",
    "kowtowcleave",

    # L
    "landswrath", "laserfocus", "lashout", "lastresort",
    "lastrespects", "lavaplume", "leafage", "leafblade",
    "leafstorm", "leaftornado", "leechlife", "leechseed",
    "leer", "letssnuggleforever", "lick", "lifedew",
    "lightscreen", "lightthatburnsthesky", "liquidation",
    "lockon", "lovelykiss", "lowkick", "lowsweep",
    "luckychant", "luminacrash", "lunarblessing", "lunardance",
    "lunge", "lusterpurge",

    # M
    "machpunch", "magiccoat", "magicpowder", "magicroom",
    "magicalleaf", "magmastorm", "magnetbomb", "magneticflux",
    "magnetrise", "magnitude", "makeitrain", "maliciousmoonsault",
    "malignantchain", "matblock", "maxdarkness", "maxflare",
    "maxflutterby", "maxgeyser", "maxguard", "maxhailstorm",
    "maxknuckle", "maxlightning", "maxmindstorm", "maxooze",
    "maxovergrowth", "maxphantasm", "maxquake", "maxrockfall",
    "maxstarfall", "maxsteelspike", "maxstrike", "maxwyrmwind",
    "meanlook", "meditate", "mefirst", "megadrain",
    "megahorn", "megakick", "megapunch", "memento",
    "menacingmoonrazemaelstrom", "metalburst", "metalclaw",
    "metalsound", "meteorassault", "meteorbeam", "meteormash",
    "metronome", "milkdrink", "mimic", "mindblown",
    "mindreader", "minimize", "miracleeye", "mirrorcoat",
    "mirrormove", "mirrorshot", "mist", "mistball",
    "mistyexplosion", "mistyterrain", "moonblast", "moongeistbeam",
    "moonlight", "morningsun", "mortalspin", "mountaingale",
    "mudbomb", "mudshot", "mudslap", "mudsport",
    "muddywater", "multiattack", "mysticalfire", "mysticalpower",

    # N
    "nastyplot", "naturalgift", "naturepower", "naturesmadness",
    "needlearm", "neverendingnightmare", "nightdaze", "nightmare",
    "nightshade", "nightslash", "nobleroar", "noretreat",
    "noxioustorque", "nuzzle",

    # O
    "oblivionwing", "obstruct", "oceanicoperetta", "octazooka",
    "octolock", "odorsleuth", "ominouswind", "orderup",
    "originpulse", "outrage", "overdrive", "overheat",

    # P
    "painsplit", "paleowave", "paraboliccharge", "partingshot",
    "payback", "payday", "peck", "perishsong",
    "petaldance", "petalblizzard", "phantomforce", "photongeyser",
    "pikapapow", "pinmissile", "plasmafists", "playnice",
    "playrough", "pluck", "poisonfang", "poisongas",
    "poisonjab", "poisonpowder", "poisontail", "pollenpuff",
    "poltergeist", "populationbomb", "pounce", "pound",
    "powder", "powdersnow", "powershift", "powersplit",
    "powerswap", "powertrick", "poweruppunch", "powerwhip",
    "precipiceblades", "present", "prismaticlaser", "protect",
    "psybeam", "psyblade", "psychic", "psychicfangs",
    "psychicterrain", "psychoboost", "psychocut", "psychoshift",
    "psychup", "psyshieldbash", "psystrike", "psywave",
    "pulverizingpancake", "punishment", "purify", "pursuit",
    "pyroball",

    # Q
    "quash", "quickattack", "quickguard", "quiverdance",

    # R
    "rage", "ragefist", "ragepowder", "ragingbull",
    "ragingfury", "raindance", "rapidspin",
    "razorleaf", "razorshell", "razorwind", "recover",
    "recycle", "reflect", "reflecttype", "refresh",
    "relicsong", "rest", "retaliate", "return",
    "revenge", "reversal", "revivalblessing", "risingvoltage",
    "roar", "roaroftime", "rockblast", "rockclimb",
    "rockpolish", "rockslide", "rocksmash", "rockthrow",
    "rocktomb", "rockwrecker", "roleplay", "rollingkick",
    "rollout", "roost", "rototiller", "round",
    "ruination",

    # S
    "sacredfire", "sacredsword", "safeguard", "saltcure",
    "sandattack", "sandsearstorm", "sandstorm", "sandtomb",
    "sappyseed", "savagespinout", "scald", "scaleshot",
    "scaryface", "scorchingsands", "scratch", "screech",
    "searingshot", "searingsunrazesmash", "secretpower",
    "secretsword", "seedbomb", "seedflare", "seismictoss",
    "selfdestruct", "shadowball", "shadowbone", "shadowclaw",
    "shadowforce", "shadowpunch", "shadowsneak", "shadowstrike",
    "sharpen", "shatteredpsyche", "shedtail", "sheercold",
    "shellsidearm", "shellsmash", "shelltrap", "shelter",
    "shiftgear", "shockwave", "shoreup", "signalbeam",
    "silktrap", "silverwind", "simplebeam", "sing",
    "sinisterarrowraid", "sizzlyslide", "sketch", "skillswap",
    "skittersmack", "skullbash", "skyattack", "skydrop",
    "skyuppercut", "slackoff", "slam", "slash",
    "sleeppowder", "sleeptalk", "sludge", "sludgebomb",
    "sludgewave", "smackdown", "smartstrike", "smellingsalts",
    "smog", "smokescreen", "snaptrap", "snarl",
    "snatch", "snipeshot", "snore", "snowscape",
    "soak", "softboiled", "solarbeam", "solarblade",
    "sonicboom", "soulstealing7starstrike", "spacialrend",
    "spark", "sparklingaria", "sparklyswirl", "spectralthief",
    "speedswap", "spicyextract", "spiderweb", "spikecannon",
    "spikes", "spikyshield", "spinout", "spiritbreak",
    "spiritshackle", "spite", "spitup", "splash",
    "splinteredstormshards", "splishysplash", "spore",
    "spotlight", "springtidestorm", "stealthrock",
    "steamroller", "steameruption", "steelbeam", "steelroller",
    "steelwing", "stickyweb", "stockpile", "stokedsparksurfer",
    "stomp", "stompingtantrum", "stoneaxe", "stoneedge",
    "storedpower", "stormthrow", "strangesteam", "strength",
    "strengthsap", "stringshot", "struggle", "strugglebug",
    "stuffcheeks", "stunspore", "submission", "substitute",
    "subzeroslammer", "suckerpunch", "sunnyday", "sunsteelstrike",
    "superfang", "superpower", "supersonic", "supersonicskystrike",
    "surf", "surgingstrikes", "swagger", "swallow",
    "sweetkiss", "sweetscent", "swift", "switcheroo",
    "swordsdance", "synchronoise", "synthesis",

    # T
    "tackle", "tailglow", "tailslap", "tailwhip",
    "tailwind", "takedown", "tarshot", "taunt",
    "tearfullook", "teatime", "technoblast", "tectonierage",
    "teeterdance", "telekinesis", "teleport", "terablast",
    "terrainpulse", "thief", "thousandarrows", "thousandwaves",
    "thrash", "throatchop", "thunder", "thunderbolt",
    "thundercage", "thunderfang", "thunderpunch", "thundershock",
    "thunderwave", "thunderouskick", "tickle", "topsyturvy",
    "torment", "toxic", "toxicspikes", "toxicthread",
    "trailblaze", "transform", "triattack", "trick",
    "trickroom", "tripleaxel", "triplearrows", "tripledive",
    "tropkick", "trumpcard", "twinbeam", "twinneedle",
    "twister",

    # U
    "uproar", "uturn",

    # V
    "vacuumwave", "vcreate", "venomdrench", "venoshock",
    "victorydance", "vinewhip", "vitalthrow", "volttackle",
    "voltswitch",

    # W
    "wakeupslap", "waterfall", "watergun", "waterpledge",
    "waterpulse", "watershuriken", "watersport", "waterspout",
    "wavecrash", "weatherball", "whirlpool", "whirlwind",
    "wickedblow", "wickedtorque", "wideguard", "wildcharge",
    "willowisp", "wingattack", "wish", "withdraw",
    "wonderroom", "woodhammer", "workup", "worryseed",
    "wrap", "wringout",

    # X
    "xscissor",

    # Y
    "yawn",

    # Z
    "zapcannon", "zenheadbutt", "zingzap", "zippyzap",
    }

    # Common Cobblemon abilities (complete list - 310 abilities)
    COMMON_ABILITIES = {
        "adaptability", "aerilate", "aftermath", "airlock", "analytic",
        "angerpoint", "angershell", "anticipation", "arenatrap", "armortail",
        "aromaveil", "asoneglastrier", "asonespectrier", "aurabreak",
        "baddreams", "ballfetch", "battery", "battlearmor", "battlebond",
        "beadsofruin", "beastboost", "berserk", "bigpecks", "blaze",
        "bulletproof", "cheekpouch", "chillingneigh", "chlorophyll", "clearbody",
        "cloudnine", "colorchange", "comatose", "commander", "competitive",
        "compoundeyes", "contrary", "corrosion", "costar", "cottondown",
        "cudchew", "curiousmedicine", "cursedbody", "cutecharm", "damp",
        "dancer", "darkaura", "dauntlessshield", "dazzling", "defeatist",
        "defiant", "deltastream", "desolateland", "disguise", "download",
        "dragonsmaw", "drizzle", "drought", "dryskin", "earlybird",
        "eartheater", "effectspore", "electricsurge", "electromorphosis",
        "embodyaspectteal", "embodyaspecthearthflame", "embodyaspectwellspring",
        "embodyaspectcornerstone", "emergencyexit", "fairyaura", "filter",
        "flamebody", "flareboost", "flashfire", "flowergift", "flowerveil",
        "fluffy", "forecast", "forewarn", "friendguard", "frisk",
        "fullmetalbody", "furcoat", "galewings", "galvanize", "gluttony",
        "goodasgold", "gooey", "gorillatactics", "grasspelt", "grassysurge",
        "grimneigh", "guarddog", "gulpmissile", "guts", "hadronengine",
        "harvest", "healer", "heatproof", "heavymetal", "honeygather",
        "hospitality", "hugepower", "hungerswitch", "hustle", "hydration",
        "hypercutter", "icebody", "iceface", "icescales", "illuminate",
        "illusion", "immunity", "imposter", "infiltrator", "innardsout",
        "innerfocus", "insomnia", "intimidate", "intrepidsword", "ironbarbs",
        "ironfist", "justified", "keeneye", "klutz", "leafguard",
        "levitate", "libero", "lightmetal", "lightningrod", "limber",
        "lingeringaroma", "liquidooze", "liquidvoice", "longreach",
        "magicbounce", "magicguard", "magician", "magmaarmor", "magnetpull",
        "marvelscale", "megalauncher", "merciless", "mimicry", "mindseye",
        "minus", "mirrorarmor", "mistysurge", "moldbreaker", "moody",
        "motordrive", "moxie", "multiscale", "multitype", "mummy",
        "myceliummight", "naturalcure", "neuroforce", "neutralizinggas",
        "noguard", "normalize", "oblivious", "opportunist", "orichalcumpulse",
        "overcoat", "overgrow", "owntempo", "parentalbond", "pastelveil",
        "perishbody", "pickpocket", "pickup", "pixilate", "plus",
        "poisonheal", "poisonpoint", "poisonpuppeteer", "poisontouch",
        "powerconstruct", "powerofalchemy", "powerspot", "prankster",
        "pressure", "primordialsea", "prismarmor", "propellertail",
        "protean", "protosynthesis", "psychicsurge", "punkrock", "purepower",
        "purifyingsalt", "quarkdrive", "queenlymajesty", "quickdraw",
        "quickfeet", "raindish", "rattled", "receiver", "reckless",
        "refrigerate", "regenerator", "ripen", "rivalry", "rkssystem",
        "rockhead", "rockypayload", "roughskin", "runaway", "sandforce",
        "sandrush", "sandspit", "sandstream", "sandveil", "sapsipper",
        "schooling", "scrappy", "screencleaner", "seedsower", "serenegrace",
        "shadowshield", "shadowtag", "sharpness", "shedskin", "sheerforce",
        "shellarmor", "shielddust", "shieldsdown", "simple", "skilllink",
        "slowstart", "slushrush", "sniper", "snowcloak", "snowwarning",
        "solarpower", "solidrock", "soulheart", "soundproof", "speedboost",
        "stakeout", "stall", "stalwart", "stamina", "stancechange",
        "static", "steadfast", "steamengine", "steelworker", "steelyspirit",
        "stench", "stickyhold", "stormdrain", "strongjaw", "sturdy",
        "suctioncups", "superluck", "supersweetsyrup", "supremeoverlord",
        "surgesurfer", "swarm", "sweetveil", "swiftswim", "swordofruin",
        "symbiosis", "synchronize", "tabletsofruin", "tangledfeet",
        "tanglinghair", "technician", "telepathy", "terashell", "terashift",
        "teraformzero", "teravolt", "thermalexchange", "thickfat",
        "tintedlens", "torrent", "toughclaws", "toxicboost", "toxicchain",
        "toxicdebris", "trace", "transistor", "triage", "truant",
        "turboblaze", "unaware", "unburden", "unnerve", "unseenfist",
        "vesselofruin", "victorystar", "vitalspirit", "voltabsorb",
        "wanderingspirit", "waterabsorb", "waterbubble", "watercompaction",
        "waterveil", "weakarmor", "wellbakedbody", "whitesmoke", "wimpout",
        "windpower", "windrider", "wonderguard", "wonderskin", "zenmode",
        "zerotohero"
    }

    # Valid egg groups
    VALID_EGG_GROUPS = {
        "monster", "water1", "bug", "flying", "field", "fairy", "grass", "humanlike",
        "water3", "mineral", "amorphous", "water2", "ditto", "dragon", "undiscovered"
    }

    # Valid experience groups
    VALID_EXP_GROUPS = {
        "slow", "medium_slow", "medium_fast", "fast", "erratic", "fluctuating"
    }

    # Valid spawn buckets
    VALID_BUCKETS = {"common", "uncommon", "rare", "ultra-rare"}

    def __init__(self, pack_path: str = None):
        if pack_path is None:
            pack_path = str(Path.home() / "Downloads" / "Mod-ResourceAndBehavior-Packs")

        self.pack_path = Path(pack_path)
        self.errors = []
        self.warnings = []
        self.info = []
        self.dex_numbers = {}  # Track dex numbers to find duplicates
        self.model_bones = {}  # Cache model bones for validation
        self.animation_names = {}  # Cache animation names (pokemon -> set of suffixes)
        self.model_texture_size = {}  # Cache declared texture_width/height per pokemon
        self.species_evolutions = {}  # Cache evolutions per pokemon (for target checks)
        self.species_pokedex_keys = {}  # Cache pokedex lang keys declared per pokemon
        self.all_species = set()  # All custom species names found

    def check_all(self):
        """Run all checks"""
        print(f"\n{'=' * 70}")
        print(f"COBBLEMON PACK ERROR CHECKER v{CHECKER_VERSION}")
        print(f"{'=' * 70}")
        print("Checks include:")
        print("   • Resolver texture/poser path verification")
        print("   • Poser → animation cross-checking")
        print("   • Texture dimensions vs model UV size")
        print("   • Evolution target validation")
        print("   • Lang file completeness (name/desc keys)")
        print("   • species_additions validation")
        print("   • Orphan file detection")
        print("   • Spawn file deep checks + pack.mcmeta validation")
        print(f"{'=' * 70}\n")
        print(f"Checking pack: {self.pack_path}\n")

        # Check pack structure
        self.check_pack_structure()

        # Find all Pokemon
        pokemon_list = self.find_all_pokemon()
        self.all_species = set(pokemon_list)

        if not pokemon_list:
            self.errors.append("No Pokémon found in pack!")
            self.print_results()
            return

        print(f"Found {len(pokemon_list)} Pokémon to check...\n")

        # Check each Pokemon
        for pokemon_name in pokemon_list:
            self.check_pokemon(pokemon_name)

        # Pack-level cross-checks (need all species data collected first)
        print("Running pack-level cross-checks...")
        self.check_evolution_targets()
        self.check_lang_file(pokemon_list)
        self.check_species_additions()
        self.check_orphan_files()
        print()

        # Print results
        self.print_results()

    def check_pack_structure(self):
        """Check basic pack structure"""
        print("Checking pack structure...")

        # Check resource pack
        resource_pack = self.pack_path / "resource_pack"
        if not resource_pack.exists():
            self.errors.append("Missing resource_pack folder!")
        else:
            self.info.append("[OK] resource_pack folder exists")
            self._check_mcmeta(resource_pack / "pack.mcmeta", "resource_pack", expected_format=34)

        # Check behavior pack
        behavior_pack = self.pack_path / "behavior_pack"
        if not behavior_pack.exists():
            self.errors.append("Missing behavior_pack folder!")
        else:
            self.info.append("[OK] behavior_pack folder exists")
            self._check_mcmeta(behavior_pack / "pack.mcmeta", "behavior_pack", expected_format=48)

        print()

    def _check_mcmeta(self, mcmeta_file: Path, pack_label: str, expected_format: int):
        """Validate a pack.mcmeta file exists and has the right pack_format for 1.21.1"""
        if not mcmeta_file.exists():
            self.errors.append(f"{pack_label}: Missing pack.mcmeta! Pack won't load without it.")
            return
        try:
            with open(mcmeta_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            pack = data.get("pack")
            if not isinstance(pack, dict):
                self.errors.append(f"{pack_label}: pack.mcmeta missing 'pack' object")
                return
            fmt = pack.get("pack_format")
            if fmt is None:
                self.errors.append(f"{pack_label}: pack.mcmeta missing 'pack_format'")
            elif fmt != expected_format:
                self.warnings.append(
                    f"{pack_label}: pack_format is {fmt}, expected {expected_format} for Minecraft 1.21.1")
            else:
                self.info.append(f"[OK] {pack_label}/pack.mcmeta valid (format {fmt})")
            if "description" not in pack:
                self.warnings.append(f"{pack_label}: pack.mcmeta has no 'description'")
        except json.JSONDecodeError as e:
            self.errors.append(f"{pack_label}: Invalid JSON in pack.mcmeta: {e}")
        except Exception as e:
            self.warnings.append(f"{pack_label}: Could not read pack.mcmeta: {e}")

    def find_all_pokemon(self) -> List[str]:
        """Find all Pokemon in the pack"""
        pokemon = set()

        # Check species files
        species_dir = self.pack_path / "behavior_pack" / "data" / "cobblemon" / "species" / "custom"
        if species_dir.exists():
            for file in species_dir.glob("*.json"):
                pokemon.add(file.stem)

        return sorted(list(pokemon))

    def check_pokemon(self, pokemon_name: str):
        """Check all files for a specific Pokemon"""
        print(f"Checking {pokemon_name.upper()}...")

        errors_found = False

        # CRITICAL: Check for case sensitivity issues
        if pokemon_name != pokemon_name.lower():
            self.errors.append(f"{pokemon_name}: CRITICAL! Pokemon name has uppercase letters")
            self.errors.append(f"  All Pokemon names must be lowercase: '{pokemon_name.lower()}'")
            errors_found = True

        # CRITICAL: Check for special characters
        import re
        if not re.match(r'^[a-z0-9_]+$', pokemon_name):
            self.errors.append(f"{pokemon_name}: CRITICAL! Pokemon name contains invalid characters")
            self.errors.append(f"  Only lowercase letters, numbers, and underscores allowed")
            errors_found = True

        # Check species file
        if not self.check_species_file(pokemon_name):
            errors_found = True

        # Check model file
        if not self.check_model_file(pokemon_name):
            errors_found = True

        # Check animation file
        if not self.check_animation_file(pokemon_name):
            errors_found = True

        # Check texture files
        if not self.check_texture_files(pokemon_name):
            errors_found = True

        # Check poser file
        if not self.check_poser_file(pokemon_name):
            errors_found = True

        # Check resolver file
        if not self.check_resolver_file(pokemon_name):
            errors_found = True

        # Check spawn file
        if not self.check_spawn_file(pokemon_name):
            errors_found = True

        if not errors_found:
            print(f"   [OK] All checks passed!\n")
        else:
            print(f"   WARNING: Issues found (see below)\n")

    def check_species_file(self, pokemon_name: str) -> bool:
        """Check species JSON file"""
        species_file = self.pack_path / "behavior_pack" / "data" / "cobblemon" / "species" / "custom" / f"{pokemon_name}.json"

        if not species_file.exists():
            self.errors.append(f"{pokemon_name}: Missing species file: {species_file}")
            return False

        try:
            with open(species_file, 'r') as f:
                data = json.load(f)

            # Check required fields
            required_fields = ["name", "nationalPokedexNumber", "primaryType", "baseStats"]
            for field in required_fields:
                if field not in data:
                    self.errors.append(f"{pokemon_name}: Missing required field '{field}' in species file")

            # Check for duplicate dex numbers
            if "nationalPokedexNumber" in data:
                dex_num = data["nationalPokedexNumber"]
                if dex_num in self.dex_numbers:
                    self.errors.append(f"{pokemon_name}: ERROR: DUPLICATE DEX NUMBER #{dex_num}!")
                    self.errors.append(f"  Already used by: {self.dex_numbers[dex_num]}")
                else:
                    self.dex_numbers[dex_num] = pokemon_name

            # Check types
            if "primaryType" in data:
                ptype = data["primaryType"]
                if ptype is None:
                    self.errors.append(f"{pokemon_name}: primaryType is null!")
                else:
                    ptype = ptype.lower()
                    if ptype not in self.VALID_TYPES:
                        self.warnings.append(f"{pokemon_name}: Invalid primary type '{ptype}'")

            if "secondaryType" in data:
                stype = data["secondaryType"]
                if stype is None:
                    # Secondary type can be null (single-type Pokemon)
                    pass
                else:
                    stype = stype.lower()
                    if stype not in self.VALID_TYPES:
                        self.warnings.append(f"{pokemon_name}: Invalid secondary type '{stype}'")

            # Check base stats
            if "baseStats" in data:
                stats = data["baseStats"]
                required_stats = ["hp", "attack", "defence", "special_attack", "special_defence", "speed"]
                for stat in required_stats:
                    if stat not in stats:
                        self.errors.append(f"{pokemon_name}: Missing base stat '{stat}'")
                    else:
                        stat_value = stats[stat]
                        if not isinstance(stat_value, (int, float)):
                            self.errors.append(
                                f"{pokemon_name}: Stat '{stat}' must be a number, got: {type(stat_value).__name__}")
                        elif stat_value < 1:
                            self.errors.append(f"{pokemon_name}: Stat '{stat}' is {stat_value} (must be at least 1)")
                        elif stat_value > 255:
                            self.warnings.append(f"{pokemon_name}: Stat '{stat}' is {stat_value} (over 255 is unusual)")

                # Calculate and warn about BST
                if all(stat in stats for stat in required_stats):
                    bst = sum(stats[stat] for stat in required_stats)
                    if bst < 180:
                        self.warnings.append(f"{pokemon_name}: Very low BST ({bst}) - weaker than Magikarp!")
                    elif bst > 720:
                        self.warnings.append(f"{pokemon_name}: Very high BST ({bst}) - stronger than Arceus!")

            # Check abilities
            if "abilities" in data:
                if not isinstance(data["abilities"], list):
                    self.errors.append(f"{pokemon_name}: abilities must be an array")
                elif len(data["abilities"]) == 0:
                    self.warnings.append(f"{pokemon_name}: Empty abilities array (will cause spawn issues)")
                else:
                    # Validate ability names (strip underscores for comparison)
                    for ability in data["abilities"]:
                        ability_clean = ability.replace("h:", "").strip().lower().replace("_", "")
                        if ability_clean not in self.COMMON_ABILITIES:
                            self.warnings.append(f"{pokemon_name}: Unknown ability '{ability}' (might be a typo)")

            # Check moves list
            if "moves" in data:
                if not isinstance(data["moves"], list):
                    self.errors.append(f"{pokemon_name}: 'moves' must be an array, got {type(data['moves']).__name__}")
                else:
                    move_count = len(data["moves"])
                    if move_count == 0:
                        self.warnings.append(f"{pokemon_name}: No moves defined (Pokemon won't know any moves!)")
                    elif move_count == 1 and data["moves"][0] in ("0:tackle", "1:tackle"):
                        self.warnings.append(f"{pokemon_name}: Only has 'tackle' - this is likely a placeholder!")

                    # Check move format and names
                    for move in data["moves"]:
                        if isinstance(move, str):
                            if ":" not in move:
                                self.errors.append(
                                    f"{pokemon_name}: Invalid move format '{move}' - must be 'level:movename'")
                            else:
                                level, move_name = move.split(":", 1)

                                # Handle special prefixes (tm, egg, tutor)
                                if level.lower() in ["tm", "egg", "tutor"]:
                                    # These are valid non-numeric levels
                                    pass
                                else:
                                    # Validate level number
                                    try:
                                        level_num = int(level)
                                        if level_num < 0:
                                            self.warnings.append(
                                                f"{pokemon_name}: Move level {level_num} is negative")
                                        elif level_num > 100:
                                            self.warnings.append(f"{pokemon_name}: Move level {level_num} is over 100")
                                    except ValueError:
                                        self.errors.append(
                                            f"{pokemon_name}: Move level '{level}' is not a valid number or prefix (use 'tm', 'egg', 'tutor', or a number)")

                                # Validate move name (disabled by default - too many moves to track)
                                # Uncomment to enable move name validation:
                                # move_name_clean = move_name.lower().strip().replace("_", "")
                                # if move_name_clean not in self.COMMON_MOVES:
                                #     self.warnings.append(f"{pokemon_name}: Unknown move '{move_name}' (might be a typo or modded move)")

            # Check catch rate
            if "catchRate" in data:
                catch_rate = data["catchRate"]
                if not isinstance(catch_rate, (int, float)):
                    self.errors.append(f"{pokemon_name}: catchRate must be a number")
                elif catch_rate < 3:
                    self.warnings.append(
                        f"{pokemon_name}: catchRate {catch_rate} is very low (harder than legendaries!)")
                elif catch_rate > 255:
                    self.errors.append(f"{pokemon_name}: catchRate {catch_rate} exceeds maximum (255)")

            # Check height and weight
            if "height" in data:
                height = data["height"]
                if height <= 0:
                    self.warnings.append(f"{pokemon_name}: height {height} is zero or negative!")
                elif height < 1:
                    self.warnings.append(f"{pokemon_name}: height {height} is very small (under 0.1m)")
                elif height > 200:
                    self.warnings.append(f"{pokemon_name}: height {height} is enormous (over 20m!)")

            if "weight" in data:
                weight = data["weight"]
                if weight <= 0:
                    self.warnings.append(f"{pokemon_name}: weight {weight} is zero or negative!")
                elif weight > 10000:
                    self.warnings.append(f"{pokemon_name}: weight {weight} is extremely heavy (over 1000kg!)")

            # Check egg groups
            if "eggGroups" in data:
                if isinstance(data["eggGroups"], list):
                    for egg_group in data["eggGroups"]:
                        if egg_group.lower() not in self.VALID_EGG_GROUPS:
                            self.warnings.append(f"{pokemon_name}: Unknown egg group '{egg_group}'")

            # NEW v2.1: Validate experienceGroup
            if "experienceGroup" in data:
                exp_group = data["experienceGroup"]
                if exp_group not in self.VALID_EXP_GROUPS:
                    self.warnings.append(f"{pokemon_name}: Unknown experienceGroup '{exp_group}'")
                    self.warnings.append(f"  Valid: {', '.join(sorted(self.VALID_EXP_GROUPS))}")

            # NEW v2.1: Validate maleRatio
            if "maleRatio" in data:
                male_ratio = data["maleRatio"]
                if isinstance(male_ratio, (int, float)):
                    if not (-1 <= male_ratio <= 1):
                        self.warnings.append(
                            f"{pokemon_name}: maleRatio {male_ratio} out of range (-1 genderless to 1 all-male)")
                else:
                    self.errors.append(f"{pokemon_name}: maleRatio must be a number")

            # NEW v2.1: Validate evolution structure + cache targets for cross-check
            if "evolutions" in data:
                evolutions = data["evolutions"]
                if isinstance(evolutions, list):
                    self.species_evolutions[pokemon_name] = evolutions
                    for i, evo in enumerate(evolutions):
                        if not isinstance(evo, dict):
                            self.errors.append(f"{pokemon_name}: Evolution #{i + 1} is not an object")
                            continue
                        if "result" not in evo:
                            self.errors.append(f"{pokemon_name}: Evolution #{i + 1} missing 'result'")
                        if "variant" not in evo:
                            self.errors.append(f"{pokemon_name}: Evolution #{i + 1} missing 'variant'")
                        elif evo["variant"] == "level_up":
                            reqs = evo.get("requirements", [])
                            has_level = any(
                                isinstance(r, dict) and r.get("variant") == "level" for r in reqs)
                            if not has_level:
                                self.warnings.append(
                                    f"{pokemon_name}: level_up evolution to '{evo.get('result', '?')}' "
                                    f"has no level requirement (will evolve at ANY level-up!)")
                        elif evo["variant"] == "item_interact" and "requiredContext" not in evo:
                            self.warnings.append(
                                f"{pokemon_name}: item_interact evolution to '{evo.get('result', '?')}' "
                                f"has no 'requiredContext' item")
                else:
                    self.errors.append(f"{pokemon_name}: 'evolutions' must be an array")

            # NEW v2.1: Cache declared pokedex lang keys for lang file check
            if isinstance(data.get("pokedex"), list):
                self.species_pokedex_keys[pokemon_name] = [
                    k for k in data["pokedex"] if isinstance(k, str)]

            return True

        except json.JSONDecodeError as e:
            self.errors.append(f"{pokemon_name}: Invalid JSON in species file: {e}")
            return False
        except Exception as e:
            self.errors.append(f"{pokemon_name}: Error reading species file: {e}")
            return False

    def check_model_file(self, pokemon_name: str) -> bool:
        """Check model .geo.json file"""
        model_file = self.pack_path / "resource_pack" / "assets" / "cobblemon" / "bedrock" / "pokemon" / "models" / pokemon_name / f"{pokemon_name}.geo.json"

        # CRITICAL: Check for wrong filename format (underscores instead of dots)
        wrong_filename = self.pack_path / "resource_pack" / "assets" / "cobblemon" / "bedrock" / "pokemon" / "models" / pokemon_name / f"{pokemon_name}_geo.json"
        if wrong_filename.exists():
            self.errors.append(
                f"{pokemon_name}: ERROR: CRITICAL BUG! Model file uses UNDERSCORES: '{pokemon_name}_geo.json'")
            self.errors.append(f"  Must use DOTS: '{pokemon_name}.geo.json' (rename the file!)")
            return False

        if not model_file.exists():
            self.errors.append(f"{pokemon_name}: Missing model file: {model_file}")
            return False

        try:
            with open(model_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Check identifier
            if "minecraft:geometry" in data:
                geometries = data["minecraft:geometry"]
                if isinstance(geometries, list) and len(geometries) > 0:
                    identifier = geometries[0].get("description", {}).get("identifier", "")
                    expected = f"geometry.{pokemon_name}"

                    # Check if identifier is completely wrong (different pokemon)
                    if identifier and not identifier.endswith(pokemon_name):
                        self.errors.append(f"{pokemon_name}: ERROR: Model identifier '{identifier}' doesn't match filename!")
                        self.errors.append(f"  Expected: '{expected}'")
                    elif identifier != expected:
                        self.warnings.append(
                            f"{pokemon_name}: Model identifier is '{identifier}', expected '{expected}'")

                    # Extract bone names for later validation
                    bones = geometries[0].get("bones", [])
                    bone_names = [bone.get("name", "") for bone in bones if isinstance(bone, dict)]
                    # Store for cross-validation with animations
                    if not hasattr(self, 'model_bones'):
                        self.model_bones = {}
                    self.model_bones[pokemon_name] = bone_names

                    # NEW v2.1: Cache declared texture size for texture dimension check
                    desc = geometries[0].get("description", {})
                    tex_w = desc.get("texture_width")
                    tex_h = desc.get("texture_height")
                    if isinstance(tex_w, (int, float)) and isinstance(tex_h, (int, float)):
                        self.model_texture_size[pokemon_name] = (int(tex_w), int(tex_h))
                    else:
                        self.warnings.append(
                            f"{pokemon_name}: Model missing texture_width/texture_height in description")

            # Check file size (warn if suspiciously small)
            file_size = model_file.stat().st_size
            if file_size < 100:
                self.warnings.append(f"{pokemon_name}: Model file is very small ({file_size} bytes) - might be empty!")

            return True

        except json.JSONDecodeError as e:
            self.errors.append(f"{pokemon_name}: Invalid JSON in model file: {e}")
            return False
        except Exception as e:
            self.errors.append(f"{pokemon_name}: Error reading model file: {e}")
            return False

    def check_animation_file(self, pokemon_name: str) -> bool:
        """Check animation .animation.json file"""
        anim_file = self.pack_path / "resource_pack" / "assets" / "cobblemon" / "bedrock" / "pokemon" / "animations" / pokemon_name / f"{pokemon_name}.animation.json"

        # CRITICAL: Check for wrong filename format (underscores instead of dots)
        wrong_filename = self.pack_path / "resource_pack" / "assets" / "cobblemon" / "bedrock" / "pokemon" / "animations" / pokemon_name / f"{pokemon_name}_animation.json"
        if wrong_filename.exists():
            self.errors.append(
                f"{pokemon_name}: ERROR: CRITICAL BUG! Animation file uses UNDERSCORES: '{pokemon_name}_animation.json'")
            self.errors.append(f"  Must use DOTS: '{pokemon_name}.animation.json' (rename the file!)")
            return False

        if not anim_file.exists():
            self.errors.append(f"{pokemon_name}: Missing animation file: {anim_file}")
            return False

        try:
            with open(anim_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Check for animations
            if "animations" not in data:
                self.errors.append(f"{pokemon_name}: No 'animations' key in animation file")
                return False

            animations = data["animations"]

            # NEW v2.1: Cache animation names for poser cross-check
            # Keys look like "animation.molecul.ground_idle" -> cache "ground_idle"
            anim_suffixes = set()
            expected_prefix = f"animation.{pokemon_name}."
            for anim_key in animations.keys():
                if anim_key.startswith(expected_prefix):
                    anim_suffixes.add(anim_key[len(expected_prefix):])
                else:
                    self.warnings.append(
                        f"{pokemon_name}: Animation key '{anim_key}' doesn't follow "
                        f"'animation.{pokemon_name}.<name>' convention (poser may not find it)")
            self.animation_names[pokemon_name] = anim_suffixes

            # Check required animations
            for required_anim in self.REQUIRED_ANIMATIONS:
                anim_key = f"animation.{pokemon_name}.{required_anim}"
                if anim_key not in animations:
                    self.errors.append(f"{pokemon_name}: Missing required animation '{required_anim}'")

            # Check recommended animations (Cobblemon falls back if absent)
            for rec_anim in self.RECOMMENDED_ANIMATIONS:
                anim_key = f"animation.{pokemon_name}.{rec_anim}"
                if anim_key not in animations:
                    self.warnings.append(
                        f"{pokemon_name}: Missing recommended animation '{rec_anim}'")
                    self.warnings.append(
                        f"  Cobblemon will fall back to ground_idle, but battles look better with it")

            # BONE MATCHING: Check if animation bones exist in model
            if hasattr(self, 'model_bones') and pokemon_name in self.model_bones:
                model_bone_names = self.model_bones[pokemon_name]

                for anim_name, anim_data in animations.items():
                    if isinstance(anim_data, dict) and "bones" in anim_data:
                        anim_bones = anim_data["bones"]
                        if isinstance(anim_bones, dict):
                            for bone_name in anim_bones.keys():
                                if bone_name not in model_bone_names:
                                    self.warnings.append(
                                        f"{pokemon_name}: Animation '{anim_name}' references bone '{bone_name}' that doesn't exist in model")
                                    self.warnings.append(f"  Model bones: {', '.join(model_bone_names)}")

            return True

        except json.JSONDecodeError as e:
            self.errors.append(f"{pokemon_name}: Invalid JSON in animation file: {e}")
            return False
        except Exception as e:
            self.errors.append(f"{pokemon_name}: Error reading animation file: {e}")
            return False

    def _read_png_size(self, png_path: Path):
        """Read width/height from a PNG's IHDR chunk. Returns (w, h) or None."""
        try:
            with open(png_path, 'rb') as f:
                header = f.read(24)
            if len(header) < 24 or header[:8] != b'\x89PNG\r\n\x1a\n':
                return None
            import struct
            width, height = struct.unpack(">II", header[16:24])
            return (width, height)
        except Exception:
            return None

    def _check_texture_dimensions(self, pokemon_name: str, texture_path: Path, label: str):
        """NEW v2.1: Compare actual PNG dimensions against the model's declared UV size"""
        if pokemon_name not in self.model_texture_size:
            return
        declared_w, declared_h = self.model_texture_size[pokemon_name]
        if declared_w <= 0 or declared_h <= 0:
            return
        size = self._read_png_size(texture_path)
        if size is None:
            return
        actual_w, actual_h = size
        if (actual_w, actual_h) == (declared_w, declared_h):
            return
        # Proportional scaling (e.g. 128x128 for a 64x64 UV map) renders fine
        if actual_w * declared_h == actual_h * declared_w:
            self.info.append(
                f"[OK] {pokemon_name}: {label} is {actual_w}x{actual_h} "
                f"(proportionally scaled from declared {declared_w}x{declared_h} — OK)")
        else:
            self.errors.append(
                f"{pokemon_name}: ERROR: {label} is {actual_w}x{actual_h} but model declares "
                f"{declared_w}x{declared_h}!")
            self.errors.append(
                f"  Mismatched aspect ratio will garble the texture in-game. "
                f"Re-export at {declared_w}x{declared_h} (or a clean multiple).")

    def check_texture_files(self, pokemon_name: str) -> bool:
        """Check texture PNG files"""
        texture_dir = self.pack_path / "resource_pack" / "assets" / "cobblemon" / "textures" / "pokemon" / pokemon_name

        # Check regular texture
        regular_texture = texture_dir / f"{pokemon_name}.png"
        if not regular_texture.exists():
            self.errors.append(f"{pokemon_name}: Missing regular texture: {regular_texture}")
            return False

        # Validate PNG format
        try:
            file_size = regular_texture.stat().st_size
            if file_size < 100:
                self.errors.append(
                    f"{pokemon_name}: Texture file suspiciously small ({file_size} bytes) - may be corrupted")

            # Check if it's actually a PNG by reading header
            with open(regular_texture, 'rb') as f:
                header = f.read(8)
                if header != b'\x89PNG\r\n\x1a\n':
                    self.errors.append(f"{pokemon_name}: CRITICAL! '{pokemon_name}.png' is not a valid PNG file!")
                    self.errors.append(f"  File may be corrupted or wrong format")
        except Exception as e:
            self.warnings.append(f"{pokemon_name}: Could not validate texture format: {e}")

        # NEW v2.1: Compare texture dimensions against model's declared UV size
        self._check_texture_dimensions(pokemon_name, regular_texture, f"{pokemon_name}.png")

        # Check shiny texture
        shiny_texture = texture_dir / f"{pokemon_name}_shiny.png"
        if not shiny_texture.exists():
            self.warnings.append(f"{pokemon_name}: Missing shiny texture: {shiny_texture}")
        else:
            # NEW v2.1: Validate shiny PNG format and dimensions too
            try:
                with open(shiny_texture, 'rb') as f:
                    if f.read(8) != b'\x89PNG\r\n\x1a\n':
                        self.errors.append(
                            f"{pokemon_name}: ERROR: '{pokemon_name}_shiny.png' is not a valid PNG file!")
            except Exception:
                pass
            self._check_texture_dimensions(pokemon_name, shiny_texture, f"{pokemon_name}_shiny.png")

        return True

    def check_poser_file(self, pokemon_name: str) -> bool:
        """Check poser JSON file"""
        poser_file = self.pack_path / "resource_pack" / "assets" / "cobblemon" / "bedrock" / "pokemon" / "posers" / f"{pokemon_name}.json"

        if not poser_file.exists():
            self.errors.append(f"{pokemon_name}: Missing poser file: {poser_file}")
            return False

        try:
            with open(poser_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Check for poses
            if "poses" not in data:
                self.errors.append(f"{pokemon_name}: No 'poses' key in poser file")
                return False

            # CRITICAL HEAD FIELD BUG CHECK
            if "head" in data:
                head_bone = data["head"]
                if head_bone is None or head_bone == "null" or head_bone == "":
                    self.errors.append(f"{pokemon_name}: ERROR: CRITICAL BUG! 'head' field is null/empty")
                    self.errors.append(f"  If no head bone, DELETE the 'head' field entirely (don't set to null!)")
                    self.errors.append(f"  This causes the 'practice dummy' bug!")
                else:
                    # Check if head bone actually exists in model
                    if hasattr(self, 'model_bones') and pokemon_name in self.model_bones:
                        model_bone_list = self.model_bones[pokemon_name]
                        if head_bone not in model_bone_list:
                            self.errors.append(f"{pokemon_name}: ERROR: Head bone '{head_bone}' doesn't exist in model!")
                            self.errors.append(f"  Model bones are: {', '.join(model_bone_list)}")

            # Check for portrait scale (common issue)
            if "portraitScale" not in data:
                self.warnings.append(f"{pokemon_name}: Missing 'portraitScale' in poser (defaults to 1.0)")

            # Check for profile translation
            if "profileTranslation" not in data:
                self.warnings.append(f"{pokemon_name}: Missing 'profileTranslation' in poser")

            # Check each pose for animation references
            poses = data.get("poses", {})
            import re as _re
            bedrock_pattern = _re.compile(r'bedrock\(\s*([a-z0-9_]+)\s*,\s*([a-z0-9_]+)\s*\)')
            for pose_name, pose_data in poses.items():
                if isinstance(pose_data, dict):
                    # Check for animations array
                    if "animations" in pose_data:
                        anims = pose_data["animations"]
                        if isinstance(anims, list):
                            for anim in anims:
                                # Warn about "look" animation when head might be missing
                                if "look" in str(anim).lower() and "head" not in data:
                                    self.warnings.append(
                                        f"{pokemon_name}: Pose '{pose_name}' has 'look' animation but no head bone defined")

                                # NEW v2.1: Validate bedrock(name, anim) references
                                for ref_name, ref_anim in bedrock_pattern.findall(str(anim)):
                                    if ref_name != pokemon_name:
                                        self.errors.append(
                                            f"{pokemon_name}: ERROR: Pose '{pose_name}' references "
                                            f"bedrock({ref_name}, ...) — wrong Pokémon name!")
                                        self.errors.append(
                                            f"  Should be bedrock({pokemon_name}, ...) — "
                                            f"likely a copy-paste from another poser")
                                    elif pokemon_name in self.animation_names:
                                        if ref_anim not in self.animation_names[pokemon_name]:
                                            available = ', '.join(sorted(self.animation_names[pokemon_name]))
                                            self.errors.append(
                                                f"{pokemon_name}: ERROR: Pose '{pose_name}' references animation "
                                                f"'{ref_anim}' that doesn't exist in animation file!")
                                            self.errors.append(f"  Available animations: {available}")

            return True

        except json.JSONDecodeError as e:
            self.errors.append(f"{pokemon_name}: Invalid JSON in poser file: {e}")
            return False
        except Exception as e:
            self.errors.append(f"{pokemon_name}: Error reading poser file: {e}")
            return False

    def check_resolver_file(self, pokemon_name: str) -> bool:
        """Check resolver JSON file"""
        # Correct location per wiki (no subfolder)
        resolver_file = self.pack_path / "resource_pack" / "assets" / "cobblemon" / "bedrock" / "pokemon" / "resolvers" / f"0_{pokemon_name}_base.json"

        # Check if file exists
        if not resolver_file.exists():
            # Try with subfolder (backwards compatibility)
            resolver_file = self.pack_path / "resource_pack" / "assets" / "cobblemon" / "bedrock" / "pokemon" / "resolvers" / pokemon_name / f"0_{pokemon_name}_base.json"

            if not resolver_file.exists():
                self.errors.append(f"{pokemon_name}: Missing resolver file (not found in either location)")
                return False

        # File exists, now validate it
        try:
            with open(resolver_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Check variations array
            if "variations" not in data:
                self.errors.append(f"{pokemon_name}: No 'variations' array in resolver")
                return False

            variations = data["variations"]
            if not isinstance(variations, list) or len(variations) == 0:
                self.errors.append(f"{pokemon_name}: Empty or invalid 'variations' in resolver")
                return False

            # Check first variation for model
            first_var = variations[0]
            if "model" in first_var:
                expected_model = f"cobblemon:{pokemon_name}.geo"
                if first_var["model"] != expected_model:
                    self.warnings.append(
                        f"{pokemon_name}: Model reference is '{first_var['model']}', expected '{expected_model}'")
            else:
                self.errors.append(f"{pokemon_name}: No 'model' field in first variation")

            # Check for poser reference
            if "poser" not in first_var:
                self.warnings.append(f"{pokemon_name}: No 'poser' field in first variation")
            else:
                # NEW v2.1: Verify the poser reference points at an existing poser file
                poser_ref = first_var["poser"]
                expected_poser = f"cobblemon:{pokemon_name}"
                if poser_ref != expected_poser:
                    self.warnings.append(
                        f"{pokemon_name}: Poser reference is '{poser_ref}', expected '{expected_poser}'")
                ref_name = str(poser_ref).split(":", 1)[-1]
                poser_path = (self.pack_path / "resource_pack" / "assets" / "cobblemon" /
                              "bedrock" / "pokemon" / "posers" / f"{ref_name}.json")
                if not poser_path.exists():
                    self.errors.append(
                        f"{pokemon_name}: ERROR: Resolver poser '{poser_ref}' has no matching file "
                        f"at posers/{ref_name}.json")

            # NEW v2.1: Verify texture paths in ALL variations resolve to real files
            found_texture = False
            for i, var in enumerate(variations):
                if not isinstance(var, dict) or "texture" not in var:
                    continue
                found_texture = True
                tex_ref = str(var["texture"])
                aspects = var.get("aspects", [])
                var_label = f"variation #{i + 1}" + (f" (aspects: {', '.join(aspects)})" if aspects else "")

                if not tex_ref.startswith("cobblemon:"):
                    self.warnings.append(
                        f"{pokemon_name}: Texture in {var_label} is '{tex_ref}' "
                        f"(expected a 'cobblemon:' namespaced path)")
                    continue
                rel_path = tex_ref.split(":", 1)[1]
                tex_path = self.pack_path / "resource_pack" / "assets" / "cobblemon" / rel_path
                if not tex_path.exists():
                    self.errors.append(
                        f"{pokemon_name}: ERROR: Resolver {var_label} points at missing texture!")
                    self.errors.append(f"  '{tex_ref}' → {tex_path}")
                    self.errors.append(f"  This causes invisible/missing textures in-game (check spelling & case)")
            if not found_texture:
                self.warnings.append(
                    f"{pokemon_name}: No 'texture' field in any resolver variation "
                    f"(Pokémon may render untextured)")

            return True

        except json.JSONDecodeError as e:
            self.errors.append(f"{pokemon_name}: Invalid JSON in resolver file: {e}")
            return False
        except Exception as e:
            self.errors.append(f"{pokemon_name}: Error reading resolver file: {e}")
            return False

    def check_spawn_file(self, pokemon_name: str) -> bool:
        """Check spawn pool JSON file"""
        spawn_file = self.pack_path / "behavior_pack" / "data" / "cobblemon" / "spawn_pool_world" / f"{pokemon_name}.json"

        if not spawn_file.exists():
            self.warnings.append(f"{pokemon_name}: Missing spawn file (Pokemon won't spawn naturally)")
            return True  # Not a critical error

        try:
            with open(spawn_file, 'r') as f:
                data = json.load(f)

            # Check for spawns
            if "spawns" not in data:
                self.errors.append(f"{pokemon_name}: No 'spawns' array in spawn file")
                return False

            # NEW v2.1: Deep-check each spawn entry
            spawns = data["spawns"]
            if isinstance(spawns, list):
                if not spawns:
                    self.warnings.append(f"{pokemon_name}: 'spawns' array is empty (won't spawn)")
                for i, spawn in enumerate(spawns):
                    if not isinstance(spawn, dict):
                        continue
                    label = f"spawn entry #{i + 1}"

                    # pokemon field should match the species
                    spawn_pokemon = spawn.get("pokemon", "")
                    base_pokemon = str(spawn_pokemon).split(" ")[0].lower()  # ignore aspect args
                    if spawn_pokemon and base_pokemon != pokemon_name:
                        self.errors.append(
                            f"{pokemon_name}: ERROR: {label} spawns '{spawn_pokemon}' — doesn't match filename!")
                        self.errors.append(f"  Likely a copy-paste from another spawn file")

                    # bucket must be valid
                    bucket = spawn.get("bucket")
                    if bucket is not None and bucket not in self.VALID_BUCKETS:
                        self.errors.append(
                            f"{pokemon_name}: {label} has invalid bucket '{bucket}'")
                        self.errors.append(f"  Valid buckets: {', '.join(sorted(self.VALID_BUCKETS))}")

                    # weight of 0 never spawns
                    weight = spawn.get("weight")
                    if isinstance(weight, (int, float)) and weight <= 0:
                        self.warnings.append(
                            f"{pokemon_name}: {label} has weight {weight} (will NEVER spawn!)")

                    # level range sanity
                    level = spawn.get("level")
                    if isinstance(level, str) and "-" in level:
                        try:
                            lo, hi = level.split("-", 1)
                            lo, hi = int(lo), int(hi)
                            if lo > hi:
                                self.errors.append(
                                    f"{pokemon_name}: {label} level range '{level}' is backwards (min > max)")
                            if hi > 100:
                                self.warnings.append(
                                    f"{pokemon_name}: {label} max level {hi} is over 100")
                        except ValueError:
                            self.warnings.append(
                                f"{pokemon_name}: {label} level '{level}' isn't a valid range (e.g. '5-30')")

            return True

        except json.JSONDecodeError as e:
            self.errors.append(f"{pokemon_name}: Invalid JSON in spawn file: {e}")
            return False
        except Exception as e:
            self.errors.append(f"{pokemon_name}: Error reading spawn file: {e}")
            return False

    # ========================================================================
    # NEW v2.1: Pack-level cross-checks
    # ========================================================================

    def check_evolution_targets(self):
        """NEW v2.1: Verify every evolution result points at a species that exists"""
        for pokemon_name, evolutions in self.species_evolutions.items():
            for evo in evolutions:
                if not isinstance(evo, dict):
                    continue
                result = str(evo.get("result", "")).split(" ")[0].lower()  # ignore aspect args
                result = result.split(":", 1)[-1]  # strip namespace if present
                if not result:
                    continue
                if result not in self.all_species:
                    self.warnings.append(
                        f"{pokemon_name}: Evolution target '{result}' is not in this pack")
                    self.warnings.append(
                        f"  If it's not a vanilla Pokémon either, the evolution will silently never fire")

    def check_lang_file(self, pokemon_list: List[str]):
        """NEW v2.1: Verify lang file has name + pokedex desc entries for every Pokémon"""
        lang_file = self.pack_path / "resource_pack" / "assets" / "cobblemon" / "lang" / "en_us.json"

        if not lang_file.exists():
            self.errors.append("Missing lang file: assets/cobblemon/lang/en_us.json")
            self.errors.append("  All Pokémon will show raw translation keys in-game!")
            return

        try:
            with open(lang_file, 'r', encoding='utf-8') as f:
                lang_data = json.load(f)
        except json.JSONDecodeError as e:
            self.errors.append(f"Invalid JSON in lang file en_us.json: {e}")
            return
        except Exception as e:
            self.warnings.append(f"Could not read lang file: {e}")
            return

        for pokemon_name in pokemon_list:
            name_key = f"cobblemon.species.{pokemon_name}.name"
            if name_key not in lang_data:
                self.warnings.append(
                    f"{pokemon_name}: Missing '{name_key}' in en_us.json (shows raw key in-game)")

            # Check the desc keys the species file actually declares
            for dex_key in self.species_pokedex_keys.get(pokemon_name, []):
                if dex_key not in lang_data:
                    self.warnings.append(
                        f"{pokemon_name}: Pokédex key '{dex_key}' declared in species file "
                        f"but missing from en_us.json")

    def check_species_additions(self):
        """NEW v2.1: Validate species_additions files (from the species editor)"""
        additions_dir = self.pack_path / "behavior_pack" / "data" / "cobblemon" / "species_additions"
        if not additions_dir.exists():
            return  # Nothing to check

        addition_files = list(additions_dir.glob("*.json"))
        if not addition_files:
            return

        print(f"   Checking {len(addition_files)} species addition(s)...")

        for add_file in addition_files:
            label = f"species_additions/{add_file.name}"
            try:
                with open(add_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            except json.JSONDecodeError as e:
                self.errors.append(f"{label}: Invalid JSON: {e}")
                continue
            except Exception as e:
                self.errors.append(f"{label}: Error reading file: {e}")
                continue

            # Target is required and must be namespaced
            target = data.get("target")
            if not target:
                self.errors.append(f"{label}: Missing 'target' field (addition does nothing)")
                continue
            if ":" not in str(target):
                self.warnings.append(
                    f"{label}: target '{target}' has no namespace (expected e.g. 'cobblemon:{target}')")
            target_name = str(target).split(":", 1)[-1].lower()

            # If targeting a custom species, it must exist; vanilla we can't verify
            if target_name in self.all_species:
                self.info.append(f"[OK] {label}: targets custom species '{target_name}'")
            else:
                self.info.append(
                    f"[OK] {label}: targets '{target_name}' (not in this pack — assuming vanilla; "
                    f"double-check spelling)")

            # Validate evolutions inside the addition
            for i, evo in enumerate(data.get("evolutions", [])):
                if not isinstance(evo, dict):
                    continue
                if "result" not in evo:
                    self.errors.append(f"{label}: Evolution #{i + 1} missing 'result'")
                else:
                    result = str(evo["result"]).split(" ")[0].split(":", 1)[-1].lower()
                    if result and result not in self.all_species:
                        self.warnings.append(
                            f"{label}: Evolution target '{result}' is not in this pack "
                            f"(verify it's vanilla or exists elsewhere)")
                if "variant" not in evo:
                    self.errors.append(f"{label}: Evolution #{i + 1} missing 'variant'")

            # Reuse the known move-replacement footgun warning
            if "moves" in data:
                self.warnings.append(
                    f"{label}: 'moves' REPLACES the target's entire move list "
                    f"({len(data['moves'])} moves) — make sure that's intended")

    def check_orphan_files(self):
        """NEW v2.1: Find posers/resolvers/models/animations/textures/spawns with no species"""
        rp_bedrock = self.pack_path / "resource_pack" / "assets" / "cobblemon" / "bedrock" / "pokemon"

        locations = [
            ("poser", rp_bedrock / "posers", lambda p: p.stem, "*.json"),
            ("model folder", rp_bedrock / "models", lambda p: p.name, None),
            ("animation folder", rp_bedrock / "animations", lambda p: p.name, None),
            ("texture folder",
             self.pack_path / "resource_pack" / "assets" / "cobblemon" / "textures" / "pokemon",
             lambda p: p.name, None),
            ("spawn file",
             self.pack_path / "behavior_pack" / "data" / "cobblemon" / "spawn_pool_world",
             lambda p: p.stem, "*.json"),
        ]

        for kind, directory, name_fn, pattern in locations:
            if not directory.exists():
                continue
            items = directory.glob(pattern) if pattern else (p for p in directory.iterdir() if p.is_dir())
            for item in items:
                name = name_fn(item)
                if name not in self.all_species:
                    self.warnings.append(
                        f"Orphan {kind} '{name}' has no species file (leftover from a "
                        f"renamed/deleted Pokémon?)")

        # Resolvers use the 0_{name}_base.json pattern
        resolvers_dir = rp_bedrock / "resolvers"
        if resolvers_dir.exists():
            import re as _re
            resolver_pattern = _re.compile(r'^\d+_(.+)_base$')
            for item in resolvers_dir.glob("*.json"):
                m = resolver_pattern.match(item.stem)
                if m and m.group(1) not in self.all_species:
                    self.warnings.append(
                        f"Orphan resolver '{item.name}' has no species file (leftover from a "
                        f"renamed/deleted Pokémon?)")

    def print_results(self):
        """Print all errors, warnings, and info.

        Entries that start with whitespace are detail lines belonging to the
        previous entry; they are printed as indented children, e.g.:

           • molecul: Animation references bone 'head' not in model!
                `- Only bones found: body, tail, leftarm
        """
        print(f"\n{'=' * 70}")
        print("RESULTS")
        print(f"{'=' * 70}\n")

        def split_issues(items):
            """Group flat list into (parent, [children]) using the
            leading-whitespace convention for detail lines."""
            issues = []
            for item in items:
                if item.startswith((' ', '\t')) and issues:
                    issues[-1][1].append(item.strip())
                else:
                    issues.append([item.lstrip(), []])
            return issues

        def print_issues(issues):
            for parent, children in issues:
                print(f"   • {parent}")
                for child in children:
                    print(f"        `- {child}")

        error_issues = split_issues(self.errors)
        warning_issues = split_issues(self.warnings)

        if error_issues:
            print(f"ERRORS ({len(error_issues)}):")
            print_issues(error_issues)
            print()

        if warning_issues:
            print(f"WARNINGS ({len(warning_issues)}):")
            print_issues(warning_issues)
            print()

        if not error_issues and not warning_issues:
            print("[OK] NO ERRORS OR WARNINGS FOUND!")
            print("   Your pack looks good!\n")

        print(f"{'=' * 70}")
        print(f"Summary: {len(error_issues)} errors, {len(warning_issues)} warnings")
        print(f"{'=' * 70}\n")


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Cobblemon Pack Error Checker - Find issues in your pack",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument('--pack-path', type=str, help='Path to pack directory')
    parser.add_argument('--version', action='version',
                        version=f'Cobblemon Pack Checker v{CHECKER_VERSION}')

    args = parser.parse_args()

    checker = CobblemonPackChecker(pack_path=args.pack_path)
    checker.check_all()


if __name__ == "__main__":
    main()
