# Render layer — the embed-payload contract for the plugin

> **Status:** `binding` (shipped 2026-07-11, render-layer slice). Code:
> [`idle_engine/render.py`](../idle_engine/render.py) · tests:
> `tests/test_render.py`. Consumer: superbot-next's plugin (the only layer
> that ever talks to the Discord API).

The render layer is PURE presentation: engine state + loaded theme pack in,
plain Discord-embed-shaped dicts out. No Discord SDK imports, no I/O, no wall
clock — callers pass `now` in, so the same state and theme always produce the
identical payload. It renders; it never mutates (offline gains are *shown*
here, *credited* only by `idle_engine.engine.apply_offline_progress`).

## Inputs

- `state: GameState` — the save being rendered.
- `theme: Theme` — a pack loaded via `idle_engine.theme.load_theme` (i.e.
  gate-valid: names ≤ 64, emoji ≤ 32, descriptions ≤ 1024, ≤ 5 currencies,
  ≤ 20 generators/upgrades).
- `now: int` (status view only) — the caller's unix timestamp.

## Payload shape

```python
{"title": str, "description": str, "color": int,   # decimal RGB from theme hex
 "fields": [{"name": str, "value": str, "inline": bool}, ...]}
```

## The three views

| Function | Shows | Returns `None` when |
|---|---|---|
| `render_status(state, theme, now)` | theme title/flavor, per-currency balances (+rate/s), per-generator counts + rates, offline gains since `state.last_seen` appended to the description | never |
| `render_shop(state, theme)` | one field per upgrade: current level → next, exact cost at current level (engine curve, `idle_engine.economy`), affordability mark | pack has no `upgrades` block |
| `render_prestige(state, theme)` | reset action as title/description, progress toward threshold with eligibility mark, held prestige balance + projected award | pack has no `prestige` block |

The pack's prestige currency renders from `state.prestige` (persistent),
every other currency from `state.balances` (run-scoped).

## Budget guarantees (hard, enforced at render time)

Every payload passes through the single validator `validate_embed` before it
is returned: title ≤ 256, field name ≤ 256, field value ≤ 1024, description
≤ 4096, ≤ 25 fields, color ∈ [0, 0xFFFFFF], no empty names/values. Two tiers:

- **Numeric/formatted overflow clamps**: any value that embeds formatted
  numbers is clamped at composition with a trailing `…` (a 2,000-digit
  balance is a display problem, not an error).
- **Theme-sourced overflow raises** `RenderBudgetError`: themed text is
  never truncated — the theme-gate already bounds it, so a violation means a
  broken pack or an engine bug, surfaced loudly instead of mangled silently.

## What the plugin must NOT do

- **No string surgery on themed text** — no truncating, casing, wrapping, or
  splicing of any title/name/value/description. The payload is final; render
  it verbatim. If it doesn't fit, that is a render-layer bug to report, not
  patch.
- No re-checking budgets with its own limits, no re-coloring, no injecting
  extra fields into these payloads (compose *separate* embeds if it needs
  platform chrome).
- No calling engine mutation functions to "refresh" a view — views are
  read-only by contract.

## Neutral scaffolding & themed label slots

The layer contributes neutral scaffolding — digits/thousands separators,
`+`/`/s`/`×`/`·`/`→`, the marks `✅`/`🔒`, and the generic label `Lv` in the
shop view — and packs may override it through schema v1's OPTIONAL `labels`
block (landed by the themed-label-slots slice; field list, substitution
semantics, and budget arithmetic in
[`docs/theme-schema.md`](theme-schema.md) § labels):

| Slot | Themes | Fallback when unset |
|---|---|---|
| `labels.offline_return` | offline-gains flavor line (template; the token `{gains}` is replaced with the formatted, clamped gains text) | bare gain lines |
| `labels.status_title` / `labels.shop_title` | the view's title, verbatim | `{emoji} {name}` |
| `labels.shop_description` | shop embed description, verbatim | `theme.description` |
| `labels.level` | shop level label | `Lv` |
| `labels.prestige_progress` | label before the prestige progress numbers | bare `N / M` |

Every slot is optional: a pack without the block renders byte-identically
to the pre-labels layer. Budget policy is unchanged — substituted numeric
text clamps, themed template/label text never truncates (overflow raises
`RenderBudgetError`).

Still parked: upgrade flavor `description` is not composed into the shop
cost field — the schema grants it the full 1024-char budget, so
composition could overflow on a legal pack; a themed shop layout with
headroom for it remains a follow-up.
