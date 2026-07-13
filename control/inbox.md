# superbot-idle · inbox

> ORDERS to this Project. **ONE writer: the manager** — never edit this file. Report order
> progress in `control/status.md` (`orders: acked=… done=…`). Protocol: `control/README.md`.

*(no orders yet — the manager appends `## ORDER 001 · <ISO8601> · status: new` blocks here)*

## ORDER 001 · 2026-07-11T04:05:00Z · status: new
priority: P3
from: fleet-manager manager — ORDER 010 per-lane relay (provenance: fm control/inbox.md ORDER 010 + fm docs/findings/model-matrix-2026-07.md; relayed via fm PR #63; this lane was out of that session's scope — completed by the follow-up relay-completion slice)
executor: superbot-idle lane coordinator — next fired session
do: Model-attribution ground truth (fleet standing rule, family-level names only per Q-0262): (1) confirm the session-card template carries a `📊 Model:` line — add it if missing; (2) every fired session records the model family its own harness/environment reports (e.g. fable-5, opus-4.8, sonnet-5) on that line in its committed session card — the Routines screen is NOT a reliable attribution surface; (3) n/a — keep the standing rule.
why: the fleet model matrix (fm docs/findings/model-matrix-2026-07.md) found per-session self-report in commits is the only reliable attribution; cross-surface disagreement is evidenced (websites PR #59 squash 2c89e96: Routines screen fable-5 vs the fired card's claude-sonnet-5).
done-when: the next fired session's committed card carries a real family-level `📊 Model:` line and the template (if any) includes it.

## ORDER 002 · 2026-07-11T10:00Z · status: new
priority: P1
from: fleet-manager on coordinator direction (cse_012o8pySy5K3AV6JWoPKryZL), owner-directed
executor: superbot-idle seat (next wake)
do: quick self-review of this lane covering roughly the last 24h (2026-07-10 ~20:00Z → now): (1) anything that WENT WRONG — red CI runs, guard/classifier denials, walls hit, drift found, mistakes made or corrected — each with a citation (PR/run/commit); (2) anything REQUIRING OWNER ATTENTION — owner-only asks, pending vetoes, risky decisions taken decide-and-flag, spend/publish items — click-level and plain language; (3) one-line current health (what shipped, what's next). Commit the review as a dated "Self-review 2026-07-11" section in control/status.md (or this lane's report convention); mirror ⚑ owner-attention items on the heartbeat so the manager sweep collects them.
why: owner-requested fleet-wide self-review (2026-07-11), relayed by the fleet-manager coordinator on the owner's in-session instruction.
done-when: the self-review section is on main within this lane's next two wakes.

## ORDER 003 · 2026-07-12T08:30Z · status: new
priority: P1
owner: SuperBot World coordinator (executor)
provenance: filed by the fleet manager — relocation of startup-prompt v3.1 W2 (prompts are STATELESS since v3.2, owner correction 2026-07-12; fleet-manager PR #108).
do: Add CI that runs the pytest suite on PR + push (today GREEN ≠ TESTED — no workflow executes the tests), then ⚑ the owner to mark it a required check. Until it exists, run the suite locally before any merge.
why: verified at HEAD c6a349d 2026-07-12: .github/workflows/ contains substrate-gate.yml + theme-gate.yml only — no job runs pytest.
done-when: the pytest workflow is green on a real PR; the ⚑ required-check ask is filed.

## ORDER 004 · 2026-07-13T09:09:36Z · status: new
priority: P2
from: fleet manager — NIGHT REPORT REQUEST, owner ask 2026-07-13 (relayed via Fleet Manager)
executor: superbot-idle seat (next wake)
do: post a THOROUGH night report, window 2026-07-12T22:30Z→now, to control/status.md AND your outbox (manager-addressed): SHIPPED (merges/PRs, numbers+SHAs) · OPEN PRs + check states · ORDERS served + outstanding · SIM-REQUESTs/asks pending · STALLS/denials verbatim · wake-chain health (failsafe + pacemaker ids/fires) · next-3.
why: owner morning review.
done-when: report in both files; Fleet Manager compiles the roll-up.

## ORDER 005 · 2026-07-13T13:40:58Z · status: new
priority: P1
from: Fleet Manager seat — Q-0264 fan-out verdict relay (relayed by the Fleet Manager seat per Q-0264, coordinator dispatch 2026-07-13)
executor: superbot-idle seat (next wake)
do: consume sim-lab VERDICT 038 for SIM-001 (economy-FEEL cluster, packet @ superbot-idle `d992c568`) — verdict CONDITIONAL: graduate the seven-parameter PROVISIONAL table → SIM-PINNED, conditional on re-registering A10 in trend form in the same PR (a doc change in docs/design/economy-v1.md, ZERO parameter changes; proposed wording in the sim's fixtures.json `a10_trend_wording_proposed` — final text is this seat's to register). Strict A10 fails, but all 6 violations sit inside the registered 0.02 wiggle band (max 0.0166, ~83% of band; trend rises 0.9175→0.9661). Also from the verdict: (a) the min-visible-delta feltness floor is engine-side and needs its own sim before registering (no constant fix is viable — ASK1 CONFIRMED-INERT); (b) PRESTIGE_BONUS_PERCENT 10→25 is a candidate row, not a mandate (ASK2 CONFIRMED, r2 0.9175→0.8006); (c) co-consumer is fm owner-queue E#52 (generator purchase curve — this verdict's honest-NULL boundary jointly with V017's priced row).
why: Q-0264 fan-in served all 9 sim-request verdicts; this is superbot-idle's SIM-001 verdict. RESUME TRIGGER cleared: this lane's dormant-queue trigger "Q-0264 ruling lands (A10 wording + multiplier values …) → unblocks economy tuning" — declared at control/status.md line 94 @ 3a4fa5f1aad4294195daf6696c38d92d81ebb669 — is fired by this relay for its SIM-001/V038 component (A10 wording + the seven-parameter table).
done-when: the graduation PR lands (economy-v1.md table → SIM-PINNED + A10 re-registered in trend form, same PR, zero parameter changes) and status.md reports this order done.
citations: sim-lab `afe18f3` control/outbox.md (VERDICT 038, ~lines 659–668) · fleet-manager control/outbox.md @ `a32eb2c` (§ "2026-07-13 · Q-0264 FAN-IN — ALL 9 SIM-REQUEST VERDICTS SERVED") · fm PR #166.

## ORDER 006 · 2026-07-13T22:03:39Z · status: new
priority: P1
from: live owner turn in the SuperBot World coordinator session, 2026-07-13 ~21:59Z, relayed by the coordinator dispatch. NOTE: inbox.md is normally owner/manager-written; a coordinator relaying a live owner turn is the sanctioned exception (stated here per doctrine).
executor: superbot-idle seat (next wake)
do: Owner text, verbatim (quote block, do not paraphrase or fix typos):
> yes make sure the sim works in bigger batches, the goal should be to get all the games to a producition grade level, tho it should not hinder the correct structure, speed is important but not more important than correctness

INTERPRETATION:
(a) sim verdict pipeline moves to bigger batches — full content waves per SIM-REQUEST instead of few-item slices;
(b) standing mission target: bring all three games to production-grade;
(c) precedence: correctness and structural integrity outrank speed — no gate/verdict/golden-parity floor is relaxed.
why: Context: owner asked why superbot-games fishing has 4 species vs the original's ~21; coordinator offered to batch-pin the remaining roster; owner said yes and generalized.
done-when: future SIM-REQUESTs from this lane batch into full content waves; production-grade is adopted as the standing target; status.md reports this order acked.

## ORDER 007 · 2026-07-13T22:14Z · status: new
priority: P1
from: Fleet Manager seat — EAP final-night fan-out (fm ORDER 045, Phase 3), relayed by coordinator dispatch 2026-07-13
executor: superbot-idle seat (next wake)
do: work the EAP final-night worklist below top-down across tonight's wakes — ORDER body relayed verbatim below.
why: owner directive 2026-07-13 ~21:34Z (fm ORDER 045) — last day of the EAP; every seat gets a full night worklist.

**EAP final-night worklist — owner directive relay (fm ORDER 045, Phase 3 fan-out).**

Owner directive, quoted VERBATIM as recorded in fm ORDER 045: "I want you to find out the current state of all repos and
dispatch instructions for all projects so they know what to do, find out if there still
need to be improvements made in existing features or else if the idea lab made any good
plans etc. the goal is to make sure each project has a full list to work on tonight since
it's the last day of the EAP."

Citations: fm ORDER 045, control/inbox.md @ ca1ce28 · docs/eap-final-night-worklists-2026-07-13.md @ ca1ce28 (doc last modified by commit e963183; landed via fm PR #178, merged 2026-07-13T22:07:14Z).

**Your seat's full night worklist, copied faithfully from the doc:**

## superbot-idle — swept @ `1f4d774`

Honest thin list — engine complete, all 5 ORDERs done (SIM-001 graduation shipped
#93; pytest CI shipped #74), zero open PRs; the queue is mostly waiting on others.

1. Catalog wave 5 — 3 data-only theme packs; explicitly sanctioned standing filler, merge on theme-gate green alone (`docs/current-state.md` roadmap item 3 @`1f4d774`) `[standing]`
2. SIM-REQUEST draft: min-visible-delta feltness floor — V038 ASK1 = CONFIRMED-INERT, needs its own sim; docs-only, unblocks a real tuning lane (`control/status.md` § ORDER 005 @`1f4d774`) `[improve]`
3. Close the `1 skipped` CI hole — CI job checking out pinned superbot-next so `plugin/tests/test_manifest.py` actually exercises the adapter contract (`docs/current-state.md` stability § @`1f4d774`) `[improve]`
4. Cross-repo pointer: the `plugins.lock.json` pin rides in superbot-next (its item 6) — track it, don't duplicate (`control/status.md` Next-3 @`1f4d774`) `[lane]`

**Blocked (do not schedule):** PRESTIGE_BONUS_PERCENT 10→25 (parked behind the SIM-PINNED re-tuning ruling, outbox ask 18:45Z) · timed-events (SIM-002 + owner Q-block) · generator-purchase economy (owner Q-block) — both Q-blocks await fleet Q-numbers from fm · OA-003 mark `pytest` required (owner click).

Why-tonight tags (from the worklists doc): `[lane]` unfinished lane work · `[standing]` standing/unconsumed
ORDER · `[verdict]` sim verdict served/approved awaiting build · `[build-direct]`
idea-engine plan marked buildable without a sim verdict · `[improve]`
feature-improvement · `[drift]` docs/heartbeat drift fix · `[deadline]` window
closes 07-14 · `[relay]` fm routing/relay debt.

---

**ORDER 031 idle-component split (reference).** fm ORDER 031 (mining/fishing/idle
finalization + casino inventory/spec; owner's words include "same for fishing and
the idle game") names superbot-idle in its owner set, but the sweep found it landed
in no seat inbox (worklists doc cross-cutting finding 1 + fm self item 3 @ ca1ce28).
The idle-game finalization component of ORDER 031 falls to THIS seat's list above;
superbot-next carries the order as primary owner in its own dispatch (fm ORDER 031
@ ca1ce28, fm control/inbox.md).


provenance: relayed by the Fleet Manager seat per owner directive, coordinator dispatch 2026-07-13
done-when: work the list top-down across tonight's wakes; ack in your inbox thread; heartbeat progress per item.
