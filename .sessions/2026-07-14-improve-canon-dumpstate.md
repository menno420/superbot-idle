# 2026-07-14 — improve: property-suite canonical serialization pins the published save format

> **Status:** `complete`

- **📊 Model:** fable-5 · medium · tests-only refactor — determinism suite `_canon` → published `dump_state` · 2026-07-14T02:10Z–02:14Z (`date -u`)

## What happened

Improvement-wave slice G (owner improvement-wave directive, 2026-07-14) —
replace the hand-rolled canonical serialization in
`tests/test_properties.py` (`_canon`, was ~line 221) with the published
`idle_engine.persistence.dump_state` API, so the determinism property
suite pins the REAL save format consumers will store. Requested by
`.sessions/2026-07-11-state-serialization.md` (💡 lines 68-76).
Tests-only — ZERO engine changes; PR #121.

1. **Comparison BEFORE the swap** (scratch sweep, not committed): re-drove
   the suite's exact trajectories — 18 packs x 3 seeds x 61 snapshots =
   3294 states — comparing old `_canon` bytes against `dump_state`
   output. Verdict: **byte-identical modulo the added constant
   `"state_version":2` field** — same seven fields, same sort order,
   same separators, same ASCII escapes; `dump_state` is a strict
   superset, so the swap strengthens the pin. Also fed all 30
   `_random_roster` states through `dump_state`: zero validation
   failures. No divergence, so no STOP condition — the requesting card's
   "same fields, same sort_keys/separators — minus the version field"
   claim verified exactly.
2. **The swap** — `_canon` now delegates: `return
   dump_state(state).encode("ascii")` (the strict encode is a free
   ASCII-contract check on top of `ensure_ascii`). Deleted the private
   seven-field `json.dumps` re-implementation and the now-unused
   `import json`; added `from idle_engine.persistence import dump_state`.
   Module docstring's determinism bullet now says snapshots are taken
   in the PUBLISHED save format.
3. **Merged origin/main pre-flip** — slice E (#119, REPL save/load)
   landed mid-flight; merged INTO the branch (never rebase published),
   telemetry rows unioned cleanly (both slices' rows present).

Verify: `python3 -m pytest tests/test_properties.py -q` → `164 passed in
1.15s`; full `python3 -m pytest -q` pre-merge → `1371 passed, 1 skipped
in 15.19s` (exactly the #120 baseline — behavior-preserving, zero test
count delta from this slice); post-merge → `1376 passed, 1 skipped in
15.23s` (+5 = slice E's new REPL save/load tests, not this slice's);
`python3 bootstrap.py check --strict` pre-flip showed ONLY the designed
born-red session-gate hold for this card, green once this card flips.
Known kit friction fired again: `.substrate/guard-fires.jsonl` dirtied
by the strict check run and blocked the merge; stash → merge → pop,
committed in this final flip commit per precedent (fourth session
running — the `merge=union` gitattribute idea from the
state-serialization card's review still stands).

## 💡 Session idea

`_drive_trajectory` snapshots are now real save strings, but nothing
yet proves they LOAD: one extra assertion would turn the determinism
sweep into a free round-trip fuzz over 3294 organic engine states —
strictly more coverage than `test_persistence.py`'s hand-picked states.
Guard recipe: in `tests/test_properties.py::_canon` (or a wrapper in
`_drive_trajectory`), assert `load_state(dump_state(state)) == state`
before returning the bytes — anchors: `idle_engine.persistence.load_state`,
`tests/test_properties.py::_drive_trajectory`, run target
`pytest tests/test_properties.py::test_identical_seed_gives_byte_identical_trajectory -q`.
Cost is ~3294 extra load_state calls (the whole file runs in ~1.2s, so
noise); benefit is the suite reds the moment dump/load disagree on any
reachable state.

## ⟲ Previous-session review

previous-session review: the improve-vector-hint card
(`.sessions/2026-07-14-improve-vector-hint.md`, slice F of this wave)
modeled "recon the exact surface before editing" — this slice took that
one step further with a compare-FIRST discipline: the 3294-state sweep
ran before a single line of the test file changed, converting the
requesting card's claim ("same fields ... minus the version field") from
trusted prose into checked fact, which is exactly what its own
regenerate-or-red hint philosophy asks of vector files. Its friction
note about `.substrate/guard-fires.jsonl` was again exact and again cost
minutes mid-merge — fourth consecutive card to say so; the
`merge=union` gitattribute retirement plan named in the
state-serialization card's review remains the single highest-leverage
kit fix this wave has surfaced.
