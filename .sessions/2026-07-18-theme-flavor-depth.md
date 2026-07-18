# 2026-07-18 — theme: enrich milestone/label flavor on thinnest packs (THM-19)

> **Status:** `complete`

- **📊 Model:** neutral builder-agent · high · player-facing content · theme flavor-depth seat · 2026-07-18T00:07Z (`date -u`)

## What / why

Every theme pack skins the engine's milestone slots (`milestones[]`) and the
render layer's label slots (`labels`) with world-specific flavor. The two
exemplar packs — `wizard-tower` and `ramen-stand` — set the quality bar: dense,
witty, world-true one-liners on every milestone rung and every label. A
catalog-wide character-count survey of milestone descriptions + label text
found three packs sitting well below that bar, their progression reading flat
by comparison:

- **`egg-farm`** — thinnest by far (milestone descriptions averaging ~59 chars
  vs the exemplars' ~76–84; label text ~185 chars vs ~235–297). As the flagship
  default pack it is the first flavor most players ever see.
- **`space-colony`** — second thinnest; milestone/label lines functional but
  sparse against the exemplars.
- **`potion-brewery`** — third; witty milestones but noticeably terse labels and
  a few placeholder-ish rungs.

This slice (menu **THM-19**, under the owner's overnight full-autonomy order)
rewrites the milestone + label flavor on exactly those three packs so they read
at exemplar density and wit while staying strictly true to each pack's world.

**STRING-ONLY DATA + regenerated corpus** — no engine, render, mechanic, id,
currency, number, or structural change. Only flavor `description`/label strings
change, each verified within its schema budget. Milestone/label text renders
into the embeds, so the render golden corpus
(`tests/vectors/render-embeds.v1.json`) is regenerated via its blessed
generator `tools/gen_render_vectors.py` as an intentional, expected corpus
change. Fully reversible; packs not chosen are untouched.

## Verification

- `python3 tools/theme_gate.py themes` — passes (every edited string within its
  schema budget; over-budget flavor is a red gate).
- `python3 -m pytest -q` — full suite green, including the render drift test
  against the regenerated corpus and any per-pack budget tests.
- `python3 bootstrap.py check --strict` — only the born-red HOLD expected.

## Landing (born-red convention)

Card born RED (`in-progress`) in the first commit alongside
`control/claims/claude-theme-flavor-depth.md`; then the flavor-enrichment +
regenerated corpus commit; card flipped `complete` as the last commit to clear
the born-red HOLD so substrate-gate goes green and the landing workflow can
merge on all-green. PR opened READY (#159); the worker does not merge its own PR.

## Result

A character-count survey of milestone descriptions + label text across all 19
packs ranked the three thinnest as `egg-farm` (717), `space-colony` (811), and
`potion-brewery` (840) — all below the exemplar band (`wizard-tower` 923,
`ramen-stand` 1049). Those three were enriched to exemplar density and wit:

- `egg-farm` — all nine milestone descriptions rewritten (catalog-worst average
  ~59 → ~93 chars): the yard now "clucks and rustles like a real farm at dawn,"
  the county fair "pins your blue ribbon before the judging even begins," and a
  golden dynasty is "measured out in farms raised, sold, and quietly remembered."
  Its six **labels were deliberately left untouched** — `egg-farm` is the
  flagship default fixture and every label string is exact-string-pinned in
  `tests/test_render.py` and `tests/test_theme.py`; rewriting them would rewrite
  the canonical assertions those tests encode, out of scope for a data-only
  flavor slice. Milestone flavor was the larger thin surface anyway. Total
  717 → 1025.
- `space-colony` — milestone descriptions (avg ~66 → ~98) and labels enriched:
  the dead planet is "ever so faintly, starting to breathe back," the dome
  "stops whistling at night and the masks come off indoors," and neighbors have
  "stopped begging and started buying from you." Total 811 → 1204.
- `potion-brewery` — the pack's strong existing jokes (the "Well, one." crate,
  "recipes follow you") were preserved; the terse rungs and labels were the ones
  enriched: the guild now "stops sending inspectors and starts sending
  spectators," the town downwind reports "unusually purple sunsets," and the
  palace "pays, for once, on time." Total 840 → 1087.

All edits are flavor strings only — no id, currency, number, or structural
field touched; milestone names (some pinned in tests) and every mechanic left
exactly as-is. `python3 tools/theme_gate.py themes` PASS (19/19 — every edited
string within its schema budget). `python3 -m pytest -q` green (1526 passed, 1
skipped) including the render drift test against the regenerated
`tests/vectors/render-embeds.v1.json` (19 packs, 76 embeds). `bootstrap.py check
--strict` showed only the expected born-red HOLD.

## 💡 Session idea

Pack flavor "thinness" is currently an eyeball property with no floor — a new or
under-written pack can ship milestone/label text far below the exemplar band
unnoticed. A lightweight catalog test that computes each pack's milestone +
label flavor character density and reds if any pack falls too far below the
catalog median (or below a fixed floor) would turn "every pack reads as richly
as the exemplars" into an enforced contract, the same way the render corpus
enforces rendered output and the color-distinctness follow-up would enforce hue
separation.

## ⟲ Previous-session review

The immediately prior slice (`theme-color-distinctness`, THM-16, #158) recolored
five packs' `embed_color` and regenerated the render corpus as an intentional
delta — the same born-red discipline and the same "flavor/skin data + blessed
corpus regen, zero mechanics" shape as this slice. That slice polished how packs
*look* in Discord; this one polishes how they *read*. Both lean on the render
golden corpus (`test-render-golden-corpus`, TEST-2, #157) to make a player-facing
change self-documenting: the enriched flavor reds the drift test until the corpus
is regenerated, so the changed embed text is an explicit, reviewed delta rather
than a silent shift.
