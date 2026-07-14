# 2026-07-14 — doc truth-fix: plugin capability string + themes schema pointer

> **Status:** `in-progress`

- **📊 Model:** fable-5 · medium · docs-only · doc truth-fix (plugin capability string + themes schema pointer) · 2026-07-14 · plugin/README.md + plugin/pyproject.toml header comment + themes/README.md only (ZERO code change)

## What this session is doing

Improvement-wave slice C (owner directive 2026-07-14): true up two VERIFIED
stale documentation claims, docs-only. Claimed first per
`control/claims/README.md`
(`control/claims/claude-improve-doc-truthfix.md`; deleted in this card's
flip commit).

1. **Plugin capability string.** `plugin/README.md` (~L6-8) says the
   manifest exports "the `idle` capability" — the actual export is
   `capabilities=("idle.game.play",)`
   (`plugin/superbot_idle_plugin/manifest.py:270`, changed by PR #85;
   the README was missed). NOTE: `capability="idle"` on the CommandSpecs
   (`manifest.py` ~L231-264) is a DIFFERENT field and is correct —
   statements about it stay untouched. Also refreshing the stale
   `plugin/pyproject.toml` header comment ("One command (`!idle` /
   `/idle`) + one status panel" — the manifest now declares 4 commands
   + 3 render handlers) — comment-only change.
2. **Themes schema pointer.** `themes/README.md:6` says the theme-gate
   validates against "the published schema (`docs/theme-schema.md`,
   forthcoming)" — that schema was published 2026-07-11 with Status
   `binding` (plus its machine twin `schema/theme.schema.json`). Drop
   "forthcoming", point at the published doc.

Both stalenesses re-verified against source at branch base `2570cd8`
before editing. Docs-gate note: `themes/README.md` carries a
`> **Status:** \`binding\`` badge at L3 (preserved as-is);
`plugin/README.md` carries none and none is added.
