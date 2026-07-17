# 2026-07-17 — theme: add apiary/beekeeping theme pack (THM-2)

> **Status:** `complete`

- **📊 Model:** neutral builder-agent · high · feature build · content seat (new theme pack, THM-2) · 2026-07-17T23:36Z (`date -u`)

## What / why

Menu **THM-2** (new playable theme content), under the owner's overnight
full-autonomy order — new theme content explicitly authorized. The catalog
ships 18 schema-v1 theme packs; every pack is a data-only skin over the same
opaque engine ids (`primary`/`prestige`, `tier1`/`tier2`, `boost1`/`boost2`)
with identical mechanics and its own world. This slice adds the **19th** pack:
an **apiary / beekeeping** theme — a honey economy where worker bees fill honey
supers, and the prestige action **splits the hive** to send a swarm to a fresh
apiary in exchange for royal jelly.

The pack is authored to the frozen v1 schema (`schema/theme.schema.json`,
`docs/theme-schema.md`): the full `theme`/`currencies`/`generators`/`upgrades`/
`prestige`/`labels`/`milestones` shape, all nine canonical milestone slots
skinned, all six themed label slots filled, a distinct honey-amber
`embed_color`, and NO `balance` block (neutral rates). Numbers mirror an
existing single-currency two-tier pack exactly (`tier1` base_rate 1, `tier2`
base_rate 5), so it is balanced-by-construction and needs no fleet tuning
verdict.

**Reversible by construction:** one new file (`themes/apiary.yaml`) plus the
pack-count guards (`tests/test_properties.py`, `docs/current-state.md`) and the
regenerated setup-code vectors (`tools/gen_setup_vectors.py` — the setup corpus
is catalog-derived, five valid vectors per pack). Deleting the file and
reverting the counts restores the 18-pack catalog.

## Verification

- `python3 tools/theme_gate.py themes` — MUST report the new pack PASS and all
  packs valid (schema v1).
- `python3 -m pytest -q` — full suite green, including the parametrized
  per-pack render/engine-cycle/slot-fill coverage that auto-includes apiary,
  the updated `test_properties.py` count guard, the regenerated
  `test_setup_vectors.py` regenerate-or-red + replay, and the
  `test_current_state_counts.py` doc guards.
- `python3 bootstrap.py check --strict` (only the born-red HOLD expected).

## Landing (born-red convention)

Card born RED (`in-progress`) in the first commit alongside
`control/claims/claude-theme-new-pack-apiary.md`; then the pack + guards + regen
vectors; card flipped `complete` as the last commit to clear the born-red HOLD
so substrate-gate goes green and the landing workflow can merge on all-green. PR
opened READY; the worker does not merge its own PR.

## 💡 Session idea

With 19 packs all sharing one numeric shape, a natural follow-up is a
catalog-level "flavor coverage" tripwire: assert every pack's currency,
generator, and prestige emoji are distinct WITHIN the pack (so no two nouns
collide in a render), and that no two packs share an `embed_color` (already
gate-adjacent) — cheap doc-honesty guards that keep the growing catalog visually
legible.

## ⟲ Previous-session review

The prior overnight slices hardened test surface (render offline-drop branch,
play REPL) and grew the engine (prestige-preview, time-to-afford). This slice is
the content sibling: instead of a test or a helper it adds genuine playable
world to the catalog, exercising the CORE/SKIN split the schema was built for —
new nouns, zero new mechanics — and keeps the same born-red session-gate
discipline and the same no-economy-pinning convention (mirrors an existing
pack's numbers rather than forking new ones).
