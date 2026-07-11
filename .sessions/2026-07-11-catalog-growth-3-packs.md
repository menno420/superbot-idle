# 2026-07-11 — catalog growth: haunted-manor + deep-sea-station + dragon-hoard + id↔filename gate

> **Status:** `complete`

- **📊 Model:** fable-5 · high · idle-engine seat (catalog-growth builder, coordinator-assigned) · 2026-07-11T01:03Z–01:1xZ (`date -u`)

## What happened

Doubled the catalog (3 → 6 packs) and landed the parked filename
convention, in one build PR after a control fast-lane claim (PR #19,
`control/claims/catalog-growth-3-packs.md`, merged then removed here).

1. **Three full schema-v1 packs**, each filling EVERY slot egg-farm
   fills over the same opaque engine ids (primary/prestige, tier1/tier2,
   boost1/boost2), data only, all budgets respected:
   `themes/haunted-manor.yaml` (ectoplasm / restless spirits; haunted
   portrait + poltergeist parlor; *hold a séance*),
   `themes/deep-sea-station.yaml` (pearls / abyssal relics; oyster bed +
   submersible drone; *surface and resupply*), `themes/dragon-hoard.yaml`
   (gold coins / ancient scales; kobold miner + tribute village; *burn it
   all and fly on*). **Schema pinch audit: ZERO pinches** — all three fit
   v1 as published, no schema or parity changes needed.
2. **id↔filename gate** (parked by slice (c) as its non-pinch observation
   (ii)): `tools/theme_gate.py::_semantic_errors` now reds when
   `theme.id` ≠ the pack's filename stem — packs live at
   `themes/<theme.id>.yaml`; documented under `docs/theme-schema.md`
   § referential checks. Design note: the stem rule makes the
   catalog-level duplicate-id collision near-impossible within one
   directory, EXCEPT `.yaml`/`.yml` stem twins — so `catalog_errors`
   stays as defense-in-depth, and the end-to-end duplicate test now
   drives exactly that twin hole.
3. Tests 170 → 186: stem check red in both directions (valid pack under
   wrong filename; edited id under right filename) + green match;
   cross-pack fixtures reworked for the stem rule (`write_pack` fixture
   names files by their theme.id so red cases red on THEIR needle);
   parametrized catalog tests (fills-every-slot, loader, full engine
   drive, no-display-data specs) cover all 6 packs plus per-pack noun
   resolution for the three new ones; core/skin guard extended with
   their distinctive nouns (manor, ectoplasm, séance/seance, spirit,
   poltergeist, pearl, abyssal, trench, oyster, submersible, kelp,
   plankton, relic, dragon, hoard, kobold, lair, pickaxe, tribute) —
   generic words (gold, coin, scale, surface, station, village, drone)
   deliberately EXCLUDED so the guard never fires on legitimate engine
   vocabulary like "rates scale with level".

Verify: `python3 -m pytest -q` → 186 passed; `python3 tools/theme_gate.py
themes` → all 6 packs PASS (schema v1); `python3 bootstrap.py check
--strict` green after this flip.

## 💡 Session idea

The stem rule quietly gave the catalog a second identity invariant with
one documented hole: `.yaml`/`.yml` twins share a stem, so the
duplicate-id check is still load-bearing. Guard recipe: if the catalog
ever standardizes on one extension, enforce it in
`tools/theme_gate.py::main` (glob only `*.yaml`, red on any `*.yml`) +
flip `test_duplicate_theme_id_via_stem_twins_reds_gate` to assert the
extension error instead — then `catalog_errors` becomes provably
unreachable and can carry a comment saying so.

## ⟲ Previous-session review

Slice (c)'s card (2026-07-11-themes-space-potion.md) parked exactly this
slice's gate as non-pinch observation (ii) ("enforcing it is a
tightening on hypothetical existing packs — follow-up") — landed here
with zero existing-pack breakage: all six packs already followed the
convention, so the tightening was free. Its 💡 (canonical-roster check
when the economy slice moves rates engine-side) remains correctly
parked — this slice added three more packs that skin the same roster by
convention, so that check's payoff grew again. Slice (e)'s card
(setup-code-v1) notes `validate_against_catalog` resolves packs by id
against `themes/` — the stem rule landed here is what makes that
resolution path deterministic (id ↔ file is now checked, not hoped).
