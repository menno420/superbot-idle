# 2026-07-13 — criteria_versions run-artifact provenance + v1-era artifact relabel

> **Status:** `complete`

- **📊 Model:** fable-5 · medium · feature build · criteria_versions provenance stamp + v1-era artifact retro-stamp + economy-v1 stale-note pointer · 2026-07-13

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

## Verify

- `python3 -m pytest -q` → **1263 passed, 1 skipped in 17.11s** (was 1262
  at HEAD; +1 = the provenance pin
  `test_report_stamps_criteria_versions_from_parity_pinned_constant`).
- Full harness run (`python3 tools/simulate.py --out …`) → **ALL PASS**,
  report carries `"criteria_versions": {"A10": "v2"}`, and the evidence
  numbers are unchanged from #95: first ratio 0.9175 (11536/12573), final
  ratio 1398/1447 ≈ 0.9661, max single-step decrease ≈ 0.0166 ≤ 0.02.
- Retro-stamp safety: the artifact loads + re-dumps byte-identical under
  the harness's exact `to_json` format BEFORE stamping (asserted in the
  stamping script), so the committed diff is exactly the 3-line
  `criteria_versions` insertion — no recorded number touched.
- `python3 bootstrap.py check --strict` pre-flip → exit 1, verbatim the
  designed born-red hold on THIS card only ("HOLD (by design): session
  card .sessions/2026-07-13-a10-v2-provenance.md declares an in-progress
  Status"); post-flip run recorded in the close-out push.
- Diff audit: none of the seven SIM-PINNED parameter values touched; the
  parity guard's parse target (economy-v1.md's `| A10 | O6 — v2 …` row)
  untouched.

## Close-out

- Claim-first honored: fast-lane PR #96 (work claim
  `control/claims/claude-a10-v2-provenance.md`) MERGED to main (70b2e8d)
  BEFORE build; claims dir + open PRs re-scanned at that HEAD, no
  competing claim or PR on this scope; claim file released in this flip
  commit per control/claims/README.md.
- Shipped in PR #97 (`claude/a10-v2-provenance`): `criteria_versions`
  stamp in `run_report` (from `A10_CRITERION_VERSION`), pinned test,
  sim-harness.md report-key mirror row + retro-stamp disclosure,
  v1-era artifact retro-stamped `{"A10": "v1"}`, economy-v1.md one-line
  **Done (PR #95, main `2ac6c5d`)** pointer on the stale Harness note.

## 💡 Session idea

The report's `label` field still hard-codes "Parameters remain PROVISIONAL
until the fleet Simulator seat / manager rules" — stale the same way the
economy-v1.md Harness note was: VERDICT 038 already graduated the table to
SIM-PINNED, so every fresh run emits an out-of-date provenance sentence.
Same cure as this PR, one layer up: pin the harness's parameter-status
wording to economy-v1.md's Status badge with a small constant + parity
test (the `test_a10_criterion_version_matches_registered_doc_form`
pattern), so a future graduation or de-graduation flips the report label
red instead of silently lying. (Deduped: #95's 💡 was the
`criteria_versions` stamp, landed here; no prior card proposes
label/status parity.)

## ⟲ Previous-session review

The a10-v2-harness-sync card's 💡 was executable as written — it named the
field, the source constants, and even pre-deduped itself against #93 — and
its Verify section quoting the evidence to the exact rational (1398/1447)
made re-verification at this session's HEAD a five-minute mechanical check.
One gap: it said "have the results-doc convention quote it" but left open
how the v1-era ARTIFACT itself should be marked (rename vs embedded field
vs companion note) — this session had to make that call; the retro-stamp
was chosen because renames would break references in frozen files
(status.md archive sections, prior cards) that convention forbids editing.
