# 2026-07-13 — ORDER 005: economy v1 parameter table PROVISIONAL → SIM-PINNED (VERDICT 038)

> **Status:** `complete`

- **📊 Model:** fable-5 · medium · docs-only · ORDER 005 — SIM-001/VERDICT-038 conditional graduation · 2026-07-13

## What this session does

Consumes sim-lab VERDICT 038 for SIM-001 (economy-FEEL cluster; relay:
control/inbox.md ORDER 005, 2026-07-13T13:40:58Z; packet @ `d992c568`
control/outbox.md § SIM-REQUEST economy-FEEL). Verdict CONDITIONAL:

- Graduate the seven-parameter table in `docs/design/economy-v1.md`
  PROVISIONAL → SIM-PINNED, conditional on re-registering A10 in trend
  form in the SAME PR. ZERO parameter value changes.
- Strict A10 fails, but all 6 violations sit inside the registered 0.02
  wiggle band (max 0.0166, ~83% of band); the consecutive-ratio trend
  rises 0.9175 → 0.9661 (toward 1) — shrinkage is not super-exponential,
  which is A10's registered intent.
- Companion `docs/design/upgrades-prestige-v0.md` status badge flipped in
  the same PR per economy-v1.md's own registered graduation semantics
  ("updating this doc and `upgrades-prestige-v0.md` together").
- Out of scope, recorded only: ASK1 CONFIRMED-INERT (min-visible-delta
  feltness floor is engine-side, needs its own sim); ASK2 CONFIRMED
  (PRESTIGE_BONUS_PERCENT 10→25 is a candidate row, NOT a mandate — no
  value changed here); co-consumer fm owner-queue E#52.

## Verify

- `python3 -m pytest -q` → **1260 passed, 1 skipped in 13.99s** (run before
  push at the doc-edit commit).
- `python3 bootstrap.py check --strict` pre-flip → exit 1, verbatim the
  designed born-red hold on THIS card only ("HOLD (by design): session card
  .sessions/2026-07-13-economy-v1-sim-pinned.md declares an in-progress
  Status"); post-flip run recorded green in the close-out push.
- Diff audit: none of the seven parameter table rows appear in the diff —
  zero numeric value changes (grep of the diff for all seven constant names
  matches only a prose ledger note, no table row).

## Close-out

- Claim-first honored: fast-lane PR #92 (claim + claimed-by) MERGED
  2026-07-13T17:29:27Z BEFORE build; no competing claim/PR on
  economy-v1.md; claim file released in this PR at session close.
- Shipped in PR #93: economy-v1.md badge + table section → SIM-PINNED
  citing VERDICT 038; A10 v2 TREND-form row + full re-registration record;
  upgrades-prestige-v0.md badge flipped same-PR per the doc's registered
  graduation semantics; ORDER 005 status ack rides the same PR (done-when
  lands atomically).
- Wall (verbatim): `Access denied: repository "menno420/sim-lab" is not
  configured for this session. Allowed repositories:
  menno420/superbot-games, menno420/superbot-idle` — verdict payload +
  fixtures.json `a10_trend_wording_proposed` unreachable; A10 v2 text
  registered from the ORDER's quoted verdict terms per the verdict's own
  delegation ("final text is this seat's to register").
- Guard recipe (follow-up): tools/simulate.py `evaluate_criteria` A10
  branch + `_o6_table` still implement A10 v1 strict; update to v2 trend
  form + flip the synthetic-measures pin in
  `tests/test_simulate.py::test_each_criterion_reds_on_its_own_violation`.

## 💡 Session idea

The doc↔engine parity test (`tests/test_economy_design_doc.py`) pins
parameter VALUES but nothing pins criterion WORDING to the harness: after
this session, `docs/design/economy-v1.md` registers A10 v2 (trend form)
while `tools/simulate.py` still evaluates A10 v1 (strict) — a silent
doc-vs-harness criterion drift the suite cannot see. Cheap durable guard:
tag each acceptance-criterion row with a machine-readable version token
(`A10 · v2`), expose the implemented criterion version from
`tools/simulate.py` (e.g. `CRITERIA_VERSIONS = {"A10": 1}`), and add a
parity test asserting doc token == harness constant — re-register a
criterion without updating the harness (or vice versa) and the suite goes
red, same pattern as the parameter-table mirror. (Deduped: the sim-harness
card's 💡 proposed the tolerance re-registration itself — now done; this
guards the REGISTRATION↔HARNESS agreement going forward. Not in any prior
card or ledger.)

## ⟲ Previous-session review

The 2026-07-11-sim-harness session's 💡 called this ruling's shape almost
exactly — "re-register A10 with an explicit tolerance (e.g. monotone trend
over a k-reset window)" — and VERDICT 038 ruled precisely that combination
(trend gate + 0.02 per-step band), which made this session's registration
a transcription job instead of a design job: pre-registering the ambiguity
(AMB-6/AMB-11) paid off. One gap it left: its guard recipe located the
harness anchors but no guard was landed, so the doc and harness now
disagree on A10 until the follow-up — the recipe above carries it forward.
