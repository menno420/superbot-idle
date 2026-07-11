# 2026-07-11 — slice (a): THEME SCHEMA v1

> **Status:** `in-progress`

- **📊 Model:** fable-5 · high · idle-engine seat (slice (a) builder, coordinator-assigned) · started 2026-07-11T00:02Z (`date -u`)

## Plan

Publish theme schema v1 in both human and machine form, and harden the
theme-gate so a passing pack is provably safe to render live:

1. `docs/theme-schema.md` — published schema v1 (every ORDER 000 slot,
   types, required/optional, string budgets, `schema_version: 1`,
   compatibility note).
2. `schema/theme.schema.json` — JSON Schema (draft 2020-12), field-for-field
   parity with the md.
3. Discord string budgets as hard schema limits (title ≤256, field value
   ≤1024, ≤25 fields, `#RRGGBB` color) so overflow is a red gate.
4. `tools/theme_gate.py` — validate every pack against the machine schema
   via `jsonschema`; require `schema_version`; reject unknown top-level
   fields; keep exit semantics (0/1/2).
5. `themes/egg-farm.yaml` — declare `schema_version: 1`.
6. Tests — md/json parity, egg-farm green, red-gate cases via tmp files.
7. `.github/workflows/theme-gate.yml` — add the `jsonschema` dep.

Claim landed first: `control/claims/theme-schema-v1.md` (PR #4, control
fast lane); removed again in this build PR's final commit.
