# 2026-07-13 — wave-4 milestones flavoring: the last 3 unskinned packs

> **Status:** `complete`

- **📊 Model:** fable-5 · medium · feature build · wave-4 milestones flavoring — last 3 unskinned packs · 2026-07-13

## What happened

Data-only content slice, ⚑ self-initiated (EAP night, ladder rung 4 —
contained + reversible), driven directly by the wave-5 card's 💡
(`.sessions/2026-07-13-eap-wave5-packs.md`): after wave 5 landed, the three
wave-4 packs — **coffee-roastery**, **arctic-outpost**, **candy-factory** —
were the ONLY packs in the 18-pack catalog without a `milestones:` block,
still rendering the neutral `Milestone 1 … Milestone 9` scaffolding in the
achievements view. Claimed first per `control/claims/README.md`
(`control/claims/claude-eap-wave4-milestones.md`, PR #108 merged before
build; deleted in this card's flip commit).

Each pack gets a flavored 9-slot `milestones:` block mirroring egg-farm's
exact structure (the skin-pack-milestones playbook,
`.sessions/2026-07-13-skin-pack-milestones.md`): the nine canonical
engine-derived slot ids (`owned-1..3`, `lifetime-1..3`, `prestige-1..3`),
each with `id` / `name` / `description` / `emoji` and nothing else. PURE
CONTENT — producer nouns for the `owned` rungs (drip stations / ice-core
drills / taffy pullers), the pack's primary currency for the `lifetime`
rungs (beans / snowpack / candies), its prestige currency for the
`prestige` rungs (reserve tins / aurora shards / crystal jars). No schema
change, no economy numbers, no thresholds (engine-side per
`docs/design/achievements-v0.md`), zero engine / test-logic / SIM-PINNED /
A10 touches — no test asserts which packs carry a `milestones:` block, so
no test edit was needed.

Verify: `python3 tools/theme_gate.py themes` → `theme-gate: all 18 pack(s)
valid (schema v1)`; `python3 -m pytest -q` → `1363 passed, 1 skipped in
17.37s` (exact baseline, 0 failures); `python3 bootstrap.py check --strict`
green once this card flips (pre-flip it held the designed born-red gate);
load-check confirmed all three packs resolve flavored nouns via
`load_theme(...)` (e.g. "☕ first full counter", "🪛 first drill line",
"🍭 first pulling floor") where origin/main rendered `Milestone 1 … 9`.

## 💡 Session idea

All 18 packs now carry flavored milestones, but nothing structural stops a
wave-6 pack from shipping bare — the wave-5 card's gate idea is still
unbuilt, and this slice (deliberately data-only) did not build it either.
Guard recipe, unchanged and now unblocked: extend the catalog-wide slot
test `test_pack_fills_every_egg_farm_slot`
(`tests/test_theme_catalog.py:91`) to assert `load_theme(pack)`
(`idle_engine/theme.py` → `Theme.milestones`, the
`dict[str, ThemeMilestone]` at `theme.py:141`) yields all nine canonical
slot ids for every pack that declares a `prestige` block — with zero
unskinned packs left, the gate can land with no grandfathering and turns
"every pack reads finished" into a red gate. The neutral fallback it
forbids is `_NEUTRAL_MILESTONE_LABEL` (`idle_engine/render.py:85`).

## ⟲ Previous-session review

previous-session review: the wave-5 card
(`.sessions/2026-07-13-eap-wave5-packs.md`) is this slice's direct driver —
its 💡 named these exact three packs as the catalog's only remaining bare
spot, and its verify tails (18/18 gate, 1363-passed baseline) were the
bar this slice had to hold, and did, with zero test flips (contrast: wave 5
paid the two-spot count-pin tax because it ADDED packs; this slice only
deepened existing ones, so the count pins never moved — evidence for that
card's still-parked single-source-of-truth idea). The
skin-pack-milestones card (`.sessions/2026-07-13-skin-pack-milestones.md`)
supplied the exact block shape and voice rules mirrored here; its warning
that `owned-*` rungs are write-only until the generator-purchase verb
lands applies verbatim to the three new blocks' `owned` flavor — still
correctly parked behind the owner Q-block. The one thing wave 5's 💡 asked
for that this slice did NOT do is the gate itself; it is re-posted above,
now with no migration cost.
