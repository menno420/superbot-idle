# 2026-07-12 — ORDER 003: pytest CI on PR + push (GREEN ≠ TESTED)

> **Status:** `complete`

- **📊 Model:** opus-4.8 · high · idle-engine seat (ORDER 003 executor, coordinator-assigned) · 2026-07-12T~09:00Z–10:18Z (`date -u`)

## What happened

Executed ORDER 003 (`control/inbox.md`, 2026-07-12T08:30Z, P1). The gap
was real and verified at HEAD 45ff2bf: `.github/workflows/` held only
`substrate-gate.yml` (session/hygiene gate) + `theme-gate.yml`
(theme-schema validation), and `grep pytest` over both returned nothing
— no CI job executed the test suite, so a green PR was never actually
test-run (GREEN ≠ TESTED). No pre-existing pytest job to duplicate.

1. **New workflow** (`.github/workflows/pytest.yml`, job/check name
   `pytest`): runs `python3 -m pytest -q` on `pull_request` and
   `push:[main]`. Invocation is the repo's canonical one, documented
   identically across README / `CONVENTIONS.md` / `docs/architecture.md`
   / `docs/AGENT_ORIENTATION.md` (`python3 -m pytest -q && python3
   bootstrap.py check --strict`). Style mirrors the LANE-OWNED
   `theme-gate.yml` — `ubuntu-latest`, `actions/checkout@v4`,
   `actions/setup-python@v5` with `python-version: "3.x"`,
   `pip install --quiet` for deps (`pytest pyyaml jsonschema`; the repo
   ships no requirements.txt/pyproject, and the engine/theme loaders the
   tests exercise import yaml + jsonschema). Kept OUT of the kit-owned
   `substrate-gate.yml` on purpose — adopt/upgrade regenerates that file
   and would overwrite hand edits.
2. **Not wired as a required check** — branch protection is owner-only;
   filed as ⚑ OA-003 in `control/status.md`. Did NOT arm auto-merge and
   did NOT merge the PR.

Local verify before push: `python3 -m pytest -q` → **1131 passed in
12.26s**; `python3 bootstrap.py check --strict` (born-red advisory path,
absent-card sentinel) → all checks passed; `python3
tools/theme_gate.py themes` → all 12 packs valid; workflow YAML parses.
On PR #74 all three check-runs concluded **success**, including the new
`pytest` job (the ORDER's done-when).

## 💡 Session idea

The three workflows now each install their Python deps ad hoc
(`theme-gate` and `pytest` both `pip install --quiet pyyaml jsonschema`;
`pytest` adds `pytest`), and the repo has no `requirements*.txt` /
`pyproject.toml`, so `scripts/env-setup.sh`'s guarded manifest installs
are all no-ops — the declared-dependency set lives nowhere machine
-readable. Guard recipe: when a dep drift bites (a test imports a package
CI didn't install), add a `requirements-dev.txt` (`pytest pyyaml
jsonschema`) at repo root and point both `pytest.yml`'s "install test
deps" step and `theme-gate.yml`'s "install validator deps" step at
`pip install -r requirements-dev.txt`; `scripts/env-setup.sh` already
installs it automatically once the file exists (its `for req in
requirements.txt requirements-dev.txt` loop). One source of truth instead
of three inline lists.

## ⟲ Previous-session review

The lane was ARCHIVED-READY/dormant (close-out PR #70/#71); this session
is a clean resume on a new ORDER, exactly the "new ORDER in
control/inbox.md" resume trigger the archived `control/status.md` QUEUE
predicted. The archive-ready snapshot's discipline held here: the born-
red-first-commit → workflow → local-verify → PR → flip-complete sequence
from the SHIPPED RECORD was followed to the letter. One inherited fact
that mattered: `.gitattributes` already marks `telemetry/model-usage.jsonl`
merge=union (append-only-ledger hygiene, PR #63), so appending the
telemetry row carried zero rebase-conflict risk against concurrent PR
#72. This slice stayed config-only and file-disjoint from #72 (docs) as
instructed — no engine/theme/mechanics/docs touched.
