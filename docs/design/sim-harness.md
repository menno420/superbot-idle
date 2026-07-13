# SIM-001 harness — executable form of the economy-v1 simulation request

> **Status:** `reference` — committed 2026-07-11. The harness COMPUTES and
> REPORTS; it never tunes and never rules. **Harness results are INPUT to the
> Q-0264 verdict, not the verdict**: every economy parameter remains
> **PROVISIONAL** until the fleet Simulator seat / manager rules on
> graduation per [`economy-v1.md`](economy-v1.md) § "Verdict semantics".

`tools/simulate.py` is the pre-registered simulation request of
[`economy-v1.md`](economy-v1.md) § "Simulation request — SIM-001 (Q-0264)"
turned into one runnable command: scenarios S1–S3 on the v1 reference world,
outputs O1–O6, acceptance criteria A1–A10 evaluated against targets T1–T10.

## How to run it

```
python3 tools/simulate.py                    # full run: JSON report to stdout
python3 tools/simulate.py --out results.json # full run: JSON report to a file
python3 tools/simulate.py --quick            # short-horizon smoke mode
```

- The **JSON report** (machine-readable) goes to stdout, or to `--out`.
- The **human summary table** (per-criterion PASS/FAIL) always goes to
  stderr, so stdout stays machine-clean.
- `--quick` shrinks the horizon to 2 simulated days and the O6 ladder to 5
  resets so the suite can smoke-test the full pipeline fast. **Criteria
  results in quick mode are NOT meaningful** — the report says so in its
  `quick_mode_warning` field.
- Exit code is 0 whenever the run completes; a failing criterion is DATA,
  not an error. The verdict row lives in the report (`criteria[]`,
  `all_pass`), and acting on it is Q-0264's call, not the harness's.

Full run cost: ~20 s, single process, stdlib only.

## What it does (and refuses to do)

- **Drives the REAL engine functions** — `tick` / `apply_offline_progress`,
  `purchase_upgrade` / `upgrade_cost`, `prestige_eligible` /
  `prestige_award` / `apply_prestige`, `build_upgrade_spec` /
  `build_prestige_spec`. No economic logic is reimplemented.
- **Exact event scheduling, not approximation**: between actions the
  engine's production rate is a constant integer, so the first whole second
  at which the next purchase or prestige eligibility is possible is
  `ceil(need / rate)` seconds away; jumping there with one `tick` call is
  exactly equal to looping 1-second ticks (that equality is the engine's
  test-enforced core invariant, `tests/test_properties.py`). S3 is therefore
  the literal "S2's policy at 1-second granularity" at closed-form speed.
- **Deterministic**: no wall clock, no randomness, integer arithmetic
  throughout (ratios reported as exact `num/den` strings alongside float
  approximations). Two runs with the same flags are byte-identical —
  test-enforced (`tests/test_simulate.py`).
- **Never tunes**: it imports the parameter table from
  `idle_engine/economy.py` and echoes it into the report; it contains no
  parameter of its own and changes none.
- **Models a NEUTRAL theme multiplier**: the reference world's bare
  `GeneratorSpec` defaults to `rate_multiplier_pct = 100`, so the
  schema-bounded theme `balance` lane (90..110, bounded-multipliers slice)
  is not swept — consistent with the catalog, where every shipped pack is
  neutral; a non-neutral proposal must bring its own sweep
  ([`theme-balance-v0.md`](theme-balance-v0.md)).

## Report layout

Top-level fields of the JSON report:

| field | contents |
|---|---|
| `label` | the PROVISIONAL / not-the-verdict statement |
| `parameters` | echo of the provisional table from `idle_engine/economy.py` |
| `world` | the v1 reference world (tier1 ×1, boost1, prestige/primary) |
| `scenarios` | per-scenario raw runs: S1, S2 (N ∈ {0.25, 2, 8, 24}), S3 |
| `outputs` | O1–O6 exactly as named in economy-v1.md |
| `measures` | the flat per-criterion inputs (unit-testable seam) |
| `criteria` | A1–A10 rows: band, measured value, PASS/FAIL, detail |
| `all_pass` | conjunction of the ten rows |
| `ambiguities` | every non-obvious spec reading (list below) |
| `auxiliary` | extra context (gap lead-in/tail, burst minima, reset counts) |

