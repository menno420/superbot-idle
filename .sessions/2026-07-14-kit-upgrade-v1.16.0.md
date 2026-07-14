# 2026-07-14 — substrate-kit upgrade v1.15.0 → v1.16.0

> **Status:** `complete`
> **Branch:** `claude/kit-upgrade-v1.16.0` · PR #134 · claim PR #133 (merged 17:33Z)

- **📊 Model:** fable-5 · medium · task-class: mechanical refactor — kit-upgrade distribution wave, vendored substrate-kit v1.15.0 → v1.16.0 (kit-owned files only) · session opened 2026-07-14T17:33Z (`date -u`)

**Goal:** distribution-wave upgrade of the vendored substrate-kit from
v1.15.0 to v1.16.0 via the canonical two-command flow
(`python3 bootstrap.py.new upgrade` → `python3 bootstrap.py upgrade
--apply-docs`), following the wave precedent (games #141, mineverse #110).
Kit-owned files only — no lane content, no `control/status.md` edits
(heartbeat `kit:` bump stays lane-owed per Q-0261.3).

## What happened

- **Vendored dist:** `bootstrap.py` replaced with the v1.16.0 release dist,
  sha256 `bba34e2102cbaf09394f39992f0501ea5cfd542d90301ef67e31a0854ca59170`
  (980,026 bytes), three-way verified: fetched games
  `claude/kit-upgrade-v1.16.0` copy == mineverse main `419d559` copy
  (byte-identical by `cmp`) == the wave's release fact. Outgoing v1.15.0
  dist banked at `.substrate/backup/bootstrap-1.15.0.py`.
- **Two-command flow, both exit 0.** `--apply-docs` applied:
  CONSTITUTION.md, docs/collaboration-model.md, docs/CAPABILITIES.md,
  docs/SKILLS.md, docs/ROUTINES.md, control/claims/README.md. Config delta
  minimal: `kit_version` 1.16.0 + kit-default `preflight_scripts`;
  `automerge.required_context` (`substrate-gate`) and `branch_patterns`
  untouched. Three new kit skills planted (chase-references,
  prep-owner-steps, rationalize).
- **Carve-out restored (the #77/#90 host card-guard):** the regen banked
  the live enabler at
  `.substrate/backup/auto-merge-enabler.pre-regen-1a0c5ec3.yml` and
  overwrote live with the bare template — exactly what the v1.15.0 session
  predicted. Restored byte-identical: pre-regen `1a0c5ec3…ade18` →
  post-regen (stripped template) `64f9db41…c64c84` → post-restore
  `1a0c5ec3…ade18`. All five live workflows byte-identical to pre-upgrade
  (substrate-gate `bf644599…`, theme-gate `ed1a594c…`, pytest `cee149c3…`,
  host-main-advisory `1289cf99…`, enabler `1a0c5ec3…`) — the PR touches
  nothing under `.github/workflows/`; required contexts untouched.
- **New plant `docs/reading-path.md`** landed with the 3-slot
  `[unrendered-banner]` strict-red. Slots answered
  (`fleet_status_command` / `fleet_dark_repos` / `fleet_siblings`) with the
  mineverse #110 fleet facts adapted to idle (hub
  `python3.10 scripts/fleet_status.py` orient; pokemon-mod-lab the only
  dark repo; roster with superbot-idle as "this repo"), then
  `bootstrap.py render --live` → 0 unfilled placeholders. Reversible via
  `bootstrap.py answer <slot> …` + `render --live`. The report's minimal
  `docs/AGENT_ORIENTATION.md` wiring hunk (read-path list line +
  fleet-reading paragraph) hand-merged; rest of that diverged doc
  untouched.
- **Verify:** `check --strict` exit 1 with exactly one exit-affecting
  finding — the `[session-card-hold]` born-red HOLD naming this card
  (proves the added-card lane survives v1.16.0); `python3 -m pytest -q` →
  1381 passed, 1 skipped (baseline-identical); theme-gate as CI runs it
  (`python3 tools/theme_gate.py themes`) → all 18 packs valid. CI on
  pre-flip head `071a935`: substrate-gate red with only the designed hold
  (run 29354866674 notice: "Designed hold — not a CI failure to
  investigate"), theme-gate/pytest/pytest-with-host green, enabler ran and
  correctly did NOT arm (the restored host guard held it).
- **Landing:** claim PR #133 (control fast lane, merged by the resident
  enabler 17:33:25Z) → born-red card first commit `7c81b46` → payload
  `071a935` → PR #134 opened ready → this flip commit last. The resident
  live auto-merge-enabler merging on green after the flip is the sanctioned
  landing path — recorded, never armed by hand. Claim file deletion follows
  as a control-only PR per the claims README.

## Lane-owed (untouched per Q-0261.3)

- `control/status.md` heartbeat `kit:` bump to v1.16.0 on the next
  overwrite.

## 💡 Session idea

v1.16.0 seeds `preflight_scripts: ["scripts/preflight.py"]` into
`substrate.config.json` by default, and now BOTH the local ritual and the
CI gate print `NOTE — preflight script scripts/preflight.py not found —
skipped` on every run. Plant `scripts/preflight.py` running this repo's
real verify line (`python3 -m pytest -q` + `python3 tools/theme_gate.py
themes`) so the local check and the CI gate converge on one check list and
the NOTE stops shipping noise. Guard recipe: config key
`preflight_scripts` in `substrate.config.json`; target file
`scripts/preflight.py`; verify: the NOTE disappears from
`python3 bootstrap.py check --strict` output and the substrate-gate log.

## ⟲ Previous-session review

Reviewed `.sessions/2026-07-14-eap-closeout.md` (PR #132): its
claim-on-main-then-serve trail (claim PR #131 squash-cited → work PR #132
with per-ORDER PR citations) was directly reusable as this session's
landing shape and needed zero adaptation; the one wave-day gap is that its
ORDER 008 re-derived `kit:` stamp (v1.15.0, correct at 11:29Z) went stale
six hours later when this upgrade landed — evidence for keeping heartbeat
kit lines derived-on-overwrite rather than treated as durable facts.
