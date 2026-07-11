# 2026-07-11 — slice (c): SPACE-COLONY + POTION-BREWERY theme packs

> **Status:** `complete`

- **📊 Model:** fable-5 · high · idle-engine seat (slice (c) builder, coordinator-assigned) · 2026-07-11T00:33Z–00:3xZ (`date -u`)

## What happened

Proved THEME SCHEMA v1 on content it wasn't designed around, in one build
PR after a control fast-lane claim (PR #10,
`control/claims/themes-space-potion.md`, merged then removed here):

1. **Two foreign packs** — `themes/space-colony.yaml` (oxygen / alien
   artifacts; solar array + hydroponics bay; polished reflectors +
   enriched nutrient feed; *launch a new colony*) and
   `themes/potion-brewery.yaml` (potions / arcane essence; cauldron +
   apprentice alchemist; hotter flames + dog-eared grimoire; *transcend
   the craft*). Each fills EVERY slot egg-farm fills, over the SAME opaque
   engine ids (primary/prestige, tier1/tier2, boost1/boost2): identical
   mechanics, different world. Data only, all budgets respected.
2. **Schema pinch audit (the point of the slice)**: both packs fit v1
   with ZERO per-file schema changes — every slot needed existed and
   every budget had room; the honest finding is that v1's shape (id +
   name + description + emoji per entity, produces/target/currency
   references) is not egg-farm-shaped. The ONE pinch was the known
   catalog-level one: per-file validation cannot see two packs claiming
   one `theme.id` (parked by slice (a) for exactly this slice) — fixed at
   the GATE, where catalog invariants live (a per-file JSON Schema cannot
   express a cross-file check): `tools/theme_gate.py::catalog_errors`
   collects `theme.id` from every per-file-valid pack and reds on
   collisions; documented under `docs/theme-schema.md` § referential
   checks (catalog-wide bullet). Non-pinch observations logged below.
3. Tests 76 → 93 (`tests/test_theme_catalog.py` + guard extension):
   catalog-wide gate pass; duplicate-`theme.id` red gate, distinct-id
   green, invalid packs excluded from the cross-pack check (no spurious
   duplicates); every shipped pack parametrically fills every egg-farm
   slot, resolves its nouns through `load_theme`, drives the engine end
   to end (tick 60s → exact level-0 upgrade cost → purchase → grind →
   prestige reset awards ≥1), and its engine specs carry zero display
   data. Core/skin guard noun list extended with the new packs'
   distinctive vocabulary (colony, oxygen, solar, hydroponics, artifact,
   potion, cauldron, brewery, alchemist, arcane, grimoire) — engine
   sources stay noun-free.

Non-pinch observations (recorded, deliberately NOT landed): (i) v1 has no
offline-return flavor slot ("while you were away…") — both new packs
would want themed copy there, but adding a slot with no render-layer
consumer is speculative; belongs with the bot/runtime slice. (ii)
`theme.id` ↔ filename stem is convention, not a check (all three packs
match); enforcing it is a tightening on hypothetical existing packs —
follow-up, not additive-urgent.

Verify: `python3 -m pytest -q` → 93 passed; `python3 bootstrap.py check
--strict` green after this flip; `python3 tools/theme_gate.py themes` →
all 3 packs PASS (schema v1).

## 💡 Session idea

Packs skin "the SAME opaque engine ids" purely by convention — nothing
enforces that two packs declare the same generator roster or base rates,
so "two servers on different themes run IDENTICAL mechanics" (README §
CORE/SKIN) is currently voluntary: egg-farm has tier1 only, the new packs
tier1+tier2, and base_rate is still theme-side. Guard recipe: when the
economy slice moves baseline rates engine-side, add a canonical-roster
check next to `tools/theme_gate.py::catalog_errors` (every pack must skin
the engine's published id roster exactly) + a parametrized test in
`tests/test_theme_catalog.py`; until then the divergence is visible in
`test_pack_drives_engine_full_cycle`'s per-pack spec handling.

## ⟲ Previous-session review

Slice (b)'s card (2026-07-11-upgrades-prestige.md) re-parked slice (a)'s
cross-pack `theme.id` gate for this slice — landed here exactly per its
pointer (gate `main`, two-file test), minutes not hours; the guard-recipe
format keeps paying. Its own 💡 (memoized rate table keyed on
(upgrades, prestige) in the runtime layer) stays correctly parked for the
plugin-runtime slice — nothing in this slice touched the hot path. The
economy-baseline debt it tracked (theme-side `base_rate`, bounded 1–1000)
did not grow here but IS now load-bearing across three packs — the
economy slice (claimed in parallel today, `economy-design-doc` claim)
should treat the roster/rate unification as its schema-revision trigger.
