# Theme schema v1 — the published contract for `themes/*.yaml`

> **Status:** `binding` — `schema_version: 1` (published 2026-07-11, slice (a) of
> ORDER 000 follow-up). Machine twin: [`schema/theme.schema.json`](../schema/theme.schema.json)
> (JSON Schema, draft 2020-12). The two are kept field-for-field identical by
> `tests/test_theme_schema.py::test_md_and_json_schema_field_parity` — edit both
> or the suite goes red.

A theme pack is **DATA ONLY**: it skins the engine's opaque ids (currencies,
generators) with every player-visible noun — names, flavor text, emoji, embed
color. It never adds mechanics. The theme-gate (`tools/theme_gate.py`, run by
`.github/workflows/theme-gate.yml`) validates every pack against the machine
schema plus the referential checks below; **a pack the gate passes must be safe
to enable on a live server unreviewed** — that property is the product.

## Versioning & compatibility

- Every pack declares `schema_version` at top level. **v1 packs declare
  exactly `1`**; a pack without it, or with any other value, is rejected.
- Unknown top-level keys (and unknown keys inside any mapping) are
  **rejected**, not ignored — a theme cannot smuggle new fields ahead of the
  schema. New capability = new schema version, published here first.
- Compatibility promise: within v1, fields are only ever **added as
  optional** with gate + doc landing together; anything that removes a field,
  changes a type, or tightens a budget on existing packs is v2 (`const: 2`,
  new migration note, gate validates each pack against its declared version).

## String budgets (hard limits — overflow is a red gate, not a render bug)

Budgets are derived from chat-embed caps: **title ≤ 256 chars, field value
≤ 1024 chars, ≤ 25 fields per embed**, and colors are decimal-RGB on the wire
so `embed_color` must be `#RRGGBB` hex. The schema encodes budgets *with
composition headroom* so every render slot fits by construction:

| Render slot | Embed cap | Schema budget | Headroom logic |
|---|---|---|---|
| Title: `{emoji} {name}` (+ status suffix) | 256 | name ≤ 64, emoji ≤ 32 | ≥ 159 chars left for suffixes |
| Field name: `{emoji} {name}` | 256 | 64 + 32 | same |
| Field value / embed description: `description` | 1024 | ≤ 1024 | description is the whole value |
| Fields per embed | 25 | ≤ 5 currencies + ≤ 20 generators | 5 + 20 = 25 |
| Upgrade-shop fields per embed | 25 | ≤ 20 upgrades | upgrades render on their own shop embed; 5 fields of headroom |
| Accent color | decimal RGB | `#RRGGBB` pattern | parses losslessly |
| Status description + offline line: `{description}\n\n{labels.offline_return with {gains} substituted}` | 4096 | description ≤ 1024, template ≤ 256 | 1024 + 2 + (256 − 7 token chars) = 1275 fixed; ≥ 2821 left for the substituted gains text (numeric — clamps) |
| Status / shop title override: `labels.status_title`, `labels.shop_title` | 256 | ≤ 256 | rendered verbatim, nothing composed — budget = cap |
| Shop description override: `labels.shop_description` | 4096 | ≤ 1024 | rendered verbatim as the embed description |
| Shop value: `{mark} {labels.level} N → N+1 · cost {emoji} {name}\n{upgrades[].description}` | 1024 | upgrade description ≤ 768, level label ≤ 32 | exact spend of the cap: description (768) + newline (1) + themed cost-line text (mark 1 + label 32 + emoji 32 + name 64 + separators 10 = 139) + digit floor (116) = 1024; the cost line is number-bearing and clamps into the room the description leaves — the description itself never truncates |
| Prestige progress value: `{mark} {labels.prestige_progress} N / M` | 1024 | label ≤ 64 | mark + label + separators ≤ ~70; ≥ 950 for digits before the numeric clamp |
| Achievements value: `{mark} N / M\n{milestones[].description}` | 1024 | milestone description ≤ 768 | shop-value arithmetic: description (768) + newline (1) leaves ≥ 255 for the number-bearing progress line, which clamps; the description never truncates |
| Achievements fields per embed | 25 | ≤ 9 engine slots | milestones render on their OWN achievements embed (the status view already spends up to 25 fields on 5 currencies + 20 generators); 16 fields of headroom |

