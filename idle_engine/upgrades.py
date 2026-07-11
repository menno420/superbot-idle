"""Upgrades: geometric cost curves and rate effects, all integer-exact.

An :class:`UpgradeSpec` is pure mechanics — id, cost curve, target
generator, effect size. Its player-visible noun lives in the theme pack
(the SKIN side); the curve SHAPE and every parameter are pre-registered
in ``docs/design/upgrades-prestige-v0.md`` (PROVISIONAL pending the
economy design doc slice + Simulator pinning, Q-0264).

Curve shape: ``cost(level) = base_cost * growth_num**level // growth_den**level``
— geometric growth evaluated in exact big-int arithmetic with a single
floor division, so every platform prices level N identically.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from collections.abc import Iterable

from idle_engine.state import GameState


def _require_positive_int(value: int, name: str, minimum: int = 1) -> None:
    if not isinstance(value, int) or isinstance(value, bool):
        raise TypeError(f"{name} must be an int")
    if value < minimum:
        raise ValueError(f"{name} must be >= {minimum}")


@dataclass(frozen=True)
class UpgradeSpec:
    """Mechanical description of one purchasable upgrade ladder.

    ``spec_id``, ``cost_currency`` and ``target`` are opaque ids mapped
    to display nouns by a theme pack. ``effect_percent`` is the additive
    percent added to the target generator's rate per level purchased
    (level 3 at 25 -> +75%).
    """

    spec_id: str
    cost_currency: str
    base_cost: int
    cost_growth_num: int
    cost_growth_den: int
    target: str
    effect_percent: int

    def __post_init__(self) -> None:
        _require_positive_int(self.base_cost, "base_cost")
        _require_positive_int(self.cost_growth_num, "cost_growth_num")
        _require_positive_int(self.cost_growth_den, "cost_growth_den")
        _require_positive_int(self.effect_percent, "effect_percent")
        if self.cost_growth_num < self.cost_growth_den:
            raise ValueError(
                "cost growth must be >= 1 (num >= den): shrinking costs are an exploit"
            )


def upgrade_cost(spec: UpgradeSpec, level: int) -> int:
    """Exact integer cost of buying ``spec`` when ``level`` are already owned."""
    _require_positive_int(level, "level", minimum=0)
    return spec.base_cost * spec.cost_growth_num**level // spec.cost_growth_den**level


def purchase_upgrade(state: GameState, spec: UpgradeSpec) -> GameState:
    """Spend ``spec.cost_currency`` to raise the upgrade one level.

    Returns a NEW GameState; the input is never mutated. Raises
    ``ValueError`` when the balance cannot cover the current level's
    cost — a purchase either happens exactly or not at all. Spending
    never touches ``lifetime``.
    """
    level = state.upgrades.get(spec.spec_id, 0)
    cost = upgrade_cost(spec, level)
    balance = state.balances.get(spec.cost_currency, 0)
    if balance < cost:
        raise ValueError(
            f"insufficient {spec.cost_currency!r} for {spec.spec_id!r} "
            f"level {level + 1}: have {balance}, need {cost}"
        )
    balances = dict(state.balances)
    balances[spec.cost_currency] = balance - cost
    upgrades = dict(state.upgrades)
    upgrades[spec.spec_id] = level + 1
    return replace(state, balances=balances, upgrades=upgrades)


def upgrade_percent(
    state: GameState, upgrade_specs: Iterable[UpgradeSpec], generator_id: str
) -> int:
    """Rate multiplier for one generator as an integer percent (100 = x1).

    Additive across levels and across upgrades sharing a target:
    ``100 + sum(effect_percent * level)``.
    """
    percent = 100
    for spec in upgrade_specs:
        if spec.target == generator_id:
            level = state.upgrades.get(spec.spec_id, 0)
            if level < 0:
                raise ValueError(f"upgrade level for {spec.spec_id!r} must be >= 0")
            percent += spec.effect_percent * level
    return percent
