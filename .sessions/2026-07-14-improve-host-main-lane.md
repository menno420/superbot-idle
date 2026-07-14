# 2026-07-14 — improve: scheduled advisory host-main CI lane (drift check vs superbot-next main)

> **Status:** `in-progress`

- **📊 Model:** fable-5 · medium · CI-config — scheduled advisory host-main lane · 2026-07-14T02:31Z– (`date -u`)

## What happened

Improvement-wave slice K (owner improvement-wave directive, 2026-07-14) —
add a cron workflow that runs the `pytest-with-host` job's steps against
UNPINNED superbot-next `main`, advisory-only (no PR/push triggers, never
gates merges), so pin drift is detected early instead of only when
someone bumps the pin. Requested by three cards:
`.sessions/2026-07-13-eap-ci-skip-hole.md` (💡 lines 63-73),
`.sessions/2026-07-13-idle-capability-3part-fix.md` (💡 lines 58-65),
`.sessions/2026-07-13-idle-liveboot-fixes.md` (💡 lines 83-90).

(in progress — filled in at flip)
