"""Buy-max / bulk-purchase math: exact bulk cost, max-affordable, atomic
bulk purchase.

Written test-first for the buy-max slice. The math here is DERIVED from
the pre-registered curve shape (docs/design/upgrades-prestige-v0.md § Bulk
purchase math addendum) — no new economy numbers, no constants changed.

The load-bearing facts these tests pin:

1. The per-level cost floors independently (``base·num^L // den^L``), so
   a geometric-series closed form with ONE final floor is NOT exact —
   the exact bulk cost is the sum of the per-level floors, and a pinned
   case shows the naive closed form diverging (it over-charges, because
   the per-level floors each discard a fractional part the single final
   floor keeps).
2. ``max_affordable_levels`` is the exact argmax over the monotone bulk
   sum — property-tested against brute force — and stays fast at
   10^3000-scale budgets (no per-level linear scan).
3. ``purchase_upgrades`` is byte-identical to n sequential
   ``purchase_upgrade`` calls and atomic on insufficient funds (distinct
   error, zero partial spend).

Randomness is stdlib-only seeded ``random.Random`` per the house
property-test style — reproducible byte-for-byte, no hypothesis.
"""

import dataclasses
import json
import time
from pathlib import Path
from random import Random

import pytest

from idle_engine import (
    GameState,
    bulk_upgrade_cost,
    load_theme,
    max_affordable_levels,
    purchase_upgrade,
    purchase_upgrades,
    upgrade_cost,
)
from idle_engine.upgrades import BulkPurchaseError, UpgradeSpec

REPO_ROOT = Path(__file__).resolve().parent.parent

# The slice (b) test spec: geometric cost 180 * (115/100)^level in "primary".
UPGRADE = UpgradeSpec(
    spec_id="boost1",
    cost_currency="primary",
    base_cost=180,
    cost_growth_num=115,
    cost_growth_den=100,
    target="tier1",
    effect_percent=25,
)

# The real v0 curve at egg-farm scale: base 60, x1.15 (economy.py table).
V0_SPEC = UpgradeSpec(
    spec_id="boost1",
    cost_currency="primary",
    base_cost=60,
    cost_growth_num=115,
    cost_growth_den=100,
    target="tier1",
    effect_percent=25,
)

# Ratio exactly 1 (num == den is allowed: growth >= 1): every level costs base.
FLAT_SPEC = UpgradeSpec(
    spec_id="flat",
    cost_currency="primary",
    base_cost=7,
    cost_growth_num=100,
    cost_growth_den=100,
    target="tier1",
    effect_percent=25,
)


def _random_spec(rng: Random) -> UpgradeSpec:
    """A random valid spec in the property suite's parameter bands."""
    return UpgradeSpec(
        spec_id="up0",
        cost_currency="cur0",
        base_cost=rng.randint(1, 10_000),
        cost_growth_num=rng.randint(100, 130),
        cost_growth_den=100,
        target="gen0",
        effect_percent=rng.randint(1, 100),
    )


def _brute_sum(spec: UpgradeSpec, from_level: int, n: int) -> int:
    """Reference: literally sum the published per-level cost curve."""
    return sum(upgrade_cost(spec, from_level + k) for k in range(n))


def _canon(state: GameState) -> bytes:
    """Canonical byte serialization of a GameState (sorted keys)."""
    return json.dumps(
        {
            "balances": state.balances,
            "owned": state.owned,
            "last_seen": state.last_seen,
            "upgrades": state.upgrades,
            "lifetime": state.lifetime,
            "prestige": state.prestige,
            "milestones": state.milestones,
        },
        sort_keys=True,
        separators=(",", ":"),
    ).encode("ascii")


# --- 1. exact bulk cost --------------------------------------------------------


def test_bulk_cost_pinned_first_levels():
    # Per-level curve (slice (b) pins): 180, 207, 238, 273, 314 ...
    assert bulk_upgrade_cost(UPGRADE, 0, 1) == 180
    assert bulk_upgrade_cost(UPGRADE, 0, 2) == 180 + 207
    assert bulk_upgrade_cost(UPGRADE, 0, 3) == 180 + 207 + 238
    assert bulk_upgrade_cost(UPGRADE, 1, 2) == 207 + 238
    assert bulk_upgrade_cost(UPGRADE, 10, 1) == upgrade_cost(UPGRADE, 10)
    assert bulk_upgrade_cost(UPGRADE, 0, 0) == 0  # empty sum, exact


