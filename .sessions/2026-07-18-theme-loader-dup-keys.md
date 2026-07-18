# 2026-07-18 — theme: reject duplicate YAML mapping keys at load time

> **Status:** `in-progress`

- **📊 Model:** Opus 4.8 (1M context) · medium · runtime bugfix · engine-loader seat (theme × malformed input) · 2026-07-18

## What / why

`idle_engine.theme.load_theme` is the engine's ground-truth theme parser.
It already re-validates, at load, every schema constraint that would
otherwise surface as a deep crash or silent corruption: `#RRGGBB` embed
colors (#164), duplicate currency / generator / upgrade / milestone ids
(#163), `produces`/`target` references, `base_rate` positivity, balance
bounds. But it parsed the pack text itself with a plain `yaml.safe_load`,
and PyYAML **silently accepts duplicate mapping keys**, keeping the LAST
value. So a pack with an accidental duplicate key — a stray second
`name:`, a copy-pasted `base_rate:`, a whole duplicated `generators:`
block — loads clean with the author's intended value dropped and no error.

Slice #166 closed this at the CI gate (`tools/theme_gate.py`). Its card
explicitly flagged the twin: the engine loader still uses `safe_load`, so
a duplicate-key pack loaded OUTSIDE the gate (a live server reading an
unvetted / user-supplied pack, or any code path calling `load_theme`
directly) still silently drops content. The gate is CI-time defense; the
loader is runtime defense, and this check was the one missing runtime
guard while every other schema constraint is already re-checked at load.
Same asymmetry class as the embed-color and duplicate-id loader fixes.

## The fix (idle_engine/theme.py — engine loader, no tools/ import)

- Added a loader-local `_StrictYAMLLoader(yaml.SafeLoader)` overriding
  `construct_mapping` to raise on the first duplicate mapping key at any
  nesting depth (preserving `flatten_mapping` and the hashable-key check
  so it stays a faithful SafeLoader otherwise).
- `load_theme` now parses via `yaml.load(text, Loader=_StrictYAMLLoader)`
  and converts the constructor-level error into the loader's own
  where-anchored `ValueError` style (path + line/column), matching the
  existing `duplicate <x> id` / malformed-color messages.
- Deliberately a loader-LOCAL copy, NOT an import from
  `tools/theme_gate.py`: the engine layer keeps its own copies of shared
  helpers (the `_HEX_COLOR` regex, `GAINS_PLACEHOLDER`) precisely to avoid
  a cross-layer `idle_engine → tools` import. The strict loader follows
  the same discipline. Parity with the gate's loader is intentional.

## What was added (test)

New cases in `tests/test_theme_loader_guards.py` (raw-YAML-text packs —
the existing `yaml.safe_dump(dict)` helper cannot express a duplicate
key):

- `test_rejects_duplicate_top_level_key` — a stray second `theme.name`
  (silent drop under `safe_load`) now raises `ValueError` naming the
  duplicate key.
- `test_rejects_duplicate_nested_key` — a duplicated leaf inside a list
  item (`generators[0].base_rate`) is caught at depth, proving detection
  is not top-level-only.

RED→GREEN proof recorded in the PR: pre-fix the duplicate-key pack loads
clean and silently keeps the last value; post-fix it raises `ValueError`.

## Verification

- `python3 -m pytest -q` — full suite green; count 1592 → 1594 sb-free
  (+2 loader tests; `docs/current-state.md` bumped, pinned-host job
  1607 → 1609).
- All 20 shipped packs still load fine (none carry duplicate keys); a
  dup-key rejection changes no valid pack's parsed output, so render
  vectors are unchanged (source-only diff).
- `python3 bootstrap.py check --strict` — only the born-red HOLD expected
  (this card, until flipped `complete`).

## Landing (born-red convention)

Card born RED (`in-progress`) in the first commit alongside
`control/claims/claude-theme-loader-dup-keys.md`; then the fix + tests +
current-state count-bump commit; card flipped `complete` as the last
commit to clear the HOLD so substrate-gate goes green and the landing
workflow merges on all-green. PR opened DRAFT then READY; the worker does
not merge its own PR.

## 💡 Session idea

#166 hardened the CI gate against duplicate YAML keys; this slice threads
the same strict-parse discipline into the engine loader so the runtime
door closes too. The two now agree: a duplicate-key pack fails loud
whether it reaches the code through CI or through a live `load_theme`
call. That completes the "fail loud on a bad pack" story for the parse
step — value checks (#163, #164) and cross-catalog checks (#165) all sit
downstream of it, and both the gate and the loader now reject the
ambiguous document before any of them run.

## ⟲ Previous-session review

The last several slices worked the theme-loader / gate seam one
malformed-input class at a time: duplicate ids (#163), malformed
embed_color (#164), save graceful-degradation across catalog drift (#165),
and the gate-side duplicate-key rejection (#166). #166's own card named
this engine-loader twin as the explicit next door to close, noting it was
an engine change with its own blast radius so it should be its own slice
rather than folded into the gate-only change. This slice is that follow-up:
minimal, loader-local, no cross-layer import, and it leaves every valid
pack's parsed output untouched.
