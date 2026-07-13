# 2026-07-13 — simulate.py status parity: derive the two leftover PROVISIONAL strings from TABLE_STATUS

> **Status:** `complete`

- **📊 Model:** Fable-class (Claude 5 family) · medium · bugfix · docstring + stderr-header status derivation + parity-test extension + outbox process ask · 2026-07-13

## What this session does

Executes the status/label idea from the previous card
(`.sessions/2026-07-13-report-table-status.md` 💡): `tools/simulate.py`
still carried two hand-written PROVISIONAL strings that #99 deliberately
left in place — the module docstring's INTEGRITY FLOOR bullet ("Every
economy parameter remains PROVISIONAL until … rules on graduation",
~line 21) and `render_summary`'s stderr header "(PROVISIONAL: input to
Q-0264, not the verdict)" — so the human-facing summary disagreed with the
JSON label it summarizes, both stale since VERDICT 038 (PR #93) graduated
the seven-parameter table to SIM-PINNED.

- Rewired both to DERIVE from the already-parity-pinned `TABLE_STATUS`
  constant: the docstring keeps a literal `{TABLE_STATUS}` placeholder
  (a literal docstring cannot interpolate) that is substituted into
  `__doc__` at import time right after the constant is defined; the
  stderr header is an f-string over the constant. No duplicated status
  literals anywhere in the module.
- Extended `test_table_status_matches_registered_doc_badge`
  (tests/test_simulate.py) to also assert (a) the interpolated module
  docstring and the `render_summary(_QUICK)` header both carry
  `TABLE_STATUS`, and (b) the RAW docstring (via `ast.get_docstring`)
  still contains the placeholder — so hard-coding a status back into
  either surface goes red, keeping the guard meaningful.
- Same PR, per the lane→manager channel: appended the SIM-PINNED
  re-tuning PROCESS ASK to `control/outbox.md` (append-only honored) —
  the lane has a CONFIRMED tuning candidate (PRESTIGE_BONUS_PERCENT
  10→25, VERDICT 038 ASK2 CONFIRMED, r2 0.9175→0.8006) but no
  SIM-REQUEST mechanism covers re-tuning a value that is already
  SIM-PINNED; asked the manager to route a process ruling (sim-lab
  re-verdict path OR re-registration protocol) with this candidate as
  the first case.
- ZERO changes to the seven SIM-PINNED values, criterion semantics, A10
  logic, or `criteria_versions` behavior.

## Verify

- `python3 -m pytest -q` → **1264 passed, 1 skipped in 16.88s** (same
  count as HEAD — the extension deepens an existing test, no new test
  function).
- Full harness run (`python3 tools/simulate.py --out …`) → **ALL PASS**;
  stderr header now "SIM-001 harness — per-criterion summary (table
  SIM-PINNED: harness output is input to a verdict, not the verdict)";
  interpolated docstring bullet reads "… registered status is SIM-PINNED
  per docs/design/economy-v1.md …"; evidence numbers UNCHANGED from #99:
  first ratio 11536/12573 ≈ 0.9175, final ratio 1398/1447 ≈ 0.9661;
  `criteria_versions` still `{"A10": "v2"}`.
- `python3 bootstrap.py check --strict` pre-flip → exit 1, verbatim the
  designed born-red hold on THIS card only ("HOLD (by design): session
  card .sessions/2026-07-13-simulate-status-parity.md declares an
  in-progress Status"); post-flip run recorded in the close-out push.
- Diff audit: none of the seven SIM-PINNED parameter values touched; A10
  gate logic and the `criteria_versions` stamp untouched; outbox strictly
  appended (no prior entry edited).

## Close-out

- Claim honored: `control/claims/claude-simulate-status-parity.md` landed
  in this branch's FIRST commit (1c62b30, alongside this born-red card +
  telemetry row); claims dir (only README.md present) + open PRs (zero)
  scanned at HEAD 4c31a2c before build — no competing claim or PR on this
  scope; claim file released in this flip commit per
  control/claims/README.md.
- Shipped in PR #100 (`claude/simulate-status-parity`): docstring
  placeholder + `__doc__` substitution, f-string stderr header, parity-test
  extension, outbox PROCESS ASK. First CI wave at head 8d9e7cc: pytest /
  theme-gate / enable-auto-merge green, substrate-gate red = the designed
  born-red hold on this card.

## 💡 Session idea

`docs/design/sim-harness.md` drifted the same way the harness strings
did: its header note (~line 6, "**PROVISIONAL** until the fleet Simulator
seat / manager rules on graduation") and its report-shape table row
(~line 68, "`label` | the PROVISIONAL / not-the-verdict statement") still
describe the table as PROVISIONAL — stale since VERDICT 038/PR #93. A doc
can't derive from a constant, so use the parity-pin half of the recipe:
reword both spots to point at the economy-v1.md Status badge / the
`TABLE_STATUS` constant, and extend
`test_table_status_matches_registered_doc_badge` with a regex pin on
sim-harness.md so the mirror doc goes red on the next re-grade (~line 88's
PROVISIONAL is the recorded 2026-07-11 run's historical description —
leave it). (Deduped: report-table-status's 💡 was the two harness strings,
landed here; a10-v2-provenance's 💡 was the JSON label, landed in #99; no
prior card touches sim-harness.md's status wording.)

## ⟲ Previous-session review

The report-table-status card's 💡 was again executable as written — it
named both stale strings with locations, the exact test to extend, and
even the `render_summary(_QUICK)` substring-assert recipe, and it
pre-deduped itself against a10-v2-provenance; this session spent its time
on the one design decision the idea left open (HOW a literal docstring
derives from a constant — placeholder + import-time `__doc__`
substitution, with an `ast.get_docstring` raw-placeholder pin so the
mechanism itself is guarded). One gap: it didn't flag that
`docs/design/sim-harness.md` mirrors the same PROVISIONAL wording in two
live spots — the sibling drift this card's 💡 now files.
