"""idle_engine — deterministic, pure-domain idle-game core.

CORE/SKIN contract: this package contains game MECHANICS only. Every
player-visible noun (names, flavor, emoji, colors) comes from a theme
pack loaded via :mod:`idle_engine.theme`. Engine modules must contain
zero theme vocabulary — a guard test enforces this. No I/O beyond
reading a theme file, no chat-platform calls, no wall-clock reads:
callers pass timestamps in, so identical inputs always yield identical
outputs.
"""

from idle_engine.state import GameState, GeneratorSpec
from idle_engine.engine import offline_progress, production_per_second, tick
from idle_engine.theme import Theme, ThemeCurrency, ThemeGenerator, load_theme

__all__ = [
    "GameState",
    "GeneratorSpec",
    "Theme",
    "ThemeCurrency",
    "ThemeGenerator",
    "load_theme",
    "offline_progress",
    "production_per_second",
    "tick",
]
