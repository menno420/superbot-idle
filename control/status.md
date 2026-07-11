# superbot-idle · status
updated: 2026-07-11T00:46:16Z
phase: SLICES (a)–(d) SHIPPED — setup-code format v1 (slice e) next (founding package: superbot docs/planning/round3-founding-package-games-idle-2026-07-10.md)
health: green
kit: v1.7.1 · check: green
boot: 2026-07-10 — idle-engine seat synced seed HEAD 28fac02, kit v1.7.1 verified via bootstrap.py --version, check --strict green, calibration posted
last-shipped: slice (d) economy design v1 + SIM-001 flag (PRs #12+#13 → main b018a28)
blockers: none
orders: acked=000 done=000

## SHIPPED RECORD
- ORDER 000 — DONE (PRs #1+#2): walking skeleton — idle_engine/ (state, tick, closed-form offline progress, theme loader), themes/egg-farm.yaml, theme-gate CI, core/skin guard test.
- slice (a) THEME SCHEMA v1 — DONE (PRs #4+#5): docs/theme-schema.md + machine schema, schema-driven theme-gate, Discord string budgets (256/1024/25) as red-gate limits.
- repo hygiene — DONE (PR #6): .gitignore.
- slice (b) upgrades + prestige — DONE (PRs #7+#8): test-first; provisional curves pre-registered in docs/design/upgrades-prestige-v0.md.
- slice (c) two more theme packs — DONE (PRs #10+#11): space-colony + potion-brewery; schema proven on foreign content with ZERO per-file schema changes; cross-pack id-collision gate added.
- slice (d) economy design — DONE (PRs #9+#12+#13): docs/design/economy-v1.md with pre-registered pacing targets T1–T10 + SIM-001 spec.
- Suite: 24 → 96 tests, all green on main. No parked PRs, no denials.

## ROUTINE RECORD (Q-0265)
- cron trigger created via mcp__claude-code-remote__create_trigger — id `trig_01TWKGFW8RUsMvxUMt2ndzqA`, name "superbot-idle failsafe wake", cron_expression "45 */2 * * *", enabled true, persistent_session_id session_01BRmUrjckzMsewsXzpc3wwW, prompt as specified by Q-0265 — VERIFIED via list_triggers.
- send_later chain links have fired + re-armed on schedule; latest re-arm fires 00:51Z.
- Both ARMED-AND-VERIFIED.

⚑ needs-owner:

**OA-001 — repo settings: Allow auto-merge + required check `substrate-gate` on `main` — RESOLVED-VERIFIED**
- Auto-merge armed successfully at creation and fired on green for PRs #1 and #2 — the VERIFIED-NEEDED criterion ("next PR shows Auto-merge enabled and lists `substrate-gate` as required") is met.

**OA-002 — repo settings: make `theme-gate` a required status check on `main` — RESOLVED-VERIFIED**
- Owner enabled theme-gate as a required check ~00:10Z; observed gating merges from PR #6 onward — auto-merge fires only after theme-gate concludes.

## QUEUE
- (e) setup-code provisioning format v1 (docs/provisioning.md + encoder/validator) — IN PROGRESS
- catalog growth: more theme packs
- runtime/bot-integration slice: Discord render layer; memoized rate table idea
- theme.id ↔ filename convention check
- offline-return flavor slot (needs render consumer)
- SIM-001 awaiting manager relay (Q-0264)
- between slices: grow catalog, deepen tests, groom roadmap

notes: seeded 2026-07-10 by the dispatch copilot at the owner's direct instruction (live dispatch chat), on the fleet seeding recipe (fourth consumer: product-forge, sim-lab precedents). Egg farm = FIRST THEME, not the product — the contract is in README.md. The coordinator overwrites this file (never append) as every session's deliberate last step.

## SIM-001 — ⚑ to manager (Q-0264): Simulator time requested for superbot-idle economy v1
- Executable request registered in `docs/design/economy-v1.md` § "Simulation request — SIM-001 (Q-0264)" (PR #12): scenarios S1–S3 (idle-only / check-in N ∈ {0.25, 2, 8, 24} h / optimal 1-s speedrun; 14-day horizon; 3+ resets) driving the REAL engine functions at the pinned commit — deterministic, integer-exact, stdlib-only.
- Outputs O1–O6 (time-to-first-upgrade, upgrade-purchase timelines, currency trajectories, time-to-prestige distribution, payback curve, 20-reset stacking) judged against pre-registered pacing targets T1–T10 via acceptance criteria A1–A10, all in the same doc.
- Every economy parameter stays PROVISIONAL (no tuning) until the Simulator's verdict; ALL-PASS graduates them sim-pinned, any FAIL gets re-registered in the doc before an engine change lands.
