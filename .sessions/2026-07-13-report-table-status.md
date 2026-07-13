# 2026-07-13 — pin run_report's parameter-table status label to economy-v1.md

> **Status:** `complete`

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
  (`**SIM-PINNED** (every numeric …`) and assert it equals the constant —
  plus assert the label actually derives from it — so a future graduation
  or de-graduation flips the report label red instead of silently lying.
- Update the existing label-shape assertion
  (`test_quick_report_shape_and_labels`) from the hard-coded
  `"PROVISIONAL"` substring to the constant.
- ZERO changes to the seven SIM-PINNED values, criterion semantics, A10
  logic, or `criteria_versions` behavior.

## Verify

- `python -m pytest -q` → **1264 passed, 1 skipped in 16.70s** (was 1263
  at HEAD; +1 = the new status-parity pin
  `test_table_status_matches_registered_doc_badge`).
- Full harness run (`python3 tools/simulate.py --out …`) → **ALL PASS**,
  label now reads "… The seven-parameter table is SIM-PINNED per
  docs/design/economy-v1.md (VERDICT 038; tuning a pinned value requires
  a fresh sim verdict).", evidence numbers unchanged from #97: first
  ratio 11536/12573 ≈ 0.9175, final ratio 1398/1447 ≈ 0.9661, max
  single-step decrease ≈ 0.0166 ≤ 0.02; `criteria_versions` still
  `{"A10": "v2"}`.
- `python3 bootstrap.py check --strict` pre-flip → exit 1, verbatim the
  designed born-red hold on THIS card only ("HOLD (by design): session
  card .sessions/2026-07-13-report-table-status.md declares an
  in-progress Status"); post-flip run recorded in the close-out push.
- Diff audit: none of the seven SIM-PINNED parameter values touched; A10
  gate logic and the `criteria_versions` stamp untouched.

## Close-out

- Claim-first honored: fast-lane PR #98 (work claim
  `control/claims/claude-report-table-status.md`) MERGED to main
  (53edf18) BEFORE build; claims dir + open PRs re-scanned at that HEAD,
  no competing claim or PR on this scope; claim file released in this
  flip commit per control/claims/README.md.
- Shipped in PR #99 (`claude/report-table-status`): `TABLE_STATUS`
  constant, label wording derived from it, parity test
  `test_table_status_matches_registered_doc_badge`, shape-test update.
  First CI wave: pytest / theme-gate / enable-auto-merge green,
  substrate-gate red = the designed born-red hold on this card.

## 💡 Session idea

`tools/simulate.py` still carries two hand-written PROVISIONAL strings
this PR deliberately left in place: the module docstring's INTEGRITY
FLOOR bullet ("Every economy parameter remains PROVISIONAL until …
rules on graduation") and `render_summary`'s stderr header
"(PROVISIONAL: input to Q-0264, not the verdict)" — so the human-facing
summary now disagrees with the JSON label it summarizes. Same cure,
zero new machinery: derive both from the already-parity-pinned
`TABLE_STATUS` (guard recipe: `render_summary` first `lines` entry +
docstring bullet ~line 21, tools/simulate.py; extend
`test_table_status_matches_registered_doc_badge` with a
`render_summary(_QUICK)` substring assert). (Deduped: a10-v2-provenance's
💡 was the JSON `label` field, landed here; no prior card touches the
stderr summary or docstring strings.)

## ⟲ Previous-session review

The a10-v2-provenance card's 💡 was again executable as written — it named
the stale sentence, the doc it drifted from, the exact test to pattern on
(`test_a10_criterion_version_matches_registered_doc_form`), and
pre-deduped itself, so this session spent its time on wording, not
archaeology. One gap: it didn't flag that
`test_quick_report_shape_and_labels` pins the old label with a hard-coded
`"PROVISIONAL"` substring assert (tests/test_simulate.py) — the one
extra file-touch this session had to discover by grep; a guard-recipe
line naming that assert would have made the slice fully mechanical.