@pytest.mark.parametrize("seed", range(20))
def test_bulk_cost_equals_per_level_sum(seed):
    rng = Random(11_000 + seed)
    for _ in range(20):
        spec = _random_spec(rng)
        from_level = rng.randint(0, 60)
        n = rng.randint(0, 80)
        assert bulk_upgrade_cost(spec, from_level, n) == _brute_sum(
            spec, from_level, n
        )


def test_bulk_cost_naive_closed_form_is_unsound():
    """The pinned divergence: floors per level, NOT one floor at the end.

    Exact rational geometric series over the REAL v0 curve (base 60,
    x1.15), first 5 levels from level 0:

        naive = floor(60 * (115^5 - 100^5) / (100^4 * 15)) = 404
        exact = 60 + 69 + 79 + 91 + 104                    = 403

    The naive single-floor closed form keeps the fractional parts the
    per-level floors discard, so it OVER-charges — an engine that used it
    would spend currency the published per-level curve never asked for.
    """
    naive = (
        V0_SPEC.base_cost
        * (V0_SPEC.cost_growth_num**5 - V0_SPEC.cost_growth_den**5)
        // (
            V0_SPEC.cost_growth_den**4
            * (V0_SPEC.cost_growth_num - V0_SPEC.cost_growth_den)
        )
    )
    exact = bulk_upgrade_cost(V0_SPEC, 0, 5)
    assert [upgrade_cost(V0_SPEC, L) for L in range(5)] == [60, 69, 79, 91, 104]
    assert exact == 403
    assert naive == 404
    assert exact != naive  # the closed form with floors is unsound


def test_bulk_cost_ratio_one_is_flat_and_instant():
    # num == den -> every level costs exactly base; huge n must be O(1).
    assert bulk_upgrade_cost(FLAT_SPEC, 0, 10) == 70
    assert bulk_upgrade_cost(FLAT_SPEC, 5, 10**30) == 7 * 10**30


def test_bulk_cost_validation():
    with pytest.raises((TypeError, ValueError)):
        bulk_upgrade_cost(UPGRADE, -1, 3)
    with pytest.raises((TypeError, ValueError)):
        bulk_upgrade_cost(UPGRADE, 0, -1)
    with pytest.raises((TypeError, ValueError)):
        bulk_upgrade_cost(UPGRADE, 0, True)  # bools are not counts
    with pytest.raises((TypeError, ValueError)):
        bulk_upgrade_cost(UPGRADE, "0", 3)


def test_bulk_cost_is_deterministic():
    assert (
        bulk_upgrade_cost(UPGRADE, 3, 40)
        == bulk_upgrade_cost(UPGRADE, 3, 40)
        == _brute_sum(UPGRADE, 3, 40)
    )


# --- 2. max affordable levels ----------------------------------------------------


def test_max_affordable_pinned_boundaries():
    # Costs from level 0: 180, 207, 238 -> cumulative 180, 387, 625.
    assert max_affordable_levels(UPGRADE, 0, 0) == 0
    assert max_affordable_levels(UPGRADE, 0, 179) == 0
    assert max_affordable_levels(UPGRADE, 0, 180) == 1
    assert max_affordable_levels(UPGRADE, 0, 386) == 1
    assert max_affordable_levels(UPGRADE, 0, 387) == 2
    assert max_affordable_levels(UPGRADE, 0, 624) == 2
    assert max_affordable_levels(UPGRADE, 0, 625) == 3


