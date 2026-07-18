# 2026-07-17 — theme: decluster embed_color values for visual distinctness (THM-16)

> **Status:** `complete`

- **📊 Model:** neutral builder-agent · high · mechanical refactor · embed-color declutter seat · 2026-07-17T23:59Z (`date -u`)

## What / why

Every theme pack carries an `embed_color` (`#RRGGBB`) that Discord paints as the
embed's left accent strip on every rendered view. Across the 19 shipped packs the
colors have drifted into near-duplicate clusters, so visually distinct themes read
as the same in Discord. A full-catalog perceptual survey (redmean distance over
all pairs) found four clusters of near-identical colors:

- **Teal/sea run** — `deep-sea-station #0B6E8C` and `pirate-cove #0E7490` sit only
  14.5 apart (near-identical), with `lighthouse-keep #1B5E8A` clustered against
  both (39.6 / 48.9).
- **Purples** — `potion-brewery #7B3FA0` and `wizard-tower #6A3FB5` at 42.8.
- **Pinks** — `idol-agency #E75480` and `candy-factory #EC5C9C` at 44.3.
- **Brown run** — `coffee-roastery #6F4E37` and `ant-colony #8B5A2B` at 53.7,
  the tightest pair in a dense warm-brown cluster.

This slice (menu **THM-16**, under the owner's overnight full-autonomy order)
recolors the minimum set of packs needed to break those clusters — moving one
pack out of each cluster (two for the 3-way teal tangle, keeping `deep-sea` as the
anchor) to a hue that is still thematically true to the pack yet perceptually
well separated from every other pack and unique across the catalog. Each edit is a
single `embed_color` data line; already-distinct packs are left untouched.

**DATA + regenerated corpus only** — no engine, render, or product-logic change.
`embed_color` is part of the rendered embeds, so the render golden corpus
(`tests/vectors/render-embeds.v1.json`) is regenerated via its blessed generator
`tools/gen_render_vectors.py` as an intentional, expected corpus change. Fully
reversible.

## Verification

- `python3 tools/theme_gate.py themes` — passes (`#RRGGBB` format upheld).
- `python3 -m pytest -q` — full suite green, including the render drift test
  against the regenerated corpus.
- `python3 bootstrap.py check --strict` — only the born-red HOLD expected.

## Landing (born-red convention)

Card born RED (`in-progress`) in the first commit alongside
`control/claims/claude-theme-color-distinctness.md`; then the recolor +
regenerated corpus commit; card flipped `complete` as the last commit to clear the
born-red HOLD so substrate-gate goes green and the landing workflow can merge on
all-green. PR opened READY (#158); the worker does not merge its own PR.

## Result

Five packs recolored, one `embed_color` line each, breaking all four near-duplicate
clusters (redmean distances, old → new):

- `potion-brewery` `#7B3FA0` → `#35C15E` — bubbling green brew; leaves the purple
  cluster entirely (no other green in the catalog).
- `pirate-cove` `#0E7490` → `#16A085` — tropical cove sea-green; breaks the 14.5
  near-duplicate with `deep-sea-station`.
- `lighthouse-keep` `#1B5E8A` → `#16346B` — deep night-sea navy; breaks the residual
  teal-run cluster (39.6 / 48.9) with `deep-sea-station`.
- `candy-factory` `#EC5C9C` → `#B026C9` — grape/berry candy violet; separates from
  `idol-agency`'s iconic pink (44.3).
- `coffee-roastery` `#6F4E37` → `#3B2417` — dark espresso roast; breaks the tightest
  warm-brown pair with `ant-colony` (53.7), thinning the run.

`deep-sea-station` kept as the teal anchor; `wizard-tower` keeps its arcane violet
and `idol-agency` its pink. After the edits every recolored pack's nearest neighbor
is ≥100 redmean; already-distinct packs (the warm-gold run, the arctic/space blues)
untouched. `tools/theme_gate.py themes` PASS (19/19, `#RRGGBB` upheld);
`python3 -m pytest -q` green (1526 passed, 1 skipped) including the render drift test
against the regenerated `tests/vectors/render-embeds.v1.json` (19 packs, 76 embeds;
a second regeneration was byte-identical — deterministic). `bootstrap.py check
--strict` showed only the expected born-red HOLD.

## 💡 Session idea

`embed_color` distinctness is currently a human-eyeball property with no test guard —
a future pack could re-cluster silently. A natural follow-up is a lightweight catalog
test that computes pairwise perceptual (redmean) distance across all packs' colors and
reds if any pair falls below a chosen floor, turning "themes look distinct in Discord"
into an enforced contract the way the render corpus enforces rendered output.

## ⟲ Previous-session review

The immediately prior slice (`test-render-golden-corpus`, TEST-2, #157) pinned the
rendered embed surface of all 19 packs byte-exactly — `embed_color` included, stored as
the Discord decimal `color` field. That corpus is exactly why this player-facing color
change is safe and self-documenting: the recolor reds the drift test until the corpus is
regenerated, so the 20 changed color fields (5 packs × 4 views) are an explicit, reviewed
delta rather than a silent shift. Same born-red session-gate discipline; this slice is the
player-visible polish complement to that test-only snapshot.
