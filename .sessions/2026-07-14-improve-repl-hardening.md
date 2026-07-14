# 2026-07-14 — REPL hardening: negative-time input + post-prestige re-grant

> **Status:** `in-progress`

- **📊 Model:** fable-5 · medium · bugfix · REPL hardening (negative-time input + post-prestige re-grant) · 2026-07-14 · tools/play.py + its tests only (ZERO engine/economy change)

## What this session is doing

Improvement-wave slice A (owner directive 2026-07-14): fix two REPRODUCED
player-facing bugs in the `tools/play.py` REPL, entrypoint-local only —
no engine, no economy number, no SIM-PINNED constant touched. Claimed first
per `control/claims/README.md`
(`control/claims/claude-improve-repl-hardening.md`; deleted in this card's
flip commit).

1. **Negative-seconds crash.** `wait -5` / `offline -5`: `int("-5")` parses
   fine in `dispatch` (`tools/play.py` ~L289-295), then `advance` /
   `go_offline` raise `ValueError("seconds must be >= 0")` (~L150/L162) —
   uncaught, so the full traceback kills the REPL. `int("abc")` IS already
   handled by the same block. Fix: validate `seconds >= 0` at the dispatch
   layer and return the existing `Usage: <verb> <seconds>` message style
   instead of propagating.
2. **Post-prestige bricked run.** `prestige do` → `apply_prestige` correctly
   wipes `owned` (engine semantics, `idle_engine/prestige.py` ~L92 — NOT
   touched), but `_prestige` (`tools/play.py` ~L236-246) never re-applies the
   entrypoint's starting grant. Result: 0 generators, +0/s, and no purchase
   path back — the run is unrecoverable. Fix REPL-LOCAL: after
   `apply_prestige`, re-seed the starting grant (`start_count`) exactly as
   session startup does. The module docstring (`tools/play.py` L15-18)
   already documents the starting grant as "a RUNTIME entrypoint choice …
   the engine has no generator purchase verb yet" — this fix is that same
   documented runtime choice applied at the one other place a run begins.
   The output says so: "run reset — starting generators re-granted".

Tests land beside the existing graceful-input test
(`tests/test_play_entrypoint.py::test_dispatch_unknown_and_bad_buy_are_graceful`,
~L83): negative `wait`/`offline` stays alive with a usage message;
a post-prestige session has the starting grant and accrues rate again.

## What happened

(to be completed at flip)

## 💡 Session idea

(to be completed at flip)

## ⟲ Previous-session review

(to be completed at flip)
