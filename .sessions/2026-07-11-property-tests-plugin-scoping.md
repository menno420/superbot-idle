# 2026-07-11 — property/invariant test suite + plugin-adapter scoping

> **Status:** `complete`

- **📊 Model:** fable-5 · high · idle-engine seat (deepening builder, coordinator-assigned) · 2026-07-11T01:50Z–02:0xZ (`date -u`)

## What happened

Claimed via `control/claims/property-tests-plugin-scoping.md` (PR #30,
control fast lane, merged 2026-07-11T01:49Z; claim removed in this
build PR's final commit). Two deliverables:

1. **`tests/test_properties.py` — 128 seeded property/invariant tests**
   (suite 405 → 533). Stdlib `random.Random(FIXED_SEED)` only — CI is
   byte-reproducible, and the repo deliberately takes no `hypothesis`
   dependency (checked: not installed).
   - *Tick/offline equivalence*: 30 random rosters
     (generators/upgrades/prestige, counts/levels/holdings) × random
     partitions of up to 10^6 s into up to 12 ticks — summed tick
     earnings == the single `offline_progress` closed form, EXACTLY
     (balances and lifetime); plus 1s-at-a-time loops and
     `apply_offline_progress == tick(elapsed)` state-for-state.
   - *Determinism*: a 60-op seeded play-through driver (tick / offline
     incl. clock-skew / own / buy / prestige) run twice per seed × 3
     seeds × all 6 packs → byte-identical canonical-JSON trajectories;
     anti-vacuity guard pins that different seeds diverge.
   - *Monotonicity/conservation*: balances/lifetime/prestige never
     negative along trajectories; lifetime monotone within a run;
     purchase spends exactly `upgrade_cost` and never touches lifetime
     or other balances (and unaffordable purchase raises); prestige
     award monotone non-decreasing in lifetime; `apply_prestige` wipes
     the run (never increases any run balance), banks exactly the
     award (>= 1 when eligible), preserves `last_seen`.
   - *Render-budget fuzz*: 25 hostile states (balances/owned up to
     10^3000, `now` past AND 2^40 future) × 6 packs × 3 views —
     `validate_embed` never raises on engine-formatted content; two
     deliberate red cases pin the themed-overflow policy (oversized
     `status_title` label and oversized pack description both raise
     `RenderBudgetError`, never clamp).
   - *Setup-code fuzz*: 1000 random valid configs round-trip
     deterministically; 4000 seeded corruptions (substitute/delete/
     insert in the body) → 3943 documented `SetupCodeError` subclasses
     (2656 ChecksumError, 1287 MalformedCodeError), 57 folded to the
     ORIGINAL config (the grammar's case/look-alike tolerance),
     **0 crc16 collisions observed** (rate 0.000%, asserted <= 0.1%);
     no other outcome possible by assertion. Prefix-corruption sweep
     stays inside the taxonomy too.
   - **No engine bugs found**: every invariant tried held on first
     run; zero test adjustments were needed to make the engine pass.
2. **`docs/plugin-adapter-scoping.md` — evidence-gated, UNVERIFIED
   path.** Raw probes (logged verbatim in the doc): superbot-next
   README/architecture/status reachable but contain NO plugin/manifest
   contract; `docs/plugins.md` + `docs/plugin-contract.md` 404;
   `superbot-plugin-hello` README 404 on main+master and the repo page
   says **"This repository is empty."** → contract UNVERIFIED, so the
   doc maps our four VERIFIED seams (setup-code decode, theme loader,
   engine API, render payloads), lists exactly what the exemplar must
   answer (manifest name/format, entry point/lifecycle, command
   registration, persistence, config ingestion, dependency policy),
   and builds NO speculative adapter code. ⚑ recommended to the
   manager for the contract pointer. Cross-linked from
   AGENT_ORIENTATION.md § Lane-layer docs (orphan check clean).

Verify: `python3 -m pytest -q` → 533 passed; `python3 bootstrap.py
check --strict` green with this card flipped; `python3
tools/theme_gate.py themes` → all 6 packs PASS.

## ⚑ needs-manager

Plugin-adapter work is blocked on the upstream contract:
`superbot-plugin-hello` is an EMPTY public repo and no reachable
superbot-next doc publishes the manifest/plugin contract (probe table
in docs/plugin-adapter-scoping.md § Evidence log). Ask: a contract
pointer or a seeding ETA for the exemplar.

## 💡 Session idea

The determinism driver (`_drive_trajectory` in tests/test_properties.py)
is a general seeded play-through harness — it already exercises tick,
offline, purchase and prestige against every pack. When the Simulator
pipeline (Q-0264) pins real economy numbers, point this same driver at
the pinned parameters and record canonical-trajectory GOLDEN files per
pack (like tests/vectors/setup-codes.v1.json): any economy change then
reds with a byte diff instead of a vibe. Guard recipe: reuse `_canon` +
`_drive_trajectory`, add `tools/gen_trajectory_vectors.py` mirroring
`tools/gen_setup_vectors.py`'s regenerate-or-red pattern, replay in a
new tests/test_trajectory_vectors.py.

## ⟲ Previous-session review

The themed-label-slots card (2026-07-11-themed-label-slots.md) fed this
slice twice: its composition-arithmetic notes (offline template fixed
text ≤ 1275 of 4096) predicted exactly why the render fuzz CAN'T
overflow on gate-legal packs — the fuzz confirmed it empirically at
10^3000 extremes — and its `_label_slot` seam gave the clean injection
point for the deliberate themed-overflow red case
(`dataclasses.replace(theme, labels=...)`, no YAML surgery needed). Its
💡 (extract a shared placeholders module if a second template slot
lands) remains open and untouched here — correctly, since this slice
added no template slots. One friction echo confirmed: its warning that
`bootstrap.py check` appends to `.substrate/guard-fires.jsonl` held —
this worktree session kept that file out of every commit.
