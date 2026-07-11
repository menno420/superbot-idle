"""Theme catalog: schema v1 proven on foreign content, at catalog scale.

Slice (c) proved the schema on two packs it was NOT designed around
(space-colony, potion-brewery); catalog growth added three more
(haunted-manor, deep-sea-station, dragon-hoard), wave 2 another three
(wizard-tower, royal-bakery, cyber-city), and wave 3 another three
(pirate-cove, ant-colony, idol-agency). Every pack must fill
every slot egg-farm fills, load through the engine's theme loader, and
drive the full engine cycle (tick, upgrade purchase, prestige reset)
with its own nouns. Plus the checks per-file JSON Schema cannot express:
`theme.id` == filename stem (per file, both directions) and cross-pack
`theme.id` uniqueness (defense-in-depth — reachable end-to-end only via
`.yaml`/`.yml` stem twins now that the stem rule holds per file).
"""

from pathlib import Path

import pytest

from idle_engine import (
    GameState,
    apply_prestige,
    load_theme,
    prestige_eligible,
    purchase_upgrade,
    tick,
)
from tools.theme_gate import catalog_errors, main, validate_file

REPO_ROOT = Path(__file__).resolve().parent.parent
THEMES_DIR = REPO_ROOT / "themes"
ALL_PACKS = sorted(THEMES_DIR.glob("*.yaml"))
EGG_FARM = THEMES_DIR / "egg-farm.yaml"
SPACE_COLONY = THEMES_DIR / "space-colony.yaml"
POTION_BREWERY = THEMES_DIR / "potion-brewery.yaml"
HAUNTED_MANOR = THEMES_DIR / "haunted-manor.yaml"
DEEP_SEA_STATION = THEMES_DIR / "deep-sea-station.yaml"
DRAGON_HOARD = THEMES_DIR / "dragon-hoard.yaml"
WIZARD_TOWER = THEMES_DIR / "wizard-tower.yaml"
ROYAL_BAKERY = THEMES_DIR / "royal-bakery.yaml"
CYBER_CITY = THEMES_DIR / "cyber-city.yaml"
PIRATE_COVE = THEMES_DIR / "pirate-cove.yaml"
ANT_COLONY = THEMES_DIR / "ant-colony.yaml"
IDOL_AGENCY = THEMES_DIR / "idol-agency.yaml"


# --- the catalog ships twelve packs, all gate-green ---------------------------


def test_catalog_ships_all_twelve_packs():
    for pack in (
        EGG_FARM,
        SPACE_COLONY,
        POTION_BREWERY,
        HAUNTED_MANOR,
        DEEP_SEA_STATION,
        DRAGON_HOARD,
        WIZARD_TOWER,
        ROYAL_BAKERY,
        CYBER_CITY,
        PIRATE_COVE,
        ANT_COLONY,
        IDOL_AGENCY,
    ):
        assert pack in ALL_PACKS, f"missing shipped pack {pack.name}"
    assert len(ALL_PACKS) >= 12


def test_whole_catalog_passes_gate_including_cross_pack_checks(capsys):
    assert main(["theme_gate", str(THEMES_DIR)]) == 0
    out = capsys.readouterr().out
    assert "FAIL" not in out


# --- every pack fills every slot egg-farm fills ------------------------------


@pytest.mark.parametrize("pack", ALL_PACKS, ids=lambda p: p.stem)
def test_pack_fills_every_egg_farm_slot(pack):
    assert validate_file(pack) == []
    theme = load_theme(pack)
    assert theme.theme_id and theme.name and theme.description
    assert theme.emoji and theme.embed_color.startswith("#")
    assert theme.currencies and theme.generators
    for currency in theme.currencies.values():
        assert currency.name and currency.description and currency.emoji
    for gen in theme.generators.values():
        assert gen.name and gen.description and gen.emoji
        assert gen.produces in theme.currencies
        assert 1 <= gen.base_rate <= 1000
    assert theme.upgrades, f"{pack.stem} must fill the upgrades slot"
    for upgrade in theme.upgrades.values():
        assert upgrade.name and upgrade.description and upgrade.emoji
        assert upgrade.target in theme.generators
    assert theme.prestige is not None, f"{pack.stem} must fill the prestige slot"
    assert theme.prestige.currency in theme.currencies
    assert theme.prestige.measures in theme.currencies
    assert theme.prestige.action_name and theme.prestige.action_description
    assert theme.prestige.action_emoji


# --- the new packs' nouns resolve through the loader -------------------------


