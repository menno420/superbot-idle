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
