# 2026-07-11 — catalog wave 3: pirate-cove + ant-colony + idol-agency (9 → 12)

> **Status:** `complete`

- **📊 Model:** fable-5 · high · idle-engine seat (catalog-wave-3 builder, coordinator-assigned) · 2026-07-11T02:44Z–02:5xZ (`date -u`)

## What happened

Grew the catalog 9 → 12 packs in one build PR after a control fast-lane
claim (PR #43, `control/claims/catalog-wave-3.md`, auto-merge armed at
creation, merged 2026-07-11T02:45:23Z; claim removed here).

1. **Three full schema-v1 packs**, each filling EVERY slot the nine
   existing packs fill — including the complete `labels` block
   (offline_return with `{gains}`, status/shop titles, shop
   description, level + prestige-progress labels) — over the same
   opaque engine ids (primary/prestige, tier1/tier2, boost1/boost2),
   data only, all budgets respected:
   `themes/pirate-cove.yaml` (doubloons / cursed relics; smuggler
   skiff + tavern crew; *bury the treasure and set sail*),
   `themes/ant-colony.yaml` (crumbs / royal jelly; forager trail +
   fungus garden; *crown a new queen*), `themes/idol-agency.yaml`
   (fans / platinum records; practice room + livestream studio;
   *graduate and debut a new group*).
   **Schema pinch audit: ZERO pinches** — all three fit v1 as
   published; no schema/ or parity changes needed.
2. **Tests 827** (from 737): twelve-packs catalog roster test +
   per-pack noun-resolution tests for the three new packs;
   parametrized catalog/render/property suites picked the new packs
   up automatically (they glob `themes/*.yaml`) — the ONLY count pin
   was `tests/test_properties.py`'s catalog assertion, flipped 9 → 12.
   Core/skin guard extended with distinctive nouns only (pirate,
   doubloon, smuggler, skiff, tavern, rum, quartermaster, cove; ant,
   crumb, pheromone, forager, leafcutter, fungus, instar; idol,
   fandom, fancam, livestream, choreography, platinum, lightstick) —
   generic words (crew, treasure, tide, captain, anchor, queen, nest,
   worker, trail, garden, jelly, fan, studio, record, stage, debut,
   graduate, agency) deliberately EXCLUDED so the guard never fires
   on legitimate engine vocabulary; new boundary negatives
   (important/quantum/spectrum for ant+rum, covered, crumbling,
   idolatrous) keep it honest. Pre-flight grep of all candidate nouns
   against `idle_engine/` + `tools/theme_gate.py`: zero hits.
3. `tests/vectors/setup-codes.v1.json` regenerated via
   `tools/gen_setup_vectors.py` (regenerate-or-red is catalog-coupled
   by design: valid=60, tolerance=73, errors=25 across 12 packs).

Verify: `python3 -m pytest -q` → 827 passed; `python3
tools/theme_gate.py themes` → all 12 packs PASS (schema v1); `python3
bootstrap.py check --strict` green after this flip.

## 💡 Session idea

The core/skin guard's noun regex is now ~40 lines of hand-ordered
alternation and every wave re-litigates the same distinctive-vs-generic
call in a comment. A tiny data shape — `FORBIDDEN_NOUNS_BY_PACK:
dict[str, list[str]]` compiled into one regex, with an `EXCLUDED:
dict[str, list[str]]` twin — would make the per-pack provenance
mechanical, let a test assert every shipped pack contributes at least
one guard noun, and turn wave N+1's guard edit into a two-list append.

## ⟲ Previous-session review

Wave 2's card (2026-07-11-catalog-wave-2.md) flagged that the vector
suite's red-path message points at the codec, not the catalog — this
session pre-empted the detour by regenerating vectors in the same
commit as the packs, so the red never fired; the suggested one-line
hint in `tools/gen_setup_vectors.py` remains a cheap, unclaimed
improvement. Its prediction pattern (parametrized suites absorb new
packs; only the property-suite pin and the named roster test need
touching) held for the third wave running — that's now a stable,
documented playbook rather than a hypothesis.
