# 2026-07-18 — theme-gate: reject duplicate YAML mapping keys

> **Status:** `in-progress`

- **📊 Model:** neutral builder-agent · medium · runtime bugfix · tooling-gate seat (theme-gate × malformed input) · 2026-07-18

## What / why

`tools/theme_gate.py` is the required-CI red gate for theme packs: its
docstring promises the strict-validation contract — "unknown keys are
rejected at every level", "a theme cannot smuggle new mechanics",
"overflow is a red gate, never a live render bug". But the gate parsed
each pack with `yaml.safe_load`, and PyYAML silently accepts **duplicate
mapping keys**, keeping the LAST value. So a pack with an accidental
duplicate key — a classic YAML footgun — passed the gate green while the
author's intended value was dropped with no warning.

Proven on current main before the fix: `egg-farm.yaml` with `theme.name`
written twice (`Egg Farm` then a stray `SHADOW NAME`) parses to
`name: 'SHADOW NAME'` and `validate_file` returns `[]` — the gate PASSES
a pack whose visible content silently diverged from its source. A
duplicated `base_rate` or a whole duplicated `generators:` block behaves
the same way: half the intent vanishes, gate stays green.

That is exactly the class of malformed pack the gate exists to red. The
fix parses through a strict loader that raises on the first duplicate key
at any nesting level, so the drop becomes a loud gate failure instead of
silent corruption.

## The fix (tools/theme_gate.py — gate-only, no engine change)

- Added `_StrictYAMLLoader(yaml.SafeLoader)` overriding `construct_mapping`
  to raise `yaml.constructor.ConstructorError("... found duplicate key
  ...")` the moment a key repeats within one mapping (preserving
  `flatten_mapping` and the hashable-key check so it stays a faithful
  SafeLoader otherwise).
- `validate_file` (and `main`'s re-parse of passing packs) now load via
  `_strict_yaml_load(...)`; the existing `except Exception` already turns
  the ConstructorError into a per-pack gate failure carrying the duplicate
  key and its line/column.
- Scope is the GATE only. The engine loader (`idle_engine.theme.load_theme`)
  is untouched — it never sees a duplicate-key pack, because the gate now
  reds before reaching the `load_theme` ground-truth step. The gate is the
  correct layer: it is the CI check that runs on every pack change.

## What was added (test)

New cases in `tests/test_theme_gate.py`:

- `test_duplicate_top_level_key_reds_gate` — a stray second `theme.name`
  (silent drop under safe_load) now returns a gate error naming the
  duplicate key, and `main` exits 1.
- `test_duplicate_nested_key_reds_gate` — a duplicated leaf inside a list
  item (`generators[0].base_rate`) is caught at depth, proving detection
  is not top-level-only.

RED→GREEN proof recorded in the PR: pre-fix `validate_file` returned `[]`
for the duplicate; post-fix it returns a `duplicate key` error.

## Verification

- `python3 -m pytest -q` — full suite green; count 1590 → 1592 sb-free
  (+2 gate tests; `docs/current-state.md` bumped, pinned-host job
  1605 → 1607 = sb-free 1592 + 15).
- All 20 shipped packs still PASS the gate (none carry duplicate keys).
- `python3 bootstrap.py check --strict` — only the born-red HOLD expected
  (this card, until flipped `complete`).

## Landing (born-red convention)

Card born RED (`in-progress`) in the first commit alongside
`control/claims/claude-theme-gate-dup-keys.md`; then the fix + tests +
current-state count-bump commit; card flipped `complete` as the last
commit to clear the HOLD so substrate-gate goes green and the landing
workflow merges on all-green. PR opened DRAFT then READY; the worker does
not merge its own PR.

## 💡 Session idea

The gate hardens the SKIN edge one malformed-input class at a time
(recent slices: duplicate ids #163, malformed embed_color #164). Duplicate
YAML keys are the structural sibling of those value-level checks — the
input is well-typed per key but the document itself is ambiguous. Natural
follow-up: the engine's own `load_theme` still uses a plain `safe_load`,
so a duplicate-key pack loaded OUTSIDE the gate (e.g. a live server
reading an unvetted pack) would still silently drop content. Threading the
same strict loader into `idle_engine.theme.load_theme` would close that
second door — but that is an engine change with its own blast radius, so
it is flagged here rather than folded into a gate-only slice.

## ⟲ Previous-session review

The last several slices worked the theme-loader / save seam: malformed
`embed_color` rejection (#164), duplicate-id guard (#163), and save
graceful-degradation across catalog drift (#165). Those pinned VALUE-level
and cross-catalog contracts. This slice moves up one level to the
DOCUMENT structure itself — the pack's YAML shape — closing the last easy
way a malformed pack could pass the required gate unnoticed. Same "fail
loud on a bad pack" discipline, applied to the parse step the earlier
value checks all sit downstream of.
