# 2026-07-13 — criteria_versions run-artifact provenance + v1-era artifact relabel

> **Status:** `in-progress`

## What this session does

Executes the run-ARTIFACT provenance idea from the previous card
(`.sessions/2026-07-13-a10-v2-harness-sync.md` 💡): after PR #95 synced the
harness to A10 v2, nothing in the report format records WHICH criterion
version a run was judged under, and the committed v1-era evidence run is
indistinguishable from a v2-era one.

- Stamp a `criteria_versions` object into `tools/simulate.py`'s report JSON
  (`run_report`), sourced from the SAME constant the doc↔harness parity
  guard pins (`A10_CRITERION_VERSION`) — no duplicated string literals —
  plus a pinned test and the `sim-harness.md` report-key mirror row.
- Relabel the v1-era artifact
  `docs/design/sim-results-2026-07-11-provisional.json` by retro-stamping
  the same field (`"criteria_versions": {"A10": "v1"}`) into it — ZERO
  recorded numbers changed, byte-exact serialization otherwise — with the
  retro-stamp disclosed in `sim-harness.md` § Provisional runs on record.
- Close the stale-note loop in `docs/design/economy-v1.md`: the A10
  re-registration record's "Harness note (follow-up, not this PR)" still
  claims the harness evaluates v1 — add a one-line done-(PR #95) pointer.
  ZERO changes to the seven SIM-PINNED values or any criterion semantics.