O2 purchase timelines and per-scenario reset details are recorded through
reset 3 (per the O2 spec); O3 is sampled every 300 s for S3 and at every
visit for S2; O6 runs a dedicated 20-reset S3 ladder with no horizon cap.

## Provisional runs on record

- [`sim-results-2026-07-11-provisional.json`](sim-results-2026-07-11-provisional.json)
  — full 14-day run at the slice-(d) parameter table, clearly labeled
  PROVISIONAL/UNOFFICIAL. Headline: **A1–A9 PASS, A10 FAIL** under the
  strict literal reading (consecutive O6 duration ratios wiggle at single
  integer-floor steps — e.g. reset 3's ratio 0.9080 < reset 2's 0.9175 —
  while the TREND rises toward 1: first ratio 0.9175, final 0.9661, so
  shrinkage is NOT super-geometric; `super_geometric_shrinkage_flag` is
  false). Whether A10's wording intends the strict gate the harness
  implements or the trend reading is exactly the kind of call Q-0264 owns.
  (That call has since been made: VERDICT 038 re-registered A10 as **v2,
  TREND form** — economy-v1.md § A10 re-registration record — and the
  harness now evaluates v2, so this run's A10 row would read PASS if
  re-evaluated; the committed JSON stays as the v1-era record.)
  A second signal for the Simulator: within the 14-day horizon the S3 run
  reaches ~80k resets (late resets shrink to seconds), which the ruling may
  care about even though no criterion covers it.

## Spec ambiguities (implemented literally, never silently)

Mirrored in the report's `ambiguities` field; ids match `tools/simulate.py`.

| id | where | literal reading implemented |
|---|---|---|
| AMB-1 | O1 × S1 | S1 never purchases → O1 is `null` for S1; first-affordable time reported separately |
| AMB-2 | O3 × S1 "every visit" | S1 has no visits → trajectory is t=0, threshold crossing, horizon |
| AMB-3 | `apply_prestige` wipes `owned` | reference world fixes tier1 count at 1 (no purchase path) → harness re-seeds `{"tier1": 1}` after every reset |
| AMB-4 | A7 "every visit before first prestige" | visits strictly earlier than the prestige visit; inclusive variant reported as auxiliary |
| AMB-5 | A8 "gap between consecutive purchases" | purchase-to-purchase only; lead-in and tail spans reported as auxiliary |
| AMB-6 | A10 v1 "non-decreasing toward 1" | RESOLVED by the v2 TREND re-registration (economy-v1.md § A10 re-registration record, VERDICT 038): gate = final consecutive ratio ≥ first, single-step decreases within a 0.02 wiggle band; the harness implements v2 (`A10_CRITERION_VERSION`, doc↔harness parity test-enforced) |
| AMB-7 | buy-then-prestige at one visit/second | purchases at the reset moment execute and are recorded, then wiped (doc blesses this order) |
| AMB-8 | A2 "by t = 15 min" | boundary inclusive (t ≤ 900 s) |
| AMB-9 | band endpoints | all bands closed at both ends except A8's strict "< 25%" |
| AMB-10 | O3 samples at action times | samples record the post-action state |
| AMB-11 | O6 super-geometric flag | flag = ratio TREND falls (final < first) — the same trend reading A10 v2 now gates on, kept as its own reported flag per the O6 spec |

## What guards it

`tests/test_simulate.py`: byte-identical double run (CLI and in-process),
S1 closed-form spot check (threshold crossing at exactly
`PRESTIGE_THRESHOLD` seconds; first S3 purchases at the hand-computed curve
values 60 → 69), red/green unit tests for every criterion's evaluation
logic on synthetic measures, band-endpoint inclusivity + A8 strictness pins,
check-in grid exactness, O5 payback hand-value, and a quick-mode smoke of
the whole pipeline.
