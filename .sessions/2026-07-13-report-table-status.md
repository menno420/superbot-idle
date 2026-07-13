# 2026-07-13 — pin run_report's parameter-table status label to economy-v1.md

> **Status:** `in-progress`

- **📊 Model:** Fable-class (Claude 5 family) · medium · bugfix · report table-status label constant + doc↔harness parity test · 2026-07-13

## What this session does

Executes the label/status-parity idea from the previous card
(`.sessions/2026-07-13-a10-v2-provenance.md` 💡): the report's `label`
field in `tools/simulate.py`'s `run_report` still hard-codes "Parameters
remain PROVISIONAL until the fleet Simulator seat / manager rules" — stale
since VERDICT 038 (PR #93) graduated the seven-parameter table to
SIM-PINNED, so every fresh run emits an out-of-date provenance sentence.

- Add a module-level `TABLE_STATUS = "SIM-PINNED"` constant next to
  `A10_CRITERION_VERSION` in `tools/simulate.py` and derive the report's
  parameter-status wording from it (label states the table is SIM-PINNED
  per docs/design/economy-v1.md; the "harness output is INPUT to the
  verdict, not the verdict" half stays — that part is still true).
- Add a doc↔harness parity test (the
  `test_a10_criterion_version_matches_registered_doc_form` pattern from
  #95): regex the Status-badge token out of `docs/design/economy-v1.md`
  and assert it equals the constant, so a future graduation or
  de-graduation flips the report label red instead of silently lying.
- ZERO changes to the seven SIM-PINNED values, criterion semantics, A10
  logic, or `criteria_versions` behavior.

## Verify

- `python3 -m pytest -q` — expect 1264+ passed (baseline 1263 at HEAD;
  +1 = the new status-parity pin).
- Full harness run (`python3 tools/simulate.py --out …`) — report label
  carries the SIM-PINNED wording sourced from the constant, still ALL
  PASS, evidence numbers unchanged from #97.
- `python3 bootstrap.py check --strict` pre-flip → exit 1 attributable
  ONLY to this card's born-red hold; post-flip → exit 0.
