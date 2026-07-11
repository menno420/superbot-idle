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
| `upgrades[].description` | string | required* | flavor text, 1–1024 chars |
| `upgrades[].emoji` | string | required* | 1–32 chars |
| `upgrades[].target` | slug | required* | MUST match a declared `generators[].id` |
| `prestige` | mapping | optional | the prestige track's skin (nouns only) |
| `prestige.currency` | slug | required* | prestige currency; MUST match a declared `currencies[].id`, ≠ `measures` |
| `prestige.measures` | slug | required* | lifetime-progress currency; MUST match a declared `currencies[].id`, ≠ `currency` |
| `prestige.action_name` | string | required* | player-visible reset-action name, 1–64 chars |
| `prestige.action_description` | string | required* | flavor text, 1–1024 chars |
| `prestige.action_emoji` | string | required* | 1–32 chars |

`upgrades` and `prestige` are v1's first OPTIONAL top-level fields (added
additively in slice (b), per the compatibility promise). `required*` means
required *within its block when the block is present* — a pack may omit the
whole block. **Both blocks are nouns-only**: cost curves, effect sizes,
thresholds and award math live engine-side (`idle_engine/economy.py`,
pre-registered in [`design/upgrades-prestige-v0.md`](design/upgrades-prestige-v0.md));
any numeric field smuggled into these blocks is rejected by
`additionalProperties: false`.

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