@pytest.mark.parametrize("seed", range(20))
def test_max_affordable_matches_brute_force(seed):
    rng = Random(12_000 + seed)
    for _ in range(15):
        spec = _random_spec(rng)
        from_level = rng.randint(0, 40)
        # Budgets swept across the interesting range, including exact
        # cumulative sums and off-by-one neighbours (the floor seams).
        k = rng.randint(0, 30)
        exact_sum = _brute_sum(spec, from_level, k)
        for budget in (
            exact_sum - 1,
            exact_sum,
            exact_sum + 1,
            rng.randint(0, exact_sum + 1000),
        ):
            if budget < 0:
                continue
            brute = 0
            total = 0
            while True:
                cost = upgrade_cost(spec, from_level + brute)
                if total + cost > budget:
                    break
                total += cost
                brute += 1
            assert max_affordable_levels(spec, from_level, budget) == brute


@pytest.mark.parametrize("seed", range(10))
def test_max_affordable_is_the_exact_argmax(seed):
    """Definitional check: bulk(n) <= budget < bulk(n + 1)."""
    rng = Random(13_000 + seed)
    for _ in range(10):
        spec = _random_spec(rng)
        from_level = rng.randint(0, 40)
        budget = rng.randint(0, 10**12)
        n = max_affordable_levels(spec, from_level, budget)
        assert bulk_upgrade_cost(spec, from_level, n) <= budget
        assert bulk_upgrade_cost(spec, from_level, n + 1) > budget


def test_max_affordable_huge_budget_completes_fast():
    """10^3000-scale budget: exponential search + bisect, never a
    per-level scan (a per-level scan with ~49k pow-evaluations would take
    tens of minutes; the bound is generous purely to keep CI honest)."""
    budget = 10**3000
    start = time.monotonic()
    n = max_affordable_levels(V0_SPEC, 0, budget)
    elapsed = time.monotonic() - start
    assert elapsed < 30.0, f"max_affordable_levels took {elapsed:.1f}s"
    # The answer is exact: verify the defining inequality with ONE
    # incremental pass (bulk of n+1, then peel the last level off).
    upper = bulk_upgrade_cost(V0_SPEC, 0, n + 1)
    last = upgrade_cost(V0_SPEC, n)
    assert upper - last <= budget < upper
    assert n > 40_000  # sanity: the scale is what this test claims


def test_max_affordable_ratio_one_huge_budget_is_closed_form():
    # Flat curve: the answer is budget // base, even at absurd scale.
    assert max_affordable_levels(FLAT_SPEC, 0, 10**3000) == 10**3000 // 7
    assert max_affordable_levels(FLAT_SPEC, 3, 20) == 2
    assert max_affordable_levels(FLAT_SPEC, 0, 6) == 0


def test_max_affordable_validation():
    with pytest.raises((TypeError, ValueError)):
        max_affordable_levels(UPGRADE, -1, 100)
    with pytest.raises((TypeError, ValueError)):
        max_affordable_levels(UPGRADE, 0, -1)
    with pytest.raises((TypeError, ValueError)):
        max_affordable_levels(UPGRADE, 0, "100")
    with pytest.raises((TypeError, ValueError)):
        max_affordable_levels(UPGRADE, 0, True)


# --- 3. atomic bulk purchase -----------------------------------------------------


def test_purchase_upgrades_pinned_exact_spend():
    state = GameState(balances={"primary": 1_000}, owned={"tier1": 1}, last_seen=1_000)
    after = purchase_upgrades(state, UPGRADE, 3)
    assert after.balances["primary"] == 1_000 - 625  # 180 + 207 + 238
    assert after.upgrades == {"boost1": 3}
    # purity: the input state is never mutated
    assert state.balances["primary"] == 1_000
    assert state.upgrades == {}


def test_purchase_upgrades_equals_n_sequential_purchases_byte_identical():
    rng = Random(14_000)
    for _ in range(25):
        spec = _random_spec(rng)
        from_level = rng.randint(0, 20)
        n = rng.randint(1, 25)
        need = _brute_sum(spec, from_level, n)
        state = GameState(
            balances={
                spec.cost_currency: need + rng.randint(0, 10**6),
                "other": rng.randint(0, 10**6),
            },
            owned={"gen0": rng.randint(0, 9)},
            last_seen=rng.randint(0, 10**9),
            upgrades={spec.spec_id: from_level} if from_level else {},
            lifetime={spec.cost_currency: rng.randint(0, 10**12)},
            prestige={"meta": rng.randint(0, 5)},
            milestones={"owned-1": 1} if rng.random() < 0.5 else {},
        )
        bulk = purchase_upgrades(state, spec, n)
        sequential = state
        for _ in range(n):
            sequential = purchase_upgrade(sequential, spec)
        assert bulk == sequential
        assert _canon(bulk) == _canon(sequential)  # byte-identical state


