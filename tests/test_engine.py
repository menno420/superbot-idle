"""Engine mechanics: tick accrual, offline progress, determinism.

Tests deliberately use OPAQUE ids ("primary", "tier1") plus the real
egg-farm theme where noun mapping matters — the engine itself never
sees a theme noun.
"""

from pathlib import Path

import pytest

from idle_engine import (
    GameState,
    GeneratorSpec,
    load_theme,
    offline_progress,
    production_per_second,
    tick,
)
from idle_engine.engine import apply_offline_progress

REPO_ROOT = Path(__file__).resolve().parent.parent

SPECS = [
    GeneratorSpec(spec_id="tier1", produces="primary", base_rate=3),
    GeneratorSpec(spec_id="tier2", produces="primary", base_rate=7),
]


def make_state(**owned: int) -> GameState:
    return GameState(balances={}, owned=owned, last_seen=1_000)


def test_tick_accrues_over_n_ticks():
    state = make_state(tier1=2, tier2=1)  # 2*3 + 1*7 = 13/sec
    n, dt = 10, 5
    for _ in range(n):
        state = tick(state, SPECS, dt)
    assert state.balances["primary"] == 13 * dt * n == 650
    assert state.last_seen == 1_000 + dt * n


def test_tick_zero_dt_and_zero_owned_accrue_nothing():
    state = make_state(tier1=4)
    assert sum(tick(state, SPECS, 0).balances.values()) == 0
    assert tick(make_state(), SPECS, 100).balances == {}


def test_tick_is_pure_and_does_not_mutate_input():
    state = make_state(tier1=1)
    tick(state, SPECS, 60)
    assert state.balances == {}
    assert state.last_seen == 1_000


def test_offline_progress_equals_looped_ticks():
    state = make_state(tier1=5, tier2=2)
    last_seen, now = 1_000, 1_000 + 3_607  # awkward, non-round span
    closed_form = offline_progress(state, SPECS, last_seen, now)
    looped = state
    for _ in range(now - last_seen):
        looped = tick(looped, SPECS, 1)
    assert closed_form == looped.balances
    applied = apply_offline_progress(state, SPECS, now)
    assert applied.balances == looped.balances
    assert applied.last_seen == now


def test_offline_progress_clock_skew_accrues_nothing():
    state = make_state(tier1=9)
    assert offline_progress(state, SPECS, 5_000, 4_000) == {"primary": 0}


def test_determinism_repeat_runs_identical():
    def run() -> tuple:
        state = make_state(tier1=3, tier2=4)
        for step in (1, 17, 300, 4):
            state = tick(state, SPECS, step)
        earned = offline_progress(state, SPECS, state.last_seen, state.last_seen + 86_400)
        return (tuple(sorted(state.balances.items())), state.last_seen,
                tuple(sorted(earned.items())))

    assert run() == run() == run()


def test_production_rates_are_integer_exact():
    state = make_state(tier1=1_000_000)
    rates = production_per_second(state, SPECS)
    assert rates == {"primary": 3_000_000}
    assert all(isinstance(v, int) for v in rates.values())


def test_engine_runs_on_theme_supplied_specs():
    theme = load_theme(REPO_ROOT / "themes" / "egg-farm.yaml")
    specs = theme.generator_specs()
    (gen,) = specs
    state = GameState(balances={}, owned={gen.spec_id: 4}, last_seen=0)
    after = tick(state, specs, 60)
    assert after.balances[gen.produces] == gen.base_rate * 4 * 60


def test_invalid_inputs_rejected():
    state = make_state(tier1=1)
    with pytest.raises(ValueError):
        tick(state, SPECS, -1)
    with pytest.raises(TypeError):
        tick(state, SPECS, 1.5)
    with pytest.raises(TypeError):
        offline_progress(state, SPECS, 0.5, 10)
    with pytest.raises(ValueError):
        GeneratorSpec(spec_id="x", produces="y", base_rate=-1)
