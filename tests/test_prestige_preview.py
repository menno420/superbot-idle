"""Prestige reset previews — read-only lookups over the award mechanic.

Three pure helpers, pinned here against the SAME pre-registered PROVISIONAL
parameters as ``test_upgrades_prestige.py`` (docs/design/upgrades-prestige-v0.md):

- ``prestige_award_if_reset`` must equal the real award path
  (:func:`prestige_award`) — the preview never forks the formula;
- ``seconds_to_prestige_eligible`` — whole seconds until lifetime reaches the
  eligibility threshold at a given production rate;
- ``seconds_to_next_prestige_award`` — whole seconds until the award ticks up
  one whole unit.

Both eta helpers reuse ``time_to_afford``, so they carry its contract: ``0`` at
or over the boundary, the ``None`` never-sentinel at ``rate == 0`` below it, and
integer-exact ceil arithmetic with no float leakage.
"""

import pytest

from idle_engine import (
    GameState,
    PrestigeSpec,
    prestige_award,
    prestige_award_if_reset,
    seconds_to_next_prestige_award,
    seconds_to_prestige_eligible,
)

# Same track as test_upgrades_prestige.py: threshold 100k lifetime "primary",
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


# --- award-if-reset mirrors the real award path ------------------------------


@pytest.mark.parametrize(
    "lifetime, award",
    [
        (0, 0),            # empty run previews a zero payoff
        (99_999, 0),       # below threshold: still a lookup, isqrt(0)
        (100_000, 1),      # isqrt(1)
        (399_999, 1),      # isqrt(3)
        (400_000, 2),      # isqrt(4)
        (1_000_000, 3),    # isqrt(10)
        (10_000_000, 10),  # isqrt(100)
    ],
)
def test_award_if_reset_matches_real_award_path(lifetime, award):
    state = make_state(lifetime={"primary": lifetime})
    assert prestige_award_if_reset(state, PRESTIGE) == award
    # the preview IS the mechanic — never a forked, drifting copy
    assert prestige_award_if_reset(state, PRESTIGE) == prestige_award(state, PRESTIGE)


def test_award_preview_is_pure_and_repeatable():
    state = make_state(lifetime={"primary": 640_000})  # isqrt(6) = 2
    assert prestige_award_if_reset(state, PRESTIGE) == 2
    assert prestige_award_if_reset(state, PRESTIGE) == 2  # no hidden state
    assert state.lifetime == {"primary": 640_000}  # input untouched


def test_award_preview_monotonic_waiting_never_decreases_it():
    # As lifetime grows, the previewed award is non-decreasing — waiting can
    # only ever pay off more, never less.
    previews = [
        prestige_award_if_reset(make_state(lifetime={"primary": lt}), PRESTIGE)
        for lt in range(0, 5_000_000, 40_000)
    ]
    assert previews == sorted(previews)
    assert all(isinstance(p, int) and not isinstance(p, bool) for p in previews)


# --- seconds to first eligibility --------------------------------------------


def test_seconds_to_eligible_before_threshold_is_exact_ceil():
    # shortfall 100_000 at 7/s: ceil(100000/7) = 14286 (14285s leaves 99995).
    state = make_state(lifetime={"primary": 0})
    assert seconds_to_prestige_eligible(state, PRESTIGE, rate=7) == 14_286
    # a non-zero head start shortens it by exactly the elapsed lifetime.
    state = make_state(lifetime={"primary": 30_000})
    assert seconds_to_prestige_eligible(state, PRESTIGE, rate=10) == 7_000


def test_seconds_to_eligible_boundary_is_zero():
    # exactly at the threshold -> already eligible -> 0 seconds.
    at = make_state(lifetime={"primary": 100_000})
    assert seconds_to_prestige_eligible(at, PRESTIGE, rate=5) == 0
    # comfortably over -> still 0.
    over = make_state(lifetime={"primary": 500_000})
    assert seconds_to_prestige_eligible(over, PRESTIGE, rate=5) == 0
    # and 0 holds even at rate 0 once already eligible (affordable beats never).
    assert seconds_to_prestige_eligible(at, PRESTIGE, rate=0) == 0


def test_seconds_to_eligible_zero_rate_below_threshold_is_never():
    state = make_state(lifetime={"primary": 99_999})
    assert seconds_to_prestige_eligible(state, PRESTIGE, rate=0) is None


# --- seconds to the next whole award unit ------------------------------------


def test_seconds_to_next_award_targets_the_isqrt_step():
    # award 1 (lifetime 100k); next unit needs (1+1)^2 * 100k = 400_000.
    # shortfall 300_000 at 100/s -> 3_000 seconds exactly.
    state = make_state(lifetime={"primary": 100_000})
    assert seconds_to_next_prestige_award(state, PRESTIGE, rate=100) == 3_000
    # from empty: award 0, next unit needs 1^2 * 100k = 100_000, at 100/s -> 1_000.
    empty = make_state(lifetime={"primary": 0})
    assert seconds_to_next_prestige_award(empty, PRESTIGE, rate=100) == 1_000


def test_seconds_to_next_award_ceils_a_partial_second():
    # award 0, next target 100_000, at 3/s: ceil(100000/3) = 33_334.
    state = make_state(lifetime={"primary": 0})
    assert seconds_to_next_prestige_award(state, PRESTIGE, rate=3) == 33_334


def test_seconds_to_next_award_is_always_positive_at_positive_rate():
    # The award is a floor, so lifetime is always strictly below the next-unit
    # target — the eta never collapses to 0 while producing, even right at a
    # boundary lifetime where the award just stepped up.
    for lifetime in (0, 99_999, 100_000, 399_999, 400_000, 1_000_000):
        state = make_state(lifetime={"primary": lifetime})
        assert seconds_to_next_prestige_award(state, PRESTIGE, rate=50) >= 1


def test_seconds_to_next_award_zero_rate_is_never():
    state = make_state(lifetime={"primary": 250_000})
    assert seconds_to_next_prestige_award(state, PRESTIGE, rate=0) is None


# --- integer-exactness at big-int scale --------------------------------------


def test_previews_are_integer_exact_no_float_leakage():
    spec = PrestigeSpec(
        awards="meta", measures="primary",
        threshold=10**24, award_divisor=10**24, bonus_percent=1,
    )
    lifetime = 3 * 10**24 + 1  # award = isqrt(3) = 1
    state = make_state(lifetime={"primary": lifetime})
    assert prestige_award_if_reset(state, spec) == 1
    rate = 10**7
    # eligible already (lifetime > threshold) -> 0.
    assert seconds_to_prestige_eligible(state, spec, rate=rate) == 0
    # next unit needs (1+1)^2 * 10^24 = 4*10^24; shortfall exact big-int ceil.
    eta = seconds_to_next_prestige_award(state, spec, rate=rate)
    shortfall = 4 * 10**24 - lifetime
    assert eta == -(-shortfall // rate)  # exact ceil-division, no float
    assert isinstance(eta, int) and not isinstance(eta, bool)


def test_previews_reject_negative_lifetime():
    # Corrupt state fails loud, mirroring the award mechanic's own guard.
    state = make_state(lifetime={"primary": -1})
    with pytest.raises(ValueError):
        prestige_award_if_reset(state, PRESTIGE)
    with pytest.raises(ValueError):
        seconds_to_prestige_eligible(state, PRESTIGE, rate=5)
    with pytest.raises(ValueError):
        seconds_to_next_prestige_award(state, PRESTIGE, rate=5)
