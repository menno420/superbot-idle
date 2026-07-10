#!/usr/bin/env python3
"""theme-gate v0 — validate every theme pack under themes/.

Checks each ``themes/*.yaml`` against the minimal required manifest:
required fields present, types correct, names non-empty, generator
``produces`` references a declared currency, positive integer rates
(all enforced by ``idle_engine.theme.load_theme``), plus v0 string
budgets so a passing pack cannot overflow a chat embed at render time
(titles <= 256 chars, descriptions <= 1024 chars).

Exits 0 when every pack passes, 1 on any violation, 2 when no packs
exist (an empty themes/ directory is a wiring error, not a pass).
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from idle_engine.theme import Theme, load_theme  # noqa: E402

TITLE_BUDGET = 256  # chat-embed title cap
TEXT_BUDGET = 1024  # chat-embed field-value cap


def check_budgets(theme: Theme, path: Path) -> list[str]:
    errors: list[str] = []

    def title(where: str, value: str) -> None:
        if len(value) > TITLE_BUDGET:
            errors.append(f"{path}:{where}: name exceeds {TITLE_BUDGET}-char title budget")

    def text(where: str, value: str) -> None:
        if len(value) > TEXT_BUDGET:
            errors.append(f"{path}:{where}: description exceeds {TEXT_BUDGET}-char text budget")

    title("theme.name", theme.name)
    text("theme.description", theme.description)
    if not (len(theme.embed_color) == 7 and theme.embed_color.startswith("#")
            and all(c in "0123456789abcdefABCDEF" for c in theme.embed_color[1:])):
        errors.append(f"{path}:theme.embed_color: must be #RRGGBB hex, got {theme.embed_color!r}")
    for c in theme.currencies.values():
        title(f"currencies[{c.currency_id}].name", c.name)
        text(f"currencies[{c.currency_id}].description", c.description)
    for g in theme.generators.values():
        title(f"generators[{g.generator_id}].name", g.name)
        text(f"generators[{g.generator_id}].description", g.description)
    return errors


def validate_file(path: Path) -> list[str]:
    try:
        theme = load_theme(path)
    except Exception as exc:  # structural violation or unreadable YAML
        return [f"{path}: {exc}"]
    return check_budgets(theme, path)


def main(argv: list[str]) -> int:
    themes_dir = Path(argv[1]) if len(argv) > 1 else REPO_ROOT / "themes"
    packs = sorted(themes_dir.glob("*.yaml")) + sorted(themes_dir.glob("*.yml"))
    if not packs:
        print(f"theme-gate: no theme packs found under {themes_dir}", file=sys.stderr)
        return 2
    failures: list[str] = []
    for pack in packs:
        errors = validate_file(pack)
        if errors:
            failures.extend(errors)
            print(f"FAIL {pack}")
            for error in errors:
                print(f"  - {error}")
        else:
            print(f"PASS {pack}")
    if failures:
        print(f"theme-gate: {len(failures)} violation(s) across {len(packs)} pack(s)", file=sys.stderr)
        return 1
    print(f"theme-gate: all {len(packs)} pack(s) valid")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
