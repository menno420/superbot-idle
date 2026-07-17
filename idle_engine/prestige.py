"""Prestige: the reset mechanic and its persistent global multiplier.

A :class:`PrestigeSpec` is pure mechanics — which currency's lifetime
earnings it measures, the eligibility threshold, the award curve, the
per-unit bonus. The prestige currency's name and the action's name are
theme-pack nouns (SKIN side). Curve shape and parameters are
pre-registered in ``docs/design/upgrades-prestige-v0.md`` (PROVISIONAL
pending the economy design doc slice + Simulator pinning, Q-0264).

Award shape: ``award = isqrt(lifetime_measured // award_divisor)`` —
integer square root of the lifetime earnings this run, in units of the
divisor. Deterministic, monotonic, strongly diminishing: doubling a run
does not double the award, so the optimal loop is reset-and-grow rather
than one endless grind.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from collections.abc import Iterable
from math import isqrt

from idle_engine.state import GameState
from idle_engine.upgrades import time_to_afford


def _require_int(value: int, name: str, minimum: int) -> None:
    if not isinstance(value, int) or isinstance(value, bool):
        raise TypeError(f"{name} must be an int")
    if value < minimum:
        raise ValueError(f"{name} must be >= {minimum}")


@dataclass(frozen=True)
class PrestigeSpec:
    """Mechanical description of one prestige (reset) track.

    ``awards`` is the opaque id of the persistent prestige currency;
    ``measures`` is the opaque id of the run currency whose LIFETIME
    earnings drive eligibility and the award. ``bonus_percent`` is the
    additive percent added to ALL production per unit of the prestige
    currency held.
    """

    awards: str
    measures: str
    threshold: int
    award_divisor: int
    bonus_percent: int

    def __post_init__(self) -> None:
        _require_int(self.threshold, "threshold", 1)
        _require_int(self.award_divisor, "award_divisor", 1)
        _require_int(self.bonus_percent, "bonus_percent", 0)
        if self.threshold < self.award_divisor:
            raise ValueError(
                "threshold must be >= award_divisor so an eligible reset always awards >= 1"
            )


def prestige_award(state: GameState, spec: PrestigeSpec) -> int:
    """Deterministic award for resetting now: isqrt(lifetime // divisor)."""
    lifetime = state.lifetime.get(spec.measures, 0)
    if lifetime < 0:
        raise ValueError(f"lifetime for {spec.measures!r} must be >= 0")
    return isqrt(lifetime // spec.award_divisor)


def prestige_eligible(state: GameState, spec: PrestigeSpec) -> bool:
    """True once this run's lifetime earnings reach the threshold."""
    return state.lifetime.get(spec.measures, 0) >= spec.threshold


def apply_prestige(state: GameState, spec: PrestigeSpec) -> GameState:
    """Reset the run and bank the award.

    Wipes balances, owned generators, upgrade levels and lifetime
    earnings; credits the prestige currency; preserves ``last_seen``
    (the wall-clock anchor is not part of the run) and every other
    prestige balance. Returns a NEW GameState; raises ``ValueError``
    when the state is not eligible — a reset either happens exactly or
    not at all.
    """
    if not prestige_eligible(state, spec):
        lifetime = state.lifetime.get(spec.measures, 0)
        raise ValueError(
            f"not eligible to reset: lifetime {spec.measures!r} is "
            f"{lifetime}, threshold is {spec.threshold}"
        )
    prestige = dict(state.prestige)
    prestige[spec.awards] = prestige.get(spec.awards, 0) + prestige_award(state, spec)
    return replace(
        state, balances={}, owned={}, upgrades={}, lifetime={}, prestige=prestige
    )


def prestige_percent(state: GameState, prestige_specs: Iterable[PrestigeSpec]) -> int:
    """Global production multiplier as an integer percent (100 = x1).

    Additive across specs: ``100 + sum(bonus_percent * units_held)``.
    Applies to every generator, this run and every run after — the
    persistence lives in ``state.prestige`` surviving resets.
    """
    percent = 100
    for spec in prestige_specs:
        held = state.prestige.get(spec.awards, 0)
        if held < 0:
            raise ValueError(f"prestige balance for {spec.awards!r} must be >= 0")
        percent += spec.bonus_percent * held
    return percent


# --- read-only reset previews -------------------------------------------------
#
# Pure lookups over the award mechanic above: what a reset would pay right now,
# and — at a given measured-currency production rate — how long until that
# payout first unlocks and until it ticks up. They change nothing; they never
# fork the award formula (they call :func:`prestige_award`) and the eta helpers
# reuse the engine's integer-exact :func:`time_to_afford` primitive, so the
# whole surface agrees to the second with no float leakage.


def prestige_award_if_reset(state: GameState, spec: PrestigeSpec) -> int:
    """Preview: prestige currency a reset would bank RIGHT NOW.

    The read-only, preview-named entry point onto the reset payoff — it
    delegates to :func:`prestige_award` (the mechanic is never forked), so
    the UI can ask "what would I get?" without invoking the reset path, and
    the answer is identical to what :func:`apply_prestige` would credit.
    Reports the award for the measured lifetime as-is, even below the
    eligibility threshold (where a reset is not yet allowed): a preview is a
    lookup, not a gate — pair it with :func:`prestige_eligible` when the
    caller needs to know whether the reset can actually happen.
    """
    return prestige_award(state, spec)


def seconds_to_prestige_eligible(
    state: GameState, spec: PrestigeSpec, rate: int
) -> int | None:
    """Whole seconds until this run's lifetime reaches the eligibility threshold.

    ``rate`` is the per-second production of the measured currency
    (``spec.measures``) — the caller passes it in (e.g. from
    :func:`idle_engine.engine.production_per_second`), keeping this a pure
    function of its inputs. The affordability dual applied to a lifetime
    target: delegates to :func:`time_to_afford` with the threshold as the
    cost and lifetime as the balance, so it inherits the engine's
    integer-exact contract — ``0`` once lifetime is at or over the threshold
    (already eligible), the ``None`` never-sentinel when nothing is produced
    (``rate == 0``) and not yet eligible, otherwise the exact integer ceil of
    the shortfall over ``rate``.
    """
    lifetime = state.lifetime.get(spec.measures, 0)
    return time_to_afford(cost=spec.threshold, balance=lifetime, rate=rate)


def seconds_to_next_prestige_award(
    state: GameState, spec: PrestigeSpec, rate: int
) -> int | None:
    """Whole seconds until the reset award grows by one whole unit.

    With the current award ``A = isqrt(lifetime // award_divisor)``, the next
    unit ``A + 1`` unlocks once lifetime reaches ``(A + 1) ** 2 *
    award_divisor`` — the exact lifetime at which the integer square root
    steps up. ``rate`` is the measured currency's per-second production,
    passed in by the caller (see :func:`seconds_to_prestige_eligible`).
    Delegates to :func:`time_to_afford` against that next-unit target, so the
    ``None`` never-sentinel (``rate == 0``) and the integer-exact ceil-division
    carry over unchanged. Because ``A`` is a floor, lifetime is always strictly
    below the next-unit target, so the result is always ``>= 1`` at a positive
    rate.
    """
    lifetime = state.lifetime.get(spec.measures, 0)
    if lifetime < 0:
        raise ValueError(f"lifetime for {spec.measures!r} must be >= 0")
    next_award = prestige_award(state, spec) + 1
    next_target = next_award * next_award * spec.award_divisor
    return time_to_afford(cost=next_target, balance=lifetime, rate=rate)
