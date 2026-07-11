"""Upgrades + prestige: purchase math, effect application (tick AND offline),
prestige award determinism, reset semantics, multiplier persistence.

Written test-first for slice (b). Tests use OPAQUE ids ("primary", "tier1",
"boost1", "meta") plus the real egg-farm theme where noun mapping matters —
the engine itself never sees a theme noun. All economy numbers asserted here
are the pre-registered PROVISIONAL parameters from
docs/design/upgrades-prestige-v0.md.
"""

from pathlib import Path

import pytest

from idle_engine import (
    GameState,
    GeneratorSpec,
    PrestigeSpec,
    UpgradeSpec,
    apply_prestige,
    load_theme,
    offline_progress,
    prestige_award,
    prestige_eligible,
    production_per_second,
    purchase_upgrade,
    tick,
    upgrade_cost,
)
from idle_engine import economy
from idle_engine.engine import apply_offline_progress

REPO_ROOT = Path(__file__).resolve().parent.parent

SPECS = [
    GeneratorSpec(spec_id="tier1", produces="primary", base_rate=3),
    GeneratorSpec(spec_id="tier2", produces="primary", base_rate=7),
]

# +25%/level on tier1, geometric cost 180 * (115/100)^level in "primary".
UPGRADE = UpgradeSpec(
    spec_id="boost1",
    cost_currency="primary",
    base_cost=180,
    cost_growth_num=115,
    cost_growth_den=100,
    target="tier1",
    effect_percent=25,
)

# Prestige currency "meta": threshold 100k lifetime "primary",
# award isqrt(lifetime // 100k), +10% global per unit held.
PRESTIGE = PrestigeSpec(
    awards="meta",
    measures="primary",
    threshold=100_000,
    award_divisor=100_000,
    bonus_percent=10,
)


def make_state(**kwargs) -> GameState:
    kwargs.setdefault("last_seen", 1_000)
    return GameState(**kwargs)


# --- upgrade purchase math ---------------------------------------------------


def test_upgrade_cost_curve_is_integer_exact_geometric():
    assert upgrade_cost(UPGRADE, 0) == 180
    assert upgrade_cost(UPGRADE, 1) == 207  # 180 * 115 // 100
    assert upgrade_cost(UPGRADE, 2) == 238  # 180 * 115^2 // 100^2 (floor)
    assert upgrade_cost(UPGRADE, 10) == 180 * 115**10 // 100**10
    costs = [upgrade_cost(UPGRADE, level) for level in range(50)]
    assert costs == sorted(costs)  # growth >= 1 -> monotonic non-decreasing
    assert all(isinstance(c, int) for c in costs)


def test_purchase_spends_and_levels_up():
    state = make_state(balances={"primary": 200}, owned={"tier1": 1})
    after = purchase_upgrade(state, UPGRADE)
    assert after.balances["primary"] == 20
    assert after.upgrades == {"boost1": 1}
    # purity: the input state is never mutated
    assert state.balances["primary"] == 200
    assert state.upgrades == {}


def test_purchase_insufficient_funds_rejected():
    state = make_state(balances={"primary": 179}, owned={"tier1": 1})
    with pytest.raises(ValueError):
        purchase_upgrade(state, UPGRADE)
    # level 1 costs 207: 200 was enough for level 0 only
    state = purchase_upgrade(make_state(balances={"primary": 200}), UPGRADE)
    with pytest.raises(ValueError):
        purchase_upgrade(state, UPGRADE)


def test_purchase_does_not_touch_lifetime():
    state = make_state(balances={"primary": 500}, lifetime={"primary": 500})
    after = purchase_upgrade(state, UPGRADE)
    assert after.lifetime == {"primary": 500}  # spending is not un-earning


# --- effects applied in tick -------------------------------------------------


def test_upgrade_effect_applies_in_tick():
    # tier1: 4 * 3 = 12/s base; one +25% level -> 12 * 125 // 100 = 15/s
    state = make_state(owned={"tier1": 4}, upgrades={"boost1": 1})
    rates = production_per_second(state, SPECS, upgrade_specs=[UPGRADE])
    assert rates == {"primary": 15}
    after = tick(state, SPECS, 10, upgrade_specs=[UPGRADE])
    assert after.balances["primary"] == 150


def test_upgrade_effect_targets_only_its_generator():
    # tier2 is untargeted: stays at base 7/s regardless of boost1 level
    state = make_state(owned={"tier2": 1}, upgrades={"boost1": 5})
    rates = production_per_second(state, SPECS, upgrade_specs=[UPGRADE])
    assert rates == {"primary": 7}


def test_tick_accrues_lifetime_alongside_balances():
    state = make_state(owned={"tier1": 2})  # 6/s
    after = tick(state, SPECS, 100)
    assert after.balances["primary"] == 600
    assert after.lifetime["primary"] == 600


def test_no_upgrades_is_backward_compatible():
    state = make_state(owned={"tier1": 2, "tier2": 1})  # 13/s
    assert production_per_second(state, SPECS) == {"primary": 13}
    assert tick(state, SPECS, 5).balances["primary"] == 65


