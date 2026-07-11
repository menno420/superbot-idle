# Archive-ready 2026-07-11

> **Status:** `historical` (frozen 2026-07-11 — the state of the lane at the moment
> the founding coordinator chat was archived; companion to
> [`2026-07-11-lane-retro.md`](2026-07-11-lane-retro.md))

## True state (one paragraph)

The engine is complete for its current scope — tick, upgrades, prestige,
achievements/milestones, and integer-exact closed-form offline progress
(tick/offline exact-equivalence property-tested) — with 12 data-only theme
packs against schema v1 (labels block + balance bounds 90..110), both
`theme-gate` and `substrate-gate` required checks on `main`; setup-code
format v1 ships with cross-language test vectors, persistence is at save
format v2 with a byte-pinned golden corpus (incl. v1→v2 migration goldens),
the render layer builds 4 budget-enforced embed views
(status/shop/prestige/achievements), and the SIM-001 harness has produced a
provisional run — A1–A9 PASS, A10 strict-reading FAIL awaiting ruling. The
suite stands at 1131 tests green; 69 PRs total merged-on-green with zero
guard/classifier/merge denials and zero red CI on `main` at any point.

## Every ⚑ waiting (the wait-list — preserved in `control/status.md`)

- **SIM-001 + A10 ruling (Q-0264, manager):** economy parameters stay
  PROVISIONAL until the fleet Simulator's official run; the provisional A10
  strict-vs-trend wording ruling, multiplier values, achievements-inclusive
  scenarios, and timed-events adoption all ride the same ruling. Spec:
  `docs/design/economy-v1.md`, results
  `docs/design/sim-results-2026-07-11-provisional.json`.
- **PLUG-001 (plugin contract, upstream):** `superbot-plugin-hello` is an
  empty public repo and superbot-next publishes no plugin/manifest doc —
  adapter work is evidence-blocked by design
  (`docs/plugin-adapter-scoping.md` § UNVERIFIED).
- **KIT-001 (kit-level suggestion, manager):** plant `merge=union`
  gitattributes for append-only ledgers fleet-wide (host-side proof: PR #63).

## What a fresh session needs to resume

1. **Read, in order:** `README.md` (lane contract) → `control/status.md`
   (heartbeat: phase, wait-list, ROUTINE RECORD, queue) → `docs/retro/`
   (this file + the lane retro) → `docs/design/` (pre-registered economy;
   nothing may be tuned outside it).
2. **If resuming autonomous operation, RE-ARM the wake loop (Q-0265):** both
   triggers were deliberately DISARMED at close-out. Recreate the failsafe
   cron + the ~15-minute `send_later` chain per the spec recorded in
   `control/status.md` § ROUTINE RECORD.
3. **Claims protocol:** claim a slice via a fast-lane PR adding
   `control/claims/<slug>.md` before building; remove the claim in the build
   PR's final commit. `control/claims/` empty (README only) = no live claims.
4. **PR merge rules:** branch → READY PR (never draft) → both gates green →
   auto-merge armed at creation; rate limit → paced retry; REST-merge ONCE on
   green if arming fails both ways; one merge attempt then park READY+green
   with a ⚑. NEVER touch `control/inbox.md` (manager-only writer). Verify
   before push: `python3 -m pytest -q && python3 bootstrap.py check --strict`.

## Nothing important is chat-only

Confirmed at close-out: the ORDER 002 self-review, the coordinator operations
model (session topology, worktree isolation, wake-loop pattern, rate-limit
ladder, zero-check-runs recipe), and the owner rulings (OA-001, OA-002, the
idea-batch mandate) were the only knowledge living solely in the archived
chat; all of it now lives in `docs/retro/2026-07-11-lane-retro.md`,
`PLATFORM-LIMITS.md`, and `control/status.md`. Everything else was already
durable: contracts in `docs/`, decisions in `docs/decisions.md`, per-session
narratives in `.sessions/`, the shipped record and wait-list in
`control/status.md`.
