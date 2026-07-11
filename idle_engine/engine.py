"""Deterministic production mechanics: tick and offline progress.

Every function here is pure: no wall clock, no randomness, no I/O.
Same inputs -> same outputs, byte for byte. All arithmetic is integer
arithmetic, so a single closed-form offline calculation equals the sum
of any number of smaller ticks covering the same span.

Multiplier model (slice (b)): each generator's per-second output is

    base_rate * count * upgrade_pct * prestige_pct // 10_000

where both pcts are integer percents (100 = x1) from
:func:`idle_engine.upgrades.upgrade_percent` and
:func:`idle_engine.prestige.prestige_percent`. The floor division
happens ONCE per generator per second, inside the rate — so the rate is
a plain integer and the closed-form offline path stays exactly equal to
looped ticks by construction.
"""

from __future__ import annotations

from collections.abc import Iterable

from idle_engine.prestige import PrestigeSpec, prestige_percent
from idle_engine.state import GameState, GeneratorSpec
from idle_engine.upgrades import UpgradeSpec, upgrade_percent


def production_per_second(
    state: GameState,
    specs: Iterable[GeneratorSpec],
    upgrade_specs: Iterable[UpgradeSpec] = (),
    prestige_specs: Iterable[PrestigeSpec] = (),
) -> dict[str, int]:
    """Integer units produced per second for each currency, given owned generators.

    Upgrade and prestige multipliers are applied here (and only here),
    so every consumer — live tick or closed-form offline credit — sees
    the identical integer rate.
    """
    upgrade_specs = tuple(upgrade_specs)
    global_pct = prestige_percent(state, prestige_specs)
    rates: dict[str, int] = {}
    for spec in specs:
        count = state.owned.get(spec.spec_id, 0)
        if count < 0:
            raise ValueError(f"owned count for {spec.spec_id!r} must be >= 0")
        if count:
            pct = upgrade_percent(state, upgrade_specs, spec.spec_id)
            produced = spec.base_rate * count * pct * global_pct // 10_000
            rates[spec.produces] = rates.get(spec.produces, 0) + produced
    return rates


def tick(
    state: GameState,
    specs: Iterable[GeneratorSpec],
    dt: int,
    upgrade_specs: Iterable[UpgradeSpec] = (),
    prestige_specs: Iterable[PrestigeSpec] = (),
) -> GameState:
    """Advance the state by ``dt`` whole seconds of production.

    Returns a NEW GameState; the input is never mutated. ``dt`` must be
    a non-negative integer number of seconds. Earnings are credited to
    balances AND to run-lifetime totals (which drive prestige awards).
    """
    if not isinstance(dt, int) or isinstance(dt, bool):
        raise TypeError("dt must be an int (whole seconds)")
    if dt < 0:
        raise ValueError("dt must be >= 0")
    rates = production_per_second(state, specs, upgrade_specs, prestige_specs)
    earned = {currency: rate * dt for currency, rate in rates.items()}
    return state.with_earnings(earned, state.last_seen + dt)


def offline_progress(
    state: GameState,
    specs: Iterable[GeneratorSpec],
    last_seen: int,
    now: int,
    upgrade_specs: Iterable[UpgradeSpec] = (),
    prestige_specs: Iterable[PrestigeSpec] = (),
) -> dict[str, int]:
    """Closed-form earnings accrued between ``last_seen`` and ``now``.

    Deterministic and exact: for constant integer rates this equals
    looping ``tick`` one second at a time over the same span — upgrade
    and prestige multipliers included, since both paths read the same
    integer rate. A ``now`` earlier than ``last_seen`` (clock skew)
    accrues nothing rather than going negative.
    """
    for name, value in (("last_seen", last_seen), ("now", now)):
        if not isinstance(value, int) or isinstance(value, bool):
            raise TypeError(f"{name} must be an int (unix seconds)")
    elapsed = max(0, now - last_seen)
    rates = production_per_second(state, specs, upgrade_specs, prestige_specs)
    return {currency: rate * elapsed for currency, rate in rates.items()}


def apply_offline_progress(
    state: GameState,
    specs: Iterable[GeneratorSpec],
    now: int,
    upgrade_specs: Iterable[UpgradeSpec] = (),
    prestige_specs: Iterable[PrestigeSpec] = (),
) -> GameState:
    """Credit offline earnings since ``state.last_seen`` and stamp ``now``."""
    earned = offline_progress(
        state, specs, state.last_seen, now, upgrade_specs, prestige_specs
    )
    return state.with_earnings(earned, max(state.last_seen, now))
