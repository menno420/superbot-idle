#!/usr/bin/env python3
"""theme-gate v1 — validate every theme pack under themes/ against schema v1.

Each ``themes/*.yaml`` is validated against the published machine schema
(``schema/theme.schema.json``, JSON Schema draft 2020-12, via the
``jsonschema`` library — the theme-gate workflow pip-installs it). The
schema enforces the data-only contract hard: ``schema_version`` is
required (must be 1), unknown keys are rejected at every level (a theme
cannot smuggle new mechanics), and chat-embed string budgets are schema
limits (names <= 64, flavor text <= 1024, emoji <= 32, <= 5 currencies +
<= 20 generators so renders never exceed 25 fields, ``#RRGGBB`` colors,
``base_rate`` bounded 1..1000) so overflow is a red gate, never a live
render bug. Human-readable twin: ``docs/theme-schema.md``.

On top of JSON Schema, the gate enforces what a schema cannot express:
unique currency/generator ids, ``produces`` referencing a declared
currency, and that the pack actually loads through
``idle_engine.theme.load_theme`` (the engine is ground truth). Across
the catalog, ``theme.id`` must be unique — per-file validation cannot
see two packs claiming the same id, so ``main`` collects ids from every
pack that passed and fails on collisions.

Exits 0 when every pack passes, 1 on any violation, 2 when no packs
exist (an empty themes/ directory is a wiring error, not a pass).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

import jsonschema  # noqa: E402
import yaml  # noqa: E402

from idle_engine.theme import load_theme  # noqa: E402

SCHEMA_PATH = REPO_ROOT / "schema" / "theme.schema.json"


def _load_validator() -> jsonschema.Draft202012Validator:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator.check_schema(schema)
    return jsonschema.Draft202012Validator(schema)


def _json_path(error: jsonschema.ValidationError) -> str:
    if not error.absolute_path:
        return "<root>"
    parts: list[str] = []
    for part in error.absolute_path:
        if isinstance(part, int):
            parts[-1:] = [f"{parts[-1]}[{part}]"] if parts else [f"[{part}]"]
        else:
            parts.append(str(part))
    return ".".join(parts)


def _semantic_errors(data: dict, path: Path) -> list[str]:
    """Checks the JSON Schema cannot express (run only on schema-clean data)."""
    errors: list[str] = []
    currency_ids = [c["id"] for c in data["currencies"]]
    generator_ids = [g["id"] for g in data["generators"]]
    upgrade_ids = [u["id"] for u in data.get("upgrades", [])]
    for label, ids in (
        ("currencies", currency_ids),
        ("generators", generator_ids),
        ("upgrades", upgrade_ids),
    ):
        dupes = sorted({i for i in ids if ids.count(i) > 1})
        if dupes:
            errors.append(f"{path}:{label}: duplicate id(s) {dupes} (ids must be unique)")
    declared = set(currency_ids)
    for i, gen in enumerate(data["generators"]):
        if gen["produces"] not in declared:
            errors.append(
                f"{path}:generators[{i}].produces: {gen['produces']!r} "
                f"is not a declared currency id"
            )
    declared_generators = set(generator_ids)
    for i, upgrade in enumerate(data.get("upgrades", [])):
        if upgrade["target"] not in declared_generators:
            errors.append(
                f"{path}:upgrades[{i}].target: {upgrade['target']!r} "
                f"is not a declared generator id"
            )
    prestige = data.get("prestige")
    if prestige is not None:
        for key in ("currency", "measures"):
            if prestige[key] not in declared:
                errors.append(
                    f"{path}:prestige.{key}: {prestige[key]!r} "
                    f"is not a declared currency id"
                )
        if prestige["currency"] == prestige["measures"]:
            errors.append(
                f"{path}:prestige: 'currency' and 'measures' must differ "
                f"(a track cannot measure the currency it awards)"
            )
    if errors:
        return errors
    try:  # the engine loader is ground truth — a schema-valid pack must load
        load_theme(path)
    except Exception as exc:
        errors.append(f"{path}: engine loader rejected pack: {exc}")
    return errors


def validate_file(path: Path, validator: jsonschema.Draft202012Validator | None = None) -> list[str]:
    validator = validator or _load_validator()
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return [f"{path}: unreadable YAML: {exc}"]
    if not isinstance(data, dict):
        return [f"{path}: theme pack must be a mapping"]
    errors = [
        f"{path}:{_json_path(error)}: {error.message}"
        for error in sorted(validator.iter_errors(data), key=lambda e: list(map(str, e.absolute_path)))
    ]
    if errors:
        return errors
    return _semantic_errors(data, path)


def catalog_errors(theme_ids: dict[Path, str]) -> list[str]:
    """Cross-pack checks over per-file-valid packs: theme.id must be unique
    across the whole catalog (per-file validation cannot see a collision —
    two packs claiming one id would silently shadow each other in any
    id-keyed catalog map)."""
    by_id: dict[str, list[Path]] = {}
    for path, theme_id in theme_ids.items():
        by_id.setdefault(theme_id, []).append(path)
    return [
        f"catalog: duplicate theme.id {theme_id!r} across packs: "
        + ", ".join(str(p) for p in sorted(paths))
        for theme_id, paths in sorted(by_id.items())
        if len(paths) > 1
    ]


def main(argv: list[str]) -> int:
    themes_dir = Path(argv[1]) if len(argv) > 1 else REPO_ROOT / "themes"
    packs = sorted(themes_dir.glob("*.yaml")) + sorted(themes_dir.glob("*.yml"))
    if not packs:
        print(f"theme-gate: no theme packs found under {themes_dir}", file=sys.stderr)
        return 2
    validator = _load_validator()
    failures: list[str] = []
    theme_ids: dict[Path, str] = {}
    for pack in packs:
        errors = validate_file(pack, validator)
        if errors:
            failures.extend(errors)
            print(f"FAIL {pack}")
            for error in errors:
                print(f"  - {error}")
        else:
            print(f"PASS {pack}")
            data = yaml.safe_load(pack.read_text(encoding="utf-8"))
            theme_ids[pack] = data["theme"]["id"]
    cross_pack = catalog_errors(theme_ids)
    for error in cross_pack:
        failures.append(error)
        print(f"FAIL {error}")
    if failures:
        print(f"theme-gate: {len(failures)} violation(s) across {len(packs)} pack(s)", file=sys.stderr)
        return 1
    print(f"theme-gate: all {len(packs)} pack(s) valid (schema v1)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
