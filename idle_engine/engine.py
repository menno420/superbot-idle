"""Deterministic production mechanics: tick and offline progress.

Every function here is pure: no wall clock, no randomness, no I/O.
Same inputs -> same outputs, byte for byte. All arithmetic is integer
arithmetic, so a single closed-form offline calculation equals the sum
of any number of smaller ticks covering the same span.
"""

from __future__ import annotations

from collections.abc import Iterable

from idle_engine.state import GameState, GeneratorSpec


def production_per_second(state: GameState, specs: Iterable[GeneratorSpec]) -> dict[str, int]:
    """Integer units produced per second for each currency, given owned generators."""
    rates: dict[str, int] = {}
    for spec in specs:
        count = state.owned.get(spec.spec_id, 0)
        if count < 0:
            raise ValueError(f"owned count for {spec.spec_id!r} must be >= 0")
        if count:
            rates[spec.produces] = rates.get(spec.produces, 0) + spec.base_rate * count
    return rates


def tick(state: GameState, specs: Iterable[GeneratorSpec], dt: int) -> GameState:
    """Advance the state by ``dt`` whole seconds of production.

    Returns a NEW GameState; the input is never mutated. ``dt`` must be
    a non-negative integer number of seconds.
    """
    if not isinstance(dt, int) or isinstance(dt, bool):
        raise TypeError("dt must be an int (whole seconds)")
    if dt < 0:
        raise ValueError("dt must be >= 0")
    balances = dict(state.balances)
    for currency, rate in production_per_second(state, specs).items():
        balances[currency] = balances.get(currency, 0) + rate * dt
    return state.with_balances(balances, state.last_seen + dt)


def offline_progress(
    state: GameState,
    specs: Iterable[GeneratorSpec],
    last_seen: int,
    now: int,
) -> dict[str, int]:
    """Closed-form earnings accrued between ``last_seen`` and ``now``.

    Deterministic and exact: for constant integer rates this equals
    looping ``tick`` one second at a time over the same span. A ``now``
    earlier than ``last_seen`` (clock skew) accrues nothing rather than
    going negative.
    """
    for name, value in (("last_seen", last_seen), ("now", now)):
        if not isinstance(value, int) or isinstance(value, bool):
            raise TypeError(f"{name} must be an int (unix seconds)")
    elapsed = max(0, now - last_seen)
    return {
        currency: rate * elapsed
        for currency, rate in production_per_second(state, specs).items()
    }


def apply_offline_progress(
    state: GameState,
    specs: Iterable[GeneratorSpec],
    now: int,
) -> GameState:
    """Credit offline earnings since ``state.last_seen`` and stamp ``now``."""
    earned = offline_progress(state, specs, state.last_seen, now)
    balances = dict(state.balances)
    for currency, amount in earned.items():
        balances[currency] = balances.get(currency, 0) + amount
    return state.with_balances(balances, max(state.last_seen, now))
