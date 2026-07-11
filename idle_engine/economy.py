"""Pre-registered economy parameters (PROVISIONAL) and spec builders.

INTEGRITY FLOOR: every number here is committed with rationale in
``docs/design/upgrades-prestige-v0.md`` BEFORE any tuning, and is
explicitly PROVISIONAL pending the economy design doc slice and
Simulator pinning (Q-0264). Themes never carry these numbers — a theme
names the slots (SKIN), this module prices them (CORE). Change a value
here and the design doc must change in the same PR, or the pre-registration
is a lie.
"""

from __future__ import annotations

from idle_engine.prestige import PrestigeSpec
from idle_engine.state import GeneratorSpec
from idle_engine.upgrades import UpgradeSpec

# --- PROVISIONAL v0 parameters (docs/design/upgrades-prestige-v0.md) ---------

#: An upgrade's level-0 cost = this many seconds of the target generator's
#: base output (one generator's worth).
UPGRADE_BASE_COST_SECONDS = 60

#: Geometric cost growth per level, as an exact rational (num, den): x1.15.
UPGRADE_COST_GROWTH_NUM = 115
UPGRADE_COST_GROWTH_DEN = 100

#: Additive percent added to the target generator's rate per upgrade level.
UPGRADE_EFFECT_PERCENT = 25

#: Lifetime earnings of the measured currency required before a reset.
PRESTIGE_THRESHOLD = 100_000

#: Award = isqrt(lifetime // divisor); divisor == threshold, so the first
#: eligible reset awards exactly 1.
PRESTIGE_AWARD_DIVISOR = 100_000

#: Additive percent added to ALL production per prestige unit held.
PRESTIGE_BONUS_PERCENT = 10


def build_upgrade_spec(upgrade_id: str, target: GeneratorSpec) -> UpgradeSpec:
    """Price one theme-declared upgrade slot against the v0 curve table."""
    return UpgradeSpec(
        spec_id=upgrade_id,
        cost_currency=target.produces,
        base_cost=target.base_rate * UPGRADE_BASE_COST_SECONDS,
        cost_growth_num=UPGRADE_COST_GROWTH_NUM,
        cost_growth_den=UPGRADE_COST_GROWTH_DEN,
        target=target.spec_id,
        effect_percent=UPGRADE_EFFECT_PERCENT,
    )


def build_prestige_spec(awards: str, measures: str) -> PrestigeSpec:
    """Bind one theme-declared prestige track to the v0 threshold/award table."""
    return PrestigeSpec(
        awards=awards,
        measures=measures,
        threshold=PRESTIGE_THRESHOLD,
        award_divisor=PRESTIGE_AWARD_DIVISOR,
        bonus_percent=PRESTIGE_BONUS_PERCENT,
    )
