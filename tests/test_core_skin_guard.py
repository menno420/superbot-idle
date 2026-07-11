"""CORE/SKIN guard: engine source must contain zero theme vocabulary.

The engine is theme-agnostic by contract (README, CONVENTIONS). This
test greps every engine module (and the generic theme-gate tool) for
egg-farm nouns; any hit means theme content leaked into core.
"""

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# Word-boundary match so e.g. "when" does not trip on "hen".
# Extended for slice (b): upgrade/prestige nouns (henhouse, golden [eggs]).
# Extended for slice (c): space-colony + potion-brewery distinctive nouns.
# Extended for catalog growth: haunted-manor + deep-sea-station +
# dragon-hoard distinctive nouns. Extended for catalog wave 2:
# wizard-tower + royal-bakery + cyber-city distinctive nouns.
# Extended for catalog wave 3: pirate-cove + ant-colony + idol-agency
# distinctive nouns.
# Deliberately EXCLUDED as too generic for a guard that scans engine
# prose/identifiers: "gold", "coin", "scale" ("scales/scaling" is
# legitimate engine vocabulary), "surface", "station", "village",
# "drone" — from wave 2: "tower", "library", "credit(s)", "city",
# "royal", "seal", "swarm", "grid", "upload", "franchise", "fragment"
# — and from wave 3: "crew", "treasure", "tide", "captain", "anchor",
# "queen", "nest", "worker(s)", "trail", "garden", "jelly", "fan(s)",
# "studio", "record(s)", "stage", "debut", "graduate/graduation",
# "agency"
# — the packs' truly distinctive nouns below carry the guard instead.
FORBIDDEN_NOUNS = re.compile(
    r"\b(egg|eggs|chicken|chickens|coop|coops|farm|farms|hen|hens"
    r"|henhouse|henhouses|golden"
    r"|colony|colonies|oxygen|solar|hydroponics|artifact|artifacts"
    r"|potion|potions|cauldron|cauldrons|brewery|breweries|alchemist"
    r"|alchemists|arcane|grimoire|grimoires"
    r"|manor|manors|haunted|ectoplasm|s[eé]ance|s[eé]ances|spirit|spirits"
    r"|poltergeist|poltergeists|phantom|phantoms"
    r"|pearl|pearls|abyssal|trench|trenches|oyster|oysters|submersible"
    r"|submersibles|kelp|plankton|relic|relics"
    r"|dragon|dragons|hoard|hoards|kobold|kobolds|lair|lairs|pickaxe"
    r"|pickaxes|tribute|tributes"
    r"|wizard|wizards|mana|scribe|scribes|quill|quills|starlight"
    r"|astral|enchanted"
    r"|bakery|bakeries|bakehouse|bakehouses|pastry|pastries|sourdough"
    r"|dough|flour|hearth|hearths|oven|ovens"
    r"|cyber|neon|uplink|overclock|overclocked|cryo-coolant"
    r"|pirate|pirates|doubloon|doubloons|smuggler|smugglers|skiff|skiffs"
    r"|tavern|taverns|rum|quartermaster|quartermasters|cove|coves"
    r"|ant|ants|crumb|crumbs|pheromone|pheromones|forager|foragers"
    r"|leafcutter|leafcutters|fungus|instar|instars"
    r"|idol|idols|fandom|fandoms|fancam|fancams|livestream|livestreams"
    r"|choreography|platinum|lightstick|lightsticks)\b",
    re.IGNORECASE,
)

THEME_AGNOSTIC_SOURCES = sorted(REPO_ROOT.glob("idle_engine/**/*.py")) + [
    REPO_ROOT / "tools" / "theme_gate.py",
]


def test_guard_scans_a_nonempty_engine():
    assert len(THEME_AGNOSTIC_SOURCES) >= 4  # package + state + engine + theme + tool


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
