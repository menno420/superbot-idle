# 2026-07-11 — state serialization v1: canonical versioned save/load + migration hook

> **Status:** `complete`

- **📊 Model:** fable-5 · high · idle-engine seat (state-serialization builder, coordinator-assigned) · 2026-07-11T02:31Z–02:4xZ (`date -u`)

## What happened

Built the persistence seam the future bot runtime needs regardless of
the blocked plugin contract (PLUG-001): a versioned, canonical,
strictly-validated save format for `GameState`. Claim rode the control
fast lane first (PR #40, `control/claims/state-serialization.md`,
auto-merge at creation → merged; removed in this PR's final commit).

1. **`idle_engine/persistence.py`** — pure stdlib. `dump_state` emits
   ONE canonical JSON spelling per state (sorted keys at every level,
   `(",", ":")` separators, ASCII escapes, explicit `state_version: 1`,
   all seven fields always present, every quantity a JSON integer —
   floats and bools refused EVERYWHERE, so the integer-exact engine
   math can't be smudged by a save/load cycle). `load_state` accepts
   any JSON spelling of a valid document but is strict about content;
   round-trip is exact both ways (`load(dump(s)) == s`;
   `dump(load(t)) == t` for canonical `t` — idempotent
   canonicalization). Dump-side validation (`InvalidStateError`)
   refuses whatever load would refuse, so every emitted string is
   loadable by construction.
2. **Error taxonomy** in the provisioning.py style — `SaveError` base +
   `MalformedSaveError` / `UnknownVersionError` / `FieldSetError` /
   `FieldTypeError` / `NegativeValueError` (+ encoder-side
   `InvalidStateError`), each condition distinct, each tested
   distinctly. Version is checked BEFORE field validation so a future
   format is never misread as a broken v1 doc.
3. **Migration hook** — `_MIGRATIONS: dict[int, callable]`, source
   version → doc at source+1, walked step-by-step to `STATE_VERSION`,
   then normal v1 validation applies to the result. EMPTY at v1 by
   design, but the dispatch is live and proven by a synthetic v0→v1
   migration in tests (register via monkeypatch, load a fabricated v0
   doc, assert migrated + bumped; misbehaving migrations — non-dict
   return, skipped or forgotten bump — fail loud). Policy documented:
   version bumps only via migration-covered changes, shipped in the
   same PR.
4. **`docs/persistence.md`** — the save-format contract: canonical
   form, field table, version policy, taxonomy table, and the explicit
   scope note that the storage BACKEND (where save strings live) is the
   runtime's concern, not the engine's — same seam split as
   provisioning. Worked examples are tested literals (md-parity,
   regenerate-or-red style). Cross-linked from architecture.md (seam
   list), repo-navigation-map.md (both rows), current-state.md ("No
   persistence layer" → "No storage backend", stability-baseline
   entry) — reachable from a read-path doc, no orphan.
5. **Tests 628 → 737 (+109)**: pinned canonical literals (empty state +
   doc examples), seeded round-trip over the property-suite's
   `_random_roster` generators (imported, not replicated) incl.
   10^3000-scale ints, insertion-order independence, per-class taxonomy
   coverage, 2000-trial seeded char fuzz (documented `SaveError`
   subclass or a GameState that itself round-trips — no other outcome;
   no checksum by design, saves are machine-carried), structured tamper
   → exact class mapping, migration dispatch/chain/misbehavior, and
   save/load mid-playthrough vs uninterrupted trajectory across all 9
   packs.

Verify: `python3 -m pytest -q` → 737 passed; `python3 tools/theme_gate.py
themes` → all 9 packs valid; `python3 bootstrap.py check --strict` green
with this card flipped. Concurrent-session note: `.substrate/guard-fires.jsonl`
dirtied mid-flight again (heartbeat PR #39 landed while building);
stash → rebase → pop, committed in this final flip commit per precedent.

## 💡 Session idea

`tests/test_properties.py::_canon` hand-rolls the exact canonical
serialization that `dump_state` now owns (same fields, same
sort_keys/separators — minus the version field). Next property-suite
touch should replace `_canon` with `dump_state(...).encode()` so the
determinism driver and the published save format can never drift apart,
and byte-identical-trajectory tests automatically pin the REAL format
consumers will store.

## ⟲ Previous-session review

The shop-composition card's idea (extract `_compose_budgeted` when a
third composed slot appears) was correctly parked — nothing in this
slice touched render, and resisting the pull to "just do the refactor
while nearby" kept this PR single-seam. Its friction note about
guard-fires.jsonl was again exactly right and again cost two minutes
mid-rebase; that is three sessions running. Pattern worth naming: the
kit's own state files are the ONLY recurring rebase friction in this
repo — everything product-side is conflict-free by the one-writer
conventions. If the kit ever grows a `merge=union` gitattribute for
`.substrate/*.jsonl`, all three cards' friction notes retire at once.
