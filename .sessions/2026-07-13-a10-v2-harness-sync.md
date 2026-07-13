# 2026-07-13 — A10 v1→v2 harness sync + criterion-version parity guard

> **Status:** `complete`

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
  (`A10_CRITERION_VERSION = "v2"`, `A10_WIGGLE_BAND = Fraction(2, 100)`).
- Update the pinned A10 tests in `tests/test_simulate.py` to the v2 form
  (including the key v1→v2 behavioral delta: an in-band dip with a rising
  trend now PASSES).
- Add a doc↔harness parity guard: a test parses the A10 version token out
  of economy-v1.md's registered criterion row and asserts it equals the
  harness constant — re-register a criterion without updating the harness
  (or vice versa) and the suite goes red.
- ZERO changes to the seven SIM-PINNED parameter values.

## Verify

- `python3 -m pytest -q` → **1262 passed, 1 skipped in 13.81s** (was 1260
  at HEAD; +2 = the v2-semantics pin and the parity guard).
- Full harness run (`python3 tools/simulate.py`) → **ALL PASS**, and the
  A10 row reproduces VERDICT 038's evidence numbers exactly: first ratio
  0.9175 (11536/12573), final ratio 1398/1447 ≈ 0.9661, max single-step
  decrease ≈ 0.0166 ≤ 0.02.
- `python3 bootstrap.py check --strict` pre-flip → exit 1, verbatim the
  designed born-red hold on THIS card only ("HOLD (by design): session
  card .sessions/2026-07-13-a10-v2-harness-sync.md declares an
  in-progress Status"); post-flip run recorded green in the close-out
  push.
- Diff audit: none of the seven SIM-PINNED parameter values touched —
  the diff is tools/simulate.py + tests/test_simulate.py +
  docs/design/sim-harness.md (AMB-6/AMB-11 mirror rows) + session card +
  telemetry row + claim release.
- CI at the impl push (head 4372f1a): pytest ✅, theme-gate ✅,
  enable-auto-merge ✅, substrate-gate ❌ = the designed pre-flip HOLD.

## Close-out

- Claim-first honored: fast-lane PR #94 (work claim
  `control/claims/claude-a10-v2-harness-sync.md`) MERGED to main
  (4ebe037) BEFORE build; claims dir + open PRs scanned at HEAD, no
  competing claim or PR on the simulate.py A10 scope; claim file released
  in this flip commit per control/claims/README.md.
- Shipped in PR #95 (`claude/a10-v2-harness-sync`): A10 v2 TREND gate in
  `_a10_v2_gate` (shared by `evaluate_criteria` and `_o6_table`'s
  reported fields), machine-readable `A10_CRITERION_VERSION`, v2 pinned
  tests (`test_a10_v2_trend_form_semantics` — in-band dip passes, over-band
  dip fails, falling trend fails, 0.02 boundary inclusive), parity guard
  (`test_a10_criterion_version_matches_registered_doc_form`), AMB-6
  recorded RESOLVED in both the report's ambiguities list and the
  sim-harness.md mirror.
- economy-v1.md untouched: the registered v2 row is the parity guard's
  parse target; its "Harness note (follow-up, not this PR)" bullet now
  reads historical — flagged below, not edited, to keep the registration
  record append-only in spirit.

## 💡 Session idea

The committed run artifact `docs/design/sim-results-2026-07-11-provisional.json`
was evaluated under the A10 **v1** gate, so its `criteria` rows (A10 FAIL,
`all_pass: false`) are now version-stamped-stale evidence — and nothing in
the report format records WHICH criterion version a run was judged under.
Cheap durable guard: emit a `criteria_versions` field into the report JSON
itself (from the same constants the parity guard pins, e.g.
`{"A10": "v2"}`), and have the results-doc convention quote it — every
committed run becomes self-describing provenance, so a future
re-registration can never silently mix v1-era evidence with v2-era claims.
(Deduped: #93's 💡 was the doc↔harness parity guard, landed here; this is
run-ARTIFACT provenance stamping, which no prior card proposes.)

## ⟲ Previous-session review

PR #93's re-registration record made this sync mechanical in the best way:
the v2 row's three clauses (trend toward 1, final ≥ first, 0.02 single-step
band) translated 1:1 into `_a10_v2_gate`, and the full-run harness then
reproduced the verdict's quoted evidence to the digit (0.9175 → 1398/1447 ≈
0.9661, max dip 0.0166 ≈ 83% of band) — a registration precise enough to be
executable is exactly what the integrity floor wants. One nit: its
"Harness note (follow-up, not this PR)" bullet in economy-v1.md goes stale
the moment this PR lands, and the record offers no slot for a "done"
pointer — the next registration record could pre-commit a one-line
follow-up ledger line to close its own loop.
