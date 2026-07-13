# substrate-kit upgrade report — v1.7.1 → v1.15.0

> Generated 2026-07-13 by `bootstrap.py upgrade`. Rollback: `python3 bootstrap.py upgrade --rollback`.

**Docs:** consumer-edited: 5 · diverged: 2 · template-improved: 6 · unchanged: 10

| planted doc | class | note |
|---|---|---|
| CONSTITUTION.md | template-improved | consumer-untouched + template improved — safe to apply with `upgrade --apply-docs` |
| docs/decisions.md | consumer-edited | template unchanged — consumer-owned, nothing to apply |
| docs/architecture.md | consumer-edited | template unchanged — consumer-owned, nothing to apply |
| docs/ownership.md | unchanged | template identical across versions |
| docs/runtime_contracts.md | unchanged | template identical across versions |
| docs/repo-navigation-map.md | consumer-edited | template unchanged — consumer-owned, nothing to apply |
| docs/helper-policy.md | unchanged | template identical across versions |
| docs/collaboration-model.md | template-improved | consumer-untouched + template improved — safe to apply with `upgrade --apply-docs` |
| docs/ai-project-workflow.md | unchanged | template identical across versions |
| docs/owner-profile.md | unchanged | template identical across versions |
| docs/AGENT_ORIENTATION.md | diverged | both the template and the doc moved — manual merge |
| docs/current-state.md | consumer-edited | template unchanged — consumer-owned, nothing to apply |
| docs/question-router.md | template-improved | consumer-untouched + template improved — safe to apply with `upgrade --apply-docs` |
| docs/CAPABILITIES.md | template-improved | consumer-untouched + template improved — safe to apply with `upgrade --apply-docs` |
| docs/SKILLS.md | unchanged | template identical across versions |
| docs/ROUTINES.md | unchanged | template identical across versions |
| docs/ideas/README.md | unchanged | template identical across versions |
| .session-journal.md | unchanged | template identical across versions |
| control/README.md | template-improved | consumer-untouched + template improved — safe to apply with `upgrade --apply-docs` |
| control/inbox.md | consumer-edited | template unchanged — consumer-owned, nothing to apply |
| control/status.md | diverged | both the template and the doc moved — manual merge |
| control/claims/README.md | template-improved | consumer-untouched + template improved — safe to apply with `upgrade --apply-docs` |
| scripts/env-setup.sh | unchanged | template identical across versions |

## ⚠️ Gate carve-outs (host additions the kit-owned regen could not keep)

- carve-out: .github/workflows/auto-merge-enabler.yml — host-added step 'Skip arming while the PR's own in-diff session card is in-progress' in job 'enable-auto-merge'
- carve-out: full pre-regen enabler banked at .substrate/backup/auto-merge-enabler.pre-regen-1a1e0ce0.yml — host additions were NOT carried into the regenerated kit-owned enabler; move them into a separate workflow file (e.g. .github/workflows/host-ci.yml) and commit that before shipping this upgrade/adopt PR. [carried from the previous upgrade report]

## Carve-out scan

- carve-out scan: .github/workflows/substrate-gate.yml — ran, 0 found
- carve-out scan: 2 carve-out line(s) reported above (see the ⚠️ section).

## Capability-ledger seed refresh

- capability-seed: docs/CAPABILITIES.md is consumer-untouched — the whole file (fence included) refreshes via `upgrade --apply-docs`; no fence-only refresh needed.

This upgrade ships the venue-scoped capability ledger (grounded-skills §4.2): entries carry a venue token (owner-live · autonomous-project · routine-fired · subagent · any) and the ledger's kit-owned seed block carries the posture decision rule. If this repo carries a local prose copy of the boot-triad/venue-posture rule (superbot Q-0270), that copy is now superseded by docs/CAPABILITIES.md's posture rule — collapse the local copy into a pointer.

## Seat-digest refresh

- seat-digest: regenerated docs/seat-digest.md (derived render — skills index + venue-filtered walls re-rendered from the current tree; venue filter preserved from the committed doc).

## Applied (--apply-docs)

