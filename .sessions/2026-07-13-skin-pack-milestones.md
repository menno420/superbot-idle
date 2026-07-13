# 2026-07-13 — skin-pack milestones: flavor the 9 unskinned packs

> **Status:** `in-progress`

- **📊 Model:** opus-4.8 · high · feature build · skin-pack milestones — the 9 unskinned packs · 2026-07-13

## What happened

Data-only content slice. Three packs already carry a flavored `milestones:`
block (egg-farm — the template — plus potion-brewery and space-colony); the
other nine render the neutral `Milestone 1 … Milestone 9` scaffolding in the
achievements view (player review, rough-edge #8). This session skins those
nine so every pack in the catalog reads finished.

Nine packs skinned: ant-colony, cyber-city, deep-sea-station, dragon-hoard,
haunted-manor, idol-agency, pirate-cove, royal-bakery, wizard-tower.

Each gets a `milestones:` block mirroring egg-farm's exact structure: the nine
canonical engine-derived slot ids (`owned-1..3`, `lifetime-1..3`,
`prestige-1..3`), each with `id` / `name` / `description` / `emoji` and nothing
else. PURE CONTENT — label text only, in each pack's own voice (producer nouns
for the `owned` rungs, the pack's primary currency for the `lifetime` rungs,
its prestige currency for the `prestige` rungs). No schema change, no economy
numbers, no thresholds: the block is label-only by schema
(`schema/theme.schema.json` § milestones — `additionalProperties: false`,
required `id`/`name`/`description`/`emoji`, thresholds/bonuses are engine-side
per `docs/design/achievements-v0.md`), and every `prestige-*` id is legal
because all nine packs declare a `prestige` block (gate check).

## 💡 Session idea

The `owned-*` milestone rungs are pre-registered at 10 / 100 / 1000 *total
generators owned*, but the player review (rough-edge #4) shows `owned` can
never grow — there is no generator-purchase verb yet, so these three rungs sit
frozen at the seed count in every pack forever. Every pack I skinned now writes
lovely flavor ("a thousand foragers", "a thousand ovens") for a rung no player
can currently reach. Guard recipe: when the economy slice lands the
generator-purchase path (`idle_engine/economy.py` gen cost curve +
`idle_engine/upgrades.py` growing `state.owned`), add a render/achievements
test that a fresh grind actually trips `owned-1` (`achievements.py:82`
threshold, `render.py:377-381` award gate) — until then the `owned` flavor is
write-only.

## ⟲ Previous-session review

Builds directly on 2026-07-11-themes-space-potion.md (slice (c)), which added
the potion-brewery/space-colony packs and, with egg-farm, established the
`milestones:` block shape I mirror here — its own close-out flagged that packs
skin "the SAME opaque engine ids purely by convention". That holds here: this
slice touches zero engine ids and zero numbers, only the noun layer, so the
CORE/SKIN parity that session pinned stays intact. Its 💡 (canonical-roster
gate when baseline rates move engine-side) remains correctly parked for the
economy slice — untouched here. The reviewed player pass
(`scratchpad/idle-player-review.md`) is the direct driver: rough-edge #8 ("9/12
packs have unskinned `Milestone N`") is exactly what this card closes.