def test_purchase_upgrades_insufficient_funds_is_atomic_distinct_error():
    # 3 levels need 625; one unit short must spend NOTHING and raise the
    # bulk-distinct error (a ValueError subclass, so callers of the
    # single-purchase contract still catch it).
    state = GameState(balances={"primary": 624}, last_seen=1_000)
    with pytest.raises(BulkPurchaseError) as excinfo:
        purchase_upgrades(state, UPGRADE, 3)
    assert isinstance(excinfo.value, ValueError)
    assert "624" in str(excinfo.value) and "625" in str(excinfo.value)
    # atomic: no partial spend, no partial levels — input untouched
    assert state.balances == {"primary": 624}
    assert state.upgrades == {}
    # 624 covers exactly 2 levels; the caller's recovery path works
    n = max_affordable_levels(UPGRADE, 0, state.balances["primary"])
    assert n == 2
    after = purchase_upgrades(state, UPGRADE, n)
    assert after.balances["primary"] == 624 - 387
    assert after.upgrades == {"boost1": 2}


def test_purchase_upgrades_error_is_distinct_from_single_purchase_error():
    state = GameState(balances={"primary": 0}, last_seen=1_000)
    with pytest.raises(ValueError) as single:
        purchase_upgrade(state, UPGRADE)
    assert not isinstance(single.value, BulkPurchaseError)
    with pytest.raises(BulkPurchaseError):
        purchase_upgrades(state, UPGRADE, 1)


def test_purchase_upgrades_conserves_lifetime_and_other_balances():
    state = GameState(
        balances={"primary": 10_000, "other": 55},
        lifetime={"primary": 777},
        prestige={"meta": 4},
        milestones={"owned-1": 1},
        last_seen=42,
    )
    after = purchase_upgrades(state, UPGRADE, 5)
    assert after.lifetime == {"primary": 777}  # spending is not un-earning
    assert after.balances["other"] == 55
    assert after.prestige == {"meta": 4}
    assert after.milestones == {"owned-1": 1}
    assert after.last_seen == 42
    spent = 10_000 - after.balances["primary"]
    assert spent == bulk_upgrade_cost(UPGRADE, 0, 5)


def test_purchase_upgrades_validation():
    state = GameState(balances={"primary": 10**9})
    with pytest.raises((TypeError, ValueError)):
        purchase_upgrades(state, UPGRADE, 0)  # a bulk purchase buys >= 1
    with pytest.raises((TypeError, ValueError)):
        purchase_upgrades(state, UPGRADE, -2)
    with pytest.raises((TypeError, ValueError)):
        purchase_upgrades(state, UPGRADE, True)


def test_purchase_upgrades_determinism():
    state = GameState(balances={"primary": 10**6}, last_seen=9)
    first = purchase_upgrades(state, UPGRADE, 12)
    second = purchase_upgrades(state, UPGRADE, 12)
    assert first == second
    assert _canon(first) == _canon(second)


# --- 4. integrity: derived from the pre-registered curve, no new numbers ---------


def test_bulk_math_agrees_with_theme_built_specs():
    """The bulk math is DERIVED: against the real egg-farm pack's spec
    (priced by idle_engine.economy's pre-registered table), bulk cost is
    exactly the sum of the already-published per-level curve — nothing
    new was priced."""
    theme = load_theme(REPO_ROOT / "themes" / "egg-farm.yaml")
    (spec,) = theme.upgrade_specs()
    assert bulk_upgrade_cost(spec, 0, 12) == _brute_sum(spec, 0, 12)
    budget = 10**9
    n = max_affordable_levels(spec, 0, budget)
    assert bulk_upgrade_cost(spec, 0, n) <= budget < bulk_upgrade_cost(spec, 0, n + 1)