def test_space_colony_nouns_resolve():
    theme = load_theme(SPACE_COLONY)
    assert theme.theme_id == "space-colony"
    assert theme.name == "Space Colony"
    assert theme.currency_name("primary") == "oxygen"
    assert theme.currency_name("prestige") == "alien artifacts"
    assert theme.generator_name("tier1") == "solar array"
    assert theme.generator_name("tier2") == "hydroponics bay"
    assert theme.upgrade_name("boost1") == "polished reflectors"
    assert theme.upgrades["boost1"].target == "tier1"
    assert theme.upgrades["boost2"].target == "tier2"
    assert theme.prestige.currency == "prestige"
    assert theme.prestige.measures == "primary"
    assert theme.prestige.action_name == "launch a new colony"


def test_potion_brewery_nouns_resolve():
    theme = load_theme(POTION_BREWERY)
    assert theme.theme_id == "potion-brewery"
    assert theme.name == "Potion Brewery"
    assert theme.currency_name("primary") == "potions"
    assert theme.currency_name("prestige") == "arcane essence"
    assert theme.generator_name("tier1") == "cauldron"
    assert theme.generator_name("tier2") == "apprentice alchemist"
    assert theme.upgrade_name("boost1") == "hotter flames"
    assert theme.upgrades["boost1"].target == "tier1"
    assert theme.upgrades["boost2"].target == "tier2"
    assert theme.prestige.currency == "prestige"
    assert theme.prestige.measures == "primary"
    assert theme.prestige.action_name == "transcend the craft"


def test_haunted_manor_nouns_resolve():
    theme = load_theme(HAUNTED_MANOR)
    assert theme.theme_id == "haunted-manor"
    assert theme.name == "Haunted Manor"
    assert theme.currency_name("primary") == "ectoplasm"
    assert theme.currency_name("prestige") == "restless spirits"
    assert theme.generator_name("tier1") == "haunted portrait"
    assert theme.generator_name("tier2") == "poltergeist parlor"
    assert theme.upgrade_name("boost1") == "midnight candles"
    assert theme.upgrades["boost1"].target == "tier1"
    assert theme.upgrades["boost2"].target == "tier2"
    assert theme.prestige.currency == "prestige"
    assert theme.prestige.measures == "primary"
    assert theme.prestige.action_name == "hold a séance"


def test_deep_sea_station_nouns_resolve():
    theme = load_theme(DEEP_SEA_STATION)
    assert theme.theme_id == "deep-sea-station"
    assert theme.name == "Deep-Sea Station"
    assert theme.currency_name("primary") == "pearls"
    assert theme.currency_name("prestige") == "abyssal relics"
    assert theme.generator_name("tier1") == "oyster bed"
    assert theme.generator_name("tier2") == "submersible drone"
    assert theme.upgrade_name("boost1") == "plankton drip line"
    assert theme.upgrades["boost1"].target == "tier1"
    assert theme.upgrades["boost2"].target == "tier2"
    assert theme.prestige.currency == "prestige"
    assert theme.prestige.measures == "primary"
    assert theme.prestige.action_name == "surface and resupply"


def test_dragon_hoard_nouns_resolve():
    theme = load_theme(DRAGON_HOARD)
    assert theme.theme_id == "dragon-hoard"
    assert theme.name == "Dragon Hoard"
    assert theme.currency_name("primary") == "gold coins"
    assert theme.currency_name("prestige") == "ancient scales"
    assert theme.generator_name("tier1") == "kobold miner"
    assert theme.generator_name("tier2") == "tribute village"
    assert theme.upgrade_name("boost1") == "sharper pickaxes"
    assert theme.upgrades["boost1"].target == "tier1"
    assert theme.upgrades["boost2"].target == "tier2"
    assert theme.prestige.currency == "prestige"
    assert theme.prestige.measures == "primary"
    assert theme.prestige.action_name == "burn it all and fly on"


def test_wizard_tower_nouns_resolve():
    theme = load_theme(WIZARD_TOWER)
    assert theme.theme_id == "wizard-tower"
    assert theme.name == "Wizard Tower"
    assert theme.currency_name("primary") == "mana"
    assert theme.currency_name("prestige") == "crystallized starlight"
    assert theme.generator_name("tier1") == "apprentice scribe"
    assert theme.generator_name("tier2") == "enchanted library"
    assert theme.upgrade_name("boost1") == "self-inking quills"
    assert theme.upgrades["boost1"].target == "tier1"
    assert theme.upgrades["boost2"].target == "tier2"
    assert theme.prestige.currency == "prestige"
    assert theme.prestige.measures == "primary"
    assert theme.prestige.action_name == "ascend to the astral plane"


