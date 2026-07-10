"""Theme loading — the SKIN side of the CORE/SKIN split.

A theme pack is a data-only YAML file. It supplies every player-visible
noun: theme name, currency names, generator names, flavor text, emoji,
and embed color. This module maps those nouns onto opaque engine ids;
nothing in this package hard-codes any theme vocabulary.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml

from idle_engine.state import GeneratorSpec


@dataclass(frozen=True)
class ThemeCurrency:
    currency_id: str
    name: str
    description: str
    emoji: str


@dataclass(frozen=True)
class ThemeGenerator:
    generator_id: str
    name: str
    description: str
    emoji: str
    produces: str
    base_rate: int


@dataclass(frozen=True)
class Theme:
    theme_id: str
    name: str
    description: str
    emoji: str
    embed_color: str
    currencies: dict[str, ThemeCurrency]
    generators: dict[str, ThemeGenerator]

    def currency_name(self, currency_id: str) -> str:
        return self.currencies[currency_id].name

    def generator_name(self, generator_id: str) -> str:
        return self.generators[generator_id].name

    def generator_specs(self) -> list[GeneratorSpec]:
        """Mechanical specs for the engine, stripped of all display data."""
        return [
            GeneratorSpec(spec_id=g.generator_id, produces=g.produces, base_rate=g.base_rate)
            for g in self.generators.values()
        ]


def _require_str(mapping: dict, key: str, where: str) -> str:
    value = mapping.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{where}: field {key!r} must be a non-empty string")
    return value


def load_theme(path: str | Path) -> Theme:
    """Load and structurally validate a theme pack from YAML."""
    path = Path(path)
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path}: theme pack must be a mapping")

    meta = data.get("theme")
    if not isinstance(meta, dict):
        raise ValueError(f"{path}: missing 'theme' mapping")
    where = f"{path}:theme"
    theme_id = _require_str(meta, "id", where)
    name = _require_str(meta, "name", where)
    description = _require_str(meta, "description", where)
    emoji = _require_str(meta, "emoji", where)
    embed_color = _require_str(meta, "embed_color", where)

    raw_currencies = data.get("currencies")
    if not isinstance(raw_currencies, list) or not raw_currencies:
        raise ValueError(f"{path}: 'currencies' must be a non-empty list")
    currencies: dict[str, ThemeCurrency] = {}
    for i, entry in enumerate(raw_currencies):
        if not isinstance(entry, dict):
            raise ValueError(f"{path}:currencies[{i}] must be a mapping")
        w = f"{path}:currencies[{i}]"
        cid = _require_str(entry, "id", w)
        currencies[cid] = ThemeCurrency(
            currency_id=cid,
            name=_require_str(entry, "name", w),
            description=_require_str(entry, "description", w),
            emoji=_require_str(entry, "emoji", w),
        )

    raw_generators = data.get("generators")
    if not isinstance(raw_generators, list) or not raw_generators:
        raise ValueError(f"{path}: 'generators' must be a non-empty list")
    generators: dict[str, ThemeGenerator] = {}
    for i, entry in enumerate(raw_generators):
        if not isinstance(entry, dict):
            raise ValueError(f"{path}:generators[{i}] must be a mapping")
        w = f"{path}:generators[{i}]"
        gid = _require_str(entry, "id", w)
        produces = _require_str(entry, "produces", w)
        if produces not in currencies:
            raise ValueError(f"{w}: 'produces' ({produces!r}) is not a declared currency id")
        base_rate = entry.get("base_rate")
        if not isinstance(base_rate, int) or isinstance(base_rate, bool) or base_rate < 1:
            raise ValueError(f"{w}: 'base_rate' must be a positive integer")
        generators[gid] = ThemeGenerator(
            generator_id=gid,
            name=_require_str(entry, "name", w),
            description=_require_str(entry, "description", w),
            emoji=_require_str(entry, "emoji", w),
            produces=produces,
            base_rate=base_rate,
        )

    return Theme(
        theme_id=theme_id,
        name=name,
        description=description,
        emoji=emoji,
        embed_color=embed_color,
        currencies=currencies,
        generators=generators,
    )
