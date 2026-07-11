# 2026-07-11 — slice (b): UPGRADES + PRESTIGE

> **Status:** `complete`

- **📊 Model:** fable-5 · high · idle-engine seat (slice (b) builder, coordinator-assigned) · 2026-07-11T00:17Z–00:3xZ (`date -u`)

## What happened

Shipped upgrades + prestige TEST-FIRST in one build PR, after a control
fast-lane claim (PR #7, `control/claims/upgrades-prestige.md`, merged then
removed here). The red-tests commit precedes the implementation commit.

1. **Upgrades (CORE)** — `idle_engine/upgrades.py`: `UpgradeSpec` (opaque
   id, cost currency, geometric cost curve as an exact rational, target
   generator, additive percent effect). `cost(L) = base_cost · num^L // den^L`
   in big-int arithmetic, ONE floor. `purchase_upgrade` spends exactly or
   raises; spending never touches lifetime earnings.
2. **Prestige (CORE)** — `idle_engine/prestige.py`: threshold eligibility on
   run-lifetime earnings, deterministic award `isqrt(lifetime // divisor)`
   (diminishing — reset-and-regrow beats one endless grind), `apply_prestige`
   wipes balances/owned/upgrades/lifetime while prestige balances and
   `last_seen` persist, linear global bonus percent applied thereafter.
3. **One rate function** — multipliers fold into `production_per_second`
   (`base·count·upgrade_pct·prestige_pct // 10_000`, floored once per
   generator-second), so tick and closed-form offline progress remain
   EXACTLY equal — test-enforced over awkward spans, with upgrades and
   prestige stacked. `GameState` grew `upgrades`/`lifetime`/`prestige`
   (run-scoped vs persistent split documented in the dataclass).
4. **Theme slots for every new noun** — schema v1's first OPTIONAL additive
   fields: `upgrades[]` (id/name/description/emoji/target, ≤20, own shop
   embed) and `prestige` (currency/measures/action_name/action_description/
   action_emoji). Nouns only: numeric smuggling reds the gate
   (`additionalProperties: false` + explicit tests). md↔json parity kept;
   theme-gate gained referential checks (upgrade target → generator id,
   prestige currency/measures → currency ids, must differ, unique upgrade
   ids). egg-farm filled: *bigger henhouse*, *golden eggs*, *sell the farm*.
5. **Integrity floor** — `docs/design/upgrades-prestige-v0.md` pre-registers
   curve SHAPES + parameters with rationale (60s base cost, ×1.15 growth,
   +25%/level, 100k threshold, isqrt award, +10%/unit), all explicitly
   PROVISIONAL pending the economy design doc slice + Simulator (Q-0264);
   `idle_engine/economy.py` is the single engine-side home for the numbers.
6. Tests 40 → 76: purchase math, effect in tick AND offline, prestige award
   determinism, reset semantics, multiplier persistence, full-cycle
   determinism, theme wiring, loader + schema red-gates, guard nouns
   extended (henhouse, golden).

Verify: `python3 -m pytest -q` → 76 passed; `python3 bootstrap.py check
--strict` green after this flip; `python3 tools/theme_gate.py themes` →
PASS (schema v1).

## 💡 Session idea

`upgrade_percent`/`prestige_percent` recompute the fold on every
`production_per_second` call by scanning all specs — fine at this scale, but
the bot loop will call it per player per tick. Guard recipe: when the
plugin-runtime slice lands, add a memoized rate table keyed on
`(upgrades, prestige)` state (both dicts change only on purchase/reset, never
on tick) in the runtime layer — NOT in the pure engine — with an equality
test against the pure path in `tests/test_engine.py`. Keeps the engine pure
and the hot loop O(1) per tick.

## ⟲ Previous-session review

Slice (a)'s card (2026-07-11-theme-schema-v1.md) parked a 💡: cross-pack
`theme.id` collision is invisible to per-file validation — still open, and
still correctly parked for the theme-catalog slice ((c) will add packs; its
builder should land that gate first). Its OTHER parked item — engine-owned
economy baselines — advanced here: every NEW number (upgrade curves,
prestige thresholds) was born engine-side in `idle_engine/economy.py` with
pre-registration, so the debt no longer grows; only the legacy
`base_rate` slot remains theme-side (bounded 1–1000), still parked for the
economy slice as planned.
