# 2026-07-14 — REPL save/load: expose persistence in the REPL

> **Status:** `in-progress`

- **📊 Model:** fable-5 · medium · feature build · REPL save/load (`save` prints the persistence-v2 blob, `load <blob>` restores it) · 2026-07-14 · tools/play.py + its tests only (ZERO engine/economy/render change)

## What this session is doing

Improvement-wave slice E (owner directive 2026-07-14): the engine has
shipped a frozen, versioned save format since the state-serialization
slice (persistence v2 — `dump_state` / `load_state` in
`idle_engine/persistence.py`, byte-contract in `docs/persistence.md`,
pinned by `tests/test_persistence.py` and the golden save corpus), but
the `tools/play.py` REPL — the engine's only player-facing entrypoint —
has no way to keep a run across sessions: quit and the save is gone.
This slice makes the REPL the persistence layer's first interactive
consumer. Claimed first per `control/claims/README.md`
(`control/claims/claude-improve-repl-saveload.md`; deleted in this
card's flip commit).

Plan, entrypoint-local only:

- `save` verb: print `dump_state(session.state)` — ONE canonical JSON
  line, copy-pasteable (the persistence module's determinism guarantee
  makes it safe to compare/diff as a string).
- `load <blob>` verb: `load_state` the rest of the line, replace the
  session state in place (same theme, same clock). The blob is
  AUTHORITATIVE: loading re-grants nothing — no starting-generator
  re-seed (that grant is a fresh-save/post-prestige runtime choice, and
  a saved state already carries its own `owned`). `last_seen` is
  rebased to the session clock on load so the restored run resumes from
  "now" instead of silently crediting phantom offline time.
- Graceful in the house dispatch style (#115/#116 patterns): malformed
  / wrong-version / mutant blobs are refused by catching the
  persistence layer's REAL error taxonomy (`SaveError` — the common
  base of `MalformedSaveError`, `UnknownVersionError`, `FieldSetError`,
  `FieldTypeError`, `NegativeValueError`; no bare except), returning
  the SAME session object with a one-line message.
- ZERO engine / economy / SIM-PINNED / render change; all existing
  verbs byte-identical. Help text + module docstring updated.
- Tests beside the existing dispatch tests in
  `tests/test_play_entrypoint.py`: save→load round-trip preserves
  state and production rate, malformed blob graceful, load-then-status
  renders, load does not re-grant.

## What happened

(to be written at flip)

## 💡 Session idea

(to be written at flip)

## ⟲ Previous-session review

(to be written at flip)