- applied: CONSTITUTION.md (template@new, hash re-recorded)
- applied: docs/collaboration-model.md (template@new, hash re-recorded)
- applied: docs/question-router.md (template@new, hash re-recorded)
- applied: docs/CAPABILITIES.md (template@new, hash re-recorded)
- applied: control/README.md (template@new, hash re-recorded)
- applied: control/claims/README.md (template@new, hash re-recorded)

## Template deltas for diverged docs

### docs/AGENT_ORIENTATION.md

```diff
--- docs/AGENT_ORIENTATION.md (template@old, current slots)
+++ docs/AGENT_ORIENTATION.md (template@new, current slots)
@@ -7,11 +7,24 @@
 
 ## Start every session
 
-1. `.claude/CLAUDE.md` — the working agreement.
-2. `docs/current-state.md` — the living status ledger.
-3. `docs/CAPABILITIES.md` — verified session capabilities & walls (the
-   discovery rule lives there; append what you learn).
-4. This file — task-specific reading routes.
+**Preflight first — land on origin's HEAD before reading anything else:**
+
+```
+git fetch origin main && git reset --hard origin/main
+```
+
+(or `git checkout -B main origin/main`; substitute your default branch).
+Then verify: local HEAD (`git rev-parse HEAD`) must equal
+`git ls-remote origin main`. A warm container clone can lag origin by
+dozens of commits, and a stale clone reads stale orders and stale state —
+every orientation read below assumes this step already ran. The hard reset
+discards uncommitted local changes by design: at session START there should
+be none; if `git status` shows work you did not author, stop and report it
+instead of resetting over it.
+
+The boot set lives in the working agreement — `CONSTITUTION.md` — and its
+orientation guidance (one list, one home). This file is not boot reading —
+open it when a task needs a route into the deeper docs.
 
 ## Binding contracts
 
@@ -28,11 +41,20 @@
 `docs/collaboration-model.md` · `docs/helper-policy.md` ·
 `docs/repo-navigation-map.md` · `docs/ai-project-workflow.md` ·
 `docs/owner-profile.md` · `docs/current-state.md` · `docs/decisions.md` ·
-`docs/question-router.md` · `docs/CAPABILITIES.md` · `docs/ideas/README.md` — plus the root
+`docs/question-router.md` · `docs/CAPABILITIES.md` · `docs/SKILLS.md` ·
+`docs/ROUTINES.md` · `docs/ideas/README.md` — plus the root
 `CONSTITUTION.md` (the working agreement) and `.session-journal.md`.
+
+Recurring action? **`docs/SKILLS.md`** — the skill index — names every
+kit-shipped skill and when to reach for it; check it before improvising a
+procedure.
+
+Arming, deleting, or auditing a scheduled trigger/routine/wake chain?
+**`docs/ROUTINES.md`** — binding choice, delivery verification,
+probe-not-record, scheduler-health signatures, pacing — read it before
+touching the trigger registry.
 
 ## Verifying any change
 
-```
-python3 -m pytest -q && python3 bootstrap.py check --strict (theme packs additionally validate via the theme-gate step once ORDER 000 lands it in CI)
-```
+See the working agreement (`CONSTITUTION.md`) and its verify guidance
+(one home, never two copies).
```

### control/status.md

```diff
--- control/status.md (template@old, current slots)
+++ control/status.md (template@new, current slots)
@@ -13,3 +13,8 @@
 The `kit:` line is your kit self-report (substrate-coordinator visibility): keep the version in
 sync with your vendored kit on every upgrade, `check:` = your last `check --strict` verdict,
 `engaged:` = the post-adopt engagement gate (yes once `check` reports ENGAGED/green live CI).
+Keep the `kit:` token PLAIN — the bold-label form `- **kit:** v1.2.3 · check: green · engaged: yes`
+does NOT parse and the fleet registry reads it as no `kit:` line at all (grammar + the valid
+bold-label-before-plain-token shape: `control/README.md` § "status.md format"). And this line is
+a self-report, not version truth — self-reports chronically lag; the kit repo's generated
+`docs/adopters.md` and your committed tree are the version truth to defer to.
```

