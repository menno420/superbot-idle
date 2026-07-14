# 2026-07-14 — doc truth-fix: plugin capability string + themes schema pointer

> **Status:** `complete`

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

## What happened

Both stale lines quoted verbatim at branch base `2570cd8` before a
character changed, then fixed in one docs-only commit (PR #117,
implementation commit `0ef5102`; born-red pair `f89efcd`).

- **Before (plugin/README.md:7-8):** "`… + `settings` + `events` + the
  `idle`` / `capability) through the `sb.plugins` entry-point group`".
  **After:** "the `idle.game.play` capability" — byte-identical to
  `capabilities=("idle.game.play",)` at
  `plugin/superbot_idle_plugin/manifest.py:270` (renamed by PR #85; the
  README was the straggler). The `capability="idle"` field on the four
  CommandSpecs (`manifest.py` ~L231-264) is a different field, still
  correct, and every statement about it is untouched — the only other
  capability mentions in the README (L19 facet list) were already
  accurate.
- **Before (plugin/pyproject.toml header):** "One command (`!idle` /
  `/idle`) + one status panel (`idle.status`)". **After:** "Four
  commands (`!idle` + `status` / `shop` / `prestige` subcommands), three
  render handlers, and one status panel" — matching the manifest's four
  `CommandSpec`s and three `idle.render.*` handler refs. Comment-only;
  no TOML value touched.
- **Before (themes/README.md:6):** "schema (`docs/theme-schema.md`,
  forthcoming)". **After:** a live relative link to the published doc
  with its real state — Status `binding`, published 2026-07-11, machine
  twin `schema/theme.schema.json`. The L3 `binding` badge preserved
  byte-for-byte.

Verify: `python3 -m pytest -q` → `1366 passed, 1 skipped in 15.67s`
(zero delta — docs-only); `python3 bootstrap.py check --strict` → the
born-red designed hold on this very card pre-flip ("This red is the
designed hold, not a defect"), green once this flip lands;
`grep -rn 'forthcoming' themes/README.md plugin/README.md
plugin/pyproject.toml` → no matches; `grep -n 'idle.game.play'
plugin/README.md plugin/superbot_idle_plugin/manifest.py` → both hits,
strings identical.

## 💡 Session idea

Both stalenesses are the same failure shape: a doc quotes a literal that
lives in exactly one source-of-truth location (a capability string in
`manifest.py`, a doc's published/forthcoming state), the source moves
(PR #85; theme-schema publication 2026-07-11), and no gate notices
because the doc checker validates badges, not cross-file literals. Guard
recipe: a `docs-literals` advisory checker — a small table of
(doc-path, regex, source-path, extractor) pairs, e.g.
(`plugin/README.md`, `` `idle\.game\.play` ``, extract
`capabilities=(...)` from `plugin/superbot_idle_plugin/manifest.py`) and
(`themes/README.md`, must-not-match `forthcoming` while
`docs/theme-schema.md` badge says `binding`). Anchors: sits beside the
badge checker in `bootstrap.py` (the `_BADGE_RE` machinery ~L1531
already parses doc heads, so the "read a badge from another doc" leg is
one function call away), and the parity test
`tests/test_theme_schema.py::test_md_and_json_schema_field_parity` is
the in-repo precedent that cross-file literal drift is testable —
this would be the docs-tier sibling of that schema-tier guard. Both of
today's stalenesses would have been caught the day their sources moved.

## ⟲ Previous-session review

previous-session review: the newest prior card at HEAD,
`.sessions/2026-07-14-improve-repl-hardening.md` (slice A, PR #115 =
branch base `2570cd8`), set the wave's evidence bar — reproduce/quote
BEFORE touching anything, then show the same probe clean after. This
card copied that discipline into docs space: both stale lines were
grepped and quoted at `2570cd8` pre-edit, and the same greps re-run
post-edit form the verify tail. Its 💡 (a `repl-fuzz` smoke test piping
an adversarial script through the real loop) and this card's 💡
(`docs-literals` cross-file checker) are converging on one lesson from
opposite ends: the repo's gates are strong inside each artifact class
but thin across seams — human-at-the-prompt paths there, doc-quotes-code
literals here. Also confirmed live: its claim-first / flip-last / delete
-claim-in-flip choreography transplanted to a docs-only slice with zero
friction, evidence the Q-0194 pair protocol is task-class-agnostic.
