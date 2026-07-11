# Theme balance multipliers v0 — MECHANISM shipped, VALUES sim-gated

> **Status:** `binding` for the mechanism, committed 2026-07-11
> (bounded-multipliers slice). This addendum is the pre-registered
> statement the integrity floor requires: the mechanism exists, and
> **no non-neutral value ships without Q-0264 approval**.

## What shipped

The founding contract's last un-exercised clause (README § CORE/SKIN
split, rule 2): *"Balance multipliers only within schema-declared
bounds."* A theme pack may now carry an optional `balance` block —
per-generator `rate_multiplier_pct`, an integer percent with **hard
bounds 90..110 declared in the JSON schema itself**
(`schema/theme.schema.json`, literal `minimum`/`maximum` keywords) and
re-validated independently by the loader (`idle_engine/theme.py`,
`RATE_MULTIPLIER_MIN`/`MAX` — defense in depth; parity between the two
is test-pinned). 100 = neutral; an absent block or unlisted generator
is 100.

The engine folds the factor into the existing single-floor integer rate
composition (`idle_engine/engine.py`):

```
rate(generator) = base_rate * count * upgrade_pct * prestige_pct
                    * milestone_pct * theme_pct // 100_000_000
```

Still ONE floor division per generator per second, so the rate stays a
plain integer and closed-form offline credit remains EXACTLY equal to
looped live ticks. Neutral is integer-identical to the previous
`// 1_000_000` fold (`(x * 100) // 100_000_000 == x // 1_000_000`), so
every pre-slice output is byte-for-byte unchanged — property-pinned.

The multiplier touches **rates only**: upgrade costs, prestige
thresholds/awards, milestone thresholds and upgrade effect sizes are
all computed without it.

## Why 90..110 (rationale, pre-registered)

Flavor-level variance only, never progression-defining. Within ±10% a
themed server feels marginally brisker or lazier, but every pacing
target in `economy-v1.md` (T1–T10) stays in the same order of
magnitude: two servers on different themes still play the SAME game —
one codebase to balance, forever (README rule 4). Anything wider is an
economy change and belongs engine-side (`idle_engine/economy.py`,
pre-registered + Simulator-pinned), not in the data lane.

## VALUES ARE SIM-GATED (the explicit statement)

**Every shipped pack stays neutral: no pack in `themes/` declares a
`balance` block, and a test pins that**
(`tests/test_theme_balance.py::test_no_shipped_pack_declares_a_balance_block`).
Setting any non-neutral value in a shipped pack is a balance-tuning
decision and routes through the Q-0264 pipeline like every other
economy number: pre-registered rationale in this doc's next revision
FIRST, Simulator verdict on the pacing impact SECOND, value THIRD.
The mechanism shipping now, values later, is deliberate — the schema
lane needed the bounds contract exercised before any tuning
conversation can even be had.

## Simulator note

`tools/simulate.py` (SIM-001) models the neutral multiplier (its
reference world builds a bare `GeneratorSpec`, which defaults to 100),
so the provisional results on record are unaffected. A future
non-neutral proposal must include a sweep at the proposed value —
within ±10% the arrival-time shifts are bounded by the same factor,
but A-criteria band edges (e.g. A2's t ≤ 900 s) can flip at the
extremes, which is exactly why the values are gated.