## Fields

Types: `slug` = lowercase `a-z0-9` words joined by single hyphens
(`^[a-z0-9]+(-[a-z0-9]+)*$`), ≤ 32 chars. All strings are non-empty. *Flavor
text lives in the `description` fields* — there is no separate flavor slot in v1.

| Field | Type | Required | Constraint / budget |
|---|---|---|---|
| `schema_version` | integer | required | must be exactly `1` |
| `theme` | mapping | required | theme identity + embed frame |
| `theme.id` | slug | required | stable machine id, ≤ 32 chars |
| `theme.name` | string | required | player-visible name, 1–64 chars |
| `theme.description` | string | required | flavor text, 1–1024 chars |
| `theme.emoji` | string | required | 1–32 chars |
| `theme.embed_color` | string | required | `#RRGGBB` hex (e.g. `"#F5C542"`) |
| `currencies` | list | required | 1–5 entries |
| `currencies[].id` | slug | required | engine currency id being skinned |
| `currencies[].name` | string | required | player-visible name, 1–64 chars |
| `currencies[].description` | string | required | flavor text, 1–1024 chars |
| `currencies[].emoji` | string | required | 1–32 chars |
| `generators` | list | required | 1–20 entries |
| `generators[].id` | slug | required | engine generator id being skinned |
| `generators[].name` | string | required | player-visible name, 1–64 chars |
| `generators[].description` | string | required | flavor text, 1–1024 chars |
| `generators[].emoji` | string | required | 1–32 chars |
| `generators[].produces` | slug | required | MUST match a declared `currencies[].id` |
| `generators[].base_rate` | integer | required | 1–1000, units of `produces`/generator/second |
| `upgrades` | list | optional | 1–20 entries when present (own shop embed, 25-field cap) |
| `upgrades[].id` | slug | required* | engine upgrade id being skinned |
| `upgrades[].name` | string | required* | player-visible name, 1–64 chars |
| `upgrades[].description` | string | required* | flavor text, 1–768 chars (composed into the shop field value — see the shop-value budget row) |
| `upgrades[].emoji` | string | required* | 1–32 chars |
| `upgrades[].target` | slug | required* | MUST match a declared `generators[].id` |
| `prestige` | mapping | optional | the prestige track's skin (nouns only) |
| `prestige.currency` | slug | required* | prestige currency; MUST match a declared `currencies[].id`, ≠ `measures` |
| `prestige.measures` | slug | required* | lifetime-progress currency; MUST match a declared `currencies[].id`, ≠ `currency` |
| `prestige.action_name` | string | required* | player-visible reset-action name, 1–64 chars |
| `prestige.action_description` | string | required* | flavor text, 1–1024 chars |
| `prestige.action_emoji` | string | required* | 1–32 chars |
| `milestones` | list | optional | 1–9 entries; noun skins for the ENGINE-DERIVED milestone slots (own achievements embed) |
| `milestones[].id` | enum | required* | canonical slot id: `owned-1..3`, `lifetime-1..3`, `prestige-1..3`; `prestige-*` require the pack's `prestige` block (gate check); each id at most once |
| `milestones[].name` | string | required* | player-visible milestone name, 1–64 chars |
| `milestones[].description` | string | required* | flavor text, 1–768 chars (composed into the achievements field value — see the achievements-value budget row) |
| `milestones[].emoji` | string | required* | 1–32 chars |
| `labels` | mapping | optional | themed render-label overrides; ≥ 1 slot when present, EVERY slot optional |
| `labels.offline_return` | string | optional | offline-gains flavor template, 1–256 chars; MUST contain `{gains}` exactly once, no other braces (gate check) |
| `labels.status_title` | string | optional | status-view title, verbatim, 1–256 chars |
| `labels.shop_title` | string | optional | shop-view title, verbatim, 1–256 chars |
| `labels.shop_description` | string | optional | shop-view description, verbatim, 1–1024 chars |
| `labels.level` | string | optional | shop level label (replaces neutral `Lv`), 1–32 chars |
| `labels.prestige_progress` | string | optional | prestige progress label (default: bare numbers), 1–64 chars |