# --- effects applied in offline path, identical to tick ----------------------


def test_offline_progress_with_upgrades_and_prestige_equals_looped_ticks():
    state = make_state(
        owned={"tier1": 5, "tier2": 2},
        upgrades={"boost1": 3},          # tier1 pct = 100 + 75 = 175
        prestige={"meta": 2},            # global pct = 100 + 20 = 120
    )
    last_seen, now = 1_000, 1_000 + 3_607  # awkward, non-round span
    closed_form = offline_progress(
        state, SPECS, last_seen, now,
        upgrade_specs=[UPGRADE], prestige_specs=[PRESTIGE],
    )
    looped = state
    for _ in range(now - last_seen):
        looped = tick(looped, SPECS, 1, upgrade_specs=[UPGRADE], prestige_specs=[PRESTIGE])
    assert closed_form == looped.balances
    applied = apply_offline_progress(
        state, SPECS, now, upgrade_specs=[UPGRADE], prestige_specs=[PRESTIGE]
    )
    assert applied.balances == looped.balances
    assert applied.lifetime == looped.lifetime
    assert applied.last_seen == now


def test_multiplier_math_floors_once_per_generator_per_second():
    # tier1: 15 base * 175 * 120 // 10000 = 31 (31.5 floored)
    # tier2: 14 base * 100 * 120 // 10000 = 16 (16.8 floored)
    state = make_state(
        owned={"tier1": 5, "tier2": 2}, upgrades={"boost1": 3}, prestige={"meta": 2}
    )
    rates = production_per_second(
        state, SPECS, upgrade_specs=[UPGRADE], prestige_specs=[PRESTIGE]
    )
    assert rates == {"primary": 47}


# --- prestige: eligibility, award determinism, reset semantics ----------------


def test_prestige_eligibility_threshold():
    below = make_state(lifetime={"primary": 99_999})
    at = make_state(lifetime={"primary": 100_000})
    assert not prestige_eligible(below, PRESTIGE)
    assert prestige_eligible(at, PRESTIGE)
    with pytest.raises(ValueError):
        apply_prestige(below, PRESTIGE)


@pytest.mark.parametrize(
    "lifetime, award",
    [
        (100_000, 1),      # isqrt(1)
        (399_999, 1),      # isqrt(3)
        (400_000, 2),      # isqrt(4)
        (1_000_000, 3),    # isqrt(10)
        (10_000_000, 10),  # isqrt(100)
    ],
)
def test_prestige_award_is_deterministic_isqrt(lifetime, award):
    state = make_state(lifetime={"primary": lifetime})
    assert prestige_award(state, PRESTIGE) == award
    assert prestige_award(state, PRESTIGE) == award  # repeatable, no hidden state


def test_apply_prestige_resets_run_and_keeps_prestige():
    state = make_state(
        balances={"primary": 12_345},
        owned={"tier1": 9, "tier2": 4},
        upgrades={"boost1": 6},
        lifetime={"primary": 400_000},
        prestige={"meta": 1},
        last_seen=77_777,
    )
    after = apply_prestige(state, PRESTIGE)
    assert after.balances == {}
    assert after.owned == {}
    assert after.upgrades == {}
    assert after.lifetime == {}
    assert after.prestige == {"meta": 3}  # 1 held + isqrt(4) awarded
    assert after.last_seen == 77_777  # wall-clock anchor survives the reset
    # purity: the input state is never mutated
    assert state.prestige == {"meta": 1} and state.balances["primary"] == 12_345


def test_prestige_multiplier_persists_after_reset_in_tick_and_offline():
    pre = make_state(lifetime={"primary": 100_000}, owned={"tier1": 1})
    post = apply_prestige(pre, PRESTIGE)  # holds 1 meta -> +10% global
    post = GameState(
        balances={}, owned={"tier1": 10}, last_seen=post.last_seen,
        upgrades={}, lifetime={}, prestige=post.prestige,
    )
    # 10 * 3 = 30/s base -> 30 * 100 * 110 // 10000 = 33/s
    ticked = tick(post, SPECS, 100, prestige_specs=[PRESTIGE])
    assert ticked.balances["primary"] == 3_300
    offline = offline_progress(
        post, SPECS, post.last_seen, post.last_seen + 100, prestige_specs=[PRESTIGE]
    )
    assert offline == {"primary": 3_300}


def test_prestige_full_cycle_determinism():
    def run() -> tuple:
        state = make_state(owned={"tier1": 40, "tier2": 30})  # 330/s
        state = tick(state, SPECS, 400)  # lifetime 132_000 >= threshold
        state = apply_prestige(state, PRESTIGE)
        state = GameState(
            balances=state.balances, owned={"tier1": 40, "tier2": 30},
            last_seen=state.last_seen, upgrades=state.upgrades,
            lifetime=state.lifetime, prestige=state.prestige,
        )
        state = tick(state, SPECS, 1_000, prestige_specs=[PRESTIGE])
        return (tuple(sorted(state.balances.items())),
                tuple(sorted(state.prestige.items())), state.last_seen)

    assert run() == run() == run()


# --- spec validation ----------------------------------------------------------


