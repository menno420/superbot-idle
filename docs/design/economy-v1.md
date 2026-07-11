# Economy v1 — pre-registered pacing targets, cost curves, and simulation request (Q-0264)

> **Status:** `binding` (targets + shapes) · **PROVISIONAL** (every numeric
> parameter) — committed 2026-07-11, slice (d), BEFORE any tuning, per the
> integrity floor (README § Integrity floor). This doc PRE-REGISTERS what the
> economy is supposed to feel like as falsifiable numbers, then hands the
> fleet's Simulator (Q-0264 pipeline) an executable request whose acceptance
> criteria are those same numbers. Parameter table parity with
> `idle_engine/economy.py` is test-enforced
> (`tests/test_economy_design_doc.py`) — tune the engine without re-registering
> here and the suite goes red.

Companion doc: `docs/design/upgrades-prestige-v0.md` (curve SHAPES and the
per-parameter rationale table, slice (b)). This doc supersedes nothing there;
it adds the player-experience targets the shapes must hit and the sim contract
that decides whether they do.

## Reference world (what every number below is measured against)

All targets and scenarios are stated against the **v1 reference world** — the
current engine surface, egg-farm-shaped but theme-independent (themes carry
zero economy numbers; nouns only):

- ONE generator `tier1`, `base_rate = 1`/s, **count fixed at 1** (a fresh save
  starts owning it; no generator purchase path exists yet in the engine).
- ONE upgrade ladder `boost1` targeting `tier1`, priced by
  `idle_engine.economy.build_upgrade_spec`.
- ONE prestige track measuring `primary`, per `build_prestige_spec`.
- Time starts at `t = 0` on a fresh save. "Time-to-X" for a check-in player is
  measured at the check-in where X is first *actionable* (the player can only
  act when present — an idle threshold crossed at 03:00 counts at the next
  visit).

## Pre-registered pacing targets

Each target is a falsifiable number with an acceptance band. A sim result
outside the band on the current provisional parameters = the parameters (not
the target) get retuned; targets only move by re-registration in a new
version of this doc with rationale.

| id | Target (player experience) | Target value | Acceptance band |
|---|---|---|---|
| T1 | Time-to-first-upgrade, active player, fresh save | 60 s | 30–180 s |
| T2 | Early-run purchase cadence: upgrade purchases in the first 15 min of active play | 8 purchases | ≥ 5 |
| T3 | Time-to-first-prestige, optimal active play | 4 h | 2–8 h |
| T4 | Time-to-first-prestige, idle-only (zero purchases, never returns) | 24 h | 18–36 h |
| T5 | Time-to-first-prestige, check-in-every-2-h player | 6 h | 4–12 h |
| T6 | Active-play advantage: T4 ÷ T3 | 7× | 4–12× |
| T7 | Offline-return payoff: MINIMUM upgrade levels affordable in one burst at any check-in visit before first prestige (N ∈ {2, 8} h) | 5 levels | ≥ 2 levels |
| T8 | No dead zone (mid-run stall): longest gap between consecutive upgrade purchases within an optimal run, before first prestige | 10% of run duration | < 25% of run duration |
| T9 | Time-between-prestiges, optimal play, resets 2–3 (each with the prior bonus stacked) | ≤ T3 each | 50–100% of prior reset's duration |
| T10 | Time-to-second-generator-tier (FUTURE mechanic — no purchase path yet; pre-registered ahead of implementation) | 30 min active | 15–45 min |

Session-length intent behind the table (the "feel" the numbers encode):
**early run** = one active 5–15 min session with a purchase every minute or
two (T1, T2); **mid run** = 2–4 check-ins per day, each affording at least one
purchase (T5, T7 — coming back must feel like opening a present, never like
being punished for leaving); **late run** = purchase gaps stretch past an
hour, which is the signal that pressing prestige beats grinding (T8, T9 —
the wall is the invitation, not a bug). T10 is registered now so the
generator-cost slice inherits a target instead of inventing one post hoc.

## Cost-curve design (why these shapes, against those targets)

