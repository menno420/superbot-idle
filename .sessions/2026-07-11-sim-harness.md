# 2026-07-11 — SIM-001 executable harness (tools/simulate.py)

> **Status:** `complete`

- **📊 Model:** fable-5 · high · sim-harness seat (SIM-001 harness builder, coordinator-assigned) · 2026-07-11T17:23Z–17:4xZ (`date -u`)

## What happened

Turned the pre-registered SIM-001 simulation request (economy-v1.md, Q-0264)
into a committed, deterministic, runnable tool — one build PR after a control
fast-lane claim (PR #52, `control/claims/sim-harness.md`, merged then removed
here). INTEGRITY FLOOR held: zero economy-parameter changes, zero verdicts —
the harness computes and reports; graduation stays with the Simulator/manager.

1. **`tools/simulate.py`** — stdlib-only, no wall clock, no randomness.
   Scenarios S1 (idle-only), S2 (check-in every N ∈ {0.25, 2, 8, 24} h:
   credit → greedy-buy → prestige iff eligible), S3 (S2's policy at
   1-second granularity), 14-day horizon, driving the REAL engine functions
   only. S3 runs as exact integer event scheduling — between actions the
   rate is a constant integer, so jumping `ceil(need/rate)` seconds with one
   `tick` is provably identical to looping 1-second ticks (the engine's
   test-enforced tick/offline equivalence) — full 14-day run in ~20 s.
   Emits O1–O6, evaluates A1–A10 against T1–T10 (exact rational arithmetic),
   JSON report to stdout/`--out`, human PASS/FAIL table to stderr,
   `--quick` smoke mode (2-day horizon, criteria flagged non-meaningful).
2. **Ambiguities implemented literally, never silently** — 11 recorded
   readings (AMB-1..11) in the report's `ambiguities` field AND
   `docs/design/sim-harness.md`: S1's null O1, post-reset re-seed of the
   fixed tier1 generator (apply_prestige wipes `owned`), A7's
   strictly-before-prestige visits, A8's purchase-to-purchase gaps, A10's
   strict non-decreasing-ratio gate vs O6's trend-based super-geometric
   flag, band-endpoint inclusivity, buy-then-prestige recording.
3. **`docs/design/sim-harness.md`** — how to run, report layout, the
   explicit statement that harness results are INPUT to the Q-0264 verdict,
   not the verdict; cross-linked from economy-v1.md's SIM-001 section
   (orphan check green).
4. **Provisional run on record** —
   `docs/design/sim-results-2026-07-11-provisional.json` (full 14-day run,
   labeled PROVISIONAL/UNOFFICIAL): **A1–A9 PASS, A10 FAIL** under the
   strict literal reading — O6 consecutive reset-duration ratios wiggle at
   single integer-floor steps (0.9175 → 0.9080 at reset 3) while the trend
   rises toward 1 (final 0.9661), so shrinkage is NOT super-geometric
   (flag false). Also surfaced for the ruling: S3 reaches ~80k resets in 14
   days (late resets shrink to ~seconds).
5. **Tests 827 → 838** (`tests/test_simulate.py`): byte-identical double
   run (CLI subprocess + in-process/CLI parity), S1 closed-form spot check
   (threshold crossing at exactly 100000 s; first purchases at 60 → 69),
   red/green per-criterion evaluation on synthetic measures, band-endpoint
   inclusivity + A8 strictness pins, check-in grid exactness, O5 payback
   hand value, quick-mode smoke.

Verify: `python3 -m pytest -q` → 838 passed; `python3 bootstrap.py check
--strict` green with this flip; `python3 tools/theme_gate.py themes` →
all 12 packs valid.

## 💡 Session idea

The A10 wording ("each reset's duration ratio non-decreasing toward 1")
is the one criterion whose literal gate trips on integer-floor noise while
its intent (no runaway shrinkage) clearly holds — the provisional run makes
that concrete with exact ratios. When the Simulator rules Q-0264, the ruling
should either bless the strict gate (and the FAIL stands until re-registered
parameters smooth the ladder) or re-register A10 with an explicit tolerance
(e.g. monotone trend over a k-reset window). Guard recipe: gate logic lives
in `evaluate_criteria` (A10 branch) + `_o6_table` in `tools/simulate.py`;
red/green pins in `tests/test_simulate.py::test_each_criterion_reds_on_its_own_violation` —
a re-registered tolerance lands as one branch change plus one synthetic-
measures test flip.

## ⟲ Previous-session review

The economy slice-(d) card pre-registered SIM-001 as "executable without
follow-up questions" — mostly true: the engine surface was exactly
sufficient (no reimplementation needed anywhere), but 11 literal-reading
choices still had to be recorded, the biggest being that `apply_prestige`
wipes `owned` while the reference world fixes tier1 at count 1 (AMB-3: the
harness re-seeds; a sim built without noticing would silently flatline
after reset 1). The upgrades-prestige card's "what the Simulator must pin"
list (dead zone, ×1.15 vs +25%, 20-reset stacking) is now answered with
committed numbers: no dead zone (A8 at 9.7% of run), first-session pacing
holds (A1/A2), and stacking is sub-exponential in trend though not in the
strict A10 gate — precisely the call Q-0264 exists to make.
