# Upgrades + Prestige v0 — pre-registered curve shapes and parameters

> **Status:** `binding` (shapes) + **SIM-PINNED** (parameters — graduated
> from PROVISIONAL 2026-07-13 by sim-lab VERDICT 038 via SIM-001/Q-0264,
> consumed per control/inbox.md ORDER 005; ZERO values changed at
> graduation) — first committed 2026-07-11 with slice (b), BEFORE any
> tuning, per the integrity floor (README § Integrity floor). Pinning
> evidence + the A10 trend-form re-registration live in the economy design
> doc ([`economy-v1.md`](economy-v1.md)); changing a value in
> `idle_engine/economy.py` without changing this doc in the same PR still
> breaks the pre-registration contract.

## Ownership (CORE/SKIN)

All numbers on this page live ENGINE-side (`idle_engine/economy.py`). Theme
packs name the slots — an upgrade's noun, the prestige currency's noun, the
reset action's noun — and carry **zero economy numbers**: the schema rejects
any numeric field in the `upgrades`/`prestige` blocks. (The one legacy
exception, `generators[].base_rate`, is bounded 1–1000 and slated to move
engine-side in the economy slice.) No pay-to-win: no purchase path exists or
is planned that buys currency, upgrades, or prestige units.

## Upgrade cost curve — SHAPE: geometric, integer-exact

```
cost(level) = base_cost * growth_num**level // growth_den**level
base_cost   = target_generator.base_rate * UPGRADE_BASE_COST_SECONDS
```

Evaluated in exact big-int arithmetic with ONE floor division, so every
platform prices level N identically (no float drift, no compounding
rounding).

| Parameter | v0 value | Rationale |
|---|---|---|
| `UPGRADE_BASE_COST_SECONDS` | 60 | first upgrade ≈ one minute of one target generator's base output: reachable in a first session, not free |
| `UPGRADE_COST_GROWTH_NUM/DEN` | 115/100 (×1.15) | the classic idle-genre growth band (1.07–1.15); the high end keeps upgrade spam in check while generators (future cost curves) carry breadth |
| `UPGRADE_EFFECT_PERCENT` | 25 | +25% of the target's base rate per level, additive (level L → ×(1 + 0.25·L)); additive-linear beats multiplicative-compounding for v0 because it cannot run away before the Simulator has pinned pacing |

## Bulk purchase math — DERIVED, not new pre-registered numbers

*(Buy-max slice addendum. Nothing on this page changed: the bulk API is
arithmetic DERIVED from the curve above — no new parameter, no repricing.)*

```
bulk_cost(f, n)          = Σ_{L=f}^{f+n-1} cost(L)          exact, floors per level
max_affordable(f, budget) = max { n : bulk_cost(f, n) <= budget }
purchase_upgrades(n)      = n sequential purchases, one atomic spend
```

**Why no closed form:** each level's cost floors independently, so the
geometric-series closed form with ONE final floor keeps fractional parts
the per-level floors discard and systematically over-charges — on this
very curve at egg-farm scale (base 60, ×1.15), the first five levels sum
to **403** exactly while the single-floor closed form says **404**
(pinned in `tests/test_bulk_purchase.py`). The exact sum is evaluated
level by level with an incremental quotient/remainder recurrence
(`idle_engine/upgrades.py`), and `max_affordable_levels` finds its argmax
by exponential search + bisection over the monotone sum, deciding probes
with the exact rational bounds `T(n) - n < bulk_cost(n) <= T(n)` — so a
10^3000-scale budget resolves without a per-level scan. Bulk purchase is
byte-identical to n sequential single purchases and all-or-nothing on
insufficient funds (`BulkPurchaseError`, nothing spent).

## Effect application — SHAPE: percent fold, floor once per generator

```
rate(generator) = base_rate * count * upgrade_pct * prestige_pct // 10_000
```

*(Extended by the achievements slice with a third factor —
`… * milestone_pct // 1_000_000`, still one floor; integer-identical to
this fold when no milestones are earned. See
[`achievements-v0.md`](achievements-v0.md) § Bonus application. Extended
again by the bounded-multipliers slice with the theme lane's
schema-bounded factor — `… * theme_pct // 100_000_000`, still one floor;
integer-identical when the theme is neutral. See
[`theme-balance-v0.md`](theme-balance-v0.md).)*

`upgrade_pct = 100 + Σ effect_percent·level` (upgrades targeting that
generator), `prestige_pct = 100 + Σ bonus_percent·units_held` (global).
The single floor keeps the per-second rate a plain integer, which is what
makes the closed-form offline credit EXACTLY equal to looped live ticks —
the offline path uses the same rate function, multiplied by elapsed
seconds. Tests enforce the equality over awkward spans.

## Prestige — SHAPE: threshold gate + isqrt award + linear persistent bonus

```
eligible        = lifetime_earned(measures) >= PRESTIGE_THRESHOLD
award           = isqrt(lifetime_earned(measures) // PRESTIGE_AWARD_DIVISOR)
prestige_pct    = 100 + PRESTIGE_BONUS_PERCENT * units_held
reset           = balances, owned, upgrades, lifetime → {} ; prestige, last_seen kept
```

| Parameter | v0 value | Rationale |
|---|---|---|
| `PRESTIGE_THRESHOLD` | 100 000 | ≈ a day of early-game base output (1/s), a few hours once upgrades stack — the genre's "first reset on day one or two" pacing target |
| `PRESTIGE_AWARD_DIVISOR` | 100 000 | equal to the threshold, so the first eligible reset awards exactly isqrt(1) = 1 — no zero-award trap; the spec validator enforces threshold ≥ divisor |
| `PRESTIGE_BONUS_PERCENT` | 10 | +10% global per unit: the first reset is felt immediately, and the isqrt award curve keeps the bonus from compounding into runaway (10 units needs 100× the first run's lifetime) |

`isqrt` (integer square root, deterministic) gives strongly diminishing
awards: doubling a run's lifetime does NOT double the award, so the optimal
loop is reset-and-regrow, not one endless grind — the core prestige feel.
Awards are computed from **run-lifetime earnings** (production only;
spending on upgrades never reduces the award), which removes any "hoard vs
spend" distortion at reset time.

## What the Simulator must pin (Q-0264, before these numbers graduate)

1. Time-to-first-upgrade, time-to-first-prestige, and time-between-prestiges
   over the first simulated week (pacing targets to be pre-registered in the
   economy design doc, slice (d)).
2. Whether ×1.15 upgrade growth against +25%/level additive effect produces
   a dead zone (upgrades stop paying back) before the first prestige.
3. Prestige bonus stacking: confirm +10%/unit stays sub-exponential across
   20 simulated resets.

Until then: these values ship for mechanics correctness, not balance truth.
