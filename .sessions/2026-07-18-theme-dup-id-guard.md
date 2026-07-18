# 2026-07-18 — theme loader: reject duplicate currency/generator ids

> **Status:** `complete`

- **📊 Model:** neutral builder-agent · medium · runtime bugfix · engine-robustness seat (theme-loader dup-id guard) · 2026-07-18T00:51Z (`date -u`)

## What / why

`idle_engine.load_theme` guards every collection it parses against a
duplicate id — EXCEPT the two most fundamental ones. The `balance`,
`upgrades`, and `milestones` blocks each raise a loud `ValueError`
("duplicate ... id") when two entries share an id, but the `currencies`
and `generators` loops build their dict with a plain
`currencies[cid] = ...` / `generators[gid] = ...`, so a second entry
under the same id SILENTLY overwrites the first — authoring-error data
loss the loader is otherwise designed to catch.

The wrong behavior is provable and worse than a shape nit: a pack that
declares two generators under id `g1` — the first producing `gold`, the
second `gem` — loads clean, and the surviving generator silently
`produces` a DIFFERENT currency than the author's first declaration
named. Same for two currencies sharing an id: the earlier name/emoji
vanish with no error. Every other loader collection treats this as a
hard reject; these two didn't.

Fix is minimal and matches the existing pattern exactly: a
seen-id check in each loop that raises
`"{where}: duplicate currency id {cid!r}"` /
`"{where}: duplicate generator id {gid!r}"` before the assignment,
mirroring the `upgrades`/`milestones` guards. No mechanics, render,
schema, or catalog surface changes — a rejected pack was already
invalid data; this just fails it loud instead of silently mangling it.

## Verification

- Two new regression tests in `tests/test_theme_loader_guards.py`
  (`test_rejects_duplicate_currency_id`,
  `test_rejects_duplicate_generator_id`) — each RED on pre-fix main
  (loader accepts the dup silently), GREEN after the guard.
- `python3 -m pytest -q` — full suite green; count 1561 → 1563.
- `python3 bootstrap.py check --strict` — only the born-red HOLD
  expected (this card, until flipped `complete`).

## Landing (born-red convention)

Card born RED (`in-progress`) in the first commit with
`control/claims/claude-theme-dup-id-guard.md`; then the fix + tests
commit; card flipped `complete` as the last commit to clear the HOLD so
substrate-gate goes green and the landing workflow merges on all-green.
PR opened DRAFT then READY; the worker does not merge its own PR.

## 💡 Session idea

The loader's structural pass is a natural place for a single
"reject-duplicate-id" helper (`_unique_ids(entries, kind)`) so a NEW
collection added later inherits the guard by construction instead of
re-deriving it — the very omission this slice fixes shows the per-loop
copy-paste can silently skip one. A tiny refactor, deferred here to keep
the bug fix minimal and reviewable; noted as a follow-up rather than
scope-creeping the fix.

## ⟲ Previous-session review

Recent slices leaned docs (suite-count reconcile #162) and theme content
(forge pack #161, apiary). The engine/render robustness lane — where
`time_to_afford` (ENG-8) and the prestige preview last landed real
mechanics coverage — is the higher-value seam when a provable bug is in
hand, and this is one: a silent-data-loss asymmetry in the loader that
the existing `test_theme_loader_guards.py` corpus proves was left
uncovered for exactly the two collections that matter most. Fixing it
keeps the loader's "fail loud on bad packs" contract honest end to end.