- **Geometric upgrade costs** (`cost(L) = base_cost · num^L // den^L`, exact
  big-int, one floor): geometric growth against the linear-additive effect
  below is what CREATES the late-run wall (T8→T9). Linear costs never wall
  (play converges to constant-interval purchases forever, so prestige never
  becomes attractive); super-geometric walls too abruptly (one purchase feels
  fine, the next is days away). Exact rational arithmetic, not floats, so
  every platform prices level N identically — a cost table is a contract.
- **Growth factor ×1.15** (`115/100`): the top of the idle-genre band
  (1.07–1.15). Chosen against T2 + T8 + T9: low enough that the first
  session chains purchases (cost only ×2 by level 6), high enough that
  purchase gaps stretch hour-long inside ~40 levels — the point where an
  optimal v1 run should be choosing prestige instead (T3). A lower factor
  never walls (prestige never beats grinding, T9 dies); a higher one starves
  T2 and blows T8's gap cap.
- **Additive integer-percent stacking** (`upgrade_pct = 100 + Σ effect·level`,
  the implemented model in `idle_engine/upgrades.py` / folded once in
  `production_per_second`): additive-linear effect against geometric cost
  guarantees marginal value per level is CONSTANT while marginal cost grows —
  so purchase gaps lengthen smoothly and monotonically (T8 measures the
  worst gap) instead of cliffing.
  Multiplicative-compounding effects can outrun their own cost curve
  (runaway) before a Simulator has ever looked at the numbers; v1 refuses
  that risk by construction.
- **Prestige award `isqrt(lifetime // divisor)`**: strongly diminishing —
  doubling a run's lifetime does not double the award, so the optimal loop is
  reset-and-regrow (T9), not one endless grind. Divisor == threshold means
  the first eligible reset awards exactly 1 (no zero-award trap at T3/T4/T5).
  The linear +10%/unit bonus on top keeps reset №2 tangibly faster (T9's
  50–100% band) without exponential stacking (SIM-001 output O6 checks it).
- **What "too fast" looks like**: T3 under 2 h (prestige is a first-session
  gimmick, nothing left for day two); T2 above ~12 (purchases are noise, not
  decisions); T9 under 50% (prestige compounding runs away — each reset
  halves the loop and the counter becomes the game).
- **What "too slow" looks like**: T1 over 3 min (first session ends before
  the first decision); T4 over 36 h (a patient idler sees nothing happen for
  a day and a half); T7 under 2 (returning after a workday buys less than
  one upgrade — the present is empty); T8 over 25% (a mid-run stall: a stretch
  where the only available action is waiting, hours before prestige is
  reachable — the classic idle-game dead zone).

## Provisional parameters (test-pinned to `idle_engine/economy.py`)

**Every value in this table is PROVISIONAL.** They shipped in slice (b) for
mechanics correctness, not balance truth. **No tuning happens until SIM-001
results land**; when a value changes, this table, the rationale above, and
`docs/design/upgrades-prestige-v0.md` change in the SAME PR (test-enforced
parity below). **Themes carry no economy numbers** — theme packs are nouns
plus schema-bounded multiplier slots only, and no bounded multiplier is
currently used by any shipped pack; the one legacy theme-side number
(`generators[].base_rate`, bounded 1–1000) is slated to move engine-side.

| Parameter | Provisional value |
|---|---|
| `UPGRADE_BASE_COST_SECONDS` | 60 |
| `UPGRADE_COST_GROWTH_NUM` | 115 |
| `UPGRADE_COST_GROWTH_DEN` | 100 |
| `UPGRADE_EFFECT_PERCENT` | 25 |
| `PRESTIGE_THRESHOLD` | 100000 |
| `PRESTIGE_AWARD_DIVISOR` | 100000 |
| `PRESTIGE_BONUS_PERCENT` | 10 |

## Simulation request — SIM-001 (Q-0264)

> Addressed to the fleet Simulator seat via ⚑ to the manager
> (`control/status.md` § SIM-001). Written to be executable without
> follow-up questions; every input is committed in this repo at the pinned
> commit. Report format: one results doc (markdown) per the Outputs section,
> plus a verdict row per Acceptance criterion.

### Scenarios

Run each scenario on the **reference world** (§ above) with the parameter
table (§ above), from a fresh save at `t = 0`, horizon **14 simulated days**,
continuing through **at least 3 prestige resets** where reachable (S2/S3):

