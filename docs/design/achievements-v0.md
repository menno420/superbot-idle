# Achievements v0 — pre-registered milestone thresholds and bonuses

> **Status:** `binding` (shapes) + **PROVISIONAL** (parameters) — committed
> 2026-07-11 with the achievements slice, BEFORE any tuning, per the
> integrity floor (README § Integrity floor). Every parameter below is
> provisional pending Simulator pinning via the Q-0264 pipeline (extend
> SIM-001's scenario set — see "What the Simulator must pin"); changing a
> value in `idle_engine/economy.py` without changing this doc in the same
> PR breaks the pre-registration contract
> (`tests/test_achievements.py::test_design_doc_parameter_table_mirrors_engine_values`).

## Ownership (CORE/SKIN)

All numbers on this page live ENGINE-side (`idle_engine/economy.py`). The
milestone SLOT SET itself is engine-derived — every pack gets the same
pre-registered ladders — so two servers on different themes run IDENTICAL
milestone mechanics whether or not their packs skin the slots. A theme's
optional `milestones` block carries **nouns only** (name/flavor/emoji per
canonical slot id, `docs/theme-schema.md` § milestones); the schema rejects
any numeric or mechanical field in it. No pay-to-win: no purchase path
exists or is planned that buys milestones or their bonuses.

## Slot model — SHAPE: three tracks × three rungs, engine-derived

Canonical slot ids are `{track}-{rank}` over three pre-registered ladders:

| Track | Metric (integer, deterministic) | Subject binding |
|---|---|---|
| `owned` | TOTAL generators owned, summed across all generator kinds | none — v0 deliberately pre-registers no per-generator track (a per-generator ladder × 20 generators would also blow the 25-field embed budget) |
| `lifetime` | run-lifetime earnings of the measured currency | the prestige track's `measures` currency; without a prestige block, the FIRST declared generator's produced currency (deterministic fallback) |
| `prestige` | prestige-currency units held | the prestige track's `currency`; the three `prestige-*` slots exist only for packs declaring a prestige track |

"Prestige count" is measured as **units held**, not resets performed: units
held is the only prestige meter in the state, it is monotone today (no
spend path exists), and a reset counter would add new state for no v0
gain. Revisit if a prestige-spend mechanic ever lands — earned milestones
would still never revoke.

## Parameters (PROVISIONAL v0 values)

| Parameter | v0 value | Rationale |
|---|---|---|
| `MILESTONE_OWNED_THRESHOLDS` | 10, 100, 1,000 | log-spaced decades, the genre's count-milestone rhythm; rung 1 is a first-session target once generator purchase lands, rung 3 a multi-prestige project |
| `MILESTONE_LIFETIME_THRESHOLDS` | 1,000, 100,000, 10,000,000 | ×100 spacing anchored on the prestige threshold: rung 1 (~17 min at base rate) lands mid-first-session, rung 2 EQUALS `PRESTIGE_THRESHOLD` so the first reset and the second milestone arrive together (a deliberate double-hit moment), rung 3 is a multi-reset goal |
| `MILESTONE_PRESTIGE_THRESHOLDS` | 1, 5, 25 | ×5 spacing over the isqrt award curve: rung 1 salutes the first reset, rung 25 needs ~625× the first run's lifetime — a long-haul meta goal |
| `MILESTONE_BONUS_PERCENT` | 5 | +5% global per milestone earned, additive — half a prestige unit's +10%, so the full 9-slot sweep (+45%) seasons progression without ever outweighing the prestige loop it decorates |

## Bonus application — SHAPE: percent fold, floor once per generator

```
rate(generator) = base_rate * count * upgrade_pct * prestige_pct * milestone_pct // 1_000_000
milestone_pct   = 100 + MILESTONE_BONUS_PERCENT * milestones_EARNED
```

One factor added to the slice-(b) fold, still with a SINGLE floor
division, so the per-second rate stays a plain integer and the closed-form
offline credit remains EXACTLY equal to looped live ticks. With no
milestones the pct is 100 and `(x * 100) // 1_000_000 == x // 10_000` —
integer-identical to the pre-slice fold, so every existing pinned output
is byte-for-byte unchanged.

## Earning — SHAPE: threshold gate, explicit award action, never revoked

```
reached(spec)   = metric(state) >= threshold          (live, side-effect free)
award           = explicit action: award_milestones(state, specs)
earned          = state.milestones[spec_id] >= 1      (persisted, save format v2)
```

- **Awarding is an ACTION-BOUNDARY step**, exactly like an upgrade
  purchase: the runtime calls `award_milestones` between production spans
  (after crediting offline progress, after purchases, after a reset).
  Production within a span reads the earned set the span started with —
  never live counters — which is what keeps tick == closed-form offline
  exact by construction. Nothing awards implicitly inside `tick`.
- **Earned once, kept forever.** `apply_prestige` wipes the run
  (balances, owned, upgrades, lifetime) but preserves `milestones`
  alongside the prestige balance and `last_seen`.

### Decision: milestones persist through prestige (recorded rationale)

Milestones are META-progression, like the prestige currency itself. The
counters two of the three tracks watch (`owned`, `lifetime`) are
run-scoped and reset at prestige; if earned milestones reset with them,
the "permanent" bonus would be run-scoped in disguise, re-earned
mechanically each run — pure grind with no decision content, and its
pacing would double-count against the prestige bonus the reset just
banked. Persisting the earned set makes each milestone a once-ever
event, keeps `milestone_pct` monotone non-decreasing across a whole
account lifetime, and gives prestige resets their genre-standard
"permanent trophies + fresh run" feel. (The `prestige` track's own metric
is persistent either way.)

## Persistence

Earned milestones ride the save format as the `milestones` mapping —
**save format v2**, bumped by this slice with the v1→v2 migration shipped
in the same PR per `docs/persistence.md` § Version policy (legacy saves
migrate with an empty earned set: achievements did not exist before v2).

## What the Simulator must pin (Q-0264, before these numbers graduate)

1. Arrival times of each rung under SIM-001's three player profiles
   (idle-only / check-in / optimal), and whether the lifetime-2 ↔
   first-prestige double-hit actually coincides for the median profile.
2. Whether +5%/milestone (up to +45% total) shifts time-to-first-prestige
   or reset cadence outside economy-v1.md's registered bands (T2–T7) —
   the milestone fold multiplies into every scenario.
3. Whether `owned` rungs 2–3 are reachable at all under the future
   generator cost curves (pre-registered ahead of that mechanic, like
   T10).

Until then: these values ship for mechanics correctness, not balance truth.
