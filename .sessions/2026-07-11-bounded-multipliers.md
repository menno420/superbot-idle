# 2026-07-11 — bounded theme multipliers: schema-bounded rate_multiplier_pct mechanism

> **Status:** `in-progress`

- **📊 Model:** fable-5 · high · idle-engine seat (bounded-multipliers builder, coordinator-assigned) · 2026-07-11T17:58Z– (`date -u`)

## Plan

Exercise the last un-exercised founding-contract clause (README § CORE/SKIN
split, rule 2): "Balance multipliers only within schema-declared bounds."
Build the MECHANISM; actual non-neutral values stay sim-gated (Q-0264).

1. Claim `control/claims/bounded-multipliers.md` on main first (fast-lane
   PR #58, auto-merge armed at creation); remove in this PR's final commit.
2. TEST-FIRST: red suite before implementation — loader + gate red/green on
   bounds/types, schema↔loader bound-constant parity, neutral byte-identity
   pin, 90%/110% fixtures driving tick/offline exactly, property-suite
   extension (random in-bounds multipliers through the equivalence sweeps).
3. Schema v1 additive optional `balance` block: per-generator
   `rate_multiplier_pct` (integer percent, 100 = neutral), hard bounds
   90..110 IN THE JSON SCHEMA (min/max) + docs/theme-schema.md rationale.
4. Engine: fold the theme pct into the single-floor rate composition
   (`// 100_000_000`); neutral is integer-identical to the previous
   `// 1_000_000` fold, so every pre-slice output is byte-for-byte
   unchanged; tick == closed-form offline stays exact by construction.
5. Catalog stays neutral — no shipped pack gets a non-neutral value; the
   sim-gating statement lands as a short docs/design/ addendum.

## What happened

(born-red — close-out pending)
