# 2026-07-15 — truth refresh: kit version claims in docs

> **Status:** `in-progress`
> **Branch:** `claude/truth-refresh` · claim `control/claims/claude-truth-refresh.md`

- **📊 Model:** fable-5 · medium · docs-only — truth refresh: correct stale kit-version claims (v1.15.0 → measured v1.16.0) in docs/ + current-state truth-stamp re-groom · session opened 2026-07-15T04:18Z (`date -u`)

**Goal:** the tree runs substrate-kit v1.16.0 (measured this session:
`python3 bootstrap.py --version` → `substrate-kit 1.16.0`, matching
`substrate.config.json` → `kit_version: "1.16.0"`; the bump landed via
PR #134 `3df5449`), but two docs still claim v1.15.0. Correct those
claims, re-stamp `docs/current-state.md` against HEAD `8a7275d`, and
re-verify the rest of the current-state ledger at HEAD (correct what
moved, keep what's still true). The OA-003 owner ask (mark `pytest`
required) stays untouched — it is still open.

**Baseline at HEAD `8a7275d` (before edits):**
`python3 bootstrap.py check --strict` → exit 0, all checks passed
(6 pre-existing advisory `model-line-class` warnings on older cards,
never exit-affecting); `python3 -m pytest -q` →
`1381 passed, 1 skipped in 12.47s`.

## What happened

(close-out pending — flipped at session end)
