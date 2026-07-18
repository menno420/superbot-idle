# 2026-07-18 — theme: durable loader↔schema parity-guard suite (capstone)

> **Status:** `complete`

- **📊 Model:** Opus 4.8 (1M context) · medium · test writing · engine-loader seat (theme × schema-vs-enforcement parity) · 2026-07-18

## 💡 Session idea

A run of slices (#164 embed_color format, #166/#167 duplicate YAML keys,
#168 base_rate ceiling) closed a whole class of bug: a constraint the
schema *declares* and the CI gate (`tools/theme_gate.py`) *enforces*, but
that `idle_engine/theme.py::load_theme` — the engine's runtime ground
truth — did **not** re-check, so a pack loaded outside the gate silently
corrupted or smuggled balance. The loader now re-checks every
value/format/uniqueness/reference/numeric-bound constraint in that class.

This slice is the **capstone**: a durable *parity-guard* so the class can
never SILENTLY regress. The individual per-constraint violation tests
(base_rate both ends, rate_multiplier both ends, embed_color format,
duplicate id/key, `produces` reference) already pin that each KNOWN
constraint stays enforced — but nothing catches a **NEW** schema
constraint added without matching loader enforcement. That meta-gap is
the real remaining value, and it is what this suite closes.

## ⟲ Previous-session review

Reviewed #168 (base_rate upper-bound, the last per-constraint member) and
its card `.sessions/2026-07-18-theme-base-rate-max.md`, plus the guard
tests in `tests/test_theme_loader_guards.py`, the semantic loader tests in
`tests/test_theme.py`, the balance-bounds loader tests in
`tests/test_theme_balance.py`, and the gate tests in
`tests/test_theme_schema.py`. Finding: per-constraint loader coverage is
comprehensive EXCEPT four reference-integrity guards that exist in the
loader but were only ever exercised through the *gate* — `upgrades[].target`,
`prestige.currency`, `prestige.measures`, and the prestige
`currency == measures` "differ" rule had **no loader-level violation test**.
So this slice is genuinely additive (capstone meta-check + those four
gap-closing loader tests), not duplication of the existing suite.

## What / why

Add `tests/test_theme_parity_guard.py`:

1. **Schema-introspection meta-check (the capstone).** Walk
   `schema/theme.schema.json` (resolving `$ref` into `$defs`) and emit a
   token `<path>:<keyword>` for every constraint-bearing keyword
   (`type`, `required`, `pattern`, `minimum`/`maximum`, `minItems`/
   `maxItems`, `minLength`/`maxLength`, `minProperties`, `const`, `enum`,
   `additionalProperties:false`). A total classifier sorts each token into
   **loader-re-checked** or a reviewed **gate-only** allow-list. The
   *dangerous* families (numeric bounds, `pattern`, `enum`, `const`,
   unknown-key rejection) are pinned to EXACT paths, so a new occurrence
   on a new field is UNCLASSIFIED and reds — forcing a human to either
   wire a loader guard or consciously mark it gate-only. The inert
   families (render-budget `maxLength`/`maxItems`, presence/type/non-empty
   `required`/`type`/`minLength`/`minItems`/`minProperties`) classify by
   keyword rule (documented, low-risk: they cannot silently change
   mechanics).

2. **Four gap-closing loader violation tests** for the reference-integrity
   guards that had no loader-level coverage: dangling `upgrades[].target`,
   dangling `prestige.currency`, dangling `prestige.measures`, and
   `prestige.currency == prestige.measures`. Same opaque-id, sb-free,
   tmp-YAML discipline as `tests/test_theme_loader_guards.py`.

Deliberately gate-only constraints (documented in the test): array
`maxItems` caps (render budget), string `maxLength` budgets (render
budget), slug charset `pattern`s (cosmetic id shape — cannot smuggle
mechanics), `schema_version` `const`/`type`/`required` (gate-owned pack
versioning), and every `additionalProperties:false` EXCEPT `labels`
(unknown keys are inert — the loader reads only the keys it knows, so a
smuggled key never reaches the engine; `labels` is the one block whose
loader actively rejects unknown slots).

TEST-ONLY plus the doc suite-count bump. No engine/loader/gate behavior
change in this slice.

## Verification

- `python3 -m pytest -q` — before/after counts recorded in the PR.
- Teeth check: temporarily loosened the loader's `upgrades[].target`
  reference guard and confirmed the corresponding parity test reds, then
  restored.
- `python3 bootstrap.py check --strict`.
- Confirmed only source/test/doc/governance files changed (no valid-pack
  output → no render-vector regen needed).
