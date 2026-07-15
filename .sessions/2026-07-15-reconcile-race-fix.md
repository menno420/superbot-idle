# 2026-07-15 — fix reconcile race: tolerate auto-merge landing before the provenance stamp

> **Status:** `in-progress`
> **Branch:** `claude/reconcile-race-fix` · claim `control/claims/claude-reconcile-race-fix.md`

- **📊 Model:** fable-5 · medium · workflow fix — tolerate the auto-merge-lands-first window in the card-guard's Head-ref provenance branch · session opened 2026-07-15T21:41Z (`date -u`)

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

(close-out pending)
