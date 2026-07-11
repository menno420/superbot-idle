"""Theme catalog (slice (c)): schema v1 proven on foreign content.

Two packs the schema was NOT designed around — space-colony and
potion-brewery — must fill every slot egg-farm fills, load through the
engine's theme loader, and drive the full engine cycle (tick, upgrade
purchase, prestige reset) with their own nouns. Plus the catalog-level
check per-file validation cannot see: cross-pack `theme.id` uniqueness.
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


# --- the catalog ships three packs, all gate-green ---------------------------


def test_catalog_ships_the_slice_c_packs():
    assert SPACE_COLONY in ALL_PACKS and POTION_BREWERY in ALL_PACKS
    assert len(ALL_PACKS) >= 3


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


def test_duplicate_theme_id_across_packs_reds_gate(tmp_path, capsys):
    src = EGG_FARM.read_text(encoding="utf-8")
    (tmp_path / "a.yaml").write_text(src, encoding="utf-8")
    # a second pack, individually valid, claiming the SAME theme.id
    (tmp_path / "b.yaml").write_text(
        src.replace("name: Egg Farm", "name: Other Skin"), encoding="utf-8"
    )
    assert main(["theme_gate", str(tmp_path)]) == 1
    out = capsys.readouterr().out
    assert "duplicate theme.id" in out
    assert "'egg-farm'" in out


def test_distinct_theme_ids_pass_cross_pack_check(tmp_path, capsys):
    src = EGG_FARM.read_text(encoding="utf-8")
    (tmp_path / "a.yaml").write_text(src, encoding="utf-8")
    (tmp_path / "b.yaml").write_text(
        src.replace("id: egg-farm", "id: other-skin"), encoding="utf-8"
    )
    assert main(["theme_gate", str(tmp_path)]) == 0
    assert "duplicate theme.id" not in capsys.readouterr().out


def test_invalid_pack_does_not_join_cross_pack_check(tmp_path, capsys):
    src = EGG_FARM.read_text(encoding="utf-8")
    (tmp_path / "a.yaml").write_text(src, encoding="utf-8")
    # same theme.id but schema-invalid: per-file failure must not also
    # produce a spurious catalog-level duplicate
    (tmp_path / "b.yaml").write_text(
        src.replace('embed_color: "#F5C542"', 'embed_color: "gold"'),
        encoding="utf-8",
    )
    assert main(["theme_gate", str(tmp_path)]) == 1
    out = capsys.readouterr().out
    assert "embed_color" in out
    assert "duplicate theme.id" not in out
