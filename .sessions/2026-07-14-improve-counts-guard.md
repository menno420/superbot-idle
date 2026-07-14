# 2026-07-14 — improve: current-state counts guard (doc counts vs ground truth)

> **Status:** `in-progress`

- **📊 Model:** fable-5 · medium · tests-only — pin docs/current-state.md count claims to ground truth · started 2026-07-14T02:30Z (`date -u`)

## What happened

Improvement-wave slice J (owner improvement-wave directive, 2026-07-14) —
a `tests/test_current_state_counts.py` that pins the machine-checkable
count claims in `docs/current-state.md` to ground truth, so the living
ledger's counts cannot rot silently between grooms. Requested twice:
`.sessions/2026-07-13-truthfix-current-state.md` (💡 lines 41-50: "a
drifted doc turns a required check red instead of waiting for a human to
notice") and `.sessions/2026-07-13-eap-night-groom.md` (💡 lines 57-67:
"the stalest lines this groom fixed were COUNTS the repo already knows").

Scope (the eap-night-groom card's own caveat, honored): guard ONLY the
clean counts —

1. **pack count** (the `**Theme catalog: N packs**` bullet) vs
   `len(glob("themes/*.yaml"))`, and
2. **setup-vector counts** (the `(N vectors: N valid … N tolerance, N
   error)` parenthetical) vs the `counts` dict in
   `tests/vectors/setup-codes.v1.json` (itself pinned to the live codec
   by regenerate-or-red in `tests/test_setup_vectors.py`).

The suite-size claim is deliberately UNGUARDED: it is self-referential
(adding the guard test itself changes the collected count), so an exact
pin would red on every tests-touching PR for a doc that is groomed, not
generated. Pytest counts stay prose.

(Implementation + verify to follow — this card is the born-red gate.)

## 💡 Session idea

(to be filled at flip)

## ⟲ Previous-session review

(to be filled at flip)
