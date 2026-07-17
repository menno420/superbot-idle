"""Defensive-guard edge cases for the idle engine's pure-domain math.

Every engine module raises on a corrupt ``GameState`` rather than
computing on it — a negative owned count, a negative upgrade level, a
negative prestige balance, or a non-int spec field must fail loud, not
produce a negative rate or award. Those guards are load-bearing (the
persistence loader is the other wall around the same no-negative
invariant), but the suite exercised the values that pass them far more
than the values that trip them. This module pins the reject side of
every guard, plus the ``0`` boundary that must be ACCEPTED, so the exact
accept/reject line is documented and a regression that drops a guard
turns red.

Sb-free by construction: opaque ids only (``"tier1"``, ``"meta"``), no
theme nouns, no host import — ``python3 -m pytest -q`` passes standalone.
"""

import pytest

from idle_engine import (
    GameState,
    GeneratorSpec,
    PrestigeSpec,
    UpgradeSpec,
    prestige_award,
    production_per_second,
)
from idle_engine.prestige import prestige_percent
from idle_engine.upgrades import upgrade_percent

SPEC = GeneratorSpec(spec_id="tier1", produces="primary", base_rate=3)


def _upgrade(**over) -> UpgradeSpec:
    kwargs = dict(
        spec_id="boost1",
        cost_currency="primary",
        base_cost=180,
        cost_growth_num=115,
        cost_growth_den=100,
        target="tier1",
        effect_percent=25,
    )
    kwargs.update(over)
    return UpgradeSpec(**kwargs)


def _prestige(**over) -> PrestigeSpec:
    kwargs = dict(
        awards="meta",
        measures="primary",
        threshold=100_000,
        award_divisor=100_000,
        bonus_percent=10,
    )
    kwargs.update(over)
    return PrestigeSpec(**kwargs)


# --- GeneratorSpec.base_rate: the type guard (the < 0 twin was pinned) --------


@pytest.mark.parametrize("bad", [1.5, "3", True, None])
def test_generator_spec_rejects_non_int_base_rate(bad):
    with pytest.raises(TypeError):
        GeneratorSpec(spec_id="x", produces="y", base_rate=bad)


def test_generator_spec_accepts_zero_base_rate():
    # 0 is the accepted boundary: a valid (if inert) generator, not an error.
    spec = GeneratorSpec(spec_id="x", produces="y", base_rate=0)
    assert spec.base_rate == 0


# --- production_per_second: a negative owned count fails before any rate ------


def test_production_rejects_negative_owned_count():
    state = GameState(owned={"tier1": -1}, last_seen=0)
    with pytest.raises(ValueError, match="owned count"):
        production_per_second(state, [SPEC])


def test_production_accepts_zero_owned_count():
    # count == 0 passes the guard and simply contributes no rate.
    state = GameState(owned={"tier1": 0}, last_seen=0)
    assert production_per_second(state, [SPEC]) == {}


# --- PrestigeSpec field guards: type (non-int) and range (below minimum) ------


@pytest.mark.parametrize(
    "field", ["threshold", "award_divisor", "bonus_percent"]
)
def test_prestige_spec_rejects_non_int_field(field):
    with pytest.raises(TypeError):
        _prestige(**{field: 1.5})


def test_prestige_spec_rejects_bool_field():
    # bool is an int subclass; the guard must still reject it.
    with pytest.raises(TypeError):
        _prestige(threshold=True)


@pytest.mark.parametrize(
    "field,value",
    [("threshold", 0), ("award_divisor", 0), ("bonus_percent", -1)],
)
def test_prestige_spec_rejects_below_minimum(field, value):
    with pytest.raises(ValueError):
        _prestige(**{field: value})


def test_prestige_spec_accepts_zero_bonus_percent():
    # bonus_percent floor is 0 (a neutral track), not 1.
    assert _prestige(bonus_percent=0).bonus_percent == 0


# --- prestige_award / prestige_percent: negative-balance guards ---------------


def test_prestige_award_rejects_negative_lifetime():
    state = GameState(lifetime={"primary": -5}, last_seen=0)
    with pytest.raises(ValueError, match="must be >= 0"):
        prestige_award(state, _prestige())


def test_prestige_percent_rejects_negative_balance():
    state = GameState(prestige={"meta": -1}, last_seen=0)
    with pytest.raises(ValueError, match="prestige balance"):
        prestige_percent(state, [_prestige()])


def test_prestige_percent_additive_across_multiple_specs():
    # 100 + 10*2 + 5*3 == 135: additive across every held track.
    state = GameState(prestige={"meta": 2, "meta2": 3}, last_seen=0)
    specs = [_prestige(awards="meta", bonus_percent=10),
             _prestige(awards="meta2", bonus_percent=5)]
    assert prestige_percent(state, specs) == 135


# --- upgrade_percent: a negative stored level fails loud ----------------------


def test_upgrade_percent_rejects_negative_level():
    state = GameState(upgrades={"boost1": -1}, last_seen=0)
    with pytest.raises(ValueError, match="upgrade level"):
        upgrade_percent(state, [_upgrade()], "tier1")


def test_upgrade_percent_zero_level_is_neutral():
    # No level owned -> exactly x1 (100%), the accepted boundary.
    state = GameState(last_seen=0)
    assert upgrade_percent(state, [_upgrade()], "tier1") == 100
