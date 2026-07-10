# themes/ — data-only theme packs

> **Status:** `binding` (seeded 2026-07-10; schema lands with ORDER 000 → slice a)

One `<name>.yaml` per theme, validated by the theme-gate against the published
schema (`docs/theme-schema.md`, forthcoming). A theme pack contains ONLY data:
display names, flavor text, emoji, art refs, embed colors, and balance
multipliers within schema-declared bounds. **No code, no new mechanics, ever.**
First theme: `egg-farm.yaml` (the flagship default). A theme the gate passes
must be safe to enable on a live Discord server unreviewed — that property is
what makes "N more themes" a standing, mass-producible work item (Q-0266).
