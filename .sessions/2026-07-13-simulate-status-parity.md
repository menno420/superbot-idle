# 2026-07-13 — simulate.py status parity: derive the two leftover PROVISIONAL strings from TABLE_STATUS

> **Status:** in-progress

- **📊 Model:** Fable-class (Claude 5 family) · medium · bugfix · docstring + stderr-header status derivation + parity-test extension + outbox process ask · 2026-07-13

## What this session does

Executes the status/label idea from the previous card
(`.sessions/2026-07-13-report-table-status.md` 💡): `tools/simulate.py`
still carries two hand-written PROVISIONAL strings that #99 deliberately
left in place — the module docstring's INTEGRITY FLOOR bullet ("Every
economy parameter remains PROVISIONAL until … rules on graduation",
~line 21) and `render_summary`'s stderr header "(PROVISIONAL: input to
Q-0264, not the verdict)" — so the human-facing summary disagrees with the
JSON label it summarizes, both stale since VERDICT 038 (PR #93) graduated
the seven-parameter table to SIM-PINNED.

- Rewire both to DERIVE from the already-parity-pinned `TABLE_STATUS`
  constant: the docstring keeps a literal `{TABLE_STATUS}` placeholder
  (a literal docstring cannot interpolate) that is substituted into
  `__doc__` at import time right after the constant is defined; the
  stderr header becomes an f-string over the constant. No duplicated
  status literals anywhere in the module.
- Extend `test_table_status_matches_registered_doc_badge`
  (tests/test_simulate.py) to also assert (a) the interpolated module
  docstring and the `render_summary(_QUICK)` header both carry
  `TABLE_STATUS`, and (b) the RAW docstring still contains the
  placeholder — so hard-coding a status back into either surface goes
  red, keeping the guard meaningful.
- Same PR, per the lane→manager channel: append the SIM-PINNED
  re-tuning process ask to `control/outbox.md` — the lane has a
  CONFIRMED tuning candidate (PRESTIGE_BONUS_PERCENT 10→25, VERDICT 038
  ASK2 CONFIRMED, r2 0.9175→0.8006) but no SIM-REQUEST mechanism covers
  re-tuning a value that is already SIM-PINNED.
- ZERO changes to the seven SIM-PINNED values, criterion semantics, A10
  logic, or `criteria_versions` behavior.

## Verify

- `python -m pytest -q` → (recorded at flip)
- Full harness run (`python3 tools/simulate.py --out …`) → (recorded at
  flip; expect ALL PASS, label/summary/docstring all reading SIM-PINNED,
  evidence numbers unchanged: first ratio ≈ 0.9175, final ratio ≈ 0.9661)
- `python3 bootstrap.py check --strict` pre-flip → (recorded at flip;
  expect exit 1 = the designed born-red hold on THIS card only)

## Close-out

(recorded at flip)
