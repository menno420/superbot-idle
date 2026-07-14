# 2026-07-14 — substrate-kit upgrade v1.15.0 → v1.16.0

> **Status:** `in-progress`
> **Branch:** `claude/kit-upgrade-v1.16.0`

- **📊 Model:** fable-5 · medium · task-class: mechanical refactor — kit-upgrade distribution wave, vendored substrate-kit v1.15.0 → v1.16.0 (kit-owned files only) · session opened 2026-07-14T17:33Z (`date -u`)

**Goal:** distribution-wave upgrade of the vendored substrate-kit from
v1.15.0 to v1.16.0 via the canonical two-command flow
(`python3 bootstrap.py.new upgrade` → `python3 bootstrap.py upgrade
--apply-docs`), following the wave precedent (games #141, mineverse #110).
Kit-owned files only — no lane content, no `control/status.md` edits
(heartbeat `kit:` bump stays lane-owed per Q-0261.3). Known carve-out to
re-apply: idle's live `.github/workflows/auto-merge-enabler.yml` carries
the host-added in-diff-card guard step (PR #77 + #90 lineage, sha256
`1a0c5ec3537eb3db43036a4127d86537a50ab012f756f052c5cf7469c21ade18`) that
the kit regeneration strips — restore byte-identical after regen, exactly
as the v1.15.0 session (`.sessions/2026-07-13-idle-kit-v1150.md`) had to.

## What happened

(in progress — close-out written at the flip commit)

## 💡 Session idea

(filled at close-out flip)

## ⟲ Previous-session review

(filled at close-out flip)