`upgrades` and `prestige` are v1's first OPTIONAL top-level fields (added
additively in slice (b), per the compatibility promise); `labels` is the
third (themed-label-slots slice); `milestones` is the fourth (achievements
slice). `required*` means required *within its block when the block is
present* — a pack may omit the whole block. **All these blocks are
nouns-only**: cost curves, effect sizes, thresholds and award math live
engine-side (`idle_engine/economy.py`, pre-registered in
[`design/upgrades-prestige-v0.md`](design/upgrades-prestige-v0.md) and
[`design/achievements-v0.md`](design/achievements-v0.md));
any numeric field smuggled into these blocks is rejected by
`additionalProperties: false`.

## `milestones` — noun skins for the engine-derived milestone slots (optional, additive)

Unlike `upgrades`/`prestige`, the `milestones` block does not DECLARE
mechanics at all: the milestone slot set is engine-derived (identical
pre-registered threshold ladders for every pack —
[`design/achievements-v0.md`](design/achievements-v0.md)), so two packs run
identical milestone mechanics whether or not either fills this block. An
entry skins ONE canonical slot id (`owned-1..3`: total generators owned;
`lifetime-1..3`: run-lifetime earnings of the measured currency;
`prestige-1..3`: prestige units held) with a name, flavor description and
emoji. Any subset may be skinned; an unskinned slot renders as the render
layer's neutral scaffolding (`Milestone {n}` + bare progress numbers), so a
pack without the block renders byte-stable neutral output. The
`prestige-1..3` slots exist only for packs declaring a `prestige` block —
skinning them without one is a red gate (a noun for a slot that does not
exist).

**`upgrades[].description` budget provenance** (shop-composition slice):
this field originally carried the generic 1024-char flavor budget but
rendered *nowhere* — the render layer parked its composition precisely
because 1024 left zero headroom. When the shop view first consumed it,
the budget was set to 768 *by* the composition arithmetic above (exact
spend of the 1024 field-value cap). No render contract ever relied on
the wider budget, and every shipped pack passed unchanged at the tighten
(catalog max: 100 chars) — which is why this landed within v1 rather
than as a v2 bump; a tighten that invalidated any existing pack would
have been v2 per the compatibility promise.

## `labels` — themed render-label slots (optional, additive)

The render layer ([`docs/render-layer.md`](render-layer.md)) contributes
neutral scaffolding for the handful of labels schema v1 originally had no
slot for. The `labels` block lets a pack theme them; **every slot is
optional and falls back to the neutral default**, so all pre-existing packs
stay valid AND render byte-identically without the block:

| Slot | Themes | Neutral fallback |
|---|---|---|
| `offline_return` | the offline-gains line appended to the status description | the bare gain lines |
| `status_title` | status-view embed title | `{theme.emoji} {theme.name}` |
| `shop_title` | shop-view embed title | `{theme.emoji} {theme.name}` |
| `shop_description` | shop-view embed description | `theme.description` |
| `level` | the level label in shop field values | `Lv` |
| `prestige_progress` | label before the prestige progress numbers | none (bare `N / M`) |

