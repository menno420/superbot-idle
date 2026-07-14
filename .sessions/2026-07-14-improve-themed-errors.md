# 2026-07-14 — REPL themed purchase errors: speak the pack's language

> **Status:** `in-progress`

- **📊 Model:** fable-5 · medium · feature build · themed insufficient-funds messages (REPL buy errors name the themed currency/upgrade, not engine ids) · 2026-07-14 · tools/play.py + its tests only (ZERO engine/economy/render change)

## What this session is doing

Improvement-wave slice H (owner directive 2026-07-13, fm ORDER 045 —
"find out if there still need to be improvements made in existing
features"; claim ledger batch #122): the `tools/play.py` REPL renders
every VIEW through the theme layer (`render_status` shows `🥚 eggs`,
never `primary`), but a failed purchase leaks raw engine ids straight
from the engine exception's message:

    > Cannot buy 'boost1': insufficient 'primary' for 'boost1' level 1: have 0, need 60

The player has never seen the word `primary` — the CORE/SKIN split
(`idle_engine/theme.py` module docstring: "nothing in this package
hard-codes any theme vocabulary") stops one layer short of the error
path. Claimed first per `control/claims/README.md`
(`control/claims/claude-improve-themed-errors.md`; deleted in this
card's flip commit).

Plan, entrypoint-local only:

- The engine's insufficiency errors (`ValueError` at
  `idle_engine/upgrades.py::purchase_upgrade`, `BulkPurchaseError` at
  `::purchase_upgrades`) are **message-only f-strings — they carry no
  structured fields** (checked before writing a line: no attributes
  beyond `args[0]`). So no string surgery on the message: the purchase
  is atomic, the session state is unchanged on failure, and the REPL
  already holds `spec`, so re-render the SAME facts (level, have, need)
  from the unchanged state via the public `upgrade_cost` /
  `bulk_upgrade_cost` — the exact numbers the engine just refused on.
- Translate ids with render.py's one composition rule
  (`_labelled`: `{emoji} {name}`): `spec.cost_currency` →
  `theme.currencies[...]` (`🥚 eggs`), `upgrade_id` →
  `theme.upgrades[...]` (`🏠 bigger henhouse`).
- All three buy paths: single (`buy <id>`), bulk (`buy <id> n`), and
  max (`buy <id> max`) — the bulk/max pre-check refusals get the same
  themed labels plus the have/cost numbers they previously omitted.
- Engine exception TEXT untouched; ZERO engine / economy / SIM-PINNED /
  render change. Success messages and the unknown-id menu keep raw ids
  (those are the ids the player must type).
- Tests beside the existing dispatch tests in
  `tests/test_play_entrypoint.py`: themed names present AND raw
  `'primary'` absent, across single/bulk/max failure paths; have/need
  numbers still present.
