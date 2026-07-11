# superbot-idle · status
updated: 2026-07-10T23:59:16Z
phase: BOOT COMPLETE — ORDER 000 shipped; THEME SCHEMA v1 in progress (founding package: superbot docs/planning/round3-founding-package-games-idle-2026-07-10.md)
health: green
kit: v1.7.1 · check: green
boot: 2026-07-10 — idle-engine seat synced seed HEAD 28fac02, kit v1.7.1 verified via bootstrap.py --version, check --strict green, calibration posted
last-shipped: ORDER 000 walking skeleton (PR #2 → main 7d04c1b)
blockers: none
orders: acked=000 done=000

## ORDER 000 RECORD
- PR #1 (control claim, head 18306ec) auto-merged 23:45:30Z → main 26cbe8a
- PR #2 (walking skeleton, head 0fb5d23) auto-merged 23:51:38Z → main 7d04c1b
- deliverables: idle_engine/ (state, tick, closed-form offline progress, theme loader), themes/egg-farm.yaml, tools/theme_gate.py + .github/workflows/theme-gate.yml, 24 pytest passing, core/skin guard test
- no parked PRs, no denials

## ROUTINE RECORD (Q-0265)
- cron trigger created via mcp__claude-code-remote__create_trigger — id `trig_01TWKGFW8RUsMvxUMt2ndzqA`, name "superbot-idle failsafe wake", cron_expression "45 */2 * * *", enabled true, next_run_at 2026-07-11T00:45:00Z, persistent_session_id session_01BRmUrjckzMsewsXzpc3wwW, prompt as specified by Q-0265 — VERIFIED via list_triggers.
- first send_later chain link: id `trig_01R4DAUXyS6BfZoqJ9raEMxv`, fire_at 2026-07-11T00:01:00Z, same session, message "continue the work loop (superbot-idle): sync HEAD -> inbox -> slice after slice, each merged-on-green; re-arm the chain (~15 min) before ending" — VERIFIED via list_triggers.
- Both ARMED-AND-VERIFIED.

⚑ needs-owner:

**OA-001 — repo settings: Allow auto-merge + required check `substrate-gate` on `main` — RESOLVED-VERIFIED**
- Auto-merge armed successfully at creation and fired on green for PRs #1 and #2 — the VERIFIED-NEEDED criterion ("next PR shows Auto-merge enabled and lists `substrate-gate` as required") is met.

**OA-002 — repo settings: make `theme-gate` a required status check on `main` (advisory until then)**
- WHAT: `theme-gate` completed green ~4s AFTER auto-merge fired on PR #2 — only `substrate-gate` is a required check, so theme-gate does not block merges.
- WHERE: github.com/menno420/superbot-idle → Settings → Branches → required status checks → add `theme-gate`.
- HOW: one click.
- WHY-IT-MATTERS: if theme packs must never merge ungated, theme-gate has to be merge-blocking; until then it is advisory-fast but not merge-blocking.

## QUEUE
- (a) THEME SCHEMA v1 — IN PROGRESS (docs/theme-schema.md + machine schema + hardened theme-gate + Discord string budgets 256/1024/25 as red-gate limits)
- (b) upgrades + prestige, test-first
- (c) two more theme packs (space colony, potion brewery) to stress the schema
- (d) economy design doc with pre-registered pacing targets + ⚑ sim request to manager (Q-0264)
- (e) setup-code provisioning format v1 (docs/provisioning.md + encoder/validator)
- between slices: grow catalog, deepen tests, groom roadmap

notes: seeded 2026-07-10 by the dispatch copilot at the owner's direct instruction (live dispatch chat), on the fleet seeding recipe (fourth consumer: product-forge, sim-lab precedents). Egg farm = FIRST THEME, not the product — the contract is in README.md. The coordinator overwrites this file (never append) as every session's deliberate last step.

## SIM-001 — ⚑ to manager (Q-0264): Simulator time requested for superbot-idle economy v1
- Executable request registered in `docs/design/economy-v1.md` § "Simulation request — SIM-001 (Q-0264)" (PR #12): scenarios S1–S3 (idle-only / check-in N ∈ {0.25, 2, 8, 24} h / optimal 1-s speedrun; 14-day horizon; 3+ resets) driving the REAL engine functions at the pinned commit — deterministic, integer-exact, stdlib-only.
- Outputs O1–O6 (time-to-first-upgrade, upgrade-purchase timelines, currency trajectories, time-to-prestige distribution, payback curve, 20-reset stacking) judged against pre-registered pacing targets T1–T10 via acceptance criteria A1–A10, all in the same doc.
- Every economy parameter stays PROVISIONAL (no tuning) until the Simulator's verdict; ALL-PASS graduates them sim-pinned, any FAIL gets re-registered in the doc before an engine change lands.
