# 2026-07-15 — fix reconcile race: tolerate auto-merge landing before the provenance stamp

> **Status:** `in-progress`
> **Branch:** `claude/reconcile-race-fix` · claim `control/claims/claude-reconcile-race-fix.md`

- **📊 Model:** fable-5 · medium · runtime bugfix — tolerate the auto-merge-lands-first window in the card-guard's Head-ref provenance branch · session opened 2026-07-15T21:41Z (`date -u`)

**Goal:** the post-#141 `reconcile` run failed on main (run 29451632916,
job 87475235876): auto-merge landed PR #141 in the ~2 s window between
the script's merged-check and the provenance branch's first
`gh pr merge --disable-auto` call, which runs with the `gh()` helper's
`fatal=True` default and exited 1 on
`GraphQL: Can't disable auto-merge for this pull request.` — the first
failure in the workflow's 7 runs. That contradicts the workflow's own
stated policy ("provenance is a survey aid, not a gate"): nothing was
mis-armed, the PR simply merged first. Make that one disarm call
tolerant (re-check merged state, notice/warning, exit 0) while leaving
the card-disarm branch's fail-loud behavior untouched.

## What happened

Verified the diagnosis element by element before editing: job
87475235876's log shows `armed=True hold_cards=none`, then `stamping
squash-body provenance: Head-ref: claude/truth-refresh`, then
`GraphQL: Can't disable auto-merge for this pull request.
(disablePullRequestAutoMerge)` and `exit code 1`; the workflow-run list
for `automerge-card-guard.yml` confirms 7 runs total, this the only
failure. In the script, the merged-check reads the PR once, and the
provenance branch's FIRST call — `gh("pr", "merge", "--disable-auto",
...)` — was the only call in that branch still riding the `fatal=True`
default (both re-arm calls were already `fatal=False`). Classic TOCTOU:
state read at T0, acted on at T0+2s, auto-merge landed in between.

The fix (one call, nothing else): that disarm call becomes
`fatal=False`; on nonzero returncode the script re-fetches the PR and
branches — merged → `::notice::` (auto-merge fired before the
provenance stamp; PR merged without Head-ref) → `sys.exit(0)`; not
merged → `::warning::` (arm left standing; the stamp can ride a later
`synchronize`) → `sys.exit(0)`. The `gh()` helper's `fatal=True`
default and the card-disarm branch's fail-loud disarm are untouched —
that loud path is load-bearing (an in-progress-card PR must never be
left silently armed). YAML re-parses clean and the embedded Python
still `ast.parse`s.

## Verify at flip

- `python3 -m pytest -q` → `1381 passed, 1 skipped`
- `python3 tools/theme_gate.py themes` → all 18 packs valid (schema v1)
- `python3 bootstrap.py check --strict` → red ONLY on this card's
  designed born-red hold; the 5 `model-line-class` advisories on older
  cards are pre-existing, untouched scope
- `python3 -c "import yaml; yaml.safe_load(open('.github/workflows/automerge-card-guard.yml'))"`
  → parses

## 💡 Session idea

superbot-games and superbot-mineverse carry the same host-owned
card-guard workflow pattern (this repo's copy was split out per the
#137 card; games' hardened guard @ `d6a9526` is the named upstream), so
their provenance branches carry the same fatal-disarm TOCTOU. No
existing card here claims the mirror: port this exact fix to both
repos. Guard recipe: in each repo's
`.github/workflows/automerge-card-guard.yml` (or the enabler-embedded
equivalent), find the provenance branch's first
`gh("pr", "merge", "--disable-auto", ...)` still on the `fatal=True`
default, apply the same `fatal=False` + merged-state re-check + exit 0;
test target: the workflow-run list stops showing failures whose last
log line is `GraphQL: Can't disable auto-merge for this pull request.`
after a PR auto-merges mid-run.

## ⟲ Previous-session review

previous-session review: `.sessions/2026-07-15-truth-refresh.md`
(PR #141) — its verify block reproduced exactly here (`1381 passed, 1
skipped`; 18 packs; strict-check red only on the born-red hold), and
its close-out was itself the trigger for this session: #141's own
auto-merge out-raced the reconcile run's provenance stamp, producing
the failure this fix tolerates — the card did nothing wrong; it hit a
workflow bug. One drift note: that card recorded 6 pre-existing
`model-line-class` advisories; this session's checker reports 5, and
`git log` shows NO older-card edits landed in between — one of the two
tallies mis-counted, so treat verify-block advisory counts as
observations, not pins. Its
💡 (a `tests/test_doc_kit_version.py` truth-guard) remains unclaimed
and worth a future slice.
