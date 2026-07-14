# 2026-07-14 — REPL save/load: expose persistence in the REPL

> **Status:** `complete`

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

Shipped as planned, on top of the just-merged bulk-buy #116 (branch
base `dc278ba`; implementation commit `68ee93f`, PR #119).
`tools/play.py` + `tests/test_play_entrypoint.py` only.

- `save` returns `dump_state(session.state)` verbatim — the ONE
  canonical line, nothing wrapped around it, so a terminal
  triple-click copies a working save. Read-only: same session object.
- `load` takes the RAW remainder of the input line
  (`command.strip().split(None, 1)`), not the whitespace-split arg:
  `load_state` accepts any JSON spelling, including blobs containing
  whitespace, and the split-args path would have truncated those at
  the first space. `_load` replaces the state and rebases the session
  clock to the loaded `last_seen` (rather than rewriting `last_seen`
  to the clock), so the blob stays byte-authoritative — an immediate
  re-`save` emits the identical string — and `status`/`offline` see
  zero phantom elapsed time. Nothing is re-granted: `owned` is
  whatever the blob says (an empty-owned save loads as empty even into
  a granted session), keeping the runtime grant a fresh-save /
  post-prestige choice only, exactly the #115 interplay to watch.
- Refusals catch `SaveError` (the real taxonomy base: malformed JSON,
  unknown version, wrong field set/type, negative quantity — each
  message names the offender) PLUS `RecursionError`, because a live
  probe showed hostile deeply-nested input (`"[" * 200000`) escapes
  `json.loads` inside `load_state` as neither `SaveError` nor
  `JSONDecodeError`. No bare except; same session object returned;
  bare `load` gets the house usage-message style.
- Scripted two-process round-trip (verbatim). Session 1,
  `printf 'wait 600\nbuy boost1 3\nsave\nquit\n' | python3
  tools/play.py`, save line:

      > {"balances":{"primary":392},"last_seen":600,"lifetime":{"primary":600},"milestones":{},"owned":{"tier1":1},"prestige":{},"state_version":2,"upgrades":{"boost1":3}}

  Session 2, `printf 'load <that blob>\nstatus\nquit\n' | python3
  tools/play.py` — fresh process starts at 0 eggs, then:

      > Save loaded.
      === 🥚 Egg Farm — the morning count ===
      A cozy backyard farm where patient chickens fund your empire.

        🥚 eggs: 392 (+1/s)
        🥇 golden eggs: 0
        🐔 chicken coop: × 1 · +1/s

  and `status` renders the identical block — byte-identical to a
  control session that earned the same state live (rate line included).
- Tests (+5, beside the existing dispatch tests): save prints exactly
  the canonical loadable one-liner; save→load round-trip preserves
  state, production rate (same `wait 10`, same balances), and re-save
  blob byte-identity; eight malformed/mutant/oversized blobs refuse
  with the same session object; load-then-status renders with
  `now == last_seen` and `offline 0` credits nothing; empty-owned load
  re-grants nothing.

Zero engine / economy / render / SIM-PINNED touches; all pre-existing
verbs byte-identical (no existing line of `dispatch` changed — the two
new verbs slot in before the `pack` branch).

Verify: `python3 -m pytest -q` → `1375 passed, 1 skipped in 15.35s` at
the implementation commit (baseline 1370 at branch base; the +5 are
this card's born tests), re-run after the pre-flip merge of
origin/main (`5e96335`, vector-hint #120 — telemetry union kept both
rows) → `1376 passed, 1 skipped in 15.11s`; `python3 bootstrap.py
check --strict` pre-flip → only the designed born-red hold on this
very card ("This red is the designed hold, not a defect"), green once
this flip lands.

## 💡 Session idea

`load` makes the golden save corpus player-reachable: every vector in
`tests/vectors/saves.v2.json` (the frozen cross-version documents, per
`docs/persistence.md` § Golden save corpus) is now a string a player
could paste into the REPL. Guard recipe: parametrize a test over the
corpus vectors and assert `dispatch(session, f"load {blob}")` either
restores a state that `status` renders or refuses with `Cannot load
save:` — never a traceback — so the corpus, today only a
persistence-layer fixture, also pins the REPL's input surface.
Anchors: `tests/vectors/saves.v2.json` loaded the way the persistence
vector tests load it; `_load` + `dispatch` in `tools/play.py`; beside
`tests/test_play_entrypoint.py::test_dispatch_load_malformed_blob_is_graceful`.
The RecursionError probe is the cautionary tale: the persistence
layer's own taxonomy did NOT cover everything `json.loads` can raise,
and only feeding hostile strings through the REAL entry path found it
— corpus-through-the-REPL institutionalizes that probe.

## ⟲ Previous-session review

previous-session review: the REPL-bulk-buy card
(`.sessions/2026-07-14-improve-repl-bulkbuy.md`, PR #116) is this
slice's direct parent and its playbook transferred almost verbatim:
pre-check hostile input before handing it to the layer below (its
argmax pre-check ↔ this card's RecursionError probe), refuse with the
SAME session object in the house message style, and capture a scripted
pipe session verbatim at the base before flipping. Verified live
rather than trusted: its `buy <id> [n|max]` verb is in the merged
`tools/play.py` this slice built on (this card's round-trip script
uses `buy boost1 3` — its verb — to make a save worth keeping), and
its 1370-count verify tail was re-measured here as the exact branch-
base baseline, drift-free this time. Its 💡 (seeded dispatcher-
contract property test over verbs × hostile args) remains unshipped
and would have covered this card's `load` + deep-nesting case for
free — third card in a row to want it; whoever picks it up should add
`save`/`load` and a nesting bomb to the hostile-arg pool.
