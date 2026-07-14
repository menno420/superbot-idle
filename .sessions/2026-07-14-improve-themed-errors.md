# 2026-07-14 — REPL themed purchase errors: speak the pack's language

> **Status:** `complete`

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

## What happened

Shipped as planned at branch base `e96870c` (implementation commit
`4c2cbd6`, PR #124). `tools/play.py` + `tests/test_play_entrypoint.py`
only; no other file's behavior changed.

- Reproduced first, scripted pipe on a fresh egg-farm save
  (`printf 'buy boost1\nbuy boost1 3\nbuy boost1 max\nquit\n' |
  python3 tools/play.py`), verbatim BEFORE — single / bulk / max:

      > Cannot buy 'boost1': insufficient 'primary' for 'boost1' level 1: have 0, need 60
      > Cannot buy 3 levels of 'boost1': cannot afford a single level.
      > Cannot buy 'boost1': cannot afford a single level.

  Same three commands AFTER, verbatim at `4c2cbd6`:

      > Cannot buy 🏠 bigger henhouse: not enough 🥚 eggs for level 1 — have 0, need 60.
      > Cannot buy 3 levels of 🏠 bigger henhouse: cannot afford a single level — the next costs 60 🥚 eggs, you have 0.
      > Cannot buy 🏠 bigger henhouse: cannot afford a single level — the next costs 60 🥚 eggs, you have 0.

  and the partially-affordable refusal (`wait 200` then
  `buy boost1 50`):

      > Cannot buy 50 levels of 🏠 bigger henhouse: can only afford 2 — you have 200 🥚 eggs.

- As planned, NO string surgery: the engine exceptions genuinely carry
  no structured fields (message-only f-strings), so the `except
  ValueError` arm in `_buy` re-renders level/have/need from the
  UNCHANGED session state via the public `upgrade_cost` /
  `bulk_upgrade_cost` — sound precisely because engine purchases are
  atomic (nothing spent on failure), so the recomputed numbers are the
  exact ones the engine refused on. Two tiny helpers
  (`_themed_currency`, `_themed_upgrade`) apply render.py's one
  composition rule `{emoji} {name}`; the raw-id `repr` fallback is
  defense only (theme-load validation guarantees every spec-referenced
  currency/upgrade is declared).
- The bulk/max pre-check refusals (which never leaked `primary` but
  did show bare `'boost1'` and NO numbers) now carry the themed labels
  plus next-cost/balance — information added, none removed. Engine
  exception text byte-untouched; success messages and the unknown-id
  menu still show raw ids, because those are the tokens the player
  must type at the prompt.
- Tests (+2): themed names present AND raw `primary`/`boost1` absent
  across all three failure paths (single exercises the real engine
  exception, not the pre-check); the partially-affordable variant
  themed with `you have N`; numbers asserted by regex shape
  (`have \d+, need \d+`), not value, per the test file's
  no-economy-pinning rule.

Verify: `python3 -m pytest -q` → `1378 passed, 1 skipped in 15.82s`
(baseline 1376 at branch base `e96870c`; the +2 are this card's born
tests); `python3 bootstrap.py check --strict` pre-flip → red only on
the designed born-red hold on this very card ("This red is the
designed hold, not a defect"), green once this flip lands.
`origin/main` did not move during the session (still `e96870c`) — no
pre-flip merge needed.

## 💡 Session idea

The leak was found by eyeball, but it is mechanically checkable: a
theme pack declares its full engine-id vocabulary (`theme.currencies`
/ `theme.upgrades` / `theme.generators` keys), so "no raw id in
player-facing text" is a property, not a spot check. Guard recipe:
parametrize over every shipped pack × every failure-producing dispatch
(`buy <id>` at 0 balance, `buy <id> n`, `buy <id> max`, and future
verbs) and assert no engine id from the pack's key sets appears in the
output — quoted or bare — EXCEPT ids the player just typed (the
unknown-id menu is legitimately raw). Anchors: `_themed_currency` /
`_themed_upgrade` / `_buy` in `tools/play.py`; the pack-wide
parametrization pattern already in
`tests/test_play_entrypoint.py::test_every_pack_starts_and_renders_all_views`
(reuse its `sorted((REPO_ROOT / "themes").glob(...))` sweep); beside
`test_dispatch_buy_insufficient_speaks_the_packs_language`. That turns
this card's egg-farm-only assertions into an 18-pack invariant and
auto-covers the next verb someone adds.

## ⟲ Previous-session review

previous-session review: the REPL-save/load card
(`.sessions/2026-07-14-improve-repl-saveload.md`, PR #119) is this
slice's direct parent in the wave and its playbook carried over:
reproduce through the REAL entry path before writing a line (its
hostile-blob RecursionError probe ↔ this card's verbatim leak pipe),
refuse with the SAME session object in the house style, and capture
scripted-pipe proof at the base and after. Verified live rather than
trusted: its `save`/`load` verbs are in the merged `tools/play.py`
this slice edited around (untouched by this diff), and its post-merge
1376 verify tail was re-measured here as the exact branch-base
baseline — drift-free. Its 💡 (golden save corpus through the REPL's
`load`) remains unshipped and is orthogonal to this card's; its
cautionary tale transferred directly: just as the persistence
taxonomy didn't cover everything `json.loads` raises, the engine's
error TEXT was never designed for players — both cards' fixes live at
the boundary layer, translating a lower layer's honest-but-raw
signals, never patching the layer itself. Fourth card in the wave to
want the seeded dispatcher-contract property test (verbs × hostile
args); this card's 💡 pack-sweep would compose with it naturally.
