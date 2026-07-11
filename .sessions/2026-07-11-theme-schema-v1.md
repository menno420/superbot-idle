# 2026-07-11 — slice (a): THEME SCHEMA v1

> **Status:** `complete`

- **📊 Model:** fable-5 · high · idle-engine seat (slice (a) builder, coordinator-assigned) · 2026-07-11T00:02Z–00:1xZ (`date -u`)

## What happened

Published theme schema v1 in one build PR, after a control fast-lane claim
(PR #4, `control/claims/theme-schema-v1.md`, merged then removed here):

1. `docs/theme-schema.md` — human-readable schema v1 (`schema_version: 1`):
   every ORDER 000 slot (theme id/name/description/emoji/embed_color,
   currency id/name/description/emoji, generator id/name/description/emoji/
   produces/base_rate) with types, required/optional, string budgets,
   versioning + compatibility note; flavor text = the description fields.
2. `schema/theme.schema.json` — JSON Schema (draft 2020-12) twin;
   field-for-field parity with the md is TEST-ENFORCED
   (`tests/test_theme_schema.py::test_md_and_json_schema_field_parity`).
3. Chat-embed budgets as HARD schema limits: names ≤64 + emoji ≤32 (the
   256-char title cap with composition headroom), descriptions ≤1024 (the
   field-value cap), ≤5 currencies + ≤20 generators (the 25-field cap),
   `#RRGGBB` colors, `base_rate` bounded 1–1000, ids slug-patterned ≤32.
   `additionalProperties: false` at every level — unknown keys red the gate
   (data-only discipline: a theme cannot smuggle mechanics).
4. `tools/theme_gate.py` → v1: jsonschema validation against the machine
   schema + semantic checks a schema can't express (unique currency/
   generator ids, `produces` referencing a declared currency, engine loader
   as ground truth). Exit semantics kept (0 pass / 1 violation / 2 empty).
5. `themes/egg-farm.yaml` declares `schema_version: 1` — the pack already
   fit v1; no schema pinches beyond the deliberate base_rate bound.
6. Tests 24 → 40: parity, egg-farm green, red-gate tmp-file cases
   (oversized title/field value, >25 fields, bad color, unknown top-level
   AND nested keys, missing/wrong schema_version, base_rate bounds,
   dangling produces, duplicate ids). theme-gate workflow now installs
   `jsonschema` alongside `pyyaml`; kit-owned substrate-gate untouched.

Verify: `python3 -m pytest -q` → 40 passed; `python3 bootstrap.py check
--strict` green after this flip; `python3 tools/theme_gate.py themes` →
PASS (schema v1).

## 💡 Session idea

theme-gate validates packs one file at a time, so two packs can declare the
same `theme.id` and both pass — a catalog-level collision the per-file
schema cannot see. Guard recipe: add a cross-pack uniqueness check in
`tools/theme_gate.py::main` (collect `theme.id` per pack after per-file
validation, fail on duplicates) + a two-tmp-file test in
`tests/test_theme_schema.py`. Belongs in the theme-catalog slice, before
"N more themes" mass production starts.

## ⟲ Previous-session review

ORDER 000's card (2026-07-10-order-000.md) parked one 💡: `base_rate` rides
in the theme pack unbounded, while the pre-registered-economy contract
wants CORE-owned baselines. Half-landed here: schema v1 BOUNDS base_rate
(1–1000) so a theme can't smuggle balance through the data lane; the full
move (engine-owned economy table + bounded `rate_multiplier`) stays parked
for the economy slice and is flagged in both schema docs. Its guard recipe
format paid off — the bound landed in minutes, no re-derivation.
