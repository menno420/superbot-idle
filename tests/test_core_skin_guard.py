"""CORE/SKIN guard: engine source must contain zero theme vocabulary.

The engine is theme-agnostic by contract (README, CONVENTIONS). This
test greps every engine module (and the generic theme-gate tool) for
distinctive theme-pack nouns; any hit means theme content leaked into
core.

Structure: FORBIDDEN_NOUNS_BY_PACK maps every shipped pack id
(themes/<id>.yaml) to its distinctive guard nouns; the tuples compile
into one word-boundary regex. A coverage test asserts the dict keys
equal the shipped catalog, so adding a pack without registering its
guard nouns is red — a pack with genuinely no distinctive noun must say
so with an explicit empty tuple.
"""

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# Deliberately EXCLUDED as too generic for a guard that scans engine
# prose/identifiers: "gold", "coin", "scale" ("scales/scaling" is
# legitimate engine vocabulary), "surface", "station", "village",
# "drone" — from wave 2: "tower", "library", "credit(s)", "city",
# "royal", "seal", "swarm", "grid", "upload", "franchise", "fragment"
# — and from wave 3: "crew", "treasure", "tide", "captain", "anchor",
# "queen", "nest", "worker(s)", "trail", "garden", "jelly", "fan(s)",
# "studio", "record(s)", "stage", "debut", "graduate/graduation",
# "agency"
# — and from wave 4: "drum", "grinder", "blend", "shop", "core", "drill",
# "team", "cache", "line", "factory", "batch", "shard", "crystal",
# "recipe", "conveyor"
# — and from wave 5: "bench", "caliber", "complication", "movement",
# "watch", "keep", "keeper", "beam", "counter", "queue", "press",
# "burner", "cart", "tare", "dies"
# — the packs' truly distinctive nouns below carry the guard instead.
#
# One entry per shipped pack, in catalog-growth order. Nouns are plain
# literals (both spellings listed where the pack uses an accent, e.g.
# séance/seance); they are re.escape()d and joined into a single
# word-boundary alternation so e.g. "when" does not trip on "hen".
FORBIDDEN_NOUNS_BY_PACK: dict[str, tuple[str, ...]] = {
    "egg-farm": (
        "egg", "eggs", "chicken", "chickens", "coop", "coops", "farm",
        "farms", "hen", "hens", "henhouse", "henhouses", "golden",
    ),
    "space-colony": (
        "colony", "colonies", "oxygen", "solar", "hydroponics",
        "artifact", "artifacts",
    ),
    "potion-brewery": (
        "potion", "potions", "cauldron", "cauldrons", "brewery",
        "breweries", "alchemist", "alchemists", "arcane", "grimoire",
        "grimoires",
    ),
    "haunted-manor": (
        "manor", "manors", "haunted", "ectoplasm", "séance", "séances",
        "seance", "seances", "spirit", "spirits", "poltergeist",
        "poltergeists", "phantom", "phantoms",
    ),
    "deep-sea-station": (
        "pearl", "pearls", "abyssal", "trench", "trenches", "oyster",
        "oysters", "submersible", "submersibles", "kelp", "plankton",
        "relic", "relics",
    ),
    "dragon-hoard": (
        "dragon", "dragons", "hoard", "hoards", "kobold", "kobolds",
        "lair", "lairs", "pickaxe", "pickaxes", "tribute", "tributes",
    ),
    "wizard-tower": (
        "wizard", "wizards", "mana", "scribe", "scribes", "quill",
        "quills", "starlight", "astral", "enchanted",
    ),
    "royal-bakery": (
        "bakery", "bakeries", "bakehouse", "bakehouses", "pastry",
        "pastries", "sourdough", "dough", "flour", "hearth", "hearths",
        "oven", "ovens",
    ),
    "cyber-city": (
        "cyber", "neon", "uplink", "overclock", "overclocked",
        "cryo-coolant",
    ),
    "pirate-cove": (
        "pirate", "pirates", "doubloon", "doubloons", "smuggler",
        "smugglers", "skiff", "skiffs", "tavern", "taverns", "rum",
        "quartermaster", "quartermasters", "cove", "coves",
    ),
    "ant-colony": (
        "ant", "ants", "crumb", "crumbs", "pheromone", "pheromones",
        "forager", "foragers", "leafcutter", "leafcutters", "fungus",
        "instar", "instars",
    ),
    "idol-agency": (
        "idol", "idols", "fandom", "fandoms", "fancam", "fancams",
        "livestream", "livestreams", "choreography", "platinum",
        "lightstick", "lightsticks",
    ),
    "coffee-roastery": (
        "coffee", "roastery", "roasteries", "bean", "beans", "barista",
        "baristas", "espresso", "arabica", "crema", "portafilter",
        "portafilters", "drip", "roasting", "roaster", "roasters",
    ),
    "arctic-outpost": (
        "arctic", "outpost", "outposts", "snowpack", "aurora", "husky",
        "huskies", "sled", "sleds", "tundra", "glacier", "glaciers",
        "permafrost", "musher", "mushers", "expedition", "expeditions",
    ),
    "candy-factory": (
        "candy", "candies", "taffy", "gumdrop", "gumdrops", "lollipop",
        "lollipops", "confection", "confections", "nougat", "caramel",
        "marshmallow", "marshmallows", "sherbet", "sugar",
    ),
    "clockwork-atelier": (
        "clockwork", "atelier", "ateliers", "horologist", "horological",
        "mainspring", "mainsprings", "escapement", "escapements", "cog",
        "cogs", "lathe", "lathes",
    ),
    "lighthouse-keep": (
        "lighthouse", "lighthouses", "fresnel", "lamplight", "wick",
        "wicks", "headland", "headlands", "seaboard", "lantern",
        "lanterns",
    ),
    "ramen-stand": (
        "ramen", "noodle", "noodles", "broth", "broths", "stockpot",
        "stockpots", "slurp", "slurps", "slurped", "ladle", "ladles",
        "ladleful", "bowl", "bowls",
    ),
}

