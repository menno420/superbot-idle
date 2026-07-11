# Platform limits — verbatim walls, do NOT re-probe

> **Status:** `living` (seeded 2026-07-10 from fleet-verified walls)

- **Direct push to main post-seed**: rejected by repository rules — always PR.
- **Auto-merge arming can fail BOTH ways on fast CI**: at creation "unstable
  status", on green "already in clean status" → REST merge on green is the path.
- **Agent self-merge can be classifier-denied** (Merge Without Review class):
  one attempt, record verbatim, park READY+green + ⚑, continue.
- **403 on tag pushes / release creation / branch deletion** — queue for the
  owner, never retry.
- **Toolsets are seat-dependent within one Project**: a coordinator may lack
  scheduler tools (`create_trigger`/`send_later`) while its spawned worker has
  them — retry walled calls from a worker BEFORE flagging owner-manual.
- **Completed routine runs are not inspectable owner-side** — the status
  heartbeat is the only readable record; trust git over any panel.
- **Shared token rate limits** fleet-wide: on "rate limit exceeded", record
  verbatim, back off.
- **PR can stall with ZERO check runs** (`mergeable_state: unknown` — GitHub
  never built the merge ref, so no workflow dispatches; observed ~5 min on
  PR #61): a `git rebase` + `push --force-with-lease` retriggers checks
  instantly. Rebase, don't wait.
