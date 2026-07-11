"""idle_engine — deterministic, pure-domain idle-game core.

CORE/SKIN contract: this package contains game MECHANICS only. Every
player-visible noun (names, flavor, emoji, colors) comes from a theme
pack loaded via :mod:`idle_engine.theme`. Engine modules must contain
zero theme vocabulary — a guard test enforces this. No I/O beyond
reading a theme file, no chat-platform calls, no wall-clock reads:
callers pass timestamps in, so identical inputs always yield identical
outputs. Economy numbers live in :mod:`idle_engine.economy`,
pre-registered in docs/design/ before any tuning.
"""

from idle_engine.state import GameState, GeneratorSpec
from idle_engine.engine import offline_progress, production_per_second, tick
from idle_engine.upgrades import UpgradeSpec, purchase_upgrade, upgrade_cost
from idle_engine.prestige import (
    PrestigeSpec,
    apply_prestige,
    prestige_award,
    prestige_eligible,
)
from idle_engine.theme import (
    Theme,
    ThemeCurrency,
    ThemeGenerator,
    ThemePrestige,
    ThemeUpgrade,
    load_theme,
)

__all__ = [
    "GameState",
    "GeneratorSpec",
    "PrestigeSpec",
    "Theme",
    "ThemeCurrency",
    "ThemeGenerator",
    "ThemePrestige",
    "ThemeUpgrade",
    "UpgradeSpec",
    "apply_prestige",
    "load_theme",
    "offline_progress",
    "prestige_award",
    "prestige_eligible",
    "production_per_second",
    "purchase_upgrade",
    "tick",
    "upgrade_cost",
]