def test_royal_bakery_nouns_resolve():
    theme = load_theme(ROYAL_BAKERY)
    assert theme.theme_id == "royal-bakery"
    assert theme.name == "Royal Bakery"
    assert theme.currency_name("primary") == "pastries"
    assert theme.currency_name("prestige") == "royal seals"
    assert theme.generator_name("tier1") == "sourdough starter"
    assert theme.generator_name("tier2") == "brick oven"
    assert theme.upgrade_name("boost1") == "stone-ground flour"
    assert theme.upgrades["boost1"].target == "tier1"
    assert theme.upgrades["boost2"].target == "tier2"
    assert theme.prestige.currency == "prestige"
    assert theme.prestige.measures == "primary"
    assert theme.prestige.action_name == "open a new royal franchise"


def test_cyber_city_nouns_resolve():
    theme = load_theme(CYBER_CITY)
    assert theme.theme_id == "cyber-city"
    assert theme.name == "Cyber City"
    assert theme.currency_name("primary") == "credits"
    assert theme.currency_name("prestige") == "legacy code fragments"
    assert theme.generator_name("tier1") == "data haven"
    assert theme.generator_name("tier2") == "courier drone swarm"
    assert theme.upgrade_name("boost1") == "cryo-coolant overclock"
    assert theme.upgrades["boost1"].target == "tier1"
    assert theme.upgrades["boost2"].target == "tier2"
    assert theme.prestige.currency == "prestige"
    assert theme.prestige.measures == "primary"
    assert theme.prestige.action_name == "upload your consciousness"


def test_pirate_cove_nouns_resolve():
    theme = load_theme(PIRATE_COVE)
    assert theme.theme_id == "pirate-cove"
    assert theme.name == "Pirate Cove"
    assert theme.currency_name("primary") == "doubloons"
    assert theme.currency_name("prestige") == "cursed relics"
    assert theme.generator_name("tier1") == "smuggler skiff"
    assert theme.generator_name("tier2") == "tavern crew"
    assert theme.upgrade_name("boost1") == "patched black sails"
    assert theme.upgrades["boost1"].target == "tier1"
    assert theme.upgrades["boost2"].target == "tier2"
    assert theme.prestige.currency == "prestige"
    assert theme.prestige.measures == "primary"
    assert theme.prestige.action_name == "bury the treasure and set sail"


def test_ant_colony_nouns_resolve():
    theme = load_theme(ANT_COLONY)
    assert theme.theme_id == "ant-colony"
    assert theme.name == "Ant Colony"
    assert theme.currency_name("primary") == "crumbs"
    assert theme.currency_name("prestige") == "royal jelly"
    assert theme.generator_name("tier1") == "forager trail"
    assert theme.generator_name("tier2") == "fungus garden"
    assert theme.upgrade_name("boost1") == "stronger pheromone markers"
    assert theme.upgrades["boost1"].target == "tier1"
    assert theme.upgrades["boost2"].target == "tier2"
    assert theme.prestige.currency == "prestige"
    assert theme.prestige.measures == "primary"
    assert theme.prestige.action_name == "crown a new queen"


def test_idol_agency_nouns_resolve():
    theme = load_theme(IDOL_AGENCY)
    assert theme.theme_id == "idol-agency"
    assert theme.name == "Idol Agency"
    assert theme.currency_name("primary") == "fans"
    assert theme.currency_name("prestige") == "platinum records"
    assert theme.generator_name("tier1") == "practice room"
    assert theme.generator_name("tier2") == "livestream studio"
    assert theme.upgrade_name("boost1") == "guest choreography coach"
    assert theme.upgrades["boost1"].target == "tier1"
    assert theme.upgrades["boost2"].target == "tier2"
    assert theme.prestige.currency == "prestige"
    assert theme.prestige.measures == "primary"
    assert theme.prestige.action_name == "graduate and debut a new group"


# --- every pack drives the engine end to end ---------------------------------


