# 2026-07-18 — theme: enrich milestone/label flavor on thinnest packs (THM-19)

> **Status:** `in-progress`

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
merge on all-green. PR opened READY; the worker does not merge its own PR.
