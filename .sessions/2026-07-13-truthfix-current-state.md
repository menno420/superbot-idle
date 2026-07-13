# 2026-07-13 — truth-fix current-state + prune merged claim files

> **Status:** `in-progress`

- **📊 Model:** opus-4.8 · low · docs-only · truth-fix current-state counts + prune merged claims · 2026-07-13

## What happened

Housekeeping docs slice. Tonight's merges (PRs #75/#76/#78/#79/#80) moved the
ground truth out from under `docs/current-state.md`, which still read the
pre-merge world set by PR #75: **12** theme packs and a **1131** test suite,
plus present-tense "does NOT exist" claims that named the plugin adapter and a
playable entrypoint as absent. All three are now false.

Measured ground truth on `main` before writing (verify-first):

- `python3 tools/theme_gate.py themes` → `all 15 pack(s) valid (schema v1)`.
- `ls themes/*.yaml` → 15 packs (adds coffee-roastery, arctic-outpost,
  candy-factory from wave 4, PR #76).
- `python3 -m pytest -q` → **1260 passed, 1 skipped**.

Truth-fixed only present-tense numbers/claims in `docs/current-state.md`:
pack count 12 → 15 (with the three wave-4 packs added to the listed catalog
set), suite 1131 → 1260, groomed-date/SHA line refreshed to 2026-07-13 against
current main, and the stale "no plugin adapter / no entrypoint / unskinned
milestones" present-tense claims corrected to match reality (adapter now EXISTS
at `plugin/`, `tools/play.py` EXISTS, all packs carry flavored milestones).
Dated historical "Recently shipped" / "Roadmap" snapshot sections were left
untouched — only false present-tense claims were edited.

Then pruned the five merged claim files per the delete-at-close convention
(each verified `merged:true` via the GitHub API before deletion):
skin-pack-milestones (#79), playability-fixes (#80), catalog-wave-4 (#76),
plug-001-adapter (#75), plug-001-adapter-inc2 (#78). Left
`control/claims/README.md` (the convention doc, maps to no PR).

No economy number and no engine logic touched — file contents treated as data.

## 💡 Session idea

`docs/current-state.md` carries hand-maintained counts (pack count, test count)
that drift every merge and need a truth-fix slice like this one to re-sync — the
count for #75 was already stale within hours. A cheap durable guard: a
`tests/test_current_state_counts.py` that greps the two magic numbers out of the
doc and asserts `pack_count == len(glob("themes/*.yaml"))` and
`suite_count == <collected test count>` (via `pytest --collect-only -q | tail`),
so a drifted doc turns a required check red instead of waiting for a human to
notice. Keeps the living ledger honest without a groom session.

## ⟲ Previous-session review

Follows the five slices that merged tonight — most directly
2026-07-13-skin-pack-milestones.md (#79) and 2026-07-13-playability-fixes.md
(#80), whose own close-outs both flagged that they deferred the
`docs/current-state.md` count bump to avoid colliding with the then-open #75
("pack-count bump is deferred — owned by open PR #75"). #75 in turn only bumped
9→12 packs / 620→1131 tests and could not see #76's wave-4 packs. So every one
of tonight's slices correctly left the ledger for a follow-up rather than racing
it — this session is that follow-up, reconciling all five at once. Their shared
discipline (data-only, economy-neutral, engine untouched) holds here too: this
slice edits only prose and deletes closed bookkeeping.
