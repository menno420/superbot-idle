#!/usr/bin/env python3
"""Repo-local preflight — the ONE check list for local ritual AND CI gate.

Contract (substrate-kit v1.16.0, `substrate.config.json` →
``preflight_scripts: ["scripts/preflight.py"]``; kit source
``_default_preflight_scripts`` + ``_run_preflight_scripts`` in
``bootstrap.py``): ``check``'s full lane runs this script from the repo
root under the same interpreter, and the CI substrate-gate's full lane
runs it too (its gate step invokes ``bootstrap.py check --strict``), so a
checker added HERE is enforced in both venues with zero workflow edits.
Exit non-zero on any failure — the runner turns that into an
exit-affecting ``preflight-script`` finding and shows the last non-empty
output line, so every failure path below ends with one clear line.

What it runs — this repo's real verify line, exactly as CI invokes it:

- ``python3 -m pytest -q``                (mirrors ``pytest.yml``)
- ``python3 tools/theme_gate.py themes``  (mirrors ``theme-gate.yml``)

Venue note: the substrate-gate runner installs NO third-party deps
(stdlib-only by design), while ``pytest.yml``/``theme-gate.yml`` pip-install
``pytest pyyaml jsonschema`` before their runs. To keep one check list that
works in BOTH venues, missing deps are installed quietly here first (a
no-op locally where they already exist). Never invokes ``bootstrap.py
check`` — the kit's nested-run guard (``_PREFLIGHT_NESTED_ENV``) exists
because the outer check owns this leg.
"""

from __future__ import annotations

import importlib.util
import subprocess
import sys

# (import-name, pip-name) — the same trio pytest.yml / theme-gate.yml
# install in CI; import names differ from pip names only for PyYAML.
_DEPS = (("pytest", "pytest"), ("yaml", "pyyaml"), ("jsonschema", "jsonschema"))

# The repo's canonical verify line (README / CONVENTIONS.md), byte-equal to
# the CI jobs' run steps so local and CI can never disagree on semantics.
_CHECKS = (
    ("pytest", [sys.executable, "-m", "pytest", "-q"]),
    ("theme-gate", [sys.executable, "tools/theme_gate.py", "themes"]),
)


def _ensure_deps() -> None:
    missing = [pip for mod, pip in _DEPS if importlib.util.find_spec(mod) is None]
    if not missing:
        return
    print(f"preflight: installing missing deps: {' '.join(missing)}")
    proc = subprocess.run(
        [sys.executable, "-m", "pip", "install", "--quiet", *missing],
        check=False,
    )
    if proc.returncode != 0:
        print(f"preflight: pip install {' '.join(missing)} failed "
              f"(exit {proc.returncode}) — cannot run the check list")
        sys.exit(1)


def main() -> int:
    _ensure_deps()
    for name, argv in _CHECKS:
        print(f"preflight: {name}: {' '.join(argv[1:])}")
        proc = subprocess.run(argv, check=False)
        if proc.returncode != 0:
            print(f"preflight: {name} FAILED (exit {proc.returncode})")
            return proc.returncode or 1
    print("preflight: all checks passed (pytest + theme-gate)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
