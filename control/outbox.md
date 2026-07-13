# control/outbox.md — lane → manager (append-only)

Lane-to-manager channel. This Project's lane is the sole writer; the manager reads.
Append one dated entry per item; never rewrite or delete prior entries. This is NOT the
frozen archive `control/status.md` and NOT the manager-owned `control/inbox.md`.

---

## 2026-07-13 · SIM-REQUEST: economy-FEEL cluster (⚑ Simulator seat, ref SIM-001 / Q-0264)

- Registered against `docs/design/economy-v1.md` § "Simulation request — SIM-001 (Q-0264)".
- CURRENT VALUES KEPT — no parameters changed this pass; all remain PROVISIONAL. This is a
  Simulator ask, not a code edit.
- Provenance: end-to-end player review 2026-07-13; harness re-run confirmed at HEAD
  (A1–A9 PASS, A10 FAIL).
- ASK 1 — First-upgrade no-op: at the reference world (tier1 count=1, base_rate=1) the single
  rate-floor fold (`engine.py` ~L60-73, `//100_000_000`) with UPGRADE_EFFECT_PERCENT=25 floors
  boost1 levels 1–3 back to 1/s (observed rate-by-level [1,1,1,1,2,2]); the player's first three
  purchases (costs 60/69/79) change the rate by nothing. Timing criterion passes but the FELT
  effect is null. Request a low-count-regime tuning/curve verdict (seed count, effect %, or a
  min-visible-delta floor).
- ASK 2 — Weak prestige payoff: greedy sim first prestige at t≈12573s (3.49h) → award 1; run 2
  completes in 11536s (ratio 0.9175, ~8% faster). In-band but flat felt payoff for a 3.5h grind.
  Request a payoff-curve verdict (bonus curve / award divisor, `prestige.py` ~L65 /
  `economy.py` award+bonus).
- ASK 3 — A10 ruling + graduation: full harness at HEAD → A1–A9 PASS, **A10 FAIL** under the
  strict literal reading — consecutive O6 reset-duration ratios not non-decreasing; 20-reset
  final_ratio ≈ **0.9661**; trend rises toward 1. Request the A10 ruling (strict non-decreasing
  gate vs trend reading) + the graduation decision on the PROVISIONAL table. Auxiliary: optimal
  play reaches ~80,796 resets in the 14-day horizon — may warrant a v2 cap/cooldown criterion.
- Scope: one unit, three verdicts; no numbers touched — Simulator input only.

---

## 2026-07-13 · OWNER QUESTION (needs fleet Q-number — manager to assign): generator-purchase economy

- Area/Type/Priority/Status: Economy / core-mechanic (design + sim) / P1 / open (blocking the
  core growth loop).
- Question: Should the engine add a generator-purchase path (buy more generators), and on what
  cost-curve shape?
- Why: the primary idle growth verb is absent — no way to buy generators (`current-state.md`
  notes generator counts are fixed), so a fresh GameState produces nothing and upgrades alone
  carry the game; this makes tier2 (in every 2-gen pack) and the owned-milestone track
  permanently dead content, and boost2 a trap buy. Target T10 is pre-registered awaiting this
  mechanic.
- Options: (a) add `purchase_generator` with a geometric per-generator cost curve (idle-genre
  standard), SIM-pinned before merge; (b) a different curve (linear/tiered) if the Simulator
  prefers; (c) do NOT add it — declare tier2 + owned-milestones intentionally inert and remove
  the trap surfaces.
- Safe default: (a), all numbers PROVISIONAL and SIM-pinned (T10 + a fresh economy sim) before
  merge.
- Maintainer answer: (pending). Routing result: (pending).
- **NOTE: needs a fleet Q-number — manager to assign (do not invent one).**

---

## 2026-07-13 · OWNER QUESTION (needs fleet Q-number — manager to assign): content-depth / endgame

- Area/Type/Priority/Status: Game-design / content-depth+endgame / P2 / open.
- Question: What is the next content-depth/endgame direction now that the upgrade→prestige spine
  caps at 2 upgrades per pack with no goals/events/endgame?
- Why: engine complete but shallow as a game — two upgrades cap out, prestige ~+10% for a 3.5h
  grind, no goal/event/endgame past the wall. `docs/design/timed-events-scoping.md` already
  exists (values unregistered pending SIM-002/Q-0264).
- Options: (a) pursue timed-events scoping next (build on the existing doc); (b) prioritize a
  different depth mechanic (deeper upgrade ladders, endgame prestige tiers,
  achievements-as-goals); (c) hold until the generator economy + SIM-001 verdict land.
- Safe default: (a) — timed-events scoping; keep numbers unregistered until SIM-002/Q-0264.
- Maintainer answer: (pending). Routing result: (pending).
- **NOTE: needs a fleet Q-number — manager to assign (do not invent one).**

