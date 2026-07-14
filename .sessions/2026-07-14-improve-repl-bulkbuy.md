# 2026-07-14 — REPL bulk buy: buy <id> [n|max]

> **Status:** `complete`

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

Shipped as planned, on top of the just-merged #114/#115 `tools/play.py`
(branch base `2570cd8`; implementation commit `bc25bea`, PR #116).
`tools/play.py` + `tests/test_play_entrypoint.py` only.

- `_buy` grew an optional `count_arg` (dispatch passes `args[1]` when
  present). Empty → the ORIGINAL single-level path, byte-identical
  (`purchase_upgrade`, same wording). Otherwise affordability is
  pre-checked with the engine argmax (`max_affordable_levels` over the
  live level + balance), then the whole climb is ONE atomic
  `purchase_upgrades` spend. The pre-check is also the hostile-input
  guard: `buy boost1 1000000000` at zero balance answers instantly with
  a refusal instead of pricing a billion levels through the bulk-cost
  recurrence.
- Graceful in the house dispatch style (#115's patterns): `0` /
  negatives / garbage → `Usage: buy <upgrade-id> [count|max] (count
  must be an integer >= 1)`; over-budget → `Cannot buy N levels of
  'boost1': can only afford K.`; `max` at zero → `Cannot buy 'boost1':
  cannot afford a single level.` — session object returned unchanged in
  every refusal. Help text + module docstring updated.
- Scripted pipe session (verbatim, `printf 'wait 600\nbuy boost1
  max\nbuy boost1 max\nbuy boost1 3\nbuy boost1 banana\nquit\n' |
  python3 tools/play.py`), after the wait shows `🥚 eggs: 600 (+1/s)`:

      > Bought 6 levels of 'boost1'.
      === 🧺 The Farm Supply Shed ===
      Trade fresh eggs for a busier, happier farm.

        🏠 bigger henhouse: 🔒 Coop size 6 → 7 · 138 🥚 eggs
          A roomier henhouse; every hen in the coop lays that bit faster.

      > Cannot buy 'boost1': cannot afford a single level.

      > Cannot buy 3 levels of 'boost1': cannot afford a single level.

      > Usage: buy <upgrade-id> [count|max] (count must be an integer >= 1)

      > Bye.

  600 eggs cover exactly 6 levels of the pinned v0 curve
  (60+69+79+91+104+120 = 523; the 77 left < 138) — the immediate second
  `buy max` refusing is the argmax's defining property, live.
- Tests (+4, beside the existing dispatch tests): `buy boost1 3` climbs
  3 levels and `buy boost1 1` keeps the single-level wording;
  `buy boost1 max` buys ≥1 and an immediate repeat affords nothing
  (exactness asserted structurally — no economy number hardcoded);
  bad counts return the SAME session object with the usage message;
  over-budget/zero-balance refusals are atomic and instant.

Zero engine / economy / render / SIM-PINNED touches; no rate-delta or
effect preview added (feltness SIM-REQUEST owns that surface).

Verify: `python3 -m pytest -q` → `1370 passed, 1 skipped in 14.78s`
(baseline at branch base re-measured: 1366 + 1 skipped; the +4 are this
card's born tests), re-run green after the pre-flip merge of
origin/main (`c2a162e`, doc-truthfix #117 — telemetry union kept both
rows); `python3 bootstrap.py check --strict` pre-flip → the born-red
designed hold on this very card ("This red is the designed hold, not a
defect"), green once this flip lands.

## 💡 Session idea

`dispatch` is the REPL's whole input surface, and both #115's bugs and
this slice's hostile-count cases share one contract: for ANY input
line, `dispatch` returns `(session, str)` or raises exactly `QuitGame`
— never an escaping traceback, and on refusal the SAME session object.
Guard recipe: a seeded property test (house style — stdlib
`random.Random`, no hypothesis) that assembles a few hundred random
command lines from the verb vocabulary × a hostile-arg pool (`-5`,
`0`, `2.5`, `banana`, `max`, `10**9`, empty, unicode) and asserts the
contract holds for each. Anchors: verbs enumerated from `_HELP` in
`tools/play.py` (so a new verb without coverage fails loudly); sits
beside `tests/test_play_entrypoint.py`'s pure-dispatch tests — the
in-process twin of the hardening card's `repl-fuzz` subprocess idea
(that one proves the LOOP survives; this one property-pins the
dispatcher contract cheaply enough for hundreds of iterations per run).
It would have caught `wait -5` (escaping ValueError) and any future
verb that parses its arg with a bare `int()`.

## ⟲ Previous-session review

previous-session review: the REPL-hardening card
(`.sessions/2026-07-14-improve-repl-hardening.md`, PR #115) is the
direct parent of this slice's shape. Its two fixes defined the graceful
patterns this verb copied — validate at the DISPATCH layer and answer
in the existing usage-message family, return the same session object on
refusal — and its card's repro-first discipline (capture the hostile
session verbatim at the branch base before changing a line) is why this
card's scripted pipe session exists. Verified live rather than trusted:
its `wait -5` fix and prestige re-grant are both in the merged
`tools/play.py` this slice built on, and its 1365-test count was
re-measured here as 1366 at base (`+1` from #114's ratchet tests
landing after its flip — exactly the docs-vs-suite drift its own ⟲
section flagged as the thing to re-verify). Its 💡 (subprocess
`repl-fuzz`) remains unshipped and is strengthened, not duplicated, by
this card's in-process dispatcher-contract twin.
