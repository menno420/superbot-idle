# 2026-07-14 — REPL bulk buy: buy <id> [n|max]

> **Status:** `in-progress`

- **📊 Model:** fable-5 · medium · feature build · REPL bulk buy (buy <id> [n|max] via existing engine bulk API) · 2026-07-14 · tools/play.py + its tests only (ZERO engine/economy/render change)

## What this session is doing

Improvement-wave slice D (owner directive 2026-07-14): the engine has
shipped exact bulk-purchase math since the buy-max slice (PRs #59/#60 —
`purchase_upgrades` / `max_affordable_levels` / `bulk_upgrade_cost` in
`idle_engine/upgrades.py`, pinned by `tests/test_bulk_purchase.py`), but
the `tools/play.py` REPL still only exposes `buy <id>` one level at a
time — buying 10 levels means typing `buy` 10 times. Claimed first per
`control/claims/README.md`
(`control/claims/claude-improve-repl-bulkbuy.md`; deleted in this card's
flip commit).

Plan, entrypoint-local only:

- Extend the `buy` verb: `buy <id> [n|max]`. Optional second arg is an
  int `n >= 1` (routed through the atomic `purchase_upgrades` — one
  all-or-nothing spend, `BulkPurchaseError` on shortfall) or the literal
  `max` (routed through `max_affordable_levels` then the same bulk
  purchase; a graceful "can't afford any" message when the answer is 0).
- Single-arg `buy <id>` behavior stays byte-identical (still
  `purchase_upgrade` ×1). Bad counts (`0`, negatives, garbage) get the
  same usage-message style `dispatch` already uses for `wait`/`offline`.
- ZERO engine / economy / SIM-PINNED change; ZERO `render.py` change.
  Explicitly NO rate-delta / effect preview on the buy line — that
  surface is enumerated in the pending feltness SIM-REQUEST and is
  verdict-owned; this slice is a REPL verb over already-shipped math.
- Tests beside the existing dispatch tests in
  `tests/test_play_entrypoint.py`: buy n, buy max, graceful bad-count,
  graceful can't-afford-any.

## What happened

(in progress)

## 💡 Session idea

(in progress)

## ⟲ Previous-session review

(in progress)
