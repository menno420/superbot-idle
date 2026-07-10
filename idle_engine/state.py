"""Pure game-state containers for the idle engine.

All quantities are integers: currency balances are integer units and
production rates are integer units-per-second, so the math is exact and
identical on every platform (no float drift, no rounding ambiguity).
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class GeneratorSpec:
    """Mechanical description of one generator kind.

    ``spec_id`` and ``produces`` are opaque identifiers that a theme
    pack maps to display nouns; the engine never interprets them as
    words. ``base_rate`` is integer currency units produced per second
    per owned generator.
    """

    spec_id: str
    produces: str
    base_rate: int

    def __post_init__(self) -> None:
        if not isinstance(self.base_rate, int) or isinstance(self.base_rate, bool):
            raise TypeError("base_rate must be an int")
        if self.base_rate < 0:
            raise ValueError("base_rate must be >= 0")


@dataclass(frozen=True)
class GameState:
    """Immutable snapshot of one save: balances, owned generators, last_seen.

    ``balances`` maps currency id -> integer units held.
    ``owned`` maps generator spec_id -> integer count owned.
    ``last_seen`` is the unix timestamp (integer seconds) up to which
    production has already been credited.
    """

    balances: dict[str, int] = field(default_factory=dict)
    owned: dict[str, int] = field(default_factory=dict)
    last_seen: int = 0

    def with_balances(self, balances: dict[str, int], last_seen: int) -> "GameState":
        """Return a new state with replaced balances and last_seen."""
        return GameState(balances=dict(balances), owned=dict(self.owned), last_seen=last_seen)
