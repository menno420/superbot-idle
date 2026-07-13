# 2026-07-13 — catalog wave 5: 3 data-only theme packs (EAP night worklist item 1)

> **Status:** `complete`

- **📊 Model:** fable-5 · medium · feature build · catalog wave 5 — 3 data-only theme packs · 2026-07-13

## What happened

Wave 5 of the theme catalog (worklist ORDER 007 item 1 @ `control/inbox.md` —
sanctioned standing filler, merges on theme-gate green alone;
`docs/current-state.md` roadmap item 3). Three new DATA-ONLY packs skin the
SAME opaque engine ids as the rest of the catalog (primary/prestige,
tier1/tier2, boost1/boost2) — identical mechanics, three new worlds, catalog
15 → 18:

1. **`themes/clockwork-atelier.yaml`** — cogs / grand complications;
   apprentice bench + mainspring lathe; jeweled bearings + tempered spring
   steel; *wind the master clock*.
2. **`themes/lighthouse-keep.yaml`** — lamplight / fresnel lenses; oil
   lantern + fresnel array; polished reflectors + counterweight drive;
   *hand over the keep*.
3. **`themes/ramen-stand.yaml`** — bowls / golden ladles; stockpot burner +
   noodle press; overnight tare + sharper brass dies; *roll the cart on*.

Each pack fills EVERY slot: theme identity + embed frame, primary+prestige
currencies, tier1+tier2 generators, boost1+boost2 upgrades, a prestige track,
the FULL 6-slot `labels` block, **and a flavored 9-slot `milestones` block**
(the skin-pack-milestones bar — no neutral `Milestone N` scaffolding in a new
pack). NO `balance` block (every shipped pack stays economy-neutral until the
Simulator blesses a non-neutral tuning). No smuggled economy numbers beyond
the shared base_rate 1/5; zero engine, schema, or SIM-PINNED touches.

Per-wave test flips (data expectations only, per the wave-4 playbook):
- Guard pre-flight: every distinctive noun grepped against `idle_engine/` and
  `tools/theme_gate.py` — zero collisions.
- `tests/test_properties.py` — count pin `len(THEME_PATHS) == 15` → `== 18`.
- `tests/vectors/setup-codes.v1.json` — REGENERATED via
  `python3 tools/gen_setup_vectors.py` (valid vectors 75 → 90; data fixture).
- `tests/test_theme_catalog.py` — named roster grown to 18 + a per-pack
  noun-resolve test for each new pack.
- `tests/test_core_skin_guard.py` — distinctive nouns appended to
  `FORBIDDEN_NOUNS` + per-pack catch assertions (generic words like "bench",
  "watch", "press", "counter", "queue" deliberately excluded, documented).

`docs/current-state.md` pack-count line deliberately NOT touched (wave-4
precedent: the doc bump rides the next current-state groom, not the wave PR).

Verify: `python3 tools/theme_gate.py themes` → `theme-gate: all 18 pack(s)
valid (schema v1)`; `python3 -m pytest -q` → `1363 passed, 1 skipped in
17.07s` (up from the 1264-passed baseline, 0 failures); `python3 bootstrap.py
check --strict` green once this card flips (pre-flip it held the designed
born-red gate, as intended).

## 💡 Session idea

The three wave-4 packs (coffee-roastery, arctic-outpost, candy-factory) are
now the ONLY packs without a `milestones:` block — they still render neutral
`Milestone 1 … Milestone 9` scaffolding in the achievements view, the exact
rough edge the skin-pack-milestones session closed for the other nine, and
nothing structural keeps a future wave from repeating the gap. Guard recipe:
skin those three packs, then extend the catalog-wide slot test
`test_pack_fills_every_egg_farm_slot` (`tests/test_theme_catalog.py`) to
assert `load_theme(pack)` (`idle_engine/theme.py`) yields a full 9-slot
milestones map for every pack that declares a prestige block — that turns
"every pack reads finished" from a per-wave courtesy into a red gate, and no
wave-6 pack can ship neutral scaffolding again.

## ⟲ Previous-session review

previous-session review: the wave-4 card (`2026-07-12-catalog-wave-4.md`)
recorded the exact playbook this slice replayed — full-slot packs over opaque
ids, count-pin flip, roster + noun-resolve tests, guard-noun extension, and
its hard-won "regenerate-or-red" setup-vector step — and it paid off again:
green first try, no schema pinch, no engine touch. That card's 💡 (the
two-spot count-pin tax: the `== N` pin plus the vector fixture both move
every wave) still holds and still bites — this wave paid the same mechanical
tax — and stays correctly parked until someone gives the count a single
source of truth. One thing wave 4 explicitly deferred (`milestones` blocks
for its own three packs) is now the catalog's only remaining bare spot; this
card's 💡 turns it into a gate so it cannot regress. The
skin-pack-milestones card (`2026-07-13-skin-pack-milestones.md`) set the
flavored-milestones bar this wave's packs meet on arrival; its warning that
`owned-*` rungs are write-only until the generator-purchase verb lands
applies to the new packs' flavor too — correctly parked behind the owner
Q-block.
