# 2026-07-11 — catalog wave 2: wizard-tower + royal-bakery + cyber-city (6 → 9)

> **Status:** `complete`

- **📊 Model:** fable-5 · high · idle-engine seat (catalog-growth-wave-2 builder, coordinator-assigned) · 2026-07-11T02:08Z–02:1xZ (`date -u`)

## What happened

Grew the catalog 6 → 9 packs in one build PR after a control fast-lane
claim (PR #33, `control/claims/catalog-wave-2.md`, auto-merge armed at
creation, merged 2026-07-11T02:02:51Z; claim removed here).

1. **Three full schema-v1 packs**, each filling EVERY slot the six
   existing packs fill — including the complete `labels` block
   (offline_return with `{gains}`, status/shop titles, shop
   description, level + prestige-progress labels) — over the same
   opaque engine ids (primary/prestige, tier1/tier2, boost1/boost2),
   data only, all budgets respected:
   `themes/wizard-tower.yaml` (mana / crystallized starlight;
   apprentice scribe + enchanted library; *ascend to the astral
   plane*), `themes/royal-bakery.yaml` (pastries / royal seals;
   sourdough starter + brick oven; *open a new royal franchise*),
   `themes/cyber-city.yaml` (credits / legacy code fragments; data
   haven + courier drone swarm; *upload your consciousness*).
   **Schema pinch audit: ZERO pinches** — all three fit v1 as
   published; no schema/ or parity changes needed.
2. **Tests 620** (from 533): nine-packs catalog test + per-pack
   noun-resolution tests for the three new packs; parametrized
   catalog/render/property suites picked the new packs up
   automatically (they glob `themes/*.yaml`) — the ONLY count pin was
   `tests/test_properties.py`'s catalog assertion, flipped 6 → 9.
   Core/skin guard extended with distinctive nouns only (wizard, mana,
   scribe, quill, starlight, astral, enchanted; bakery, bakehouse,
   pastry, sourdough, dough, flour, hearth, oven; cyber, neon, uplink,
   overclock, cryo-coolant) — generic words (tower, library, credits,
   city, royal, seal, swarm, grid, upload, franchise, fragment)
   deliberately EXCLUDED so the guard never fires on legitimate engine
   vocabulary; new boundary negatives (proven, describes/flourish,
   cybersecurity, manager) keep it honest.
3. `tests/vectors/setup-codes.v1.json` regenerated via
   `tools/gen_setup_vectors.py` (regenerate-or-red is catalog-coupled
   by design: valid=45, tolerance=55, errors=25 across 9 packs).

Verify: `python3 -m pytest -q` → 620 passed; `python3
tools/theme_gate.py themes` → all 9 packs PASS (schema v1); `python3
bootstrap.py check --strict` green after this flip.

## 💡 Session idea

The setup-code vector file is now the catalog's third identity surface
(after the stem rule and the duplicate-id check): any pack add/remove
reds `test_every_shipped_pack_has_valid_vectors` until regenerated.
That's the right ratchet, but the failure message points at the codec
("regenerate with…") not at the catalog; a one-line hint in
`tools/gen_setup_vectors.py`'s red-path ("did the catalog change?")
would save the next pack author the same two-minute detour this
session took.

## ⟲ Previous-session review

Wave 1's card (2026-07-11-catalog-growth-3-packs.md) predicted the
parametrized suites would absorb new packs without edits — exactly
right: catalog + render + property tests all globbed the three new
packs automatically; only the property suite's deliberate count pin
and the named-pack roster test needed touching. Its 💡 (enforce a
single `.yaml` extension to make `catalog_errors` provably
unreachable) remains parked and unaffected — wave 2 ships `.yaml`
only. The property-suite card's count pin (`== 6`, "expects the 6-pack
catalog") did its job as designed: it turned silent coverage growth
into an explicit, reviewed flip.