- **S1 — idle-only**: never purchases, never prestiges. Pure accrual.
- **S2 — check-in-every-N-hours**: at each visit, credit elapsed production,
  then buy upgrade levels **greedily** (repeat-buy while affordable), then
  prestige **iff eligible** (prestige AFTER buying is fine — spending never
  reduces the award; lifetime measures production only). Run N ∈
  {0.25, 2, 8, 24} as four sub-scenarios.
- **S3 — optimal-play speedrun**: S2's policy at 1-second granularity
  (greedy-buy is the optimal proxy under additive-linear effects; if the
  Simulator wants to also test a threshold policy — e.g. buy only when
  payback < X — report it as S3b, not instead of S3).

### Inputs

- Engine at the pinned commit of this PR (`menno420/superbot-idle`,
  `idle_engine/`): drive the REAL functions — `tick` / `offline_progress`
  (they are proven exactly equal), `purchase_upgrade`, `upgrade_cost`,
  `prestige_eligible`, `prestige_award`, `apply_prestige`,
  `build_upgrade_spec`, `build_prestige_spec`. Pure Python, stdlib-only,
  deterministic, integer-exact — a re-implementation is unnecessary and
  unwanted (float drift would invalidate the run).
- Reference world constants: `GeneratorSpec(spec_id="tier1",
  produces="primary", base_rate=1)`, owned `{"tier1": 1}`, upgrade
  `build_upgrade_spec("boost1", tier1)`, prestige
  `build_prestige_spec(awards="prestige", measures="primary")`.
- No randomness anywhere in the engine: a single run per scenario is the
  distribution's support unless the Simulator varies policy (S3b).

### Outputs

- **O1** — time-to-first-upgrade per scenario (seconds).
- **O2** — upgrade-purchase timeline per scenario: `(t, level_after, cost,
  balance_after)` per purchase, per run (through reset 3).
- **O3** — currency trajectory: `(t, balance[primary], lifetime[primary])`
  sampled at ≤ 5-min resolution for S3, at every visit for S1/S2.
- **O4** — time-to-prestige distribution: first-prestige time per scenario,
  plus per-reset durations for resets 1→3 (S2/S3).
- **O5** — payback curve: per level L, `upgrade_cost(L) /
  (base_rate · EFFECT/100)` in hours, annotated with the level an S3 run
  holds at each prestige.
- **O6** — prestige stacking: per-reset duration and cumulative bonus percent
  across 20 simulated S3 resets (horizon may extend for this output alone);
  flag if reset-duration shrinkage is super-geometric.

### Acceptance criteria

| Criterion | PASS condition (against the targets table) |
|---|---|
| A1 | S3's O1 within T1's band (30–180 s) |
| A2 | S3's O2 shows ≥ 5 purchases by t = 15 min (T2) |
| A3 | S3's first-prestige time within T3's band (2–8 h) |
| A4 | S1 crosses `PRESTIGE_THRESHOLD` lifetime within T4's band (18–36 h) |
| A5 | S2(N=2)'s first-prestige time within T5's band (4–12 h) |
| A6 | A4's time ÷ A3's time within T6's band (4–12×) |
| A7 | O2 for S2(N=2) and S2(N=8): every visit before first prestige buys ≥ 2 levels (T7) |
| A8 | O2 for S3: max gap between consecutive purchases before first prestige < 25% of the run's duration (T8) |
| A9 | O4: resets 2 and 3 each take 50–100% of the preceding reset's duration (T9) |
| A10 | O6: cumulative bonus growth across 20 resets is sub-exponential (each reset's duration ratio non-decreasing toward 1) |

**Verdict semantics**: ALL PASS → the parameter table graduates
PROVISIONAL → SIM-PINNED in a follow-up PR updating this doc and
`upgrades-prestige-v0.md` together. ANY FAIL → the Simulator reports which
criterion broke and by how much; new parameter values are RE-REGISTERED here
(new doc version, same-PR engine change) before any engine tuning lands.
T10 is out of SIM-001's scope (mechanic not yet implemented) and carries no
criterion.
