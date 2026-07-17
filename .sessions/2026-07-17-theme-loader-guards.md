# 2026-07-17 — theme loader-guard tests: pin the 14 structural-shape guards in `load_theme`

> **Status:** `complete`

- **📊 Model:** neutral builder-agent · high · tests · idle-engine seat (theme loader coverage) · 2026-07-17T16:28Z (`date -u`)

## What / why

`idle_engine/theme.py` is the only engine-core module under 100% coverage (94%).
The 14 missed lines are all defensive **structural-shape** guards in `load_theme` —
the checks that reject a malformed theme pack *before* any semantic/referential
validation runs: a non-mapping pack, a missing `theme` block, `currencies`/
`generators` that are not non-empty lists, non-mapping list items in the
`currencies`/`generators`/`balance`/`upgrades`/`milestones` blocks, a duplicate
upgrade id, and the "when present, must be a (non-empty) list/mapping" guards on
the optional `upgrades`/`prestige`/`labels`/`milestones` blocks.

The existing `tests/test_theme.py` covers only the *semantic* rejections
(unknown currency reference, unknown/duplicate milestone slot, bad offline
template, unknown label slot) and the happy-path noun mapping — it never trips
the structural guards, so a regression that dropped one would stay green. This
slice pins the reject side of every one, mirroring the accept/reject discipline
`tests/test_engine_guards.py` already established for the pure-domain math.

Test-only: no product code changes. New file
`tests/test_theme_loader_guards.py`, one case per guard, each building a minimal
malformed pack dict and asserting `pytest.raises(ValueError, match=…)` against
the exact message fragment read from the source (not guessed).

## Verification

- `python3 -m pytest -q` — full sb-free suite (recorded in the flip commit).
- Coverage of `idle_engine/theme.py` → 100% (the 14 previously-missed guard
  lines exercised); engine core fully covered.
- `python3 bootstrap.py check --strict`.

## Landing (born-red convention)

Card born RED (`in-progress`) in the first commit alongside
`control/claims/claude-theme-loader-guards.md`; then the test file + the
`docs/current-state.md` suite-count truth fix; card flipped `complete` as the
last commit to clear the born-red HOLD so substrate-gate goes green and the
landing workflow can merge on all-green. PR opened READY; the worker does not
merge its own PR.

## 💡 Session idea

Coverage now pins the reject side of every `load_theme` structural guard, but a
guard whose *message* drifts (e.g. a copy-edit that renames a block) would still
pass a `match=` fragment if the fragment is loose. A cheap follow-up: assert the
guard messages against a single source-of-truth table so a wording change turns
one obvious test red instead of silently loosening the contract — the same
"one canonical string, asserted both ways" discipline the label/milestone
semantic tests already lean on.

## ⟲ Previous-session review

The prior tests slice (`tests: cover idle_engine defensive-guard edge cases`,
PR #146) pinned the pure-domain math guards in `tests/test_engine_guards.py`
but stopped at the engine core's *values*; it did not touch the SKIN loader, so
`idle_engine/theme.py` stayed the lone sub-100% engine-core module at 94%. This
session extends the identical accept/reject discipline to the loader's structural
pass, closing the last 14 lines. No product code changed by either slice.
