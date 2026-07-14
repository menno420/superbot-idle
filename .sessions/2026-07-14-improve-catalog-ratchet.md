# 2026-07-14 — improve: catalog ratchet tests (milestones/labels slots + maxItems pairing)

> **Status:** `complete`

- **📊 Model:** fable-5 · medium · tests-only · catalog ratchet — milestones/labels slot assertions + balance/generators maxItems pin · 2026-07-14

## What happened

Improvement-wave slice B (owner improvement-wave directive, 2026-07-14) —
test-only ratchet, twice requested by session cards, zero pack/engine
changes. Two ratchets landed:

1. **Milestones/labels slot ratchet** — extended the catalog-wide slot test
   `test_pack_fills_every_egg_farm_slot` (`tests/test_theme_catalog.py`),
   which previously asserted currencies/generators/upgrades/prestige slots
   but never milestones or labels: a pack could drop its whole `milestones:`
   or `labels:` block and stay green. New assertions, for every pack (all 18
   declare a prestige block): `load_theme(pack).milestones` fills all nine
   canonical slot ids — derived from egg-farm THE TEMPLATE as
   `MILESTONE_SLOTS` (`tests/test_theme_catalog.py:58`) and cross-checked
   equal to the engine-derived set from `theme.milestone_specs()`
   (`idle_engine/theme.py:192`) — each slot skinned with
   name+description+emoji; and the full six-slot `labels` block
   (`LABEL_SLOTS`, derived from the template's `ThemeLabels` fields) is
   present with non-empty strings. Requested by
   `.sessions/2026-07-13-eap-wave4-milestones.md` (💡 lines 41-52) and
   `.sessions/2026-07-13-eap-wave5-packs.md` (💡 lines 54-64).
2. **Schema cap pairing** — `test_balance_cap_pairs_with_generator_cap`
   (`tests/test_theme_balance.py:88`): one assertion pinning
   `schema.properties.balance.maxItems == generators.maxItems`, from
   `.sessions/2026-07-11-bounded-multipliers.md` (💡 lines 72-80).

All 18 packs already comply (recon-verified pre-slice), so the ratchet
landed green — it converts "every pack reads finished" from a per-wave
courtesy into a red gate.

Verify: `python3 -m pytest -q` → `1364 passed, 1 skipped in 15.11s`
(baseline 1363 + exactly the one new test function, 0 failures);
`python3 tools/theme_gate.py themes` → `theme-gate: all 18 pack(s) valid
(schema v1)`; `python3 bootstrap.py check --strict` green once this card
flips (pre-flip it held the designed born-red gate). **Mutation proof**
(local, uncommitted, restored after): removed the `prestige-3` milestone
entry from `themes/ramen-stand.yaml` → `python3 -m pytest -q
"tests/test_theme_catalog.py::test_pack_fills_every_egg_farm_slot[ramen-stand]"`
went red with `AssertionError: ramen-stand must skin every canonical
milestone slot` / `Extra items in the right set: 'prestige-3'` /
`1 failed in 0.15s`; `git checkout -- themes/ramen-stand.yaml` → same
test `1 passed`.

## 💡 Session idea

The label ratchet asserts the six slots are non-empty strings, but the
schema's per-slot LENGTH budgets (docs/theme-schema.md § labels) and the
`{gains}` substitution token in `offline_return` are only gate-checked —
a render-side truncation bug would pass every test here. Guard recipe: one
parametrized test in `tests/test_theme_render.py` feeding each pack's
`theme.labels.offline_return` through the render layer's formatter
(`idle_engine/render.py`) with an adversarially wide `{gains}` value,
asserting the substituted string stays within the documented embed budget —
anchors: `ThemeLabels` (`idle_engine/theme.py:88`), `LABEL_SLOTS`
(`tests/test_theme_catalog.py:59`), budget arithmetic in
`docs/theme-schema.md § labels`.

## ⟲ Previous-session review

previous-session review: the wave-4 card
(`.sessions/2026-07-13-eap-wave4-milestones.md`) is this slice's direct
driver — its 💡 carried the wave-5 card's guard recipe forward verbatim
("still unbuilt … now unblocked"), correctly noting that with zero
unskinned packs left the gate could land with no grandfathering, which is
exactly how it landed: green on arrival, red only under mutation. Its
anchors were accurate (`test_pack_fills_every_egg_farm_slot` at
`tests/test_theme_catalog.py:91`, `Theme.milestones` at
`idle_engine/theme.py:141`), saving the re-derivation grep pass the
.sessions README warns about — evidence the guard-recipe doctrine pays.
One gap: both requesting cards asked only for the milestones ratchet;
the labels block had the identical exposure (droppable, gate-green) and
neither card flagged it — this slice closed both under the owner
directive's "slot assertions" scope. The bounded-multipliers card's
one-line maxItems pairing recipe was likewise exact and landed as written.
