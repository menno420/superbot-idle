# 2026-07-20 — theme: add vineyard/winery theme pack (wave 6, 21st)

> **Status:** `in-progress`

- **📊 Model:** Opus · high · data-authoring · content seat (new theme pack) · 2026-07-20

## What / why

⚑ **Self-initiated.** The executable backlog is dry and the roadmap is blocked
on fleet sim numbers, so this session takes the standing, mass-producible work
item (Q-0266): ship one more data-only theme pack. Contained to data + tests —
no engine code, no second repo, no secret.

The catalog ships 20 schema-v1 theme packs (waves 1–5); every pack is a
data-only skin over the same opaque engine ids (`primary`/`prestige`,
`tier1`/`tier2`, `boost1`/`boost2`) with identical mechanics and its own world.
This slice adds the **21st** pack (the first of a "wave 6"): a **vineyard /
winery** theme — a hillside estate where hand-tended vine rows and a great
estate winepress fill cask after cask of wine, and the prestige action **lays
down the cellar**, bottling the finest of the year into a grand cru vintage
before replanting for a new season.

The pack is authored to the frozen v1 schema (`schema/theme.schema.json`,
`docs/theme-schema.md`): the full
`theme`/`currencies`/`generators`/`upgrades`/`prestige`/`labels`/`milestones`
shape, all nine canonical milestone slots skinned, all six themed label slots
filled, a distinct claret `embed_color`, and NO `balance` block (neutral
rates). Numbers mirror the existing two-tier forge pack exactly (`tier1`
base_rate 1, `tier2` base_rate 5), so it is balanced-by-construction and needs
no fleet tuning verdict — staying inside the value ranges the sibling packs use.

**Reversible by construction:** one new file (`themes/vineyard.yaml`) plus the
catalog-sync guards it must satisfy — the pack-count guard
(`tests/test_properties.py`), the doc counts (`docs/current-state.md`), the
vineyard guard-noun entry (`tests/test_core_skin_guard.py`), and the
regenerated catalog-derived vector corpora (`tests/vectors/setup-codes.v1.json`,
`tests/vectors/render-embeds.v1.json`). Deleting the file and reverting the
counts restores the 20-pack catalog.

## Verification

- `python3 tools/theme_gate.py themes` — MUST report the new pack PASS and all
  packs valid (schema v1).
- `python3 -m pytest -q` — full suite green, including the parametrized
  per-pack render/engine-cycle/slot-fill coverage that auto-includes vineyard,
  the updated `test_properties.py` count guard, the regenerated
  `test_setup_vectors.py` / `test_render_vectors.py` regenerate-or-red +
  replay, the `test_core_skin_guard.py` catalog-sync guard, and the
  `test_current_state_counts.py` doc guards.
- `python3 bootstrap.py check --strict` (only the born-red HOLD expected).

## Landing (born-red convention)

Card born RED (`in-progress`) in the first commit alongside
`control/claims/claude-idle-theme-wave6.md`; then the pack + guards + regen
vectors; card flipped `complete` as the last commit to clear the born-red HOLD
so substrate-gate goes green and the landing workflow can merge on all-green.
PR opened READY; the worker does not merge its own PR.

## 💡 Idea

The nine milestone `name`s in every pack are freeform flavor with no gate on
their internal shape, yet each pack reuses the same rung skeleton
(first-X → hundred-X → empire, first-thousand → renown → legend, first-prestige
→ rack → master). A cheap "milestone silhouette" doc-honesty guard could assert
each pack fills all nine slots with pairwise-distinct `name`s and non-empty
flavor — catching a copy-paste pack that duplicated a rung noun before it ships
a confusing achievements embed, and scaling automatically with the roster.

## ⟲ Previous-session review

Predecessor **PR #174** (`2026-07-20-readiness-currentstate-claims.md`) was a
docs+control readiness sweep, not a content slice: it re-stamped
`docs/current-state.md` to HEAD, corrected a stale "In flight" note (verified
zero open PRs on live GitHub), recorded ORDER 011 + the merge-doctrine
de-walling, and pruned 23 orphaned claim files left by already-merged PRs
(#150–#173), keeping only the README. It touched no code (suite unchanged at
1607/1 skipped) and left history-bearing shipped cards alone. It holds up: the
claim dir it cleaned is boot-clean, and this session's own claim file is the
first new entry since that prune — confirming the readiness baseline it
established. Its 💡 (a `bootstrap claim --sweep-merged` verb to auto-reconcile
claims against merged PRs) is still a sensible unbuilt follow-up.
