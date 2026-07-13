# superbot-idle · status
updated: 2026-07-12T10:17Z
phase: RESUMED for ORDER 003 (pytest CI) — a P1 order landed in control/inbox.md (2026-07-12T08:30Z), waking the lane from ARCHIVED-READY; addressed by PR #74. Meanwhile the PLUG-001 docs-only un-park landed via PR #72 (upstream superbot-next plugin contract VERIFIED to EXIST — see PLUG-001 section below). Founding chat knowledge remains in durable homes (docs/retro/2026-07-11-lane-retro.md + docs/retro/2026-07-11-archive-ready.md, PR #70). Wake loop remains per ROUTINE RECORD below.
health: green
kit: v1.7.1 · check: green
boot: 2026-07-10 — idle-engine seat synced seed HEAD 28fac02, kit v1.7.1 verified via bootstrap.py --version, check --strict green, calibration posted
last-shipped: ORDER 003 — pytest CI workflow (PR #74); prior: PLUG-001 docs-only un-park (PR #72), close-out + archive prep (PR #70 + heartbeat PR #71)
blockers: SIM-001/Q-0264 and KIT-001 still open (⚑ blocks below). PLUG-001 CLEARED 2026-07-12 — contract found, un-parked (see PLUG-001 section below).
orders: acked=000-004 done=000-004 (003 done-when met: PR #74 MERGED 2026-07-12T19:40:02Z with the `pytest` check green + the ⚑ required-check ask filed as OA-003 below; 004 = NIGHT REPORT section at end of this file)

## ORDER 003 — pytest CI on PR + push (2026-07-12T08:30Z, P1)
- ADDRESSED by **PR #74** (`order-003-pytest-ci`): adds `.github/workflows/pytest.yml`, a new workflow that runs `python3 -m pytest -q` on every `pull_request` and `push` to `main`. Job/check name `pytest`, so it shows as its own check-run.
- Gap was real (verified at HEAD 45ff2bf, per inbox): `.github/workflows/` held only `substrate-gate.yml` + `theme-gate.yml`; grep for `pytest` in both returned nothing — no CI job executed the suite, so GREEN ≠ TESTED.
- Style mirrors `theme-gate.yml` (ubuntu-latest, `actions/checkout@v4`, `actions/setup-python@v5`, `python-version: "3.x"`, `pip install --quiet pytest pyyaml jsonschema`). Invocation is the repo's canonical one (README / CONVENTIONS.md / docs/architecture.md).
- Local verify before push: `python3 -m pytest -q` → 1131 passed in 12.26s; `bootstrap.py check --strict` (born-red advisory path) → all checks passed; `theme_gate.py themes` → 12 packs valid; workflow YAML parses.
- Check-run state on PR #74: substrate-gate ✓ success, theme-gate ✓ success, **pytest ✓ success** (the new job — the done-when). See OA-003 below for the remaining owner-only step.

## Self-review 2026-07-11 (ORDER 002)

MOVED at close-out → `docs/retro/2026-07-11-lane-retro.md` § 1 (verbatim, with the coordinator operations knowledge and in-chat owner rulings alongside it).

## SHIPPED RECORD
- ORDER 000 — DONE (PRs #1+#2): walking skeleton — idle_engine/ (state, tick, closed-form offline progress, theme loader), themes/egg-farm.yaml, theme-gate CI, core/skin guard test.
- slice (a) THEME SCHEMA v1 — DONE (PRs #4+#5): docs/theme-schema.md + machine schema, schema-driven theme-gate, Discord string budgets (256/1024/25) as red-gate limits.
- repo hygiene — DONE (PR #6): .gitignore.
- slice (b) upgrades + prestige — DONE (PRs #7+#8): test-first; provisional curves pre-registered in docs/design/upgrades-prestige-v0.md.
- slice (c) two more theme packs — DONE (PRs #10+#11): space-colony + potion-brewery; schema proven on foreign content with ZERO per-file schema changes; cross-pack id-collision gate added.
- slice (d) economy design — DONE (PRs #9+#12+#13): docs/design/economy-v1.md with pre-registered pacing targets T1–T10 + SIM-001 spec.
- slice (e) setup-code format v1 — DONE (PRs #15+#16): IDLE1- prefixed Crockford-base32 codes with CRC16; encode/decode/catalog-validate in idle_engine/provisioning.py; docs/provisioning.md as the websites-lane consumption contract with test-pinned literal example codes.
- render layer — DONE (PRs #18+#20): idle_engine/render.py pure embed-payload builder, status/shop/prestige views, hard budget enforcement, docs/render-layer.md.
- catalog growth — DONE (PRs #19+#21): haunted-manor, deep-sea-station, dragon-hoard; 6 packs total; theme.id↔filename-stem gate; zero schema pinches.
- setup-code cross-language test vectors — DONE (PRs #23+#25): tests/vectors/setup-codes.v1.json (90→92 vectors), generator + regenerate-or-red tests.
- leading-zero version-prefix fix — DONE (PRs #26+#28): grammar-compliant MalformedCodeError, red-first.
- themed-label slots — DONE (PRs #24+#27): schema labels block, gate placeholder semantics, render consumption with pinned neutral fallback, all 6 packs filled.
- property/invariant test suite + plugin-adapter scoping — DONE (PRs #30+#31): 128 seeded property tests — tick/offline exact equivalence, 6-pack determinism trajectories, conservation/monotonicity, render-budget fuzz at 10^3000 scale, 4000-corruption setup-code fuzz with 0 crc16 collisions; zero engine bugs found; docs/plugin-adapter-scoping.md evidence-gated.
- catalog growth wave 2 — DONE (PRs #33+#34): wizard-tower, royal-bakery, cyber-city; 9 packs total; zero schema pinches; setup-code vectors regenerated to 125 total.
- docs grooming — DONE (PRs #35+#37): current-state rewritten with groomed roadmap, architecture layers/invariants documented, decisions D-0002..D-0007 ledgered, stale ORDER-000-era claims fixed.
- shop composition — DONE (PRs #36+#38): themed upgrade descriptions composed into shop view, exact-cap arithmetic 768+1+139+116=1024, schema description cap tightened 1024→768 with zero shipped-pack impact, fallback pinned byte-identical.
- state serialization v1 — DONE (PRs #40+#41): idle_engine/persistence.py canonical versioned save/load, error taxonomy, empty-but-proven migration registry, docs/persistence.md contract, +109 tests incl. mid-playthrough trajectory identity across 9 packs.
- catalog growth wave 3 — DONE (PRs #43+#44): pirate-cove, ant-colony, idol-agency; 12 packs total; zero schema pinches; setup-code vectors regenerated 60/73/25.
- ORDER 001 (model attribution, Q-0262) — DONE (PRs #47 claim + #48 build): .sessions/README.md `📊 Model:` marker confirmed present and strengthened with the standing-rule instructions (family-level, harness-self-reported, never the Routines screen); fired card .sessions/2026-07-11-order-001-model-attribution.md carries `📊 Model: fable-5` from the session's own harness self-report (exact id claude-fable-5); legacy audit: all 18 prior cards already carry the line (all fable-5), none rewritten; 827 tests + check --strict green.
- SIM-001 executable harness — DONE (PRs #52+#54): tools/simulate.py deterministic runner of the pre-registered scenarios S1–S3 driving the REAL engine functions, docs/design/sim-harness.md, provisional results committed (docs/design/sim-results-2026-07-11-provisional.json); suite 827 → 838.
- achievements/milestones layer — DONE (PRs #53+#56): idle_engine milestones with engine-derived slots owned/lifetime/prestige ×3, pre-registered PROVISIONAL numbers in docs/design/achievements-v0.md, +5%/earn global bonus max +45%, milestones persist through prestige, save format v2 with first real v1→v2 migration, schema noun slots filled in 3 packs, budget-safe render_achievements view; test-first, suite 838 → 943.
- buy-max/bulk-purchase math — DONE (PRs #59+#60): exact per-level-floored bulk cost with pinned 403-vs-404 naive-closed-form divergence, bisected max_affordable fast at 10^3000 scale, atomic purchase_upgrades; +67 tests.
- bounded theme-multiplier mechanism — DONE (PRs #58+#61): schema-declared 90..110 bounds on per-generator rate_multiplier_pct, loader defense-in-depth, single-floor fold extended to //10^8 with byte-identical neutral behavior, catalog all-neutral values sim-gated per docs/design/theme-balance-v0.md — the founding "bounded multipliers" clause now exercised; +30 tests.
- append-only-ledger union hygiene — DONE (PRs #62+#63): root .gitattributes merge=union for guard-fires.jsonl + telemetry/model-usage.jsonl, union behavior demonstrated, ends the recurring rebase conflicts.
- golden save corpus — DONE (PRs #65+#66): tests/vectors/saves.v2.json with 45 vectors incl. byte-pinned v1→v2 migration goldens, generator + regenerate-or-red tests, same-PR extension policy in docs/persistence.md; suite 1040 → 1131, zero persistence bugs found.
- timed-events scoping — DONE (PRs #67+#68): docs/design/timed-events-scoping.md + plan badge; recommends piecewise-exact offline integration; all values deliberately unregistered pending SIM-002/Q-0264; no code built.
- close-out + archive prep — DONE (PR #70 + this PR #71): chat-only knowledge captured into docs/retro/ (lane retro + archive-ready snapshot), PLATFORM-LIMITS zero-check-runs wall added, wake loop disarmed, lane flipped ARCHIVED-READY.
- Suite: 24 → 1131 tests green. 69 lane PRs + these merged-on-green. No parked PRs, no denials.

## FOUNDING PACKAGE — done-when status
- core loop shipped+tested ✓
- theme schema + gate proven by 3 live packs ✓
- setup-code format versioned + websites-consumable ✓
- plugin-shaping — render layer + scoping doc shipped; PLUG-001 UN-PARKED 2026-07-12 (upstream contract VERIFIED at superbot-next docs/game-plugin-contract.md @ d3dba9b); the adapter itself is still unbuilt — next slice

## ROUTINE RECORD (Q-0265) — DISARMED at close-out 2026-07-11
- Cron trigger `trig_01TWKGFW8RUsMvxUMt2ndzqA` ("superbot-idle failsafe wake", cron "45 */2 * * *", persistent_session_id session_01BRmUrjckzMsewsXzpc3wwW) — DELETED via mcp__claude-code-remote delete_trigger as the session's final act (after this heartbeat pushed); pending send_later chain links likewise listed + deleted. Verbatim call outcomes in the archived session's final report; disarm state verifiable via list_triggers.
- RE-ARM SPEC for a resuming session (this is the recipe the founding session used): (1) failsafe cron — create_trigger with name "superbot-idle failsafe wake", cron_expression "45 */2 * * *", bound to the resuming coordinator session, prompt per Q-0265 (wake, read control/inbox.md + status.md, act or heartbeat); (2) pacemaker — a ~15-minute send_later chain where each firing re-arms the next link as its first act. Verify both via list_triggers before relying on them.

⚑ needs-owner:

**OA-001 — repo settings: Allow auto-merge + required check `substrate-gate` on `main` — RESOLVED-VERIFIED**
- Auto-merge armed successfully at creation and fired on green for PRs #1 and #2 — the VERIFIED-NEEDED criterion ("next PR shows Auto-merge enabled and lists `substrate-gate` as required") is met.

**OA-002 — repo settings: make `theme-gate` a required status check on `main` — RESOLVED-VERIFIED**
- Owner enabled theme-gate as a required check ~00:10Z; observed gating merges from PR #6 onward — auto-merge fires only after theme-gate concludes.

**OA-003 — ⚑ OWNER ASK: add `pytest` as a REQUIRED status check on `main` (owner-only) — OPEN**
- ORDER 003's done-when has two halves: (1) the pytest workflow green on a real PR — DONE (PR #74, the `pytest` check-run is green); (2) ⚑ the owner to mark it a required check — THIS ASK.
- REQUEST: in GitHub repo Settings → Branches → branch protection for `main`, add the status check named **`pytest`** to the required checks (alongside the existing `substrate-gate` + `theme-gate`). This is branch-protection config, which only the owner can change — a worker cannot self-mark a required check.
- WHY: until `pytest` is required, a PR can still merge green without the suite having passed (a run could be skipped/cancelled and merge would not be blocked). Making it required is what finally makes GREEN == TESTED for merges to `main`.
- VERIFIED-NEEDED: a subsequent PR shows `pytest` listed among the required checks and auto-merge holds until it concludes.
- DO NOT: this worker did NOT arm auto-merge and did NOT merge PR #74 — leaving the merge decision to the owner/coordinator per lane convention.

## PLATFORM-LIMITS
- Two transient GitHub rate-limit hits ("API rate limit already exceeded for user ID 225413533"): PR #26 arming → REST fallback; PR #27 arming → paced retry succeeded. Recorded per PLATFORM-LIMITS; workers now pace GitHub calls.
- PR #61 sat ~5 min with ZERO check runs (mergeable_state: unknown — GitHub never built the merge ref); rebase + --force-with-lease retriggered checks instantly. Recorded in PLATFORM-LIMITS.md (PR #70).

## PLUG-001 — RESOLVED / UN-PARKED 2026-07-12: superbot-next plugin contract FOUND (⚑ cleared)
- CONTRACT FOUND: superbot-next `docs/game-plugin-contract.md` @ `d3dba9b` (binding; owner decision 2026-07-09). A 2026-07-12 re-probe re-listed the superbot-next repo tree; the contract was published all along at a different path than the two the 2026-07-11 probe hypothesized.
- Probe nuance kept (old history not wrong): the two old URLs (docs/plugins.md, docs/plugin-contract.md) are STILL 404 today — only the guessed filenames were wrong, not the probe method. The standalone menno420/superbot-plugin-hello repo is STILL EMPTY; the working exemplar lives in-tree at superbot-next examples/superbot-plugin-hello/.
- Contract shape (host-side real, not just spec): entry point group `sb.plugins`, module exports MANIFEST/MANIFESTS, refs via @handler/@panel/@workflow/@provider + idempotent ENSURE_REFS; v1 facets commands/panels/settings(+bindings)/events/capabilities; host-owned (refused at gate) stores/data_invariants/wizard_sections; pin/hash lifecycle via tools/plugin_pin.py → host-PR pin diff → boot-time discovery+pin-verify+register, drift/unpinned ⇒ FAILED_STARTUP(plugin_gate). Host impl: sb/app/plugin_host.py, plugins.lock.json.
- Docs un-parked via PR #72 (READY, substrate-gate + theme-gate both green 2026-07-12T00:22Z): plugin-adapter-scoping.md dated re-probe section supersedes the UNVERIFIED verdict; current-state.md + persistence.md + AGENT_ORIENTATION.md flipped to VERIFIED.
- NEXT STEP: the adapter slice (a separate, non-docs slice) per docs/plugin-adapter-scoping.md § Re-probe 2026-07-12 — thin plugin/ shell exporting a SubsystemManifest over the four verified seams, pinned via tools/plugin_pin.py. No adapter code exists yet.
- ⚑ to manager: no longer a blocker-ask. Optional follow-up only — owner may create the standalone superbot-plugin-hello repo (still empty); exemplar is in-tree meanwhile.

## KIT-001 — ⚑ to manager: kit-level suggestion
- Plant merge=union gitattributes for append-only ledgers fleet-wide (host-side proof: PR #63; four slices had hand-resolved guard-fires conflicts before it).

## QUEUE — dormant (lane archived; resume triggers listed)
- RESUME TRIGGER: new ORDER in control/inbox.md (manager) — a fresh session reads README.md → this file → docs/retro/2026-07-11-archive-ready.md and re-arms the wake loop per ROUTINE RECORD.
- RESUME TRIGGER: Q-0264 ruling lands (A10 wording + multiplier values + achievements-inclusive sim + timed-events adoption) → unblocks economy tuning + timed-events build.
- RESUME TRIGGER: PLUG-001 unblocks (plugin contract published / exemplar seeded) → adapter slice per docs/plugin-adapter-scoping.md. — FIRED 2026-07-12: contract FOUND at superbot-next docs/game-plugin-contract.md @ d3dba9b; docs un-parked (PR #72). REMAINING resume: build the adapter slice (non-docs) when scheduled.
- RESUME TRIGGER: KIT-001 response (kit-level merge=union) — informational, no build.
- ON-DEMAND: catalog wave 4+ (theme packs merge on theme-gate green alone).
- DEFERRED: memoized rate table (needs bot runtime); setup-code v2 bound ruling.

notes: seeded 2026-07-10 by the dispatch copilot at the owner's direct instruction (live dispatch chat), on the fleet seeding recipe (fourth consumer: product-forge, sim-lab precedents). Egg farm = FIRST THEME, not the product — the contract is in README.md. The coordinator overwrites this file (never append) as every session's deliberate last step. ARCHIVED 2026-07-11: founding coordinator chat archived by owner order; durable homes for its knowledge are docs/retro/2026-07-11-lane-retro.md + docs/retro/2026-07-11-archive-ready.md.

## SIM-001 — ⚑ to manager (Q-0264): Simulator time requested for superbot-idle economy v1
- Executable request registered in `docs/design/economy-v1.md` § "Simulation request — SIM-001 (Q-0264)" (PR #12): scenarios S1–S3 (idle-only / check-in N ∈ {0.25, 2, 8, 24} h / optimal 1-s speedrun; 14-day horizon; 3+ resets) driving the REAL engine functions at the pinned commit — deterministic, integer-exact, stdlib-only.
- Outputs O1–O6 (time-to-first-upgrade, upgrade-purchase timelines, currency trajectories, time-to-prestige distribution, payback curve, 20-reset stacking) judged against pre-registered pacing targets T1–T10 via acceptance criteria A1–A10, all in the same doc.
- Every economy parameter stays PROVISIONAL (no tuning) until the Simulator's verdict; ALL-PASS graduates them sim-pinned, any FAIL gets re-registered in the doc before an engine change lands.
- PROVISIONAL RUN COMPLETE 2026-07-11 (unofficial, harness PR #54, results docs/design/sim-results-2026-07-11-provisional.json): A1–A9 PASS within bands; A10 FAILS the strict literal reading (consecutive prestige-duration ratios wiggle at integer-floor steps 0.9175→0.9080 at reset 3; trend rises toward 1, final 0.9661 — shrinkage not super-geometric). RULING NEEDED (Q-0264): does the pre-registered A10 wording mean the strict non-decreasing gate (FAIL stands → re-register before tuning) or the trend reading (PASS)? Auxiliary signal for the ruling: optimal play reaches ~80,796 resets in 14 days (late resets ~13 s each) — uncovered by any criterion, likely wants a pre-registered cap/cooldown criterion in v2 of the doc. Spec ambiguities AMB-1..11 recorded in the harness doc. Parameters remain PROVISIONAL; no tuning done.
- INTERACTION NOTE (PR #56): achievements shift pacing +5..45% for earning players; tools/simulate.py currently models a zero-achievements player — the Q-0264 ruling/next sim round should pin achievements-inclusive scenarios (recorded in achievements-v0.md § What the Simulator must pin).

## NIGHT REPORT 2026-07-13T09:25Z (ORDER 004 — owner ask 2026-07-13, fm relay)

> This file is a frozen archive (overwrite-at-close convention); this section is
> appended ONLY under the explicit at-HEAD ORDER 004 (control/inbox.md, landed via
> PR #83, MERGED 2026-07-13T09:10:44Z — API-verified before writing). Window:
> 2026-07-12T22:30Z → 2026-07-13T09:25Z.

### SHIPPED (merges API-verified; squash SHA on main · merged_at UTC)
- #77 ci: auto-merge-enabler install (fm ORDER 029) — 457407c · 00:03:09Z
- #79 feat(themes): flavored milestones for the 9 unskinned packs — 7af705c · 01:03:48Z
- #80 playability: ready-glyph milestones + trap-buy guard + tools/play.py REPL — 4af4338 · 01:12:29Z
- #76 catalog wave 4: coffee-roastery, arctic-outpost, candy-factory (12→15 packs) — ac0af23 · 01:23:35Z
- #75 PLUG-001 adapter inc1: thin plugin/ exporting a SubsystemManifest — 86f631d · 01:26:30Z
- #78 PLUG-001 adapter inc2: settings + events + live render forwarding — 497db5a · 01:34:21Z
- #81 docs truth-fix: 12→15 packs, 1131→1260 tests + claim prune — c925a45 · 01:44:12Z
- #82 outbox: SIM-001 follow-up + 2 owner Q-blocks — c735075 · 01:50:23Z
- #83 control: ORDER 004 landing (manager-written) — 161bc7d · 09:10:44Z
- Suite → **1260 passed, 1 skipped** — VERIFIED locally at HEAD 161bc7d (`python3 -m pytest -q`); 15 theme packs.

### OPEN PRs + check states
- None — zero open PRs (API-verified 2026-07-13T09:15Z).

### ORDERS served + outstanding
- 001–002 done pre-window; 003 done (PR #74 merged 2026-07-12T19:40:02Z pre-window, pytest check green; ⚑ required-check ask = OA-003, still awaiting the owner click); 004 = this report. Outstanding: none.

### SIM-REQUESTs / asks pending
- SIM-001 economy-FEEL cluster (control/outbox.md 2026-07-13, ref Q-0264): first-upgrade no-op, weak prestige payoff, and the A10 ruling — harness at HEAD is A1–A9 PASS / **A10 FAIL** under the strict reading (20-reset final_ratio ≈ 0.9661, trend rising toward 1) + graduation decision.
- 2 owner Q-blocks awaiting fleet Q-numbers (control/outbox.md): generator-purchase economy (P1) · content-depth/endgame (P2).
- OA-003 (above): owner to mark `pytest` a required check on main.

### STALLS / denials (verbatim)
- None this window in this repo.

### Wake-chain health (SEAT-LEVEL — one chain serves games/idle/mineverse; the order asks per-repo, the chain is per-seat; this repo's own founding trigger stays DISARMED per ROUTINE RECORD above)
- Failsafe cron `trig_0131tbQZs8HKmxKR4u5ZD1Hb` "SuperBot World failsafe wake", cron `15 1-23/2 * * *` — API-verified live 2026-07-13T09:16Z: enabled, last fired 09:15:25Z, next 11:15:00Z. Overnight fires 01:15/03:15/05:15/07:15 on schedule (lane-reported; API exposes only the last fire).
- send_later pacemaker chain continuous; current tick `trig_01K5pWUeY1YEM6taMeWmHvG8` fires 09:19Z (API-verified live).
- One duplicate-tick incident ~02:35Z detected and pruned the same wake; anti-stack check added since (lane-reported).

### Next-3
1. Host-side `plugins.lock.json` pin for the idle adapter (a superbot-next PR, via that lane).
2. Act on the Q-0264 / A10 ruling when it lands (graduate or re-register the PROVISIONAL table).
3. Catalog wave 5 on demand (data-only packs merge on theme-gate green alone).
