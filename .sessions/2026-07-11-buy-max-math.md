# 2026-07-11 — buy-max math: exact bulk upgrade cost + max-affordable + atomic bulk purchase

> **Status:** `complete`

- **📊 Model:** fable-5 · high · idle-engine seat (buy-max-math builder, coordinator-assigned) · 2026-07-11T17:59Z–18:1xZ (`date -u`)

## What happened

Landed the buy-max / bulk-purchase math in one build PR after a control
fast-lane claim (PR #59, `control/claims/buy-max-math.md`, merged then
removed here). TEST-FIRST: the red suite (+67 tests,
`tests/test_bulk_purchase.py`) was committed before any implementation.
All DERIVED math — zero economy constants touched, no new pre-registered
numbers (short addendum in `docs/design/upgrades-prestige-v0.md`).

1. **`bulk_upgrade_cost(spec, from_level, n)`** — EXACT integer sum of
   the next n level costs. The load-bearing negative result, pinned in
   tests: the per-level cost floors independently
   (`base·num^L//den^L`), so the geometric-series closed form with ONE
   final floor is UNSOUND — it keeps fractional parts the per-level
   floors discard and over-charges. On the real v0 curve at egg-farm
   scale (base 60, ×1.15), levels 0–4 cost 60+69+79+91+104 = **403**
   exact while the single-floor closed form says **404**. The exact sum
   is computed by an incremental quotient/remainder recurrence
   (q′ = (num·q + a)//den with (a, b) = divmod(num·r, den^L)) — O(n)
   steps of small-by-big multiplies and one tiny-quotient division, no
   fresh big-pow + full division per level. Ratio gcd-reduced; a reduced
   ratio of exactly 1 (num == den is legal, growth ≥ 1) short-circuits
   to `base·n` in O(1).
2. **`max_affordable_levels(spec, from_level, budget)`** — largest n
   with bulk cost ≤ budget, by exponential search + bisection over the
   monotone exact sum, never a per-level scan. Probes are decided by
   exact rational bounds T(k) − k < B(k) ≤ T(k) (T = unfloored
   geometric series; each of k floors discards < 1) as integer
   cross-multiplications — a 10^3000-scale budget resolves in dozens of
   cheap probes (test pins < 30 s wall, actual well under 2 s including
   the exact verification pass; a per-level scan would be ~49k
   pow-evaluations). Budgets inside the width-k ambiguity window fall
   back to the exact O(k) sum — correctness anchored, property-tested
   against brute force incl. exact-sum ±1 seam budgets.
3. **`purchase_upgrades(state, spec, n)`** — one atomic spend,
   byte-identical (canonical-JSON pinned) to n sequential
   `purchase_upgrade` calls; insufficient funds raise the distinct
   `BulkPurchaseError` (a `ValueError` subclass, so existing catch
   sites still work) with NOTHING spent; conservation pinned (lifetime,
   other balances, prestige, milestones, last_seen untouched).
4. **Render deliberately untouched**: the shop cost line's 1024-char
   composition arithmetic is pinned exact (768+1+139+116 = 1024, PR
   #38) — a bulk-cost line does not fit the existing budget arithmetic,
   so it was left out rather than reworking a pinned seam mid-slice.

Tests 943 → 1010. Verify: `python3 -m pytest -q` → 1010 passed;
`python3 bootstrap.py check --strict` green with this flip;
`python3 tools/theme_gate.py themes` → all 12 packs valid. Concurrent
bounded-multipliers claim (PR #58) landed mid-flight — zero surface
overlap, clean rebase, only `.substrate/guard-fires.jsonl` needed the
usual stash/pop care.

## 💡 Session idea

A future buy-max shop affordance (the ✅/🔒 mark could become
"✅ ×N affordable" using `max_affordable_levels`) needs render budget
room the current shop composition doesn't have: the cost line's clamp
room is exactly 1024 − 768 − 1 = 255 chars and the arithmetic is
byte-pinned. Guard recipe: if a bulk line is ever added, re-derive the
composition table in docs/theme-schema.md § budgets in the SAME PR and
re-pin `SHOP_FLAVOR_LIMIT` arithmetic in tests/test_render.py — the two
are deliberately locked together so neither drifts alone.

## ⟲ Previous-session review

The achievements-layer card (2026-07-11-achievements-layer.md) predicted
concurrent-worker collisions would stay confined to
`.substrate/guard-fires.jsonl` — held exactly again here (third slice
running: sim-harness → achievements → this one; the kit-level
`merge=union` gitattribute idea from the ORDER-002 self-review is now
three-for-three justified). Its milestone fold work also mattered
materially to THIS slice's scope discipline: bulk purchase deliberately
does NOT auto-award milestones — awarding stays an explicit
action-boundary step (`award_milestones`), so a bulk buy behaves exactly
like n sequential buys with no hidden award in between, preserving the
tick == closed-form-offline exactness its design protected. Its A10
integer-floor-noise warning is mirrored here too: the huge-budget test
asserts a generous wall-clock bound and the defining inequality rather
than any brittle literal digit pins.