FORBIDDEN_NOUNS = re.compile(
    r"\b("
    + "|".join(
        re.escape(noun)
        for nouns in FORBIDDEN_NOUNS_BY_PACK.values()
        for noun in nouns
    )
    + r")\b",
    re.IGNORECASE,
)

THEME_AGNOSTIC_SOURCES = sorted(REPO_ROOT.glob("idle_engine/**/*.py")) + [
    REPO_ROOT / "tools" / "theme_gate.py",
]


def test_guard_scans_a_nonempty_engine():
    assert len(THEME_AGNOSTIC_SOURCES) >= 4  # package + state + engine + theme + tool


def test_every_shipped_pack_registers_guard_nouns():
    # Ratchet: the noun table's keys must equal the shipped catalog.
    # A new themes/<id>.yaml is red here until the pack registers its
    # distinctive nouns (or an explicit empty tuple documenting that it
    # has none); a removed pack is red until its stale entry is dropped.
    shipped = {path.stem for path in (REPO_ROOT / "themes").glob("*.yaml")}
    registered = set(FORBIDDEN_NOUNS_BY_PACK)
    assert shipped == registered, (
        "FORBIDDEN_NOUNS_BY_PACK is out of sync with themes/*.yaml:\n"
        f"  shipped but unregistered: {sorted(shipped - registered)}\n"
        f"  registered but not shipped: {sorted(registered - shipped)}"
    )


def test_engine_sources_contain_no_theme_nouns():
    violations = []
    for source in THEME_AGNOSTIC_SOURCES:
        for lineno, line in enumerate(source.read_text(encoding="utf-8").splitlines(), 1):
            match = FORBIDDEN_NOUNS.search(line)
            if match:
                violations.append(f"{source.relative_to(REPO_ROOT)}:{lineno}: {match.group(0)!r}")
    assert not violations, "theme nouns leaked into engine core:\n" + "\n".join(violations)