def test_invalid_specs_rejected():
    with pytest.raises((TypeError, ValueError)):
        UpgradeSpec(
            spec_id="x", cost_currency="c", base_cost=0,
            cost_growth_num=115, cost_growth_den=100, target="g", effect_percent=25,
        )
    with pytest.raises((TypeError, ValueError)):
        UpgradeSpec(
            spec_id="x", cost_currency="c", base_cost=10,
            cost_growth_num=99, cost_growth_den=100, target="g", effect_percent=25,
        )  # shrinking costs are a balance exploit
    with pytest.raises((TypeError, ValueError)):
        PrestigeSpec(
            awards="m", measures="p", threshold=50, award_divisor=100, bonus_percent=10
        )  # threshold < divisor could award 0 on an eligible reset


# --- theme wiring: every new noun comes from the pack -------------------------


def test_egg_farm_supplies_upgrade_and_prestige_nouns():
    theme = load_theme(REPO_ROOT / "themes" / "egg-farm.yaml")
    upgrade = theme.upgrades["boost1"]
    assert upgrade.name == "bigger henhouse"
    assert upgrade.target == "tier1"
    assert upgrade.emoji and upgrade.description
    assert theme.upgrade_name("boost1") == "bigger henhouse"
    assert theme.prestige is not None
    assert theme.prestige.currency == "prestige"
    assert theme.prestige.measures == "primary"
    assert theme.currency_name("prestige") == "golden eggs"
    assert theme.prestige.action_name == "sell the farm"
    assert theme.prestige.action_description and theme.prestige.action_emoji


def test_theme_builds_engine_specs_from_preregistered_economy():
    theme = load_theme(REPO_ROOT / "themes" / "egg-farm.yaml")
    (spec,) = theme.upgrade_specs()
    assert spec.spec_id == "boost1"
    assert spec.target == "tier1"
    assert spec.cost_currency == "primary"
    # PROVISIONAL pre-registered parameters (docs/design/upgrades-prestige-v0.md)
    assert spec.base_cost == 1 * economy.UPGRADE_BASE_COST_SECONDS == 60
    assert (spec.cost_growth_num, spec.cost_growth_den) == (115, 100)
    assert spec.effect_percent == 25
    prestige = theme.prestige_spec()
    assert prestige is not None
    assert prestige.awards == "prestige"
    assert prestige.measures == "primary"
    assert prestige.threshold == 100_000
    assert prestige.award_divisor == 100_000
    assert prestige.bonus_percent == 10
    # specs carry ZERO display data — the core/skin seam
    for engine_side in (spec, prestige):
        assert not hasattr(engine_side, "name")
        assert not hasattr(engine_side, "emoji")


def test_engine_end_to_end_on_theme_specs():
    theme = load_theme(REPO_ROOT / "themes" / "egg-farm.yaml")
    gen_specs = theme.generator_specs()
    upgrade_specs = theme.upgrade_specs()
    prestige_spec = theme.prestige_spec()
    state = GameState(owned={"tier1": 1}, last_seen=0)
    state = tick(state, gen_specs, 60, upgrade_specs=upgrade_specs)
    assert state.balances["primary"] == 60  # enough for the level-0 upgrade
    state = purchase_upgrade(state, upgrade_specs[0])
    assert state.upgrades == {"boost1": 1}
    assert state.balances["primary"] == 0
    assert state.lifetime["primary"] == 60
    # 1 * 1 * 125 * 100 // 10000 = 1/s still (integer floor at tiny scale)
    state = tick(state, gen_specs, 100_000, upgrade_specs=upgrade_specs)
    assert prestige_eligible(state, prestige_spec)
    after = apply_prestige(state, prestige_spec)
    assert after.prestige == {"prestige": 1}
    assert after.owned == {} and after.upgrades == {}


# --- theme loader rejects broken upgrade/prestige wiring ----------------------


def test_loader_rejects_dangling_upgrade_target(tmp_path):
    src = (REPO_ROOT / "themes" / "egg-farm.yaml").read_text(encoding="utf-8")
    broken = src.replace("target: tier1", "target: nonexistent")
    path = tmp_path / "broken.yaml"
    path.write_text(broken, encoding="utf-8")
    with pytest.raises(ValueError, match="not a declared generator"):
        load_theme(path)


def test_loader_rejects_prestige_measuring_undeclared_currency(tmp_path):
    src = (REPO_ROOT / "themes" / "egg-farm.yaml").read_text(encoding="utf-8")
    broken = src.replace("measures: primary", "measures: nonexistent")
    path = tmp_path / "broken.yaml"
    path.write_text(broken, encoding="utf-8")
    with pytest.raises(ValueError, match="not a declared currency"):
        load_theme(path)


def test_loader_rejects_prestige_currency_equal_to_measures(tmp_path):
    src = (REPO_ROOT / "themes" / "egg-farm.yaml").read_text(encoding="utf-8")
    broken = src.replace("measures: primary", "measures: prestige")
    path = tmp_path / "broken.yaml"
    path.write_text(broken, encoding="utf-8")
    with pytest.raises(ValueError, match="must differ"):
        load_theme(path)