@pytest.mark.parametrize("pack", ALL_PACKS, ids=lambda p: p.stem)
def test_pack_drives_engine_full_cycle(pack):
    theme = load_theme(pack)
    gen_specs = theme.generator_specs()
    upgrade_specs = theme.upgrade_specs()
    prestige_spec = theme.prestige_spec()
    assert prestige_spec is not None

    first_upgrade = upgrade_specs[0]
    target = next(s for s in gen_specs if s.spec_id == first_upgrade.target)

    # tick: 60s on one target generator earns exactly the level-0 cost
    # (economy v0: base_cost = base_rate * 60s, same curve for every theme)
    state = GameState(owned={target.spec_id: 1}, last_seen=0)
    state = tick(state, gen_specs, 60, upgrade_specs=upgrade_specs)
    assert state.balances[target.produces] == first_upgrade.base_cost

    # upgrade: purchase spends exactly, levels up
    state = purchase_upgrade(state, first_upgrade)
    assert state.upgrades == {first_upgrade.spec_id: 1}
    assert state.balances[target.produces] == 0

    # prestige: grind to the threshold, reset, prestige currency awarded
    state = tick(state, gen_specs, 200_000, upgrade_specs=upgrade_specs)
    assert prestige_eligible(state, prestige_spec)
    after = apply_prestige(state, prestige_spec)
    assert after.prestige.get(prestige_spec.awards, 0) >= 1
    assert after.owned == {} and after.upgrades == {} and after.balances == {}


@pytest.mark.parametrize("pack", ALL_PACKS, ids=lambda p: p.stem)
def test_pack_specs_carry_no_display_data(pack):
    theme = load_theme(pack)
    for spec in (
        theme.generator_specs() + theme.upgrade_specs() + [theme.prestige_spec()]
    ):
        assert not hasattr(spec, "name")
        assert not hasattr(spec, "emoji")
        assert not hasattr(spec, "description")


# --- cross-pack theme.id uniqueness (per-file validation can't see this) -----


def test_catalog_errors_unit():
    assert catalog_errors({}) == []
    assert catalog_errors({Path("a.yaml"): "one", Path("b.yaml"): "two"}) == []
    errors = catalog_errors(
        {Path("a.yaml"): "one", Path("b.yaml"): "one", Path("c.yaml"): "two"}
    )
    assert len(errors) == 1
    assert "'one'" in errors[0]
    assert "a.yaml" in errors[0] and "b.yaml" in errors[0]
    assert "c.yaml" not in errors[0]


def test_duplicate_theme_id_via_stem_twins_reds_gate(tmp_path, capsys):
    # With id == filename stem enforced per file, two packs claiming one id
    # can only BOTH pass per-file as `.yaml`/`.yml` stem twins — exactly the
    # hole the catalog-level check still covers, end to end.
    src = EGG_FARM.read_text(encoding="utf-8")
    (tmp_path / "egg-farm.yaml").write_text(src, encoding="utf-8")
    (tmp_path / "egg-farm.yml").write_text(
        src.replace("name: Egg Farm", "name: Other Skin"), encoding="utf-8"
    )
    assert main(["theme_gate", str(tmp_path)]) == 1
    out = capsys.readouterr().out
    assert "duplicate theme.id" in out
    assert "'egg-farm'" in out


def test_duplicate_theme_id_under_wrong_filename_reds_per_file(tmp_path, capsys):
    # The pre-stem-rule collision shape (same id, different .yaml filename)
    # now reds EARLIER, at the per-file stem check — never reaching main green.
    src = EGG_FARM.read_text(encoding="utf-8")
    (tmp_path / "egg-farm.yaml").write_text(src, encoding="utf-8")
    (tmp_path / "impostor.yaml").write_text(
        src.replace("name: Egg Farm", "name: Other Skin"), encoding="utf-8"
    )
    assert main(["theme_gate", str(tmp_path)]) == 1
    assert "filename stem" in capsys.readouterr().out


def test_distinct_theme_ids_pass_cross_pack_check(tmp_path, capsys):
    src = EGG_FARM.read_text(encoding="utf-8")
    (tmp_path / "egg-farm.yaml").write_text(src, encoding="utf-8")
    (tmp_path / "other-skin.yaml").write_text(
        src.replace("id: egg-farm", "id: other-skin"), encoding="utf-8"
    )
    assert main(["theme_gate", str(tmp_path)]) == 0
    assert "duplicate theme.id" not in capsys.readouterr().out


def test_invalid_pack_does_not_join_cross_pack_check(tmp_path, capsys):
    src = EGG_FARM.read_text(encoding="utf-8")
    (tmp_path / "egg-farm.yaml").write_text(src, encoding="utf-8")
    # a stem twin with the same theme.id but schema-invalid: per-file failure
    # must not also produce a spurious catalog-level duplicate
    (tmp_path / "egg-farm.yml").write_text(
        src.replace('embed_color: "#F5C542"', 'embed_color: "gold"'),
        encoding="utf-8",
    )
    assert main(["theme_gate", str(tmp_path)]) == 1
    out = capsys.readouterr().out
    assert "embed_color" in out
    assert "duplicate theme.id" not in out
