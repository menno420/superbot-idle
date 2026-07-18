# 2026-07-18 — docs: reconcile stale suite counts in current-state

> **Status:** `complete`

- **📊 Model:** neutral builder-agent · low · docs-only · docs-truth seat (suite-count reconcile) · 2026-07-18T00:00Z (`date -u`)

## What / why

The `docs/current-state.md` living ledger claimed **1415 passing, 1 skipped
sb-free**, groomed 2026-07-15 against `8a7275d` (post-PR #139). Since then the
catalog grew by the apiary and forge packs (PRs up to #161) plus other slices,
and each parametrized per-pack test family lifts the collected count. A fresh
`python3 -m pytest -q` at HEAD `97e4c71` reports **1561 passed, 1 skipped** —
a 146-test drift the doc never absorbed.

This slice reconciles the sb-free suite claim (**1415 → 1561**, two mentions:
the header groom note and the Stability-baseline "Test suite" bullet) and the
present-tense `pytest-with-host` job count (**1378 → 1576**): the host job runs
the sb-free set plus the 15 manifest-contract tests that show as `1 skipped`
sb-free, i.e. `1561 + 15 = 1576` passed with zero skips — arithmetic the same
bullet already states ("the 15 extra manifest-contract tests on top of that").

Deliberately **not** touched: the historical PR-#107 "Recently shipped" line
(`1378 passed` at that PR's time is a dated shipped-record fact, not a
present-tense claim), and every other historical `N → M` narrative count. The
counts-guard test (`tests/test_current_state_counts.py`) leaves the suite-size
claim unguarded by design (self-referential), so this is a pure prose
truth-fix with no test coupling.

## Verification

- `python3 -m pytest -q` — full suite green (the count the doc now reports).
- `python3 bootstrap.py check --strict` — only the born-red HOLD expected
  (this card, until flipped `complete`).

## Landing (born-red convention)

Card born RED (`in-progress`) in the first commit alongside
`control/claims/claude-docs-suite-count-reconcile.md`; then the doc edit; card
flipped `complete` as the last commit to clear the HOLD so substrate-gate goes
green and the landing workflow merges on all-green. PR opened READY; the worker
does not merge its own PR.

## 💡 Session idea

The counts-guard test already pins the pack total and the setup-vector tallies
to ground truth so they red on drift, but it deliberately skips the suite-size
claim because it is self-referential (any added test moves the number). A
middle path exists: a guard that does not pin the exact integer but asserts the
doc's claimed sb-free count is **not less than** a floor recorded at last groom
(monotone — the suite only grows), or a `make groom-counts` helper that prints
the current `pytest`/pack/vector numbers next to the doc's claims so a groomer
sees the delta in one command instead of hand-diffing. Cheap, and it would have
surfaced this 146-test gap the day it opened.

## ⟲ Previous-session review

The prior content slices (apiary #-, forge #161) each bumped the machine-guarded
pack count (19 → 20) via `test_properties.py` + the counts-guard, but neither
touched the prose suite-size line — correctly, per the standing trap that
feature slices must not edit the conflict-magnet suite-count line. That is
exactly why a dedicated reconcile slice exists: the guarded counts stay honest
per-merge, while the unguarded prose count is swept periodically. This slice is
that sweep for the 2026-07-15 → 2026-07-18 window.
