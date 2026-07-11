# superbot-idle · status
updated: 2026-07-11T04:23:53Z
phase: STEADY-STATE HOLD — founding package complete, volume backlog cleared honestly (44 PRs, zero denials, zero parked); lane deliberately holds new engine surface pending PLUG-001 (plugin contract upstream), SIM-001 (Simulator verdict), or new inbox ORDERs; chain (15-min) + failsafe cron continue monitoring inbox; catalog can grow on demand (founding package: superbot docs/planning/round3-founding-package-games-idle-2026-07-10.md)
health: green
kit: v1.7.1 · check: green
boot: 2026-07-10 — idle-engine seat synced seed HEAD 28fac02, kit v1.7.1 verified via bootstrap.py --version, check --strict green, calibration posted
last-shipped: ORDER 001 — model-attribution ground truth; template guidance + compliant fired card (PRs #47+#48 → main b02f71c)
blockers: plugin adapter (PLUG-001), economy tuning (SIM-001) — both upstream
orders: acked=000-001 done=000-001

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
- Suite: 24 → 827 tests green. No parked PRs, no denials.

## FOUNDING PACKAGE — done-when status
- core loop shipped+tested ✓
- theme schema + gate proven by 3 live packs ✓
- setup-code format versioned + websites-consumable ✓
- plugin-shaping — ongoing (render layer in progress)

## ROUTINE RECORD (Q-0265)
- cron trigger created via mcp__claude-code-remote__create_trigger — id `trig_01TWKGFW8RUsMvxUMt2ndzqA`, name "superbot-idle failsafe wake", cron_expression "45 */2 * * *", enabled true, persistent_session_id session_01BRmUrjckzMsewsXzpc3wwW, prompt as specified by Q-0265 — VERIFIED via list_triggers.
- send_later chain links have fired + re-armed on schedule; latest re-arm fires 00:51Z.
- Both ARMED-AND-VERIFIED.

⚑ needs-owner:

**OA-001 — repo settings: Allow auto-merge + required check `substrate-gate` on `main` — RESOLVED-VERIFIED**
- Auto-merge armed successfully at creation and fired on green for PRs #1 and #2 — the VERIFIED-NEEDED criterion ("next PR shows Auto-merge enabled and lists `substrate-gate` as required") is met.

**OA-002 — repo settings: make `theme-gate` a required status check on `main` — RESOLVED-VERIFIED**
- Owner enabled theme-gate as a required check ~00:10Z; observed gating merges from PR #6 onward — auto-merge fires only after theme-gate concludes.

## PLATFORM-LIMITS
- Two transient GitHub rate-limit hits ("API rate limit already exceeded for user ID 225413533"): PR #26 arming → REST fallback; PR #27 arming → paced retry succeeded. Recorded per PLATFORM-LIMITS; workers now pace GitHub calls.

## PLUG-001 — ⚑ to manager: superbot-next plugin contract unavailable upstream
- Raw-probe evidence: superbot-plugin-hello is an empty public repo; superbot-next publishes no plugin/manifest doc — plugins.md and plugin-contract.md both 404.
- Ask: a contract pointer, or an ETA for exemplar seeding.
- Until then, adapter work is evidence-blocked by design — no speculative code, per docs/plugin-adapter-scoping.md § UNVERIFIED.

## QUEUE
- ON HOLD-PENDING-UPSTREAM: plugin adapter (PLUG-001)
- ON HOLD-PENDING-UPSTREAM: economy tuning (SIM-001)
- DEFERRED: memoized rate table (needs bot runtime)
- DEFERRED: setup-code v2 bound ruling
- ON-DEMAND: catalog wave 4+
- SIM-001 + PLUG-001 awaiting manager

notes: seeded 2026-07-10 by the dispatch copilot at the owner's direct instruction (live dispatch chat), on the fleet seeding recipe (fourth consumer: product-forge, sim-lab precedents). Egg farm = FIRST THEME, not the product — the contract is in README.md. The coordinator overwrites this file (never append) as every session's deliberate last step.

## SIM-001 — ⚑ to manager (Q-0264): Simulator time requested for superbot-idle economy v1
- Executable request registered in `docs/design/economy-v1.md` § "Simulation request — SIM-001 (Q-0264)" (PR #12): scenarios S1–S3 (idle-only / check-in N ∈ {0.25, 2, 8, 24} h / optimal 1-s speedrun; 14-day horizon; 3+ resets) driving the REAL engine functions at the pinned commit — deterministic, integer-exact, stdlib-only.
- Outputs O1–O6 (time-to-first-upgrade, upgrade-purchase timelines, currency trajectories, time-to-prestige distribution, payback curve, 20-reset stacking) judged against pre-registered pacing targets T1–T10 via acceptance criteria A1–A10, all in the same doc.
- Every economy parameter stays PROVISIONAL (no tuning) until the Simulator's verdict; ALL-PASS graduates them sim-pinned, any FAIL gets re-registered in the doc before an engine change lands.
