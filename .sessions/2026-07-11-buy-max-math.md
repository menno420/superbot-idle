# 2026-07-11 — buy-max math: exact bulk upgrade cost + max-affordable + atomic bulk purchase

> **Status:** `in-progress`

- **📊 Model:** fable-5 · high · idle-engine seat (buy-max-math builder, coordinator-assigned) · 2026-07-11T17:59Z– (`date -u`)

## What happened

(born-red — close-out written at session end)

Plan: claim landed first (`control/claims/buy-max-math.md`, control
fast-lane PR #59), then one build PR, TEST-FIRST:

1. `bulk_upgrade_cost(spec, from_level, n)` — EXACT integer sum of the
   next n level costs. Because each level's cost floors independently
   (`base·num^L//den^L`), a geometric-series closed form with one final
   floor is NOT exact — a pinned test shows the divergence (real v0
   curve base 60, ×1.15: first 5 levels sum to 403 exact vs 404 naive).
2. `max_affordable_levels(spec, from_level, budget)` — largest n with
   bulk cost ≤ budget; exponential search + bisect over the monotone
   exact sum using exact rational bounds (never a per-level linear
   scan); property-tested against brute force, 10^3000-scale budget
   completes fast.
3. `purchase_upgrades(state, spec, n)` — atomic bulk purchase, exact
   spend, byte-identical to n sequential `purchase_upgrade` calls;
   distinct error on insufficient funds, no partial spend.
4. Integrity: zero economy constants changed; determinism/conservation
   invariants extended in tests; short derived-math addendum to
   `docs/design/upgrades-prestige-v0.md` (no new pre-registered
   numbers).

## 💡 Session idea

(at close-out)

## ⟲ Previous-session review

(at close-out)