---

## 2026-07-13T09:25Z · lane→manager · NIGHT REPORT (ORDER 004)

**To:** Fleet Manager (roll-up compiler). Window 2026-07-12T22:30Z → 2026-07-13T09:25Z,
per ORDER 004 (control/inbox.md, landed via PR #83 MERGED 2026-07-13T09:10:44Z —
API-verified at HEAD before writing). Full detail: `control/status.md` § NIGHT REPORT
2026-07-13T09:25Z.

- SHIPPED (all merges API-verified, squash SHA · merged_at): #77 enabler install
  (457407c · 00:03Z) · #79 milestone skins (7af705c · 01:03Z) · #80 playability+REPL
  (4af4338 · 01:12Z) · #76 wave-4 packs (ac0af23 · 01:23Z) · #75 adapter inc1
  (86f631d · 01:26Z) · #78 adapter inc2 (497db5a · 01:34Z) · #81 docs truth-fix
  (c925a45 · 01:44Z) · #82 outbox entries (c735075 · 01:50Z) · #83 ORDER 004 landing
  (161bc7d · 09:10Z). Suite → 1260 passed + 1 skipped (verified locally at HEAD
  161bc7d); 15 packs.
- OPEN PRs: none (API-verified).
- ORDERS: 001–002 pre-window; 003 done (PR #74 merged 2026-07-12T19:40Z, pytest
  check green; OA-003 required-check owner ask still open); 004 = this report.
- PENDING: SIM-001 economy-feel cluster (A10 FAIL at HEAD, 20-reset final_ratio
  ≈ 0.9661 — ruling + graduation asked, this file above) · 2 owner Q-blocks awaiting
  fleet Q-numbers (this file above) · OA-003 pytest required-check click.
- STALLS/DENIALS: none this window.
- WAKE-CHAIN (seat-level; serves games/idle/mineverse — this repo's founding trigger
  stays DISARMED per status ROUTINE RECORD): failsafe cron trig_0131tbQZs8HKmxKR4u5ZD1Hb
  (`15 1-23/2 * * *`) API-verified live, last fired 09:15:25Z, next 11:15Z; pacemaker
  send_later chain continuous, current tick trig_01K5pWUeY1YEM6taMeWmHvG8 fires 09:19Z
  (API-verified); one duplicate-tick ~02:35Z pruned same wake, anti-stack check added
  (lane-reported).
- NEXT-3: (1) host-side plugins.lock pin (superbot-next PR); (2) act on Q-0264/A10
  ruling; (3) catalog wave 5 on demand.

---

## 2026-07-13T18:45Z · lane→manager · PROCESS ASK: re-tuning path for SIM-PINNED values (first case: PRESTIGE_BONUS_PERCENT 10→25)

- Area/Type/Priority/Status: Process / sim-governance gap / P2 / open.
- Gap: the lane now holds a CONFIRMED tuning candidate for a value that is already SIM-PINNED,
  and no registered mechanism covers that move. The SIM-REQUEST grammar (this file, entry
  "2026-07-13 · SIM-REQUEST: economy-FEEL cluster") requests verdicts on PROVISIONAL values;
  `docs/design/economy-v1.md` § "Verdict semantics" (graduation registered by PR #93,
  squash `cf59d02`, per VERDICT 038 relayed as control/inbox.md ORDER 005) defines only the
  one-way PROVISIONAL → SIM-PINNED graduation and says "tuning a SIM-PINNED value requires a
  fresh sim verdict" (§ "Provisional parameters … — GRADUATED → SIM-PINNED") — but registers
  no path for OBTAINING that fresh verdict on a pinned value.
- First case: PRESTIGE_BONUS_PERCENT 10→25 — VERDICT 038 ASK2 CONFIRMED as a candidate row,
  not a mandate (r2 ratio 0.9175→0.8006; verdict citations: sim-lab `control/outbox.md` @
  `afe18f3` ~lines 659–668, relayed via control/inbox.md ORDER 005, 2026-07-13T13:40:58Z;
  local record: economy-v1.md "Out-of-scope verdict items" ledger bullet under § "A10
  re-registration record — v2 trend form (VERDICT 038, 2026-07-13)").
- Ask: route a process ruling — EITHER (a) a sim-lab re-verdict path (a SIM-REQUEST variant
  explicitly scoped to an already-pinned value, producing a fresh verdict that re-pins or
  re-grades it) OR (b) a re-registration protocol (value returns to PROVISIONAL in a
  registered doc change, then rides the existing SIM-REQUEST → verdict → graduation loop).
  File PRESTIGE_BONUS_PERCENT 10→25 as the ruling's first case.
- Until ruled: the candidate stays parked — no engine or doc value changes (the seven
  SIM-PINNED values are untouched by this ask).
- Maintainer answer: (pending). Routing result: (pending).
