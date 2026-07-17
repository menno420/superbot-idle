# 2026-07-17 — theme loader-guard tests: pin the 14 structural-shape guards in `load_theme`

> **Status:** `in-progress`

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
