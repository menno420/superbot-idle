# 2026-07-18 — theme: enforce base_rate upper bound (schema maximum 1000) at load

> **Status:** `complete`

- **📊 Model:** Opus 4.8 (1M context) · medium · runtime bugfix · engine-loader seat (theme × schema-vs-enforcement parity) · 2026-07-18

## What / why

`idle_engine.theme.load_theme` is the engine's ground-truth theme parser.
It re-validates, at load, the schema constraints that would otherwise
surface as a deep crash or silent corruption: `#RRGGBB` embed colors
(#164), duplicate ids (#163), duplicate YAML keys (#167), `produces` /
`target` references, and the `balance[].rate_multiplier_pct` bounds
90..110 (re-checked BOTH ends as defense in depth).

The schema declares `generators[].base_rate` an integer bounded
**1..1000** — the comment is explicit: *"Bounded 1-1000 in v1 so a theme
cannot smuggle economy balance."* The gate (jsonschema) enforces both
ends. The loader enforced only the **lower** bound (`base_rate < 1` →
"must be a positive integer") — the upper bound `<= 1000` was missing.
So a pack with `base_rate: 999999`, loaded directly via `load_theme`
(a live server reading an unvetted / user-supplied pack, or any code path
calling the loader outside the CI gate), loaded **clean** and carried an
out-of-bounds rate straight into the engine economy — no crash, no error,
the exact balance-smuggling the schema bound exists to prevent.

Same asymmetry class as the embed-color, duplicate-id and duplicate-key
loader fixes: a schema constraint the gate enforces but the loader — the
runtime ground truth — did not. This is the numeric-bound member of that
family, and it was only HALF closed (lower bound only) until now.

## The fix (idle_engine/theme.py — engine loader, no tools/ import)

- Added loader-local `BASE_RATE_MIN = 1` / `BASE_RATE_MAX = 1000`
  constants (parity with the schema's `minimum` / `maximum`, pinned by
  test), documented as the defense-in-depth twin of the schema bounds —
  mirroring the existing `RATE_MULTIPLIER_MIN/MAX` block.
- The `base_rate` guard now type-checks, then re-checks BOTH bounds with
  a where-anchored `ValueError` ("... is outside the schema-declared
  bounds 1..1000"), matching the balance-bounds message.
- Loader-LOCAL, NOT an import from `tools/theme_gate.py`: the engine
  layer keeps its own copies of shared constraints (the `_HEX_COLOR`
  regex, `GAINS_PLACEHOLDER`, the strict YAML loader) to avoid a
  cross-layer `idle_engine → tools` import. Parity with the gate is
  intentional.

## What was added (test)

New cases in `tests/test_theme_loader_guards.py`:

- `test_rejects_base_rate_above_schema_max` — `1001 / 5000 / 999999` each
  now raise `ValueError` (RED on main: they loaded clean).
- `test_accepts_base_rate_at_schema_max` — the boundary value `1000`
  still loads (guard is inclusive, does not over-reject valid packs).

RED→GREEN proof recorded in the PR: pre-fix `base_rate: 999999` loads
clean; post-fix it raises `ValueError`.

## Verification

- `python3 -m pytest -q` — full suite green; count bumped in
  `docs/current-state.md` to the exact new total.
- All 20 shipped packs still load / pass (none carry `base_rate > 1000`;
  every shipped rate is at the low end). A pure validation-tightening
  that rejects an out-of-bounds value changes NO valid pack's parsed
  output → render vectors unchanged (source-only diff).
- `python3 bootstrap.py check --strict` — only the born-red HOLD expected
  (this card, until flipped `complete`).

## Landing (born-red convention)

Card born RED (`in-progress`) in the first commit alongside
`control/claims/claude-theme-base-rate-max.md`; then the fix + tests +
current-state count-bump commit; card flipped `complete` as the last
commit to clear the HOLD so substrate-gate goes green and the landing
workflow merges on all-green. PR opened DRAFT then READY; the worker does
not merge its own PR.

## 💡 Session idea

The schema-vs-enforcement parity hunt has now walked the whole family of
"schema declares it, loader is ground truth so re-check it": format
(embed_color #164), uniqueness (dup ids #163), document ambiguity (dup
YAML keys #167), and — with this slice — the numeric BOUND. `base_rate`
was the one constraint the loader enforced only halfway (positivity but
not the ceiling), so it was the highest-value remaining gap: not a shape
nit but a balance-smuggling hole, since an over-max rate silently changes
the economy rather than failing loud. The loader and gate now agree on
both ends of every numeric bound they share (`base_rate` 1..1000,
`rate_multiplier_pct` 90..110).

## ⟲ Previous-session review

Recent slices worked the theme-loader / gate seam one malformed-input
class at a time: duplicate ids (#163), malformed embed_color (#164), save
graceful-degradation across catalog drift (#165), gate-side duplicate-key
rejection (#166) and its engine-loader twin (#167). Each closed a
schema-vs-enforcement gap where a constraint the schema declared was not
re-enforced by the runtime loader. This slice is the same discipline
applied to the last unenforced numeric bound: `base_rate`'s ceiling. With
it, the "fail loud on a bad pack" story for value constraints is
complete — every schema-declared bound the loader can see is now
re-checked at load, both ends.
