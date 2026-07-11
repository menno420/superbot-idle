# 2026-07-11 — shop composition: themed upgrade descriptions in shop view within budget arithmetic

> **Status:** `complete`

- **📊 Model:** fable-5 · high · idle-engine seat (shop-composition builder, coordinator-assigned) · 2026-07-11T02:17Z–02:2xZ (`date -u`)

## What happened

Landed the LAST parked render-layer item (docs/render-layer.md) in one
build PR after a control fast-lane claim (PR #36,
`control/claims/shop-composition.md`, merged then removed here): each
upgrade's themed `description` is now composed into the shop view's
field values, with arithmetic that guarantees the 1024-char field-value
budget worst-case.

1. **Composition contract** (idle_engine/render.py `render_shop`): the
   field value is `{cost line}\n{description}`. The two budget tiers
   split exactly along the newline — the number-bearing cost line
   (mark, level, cost) clamps into precisely the room the description
   leaves (`1024 − len(description) − 1`); the description is
   theme-sourced and never truncated (overflowing its slot raises
   `RenderBudgetError`, the theme-overflow tier — an explicit check,
   because the numeric clamp would otherwise silently starve the cost
   line instead of surfacing the broken pack).
2. **The arithmetic** (the slice's core): description (768) + newline
   (1) + themed cost-line fixed text (mark 1 + level label 32 +
   currency emoji 32 + currency name 64 + separators 10 = 139) + digit
   floor (116) = **1024 exactly**. Documented in docs/theme-schema.md
   (budget table row + § labels bullet + provenance note) and
   docs/render-layer.md (§ Shop composition, parked item removed).
3. **Schema cap tightened 1024 → 768** for `upgrades[].description`
   (new `$defs.shop_flavor_text`). Judged in-bounds for v1 because the
   field previously rendered NOWHERE (its composition was parked
   precisely for lacking headroom), so no render contract relied on the
   wider budget, and every shipped pack passes unchanged — catalog max
   was 100 chars across all 9 packs. A tighten that invalidated any
   existing pack would have been v2; provenance note says so in the doc.
   `render.SHOP_FLAVOR_LIMIT == $defs.shop_flavor_text.maxLength == 768`
   is pinned by test so neither side can drift alone.
4. **Fallback pinned byte-identical**: an upgrade without a description
   (hand-built `Theme` objects only — the gate requires the field)
   renders the bare cost line exactly as the pre-composition layer, no
   newline appended.
5. **Tests 620 → 628**: exact composed pin (egg-farm), fallback pin
   (both marks), worst-case extremes (768-char flavor × 32-char level
   label × 96-char currency label × 10^607 cost: value spends the cap
   exactly, flavor verbatim, cost line clamps with `…`), boundary 768
   never raises across 0–10^2000 balances, 769 raises, schema red-gate
   at 769 / green at 768, schema↔render budget-sync pin; all 9 packs
   render green; render fuzz (tests/test_properties.py) untouched and
   green.

Verify: `python3 -m pytest -q` → 628 passed; `python3
tools/theme_gate.py themes` → all 9 packs valid; `python3 bootstrap.py
check --strict` green with this card flipped.

## 💡 Session idea

The shop value is now the SECOND slot where the two budget tiers
compose in one string (after `labels.offline_return`), and both
implement the same shape by hand: "fixed themed text never truncates,
numeric remainder clamps into `cap − fixed`". If a third composed slot
lands (a prestige-award flavor line is the obvious candidate), extract
a tiny `_compose_budgeted(themed_fixed, numeric, cap)` helper in
render.py that computes the room, clamps the numeric part, and raises
the theme-overflow tier — then the arithmetic lives (and is tested)
once instead of being re-derived per slot in docs and code.

## ⟲ Previous-session review

The themed-label-slots card (2026-07-11-themed-label-slots.md) parked
this slice with the exact blocker ("the schema still grants that field
the full 1024, so it stays parked pending a themed shop layout with
real headroom") — and that framing quietly assumed the headroom had to
come from LAYOUT. It didn't: the field had never rendered anywhere, so
its 1024 budget was headroom nobody used, and tightening it AT the
moment of first consumption is compatibility-clean in a way a later
tighten never would have been. Lesson worth keeping: grant a flavor
field its render budget when a renderer first consumes it, not before —
un-consumed budget is a liability the compatibility promise makes
expensive to reclaim. Its union-merge friction note about
`.substrate/guard-fires.jsonl` was again exactly right: the file
dirtied mid-session (concurrent docs-grooming PR #37 merged mid-flight)
and stash → rebase → pop resolved it without conflict.
