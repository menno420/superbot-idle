---
name: quality-gate
description: "Run the project's full verification before pushing and report what must be fixed."
---

# quality-gate

Prove a change is good before pushing superbot-idle.

1. Run `python3 -m pytest -q && python3 bootstrap.py check --strict (theme packs additionally validate via the theme-gate step once ORDER 000 lands it in CI)` — the project's full verification (tests + lint/types).
2. Run `python3 bootstrap.py check --strict` — doc + session-log hygiene.
3. Report every failure with the exact command to reproduce it.
4. Do NOT push on red — green here should mean green in CI.

Declared capabilities: run.