**`offline_return` substitution semantics** (exact): the template must
contain the literal token `{gains}` exactly once and no other `{`/`}`
characters (red gate). At render time the token — and ONLY the token; no
other formatting or escaping is applied — is replaced with the formatted
gains text (one `+{amount} {emoji} {name}` line per currency gained,
newline-joined), and the resulting line is appended to the theme
description after a blank line. The gains text is numeric-bearing so it
CLAMPS to the room left by the fixed template text; the template itself is
theme-sourced so it is never truncated (overflow raises, per the render
layer's two-tier budget policy).

**Budget arithmetic** (why composed output cannot bust embed caps):

- *Offline line*: description cap 4096 ≥ `theme.description` (≤ 1024) +
  `"\n\n"` (2) + template minus token (≤ 256 − 7 = 249) = 1275 fixed,
  leaving ≥ 2821 chars for the substituted gains, which clamp to exactly
  the room available.
- *Titles* (`status_title`, `shop_title`): rendered verbatim, nothing
  composed in — budget equals the 256-char title cap.
- *`shop_description`*: verbatim as the embed description — 1024 ≤ 4096.
- *`level`*: shop value composes `{mark} {label} N → N+1 · cost {emoji}
  {name}` on the cost line (plus the upgrade `description` on the line
  below, shop-composition slice) — mark (1) + label (≤ 32) + emoji (≤ 32)
  + name (≤ 64) + separators (10) = 139 fixed; with the description at
  its 768 budget and the joining newline, ≥ 116 chars remain for digits;
  the cost line is number-bearing and clamps into exactly that room.
- *`prestige_progress`*: value composes `{mark} {label} N / M` — mark +
  label (≤ 64) + separators ≤ ~70 of 1024, ≥ 950 for digits; clamps.

## Referential checks (enforced by the gate, beyond JSON Schema)

- `generators[].produces` references a declared `currencies[].id`.
- `currencies[].id` values are unique; `generators[].id` values are unique;
  `upgrades[].id` values are unique (duplicates would silently collapse in
  the engine's id maps).
- `upgrades[].target` references a declared `generators[].id`.
- `prestige.currency` and `prestige.measures` each reference a declared
  `currencies[].id`, and differ from each other (a track cannot measure the
  currency it awards).
- **Filename convention:** `theme.id` must equal the pack's filename stem —
  a pack lives at `themes/<theme.id>.yaml`. Catalog tooling and setup codes
  resolve packs by id, so a mismatched filename would ship a pack unreachable
  by the name it answers to. Checked per file; a mismatch is a red gate.
- `labels.offline_return`, when present, contains the substitution token
  `{gains}` **exactly once**, and no other `{`/`}` characters — an unknown
  placeholder (or a stray brace) is a red gate, so render-time substitution
  can never hit a token it does not know.
- `milestones[].id` values are unique (a duplicate would silently collapse
  in the theme's id map), and the `prestige-1..3` ids appear only in packs
  declaring a `prestige` block (the slot must exist to be skinned).
- The pack must load through `idle_engine.theme.load_theme` — the schema's
  ground truth is what the engine actually accepts.
- **Catalog-wide** (checked across all of `themes/`, not per file):
  `theme.id` is unique across every pack in the catalog — two packs
  claiming one id would silently shadow each other in any id-keyed
  catalog map, and per-file validation cannot see the collision.

## Balance bound (integrity floor)

`base_rate` is capped 1–1000 in v1 so a theme cannot smuggle economy balance
through the data lane. Baseline economy numbers are slated to move
engine-side (themes then carry only schema-bounded multipliers) in the
economy slice — see `.sessions/2026-07-10-order-000.md` § Session idea; that
change will be a schema revision published here.

## Minimal valid pack

```yaml
schema_version: 1
theme:
  id: egg-farm
  name: Egg Farm
  description: A cozy backyard farm where patient chickens fund your empire.
  emoji: "🥚"
  embed_color: "#F5C542"
currencies:
  - id: primary
    name: eggs
    description: Fresh eggs, the farm's lifeblood.
    emoji: "🥚"
generators:
  - id: tier1
    name: chicken coop
    description: A humble coop; each hen lays with metronomic dedication.
    emoji: "🐔"
    produces: primary
    base_rate: 1
```