def test_guard_pattern_actually_catches_nouns():
    # Self-check that the guard is not vacuous.
    assert FORBIDDEN_NOUNS.search("a chicken coop")
    assert FORBIDDEN_NOUNS.search("Egg Farm")
    assert FORBIDDEN_NOUNS.search("a bigger henhouse")
    assert FORBIDDEN_NOUNS.search("Golden Eggs")
    assert FORBIDDEN_NOUNS.search("launch a new colony")
    assert FORBIDDEN_NOUNS.search("Oxygen from the solar array")
    assert FORBIDDEN_NOUNS.search("alien artifacts")
    assert FORBIDDEN_NOUNS.search("a Potion Brewery cauldron")
    assert FORBIDDEN_NOUNS.search("arcane essence")
    assert FORBIDDEN_NOUNS.search("the apprentice alchemist's grimoire")
    assert FORBIDDEN_NOUNS.search("the Haunted Manor's ectoplasm")
    assert FORBIDDEN_NOUNS.search("hold a séance for restless spirits")
    assert FORBIDDEN_NOUNS.search("hold a seance")  # ASCII spelling too
    assert FORBIDDEN_NOUNS.search("a poltergeist in the parlor")
    assert FORBIDDEN_NOUNS.search("pearls from the oyster bed")
    assert FORBIDDEN_NOUNS.search("abyssal relics from the trench")
    assert FORBIDDEN_NOUNS.search("a submersible combing the kelp")
    assert FORBIDDEN_NOUNS.search("the Dragon Hoard grows")
    assert FORBIDDEN_NOUNS.search("a kobold miner's pickaxe")
    assert FORBIDDEN_NOUNS.search("tribute from the lair")
    assert FORBIDDEN_NOUNS.search("the Wizard Tower brims with mana")
    assert FORBIDDEN_NOUNS.search("an apprentice scribe's quill")
    assert FORBIDDEN_NOUNS.search("crystallized starlight on the astral plane")
    assert FORBIDDEN_NOUNS.search("the enchanted library hums")
    assert FORBIDDEN_NOUNS.search("a Royal Bakery pastry")
    assert FORBIDDEN_NOUNS.search("sourdough proofing by the hearth")
    assert FORBIDDEN_NOUNS.search("stone-ground flour for the brick oven")
    assert FORBIDDEN_NOUNS.search("a bakehouse full of pastries")
    assert FORBIDDEN_NOUNS.search("Cyber City neon")
    assert FORBIDDEN_NOUNS.search("a skyline uplink, overclocked")
    assert FORBIDDEN_NOUNS.search("the cryo-coolant overclock kicks in")
    assert FORBIDDEN_NOUNS.search("a Pirate Cove smuggler skiff")
    assert FORBIDDEN_NOUNS.search("doubloons for the tavern crew")
    assert FORBIDDEN_NOUNS.search("the quartermaster counts the rum")
    assert FORBIDDEN_NOUNS.search("an Ant Colony forager trail")
    assert FORBIDDEN_NOUNS.search("crumbs for the fungus garden")
    assert FORBIDDEN_NOUNS.search("pheromone markers guide the leafcutter")
    assert FORBIDDEN_NOUNS.search("royal jelly at the next instar")
    assert FORBIDDEN_NOUNS.search("an Idol Agency livestream studio")
    assert FORBIDDEN_NOUNS.search("the fandom shares a viral fancam")
    assert FORBIDDEN_NOUNS.search("choreography drills for a platinum record")
    assert FORBIDDEN_NOUNS.search("a Coffee Roastery drip station")
    assert FORBIDDEN_NOUNS.search("reserve blends of arabica beans")
    assert FORBIDDEN_NOUNS.search("espresso crema pulled by the barista")
    assert FORBIDDEN_NOUNS.search("an Arctic Outpost husky sled team")
    assert FORBIDDEN_NOUNS.search("aurora shards drifting over the snowpack")
    assert FORBIDDEN_NOUNS.search("a musher crossing the tundra glacier")
    assert FORBIDDEN_NOUNS.search("a Candy Factory taffy puller")
    assert FORBIDDEN_NOUNS.search("gumdrops dusted in sugar")
    assert FORBIDDEN_NOUNS.search("a nougat caramel lollipop confection")
    assert FORBIDDEN_NOUNS.search("a Clockwork Atelier mainspring lathe")
    assert FORBIDDEN_NOUNS.search("cogs filed by the horologist")
    assert FORBIDDEN_NOUNS.search("the escapement ticks in its case")
    assert FORBIDDEN_NOUNS.search("a Lighthouse Keep fresnel array")
    assert FORBIDDEN_NOUNS.search("lamplight thrown from the headland")
    assert FORBIDDEN_NOUNS.search("a trimmed wick in the lantern")
    assert FORBIDDEN_NOUNS.search("a Ramen Stand noodle press")
    assert FORBIDDEN_NOUNS.search("bowls of broth from the stockpot")
    assert FORBIDDEN_NOUNS.search("a golden ladle slurped clean")
    assert not FORBIDDEN_NOUNS.search("when the tick happens")
    assert not FORBIDDEN_NOUNS.search("prestige multiplier upgrade")
    assert not FORBIDDEN_NOUNS.search("essential engine invariants")
    assert not FORBIDDEN_NOUNS.search("rates scale with upgrade level")
    assert not FORBIDDEN_NOUNS.search("goldilocks tick granularity")
    assert not FORBIDDEN_NOUNS.search("inspirited")  # boundary: not 'spirit'
    assert not FORBIDDEN_NOUNS.search("a proven approach")  # boundary: not 'oven'
    assert not FORBIDDEN_NOUNS.search("describes the flourish")  # not 'scribe'/'flour'
    assert not FORBIDDEN_NOUNS.search("cybersecurity")  # boundary: not 'cyber'
    assert not FORBIDDEN_NOUNS.search("the state manager")  # boundary: not 'mana'
    assert not FORBIDDEN_NOUNS.search("an important invariant")  # boundary: not 'ant'
    assert not FORBIDDEN_NOUNS.search("a quantum of spectrum")  # boundary: not 'ant'/'rum'
    assert not FORBIDDEN_NOUNS.search("covered by the gate")  # boundary: not 'cove'
    assert not FORBIDDEN_NOUNS.search("crumbling assumptions")  # boundary: not 'crumb'
    assert not FORBIDDEN_NOUNS.search("idolatrous constants")  # boundary: not 'idol'
