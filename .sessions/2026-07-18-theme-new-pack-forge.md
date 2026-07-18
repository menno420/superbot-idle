# 2026-07-18 — theme: add forge/blacksmith theme pack

> **Status:** `in-progress`

- **📊 Model:** neutral builder-agent · high · feature build · content seat (new theme pack) · 2026-07-18T00:31Z (`date -u`)

## What / why

Menu **THM** (new playable theme content), under the owner's overnight
full-autonomy order — new theme content explicitly authorized. The catalog
ships 19 schema-v1 theme packs; every pack is a data-only skin over the same
opaque engine ids (`primary`/`prestige`, `tier1`/`tier2`, `boost1`/`boost2`)
with identical mechanics and its own world. This slice adds the **20th** pack:
a **forge / blacksmith** theme — an ore-to-ingot economy where an apprentice
smith and a water-driven trip-hammer beat out iron ingots in the foundry, and
the prestige action **quenches and reforges** the whole batch to set aside a
billet of damascus steel and begin the forge anew.

The pack is authored to the frozen v1 schema (`schema/theme.schema.json`,
`docs/theme-schema.md`): the full `theme`/`currencies`/`generators`/`upgrades`/
`prestige`/`labels`/`milestones` shape, all nine canonical milestone slots
skinned, all six themed label slots filled, a distinct ember-orange
`embed_color`, and NO `balance` block (neutral rates). Numbers mirror an
existing single-currency two-tier pack exactly (`tier1` base_rate 1, `tier2`
base_rate 5), so it is balanced-by-construction and needs no fleet tuning
verdict.

**Reversible by construction:** one new file (`themes/forge.yaml`) plus the
pack-count guards (`tests/test_properties.py`, `docs/current-state.md`), the
forge guard-noun entry (`tests/test_core_skin_guard.py`), and the regenerated
setup-code + render-corpus vectors (`tests/vectors/setup-codes.v1.json`,
`tests/vectors/render-embeds.v1.json` — both catalog-derived). Deleting the
file and reverting the counts restores the 19-pack catalog.

## Verification

- `python3 tools/theme_gate.py themes` — MUST report the new pack PASS and all
  packs valid (schema v1).
- `python3 -m pytest -q` — full suite green, including the parametrized
  per-pack render/engine-cycle/slot-fill coverage that auto-includes forge,
  the updated `test_properties.py` count guard, the regenerated
  `test_setup_vectors.py` / `test_render_vectors.py` regenerate-or-red +
  replay, the `test_core_skin_guard.py` catalog-sync guard, and the
  `test_current_state_counts.py` doc guards.
- `python3 bootstrap.py check --strict` (only the born-red HOLD expected).

## Landing (born-red convention)

Card born RED (`in-progress`) in the first commit alongside
`control/claims/claude-theme-new-pack-forge.md`; then the pack + guards + regen
vectors; card flipped `complete` as the last commit to clear the born-red HOLD
so substrate-gate goes green and the landing workflow can merge on all-green. PR
opened READY; the worker does not merge its own PR.
