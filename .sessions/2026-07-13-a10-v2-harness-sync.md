# 2026-07-13 — A10 v1→v2 harness sync + criterion-version parity guard

> **Status:** `in-progress`

- **📊 Model:** fable-5 · medium · bugfix · A10 harness sync to v2 TREND form + doc↔harness version parity guard · 2026-07-13

## What this session does

Executes the follow-up flagged by PR #93's close-out guard recipe (and the
economy-v1.md re-registration record's own "Harness note"): after VERDICT
038's conditional graduation, `docs/design/economy-v1.md` registers A10 at
**v2 (TREND form)** while `tools/simulate.py` still evaluates the **v1
strict per-step gate** — a live doc↔harness criterion drift.

- Sync `tools/simulate.py` (`evaluate_criteria` A10 branch + `_o6_table`)
  to A10 v2 exactly as registered: the consecutive reset-duration ratio
  sequence rises toward 1 across the window (final consecutive ratio ≥
  first consecutive ratio), and any single-step ratio decrease stays
  within a 0.02 wiggle band of its predecessor.
- Expose the implemented criterion version machine-readably
  (`A10_CRITERION_VERSION = "v2"`).
- Update the pinned A10 tests in `tests/test_simulate.py` to the v2 form
  (including the key v1→v2 behavioral delta: an in-band dip with a rising
  trend now PASSES).
- Add a doc↔harness parity guard: a test parses the A10 version token out
  of economy-v1.md's registered criterion row and asserts it equals the
  harness constant — re-register a criterion without updating the harness
  (or vice versa) and the suite goes red.
- ZERO changes to the seven SIM-PINNED parameter values.
