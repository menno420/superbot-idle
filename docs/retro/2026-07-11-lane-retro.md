# Lane retro — 2026-07-11 (close-out of the founding coordinator session)

> **Status:** `historical` (frozen 2026-07-11 at lane archive; the coordinator chat
> that produced this record is archived — this file and its sibling
> [`2026-07-11-archive-ready.md`](2026-07-11-archive-ready.md) are the durable
> homes for everything that previously lived only in that chat)

## 1. Self-review 2026-07-11 (ORDER 002) — MOVED here from `control/status.md`

> Moved verbatim at close-out; `control/status.md` keeps a one-line pointer.
> Window: 2026-07-10 ~20:00Z → 2026-07-11 10:11Z.

### What went wrong (all recovered in-session; none open)
- **Transient GitHub rate limits (fleet-shared account):** auto-merge arming on PR #26 failed
  twice — verbatim `API rate limit already exceeded for user ID 225413533` — and the documented
  REST-merge-once-on-green fallback was used; PR #27 arming failed twice with the same error and
  a paced retry succeeded. Recorded in § PLATFORM-LIMITS (heartbeat PR #29); workers pace GitHub
  calls since.
- **Real decoder bug, found and fixed red-first:** `decode_setup` accepted leading-zero version
  prefixes (`IDLE01-` parsed as v1) contra docs/provisioning.md § Grammar ("no leading zeros").
  Surfaced by the test-vector slice and deliberately reported-not-fixed in PR #25's ⚑; ruled
  grammar-wins (docs/decisions.md D-0005), fixed in PR #28 — red-first `MalformedCodeError`
  tests, `_PREFIX_RE` tightened, 2 new error vectors (23 → 25).
- **Recurring mid-flight dirtying of `.substrate/guard-fires.jsonl`** (the kit appends to it on
  every `check`, so any two concurrent sessions collide there): first union-merge on PR #27 when
  the vectors PR #25 merged mid-flight, recurred on PR #38 (docs-grooming #37 merged mid-flight)
  and PR #41 (heartbeat #39 merged mid-flight) — each resolved by stash → rebase → pop with full
  re-verify before push, zero content conflicts (friction notes: session cards
  themed-label-slots / shop-composition / state-serialization; a kit-level `merge=union`
  gitattribute for `.substrate/*.jsonl` would retire the pattern).
- **Doc drift found + fixed:** the orientation docs still described the seed state ~30 merges
  later — docs/current-state.md an empty skeleton; architecture.md + AGENT_ORIENTATION.md still
  saying theme-gate would be enforced "once ORDER 000 lands it in CI" long after OA-002 made it
  a required check — corrected in docs-grooming PRs #35+#37.
- **One mid-session strict-check red in slice (d):** the new economy design doc flagged as a
  read-path orphan; cross-linked before PR #12 opened. Later slices applied the lesson
  proactively ("no red loop" — setup-code-v1 card).
- **Decide-and-flag schema tighten:** `upgrades[].description` cap 1024 → 768 in PR #38 —
  required for the exact worst-case shop-composition arithmetic (768+1+139+116 = 1024);
  in-bounds because the field had rendered NOWHERE before and zero shipped packs exceeded it
  (catalog max 100 chars). Provenance noted in docs/theme-schema.md.
- **No guard/classifier/merge denials, no parked PRs, no red CI on main at any point:** all 100
  main-branch workflow runs to date concluded success; 48 lane PRs merged on green (50 repo PRs
  total incl. the manager's inbox appends #46/#50).

### Requiring owner attention (click-level, plain language)
- **Nothing requires a click right now.** OA-001 (auto-merge + required `substrate-gate`) and
  OA-002 (required `theme-gate`) were both done by the owner and are RESOLVED-VERIFIED in
  `control/status.md`.
- ⚑ **PLUG-001** (block in `control/status.md`): the plugin adapter is blocked upstream —
  `superbot-plugin-hello` is an EMPTY public repo and superbot-next publishes no plugin
  contract. If the owner controls that repo, seeding the exemplar unblocks this lane; otherwise
  it waits on the manager.
- ⚑ **SIM-001** (block in `control/status.md`, Q-0264): economy numbers stay provisional until
  the fleet Simulator runs the pre-registered scenarios — manager relay, no owner click.
- FYI — decide-and-flag decisions taken without asking, all recorded: grammar-wins setup-code
  ruling (PRs #26+#28, D-0005), description-cap tighten (PR #38), steady-state hold (PR #45).

### Health (as of the ORDER 002 window)
green — founding package + volume backlog fully shipped (48 lane PRs merged-on-green, 827
tests, 12 theme packs, ORDER 001 done); lane holds new engine surface pending
PLUG-001/SIM-001 or new ORDERs; chain + failsafe cron watching the inbox.

## 2. Coordinator operations knowledge (previously chat-only)

How this lane actually ran, captured so a fresh session can reproduce the
operating model without the archived chat:

- **Session topology:** the lane ran as ONE coordinator session
  (`cse_01BRmUrjckzMsewsXzpc3wwW`) that dispatched Agent-tool workers into
  **isolated git worktrees**. Worker seats execute INSIDE the coordinator
  session, which has two load-bearing consequences: (1) `send_later` self-binds
  correctly — a worker arming the chain arms it for the coordinator session,
  which is exactly what Q-0265 wants; (2) trigger/scheduler tools
  (`create_trigger`, `send_later`, `list_triggers`, `delete_trigger`) are
  worker-reachable even when a surface suggests otherwise (see
  `PLATFORM-LIMITS.md` — toolsets are seat-dependent; retry walled calls from a
  worker BEFORE flagging owner-manual).
- **The wake loop (Q-0265) that kept the lane alive:** a failsafe cron trigger
  — id `trig_01TWKGFW8RUsMvxUMt2ndzqA`, name "superbot-idle failsafe wake",
  `cron 45 */2 * * *`, bound to the coordinator session — PLUS a self-re-arming
  ~15-minute `send_later` chain (each firing re-arms the next link as its first
  act). The chain is the pacemaker, the cron the failsafe; the pattern kept the
  loop alive across ~40 watch cycles with zero missed heartbeats. Both were
  DISARMED at close-out (see the archive-ready doc + status ROUTINE RECORD);
  a resuming session must re-arm both per the spec in `control/status.md`.
- **Parallel git workers REQUIRE isolated worktrees** (fleet-verified, and
  re-verified here): two workers sharing one checkout corrupt each other's
  index/branch state; the Agent-tool `worktree` isolation mode is the correct
  primitive. The one shared-file exception (`.substrate/guard-fires.jsonl`,
  appended by every `check`) was retired by the `merge=union` gitattribute
  (PR #63).
- **GitHub auto-merge arming rate limits** (fleet-shared token) recovered via
  paced retry, falling back to a single REST merge on green — the ladder in
  `CONVENTIONS.md` held every time it was needed (PRs #26, #27; details in § 1).
- **Zero-check-runs stall + rebase retrigger:** one PR (#61) sat ~5 minutes
  with ZERO check runs — `mergeable_state: unknown`, GitHub never built the
  merge ref, so no workflow was ever dispatched. A
  `git rebase` + `push --force-with-lease` retriggered checks instantly. Now
  recorded as a standing wall/recipe in `PLATFORM-LIMITS.md` (added at
  close-out; it was not there before).

## 3. Owner rulings delivered in chat (previously chat-only)

- **OA-001** — owner enabled repo auto-merge + required `substrate-gate` check
  on `main` (verified from PR #1 onward).
- **OA-002** — owner added `theme-gate` as a required check on `main`
  (~2026-07-11 00:10Z; observed gating merges from PR #6 onward).
- **Idea batch was owner-requested:** the owner explicitly asked, verbatim,
  "do you have any other ideas you can implement?" — that request is the
  mandate that produced the PR #52–#68 batch (sim harness, achievements +
  save v2, buy-max, bounded multipliers, union hygiene, golden corpus,
  timed-events scoping). It was a one-time mandate, not a standing order:
  post-batch the lane returned to steady-state hold.

## 4. Pointers

- True-state snapshot + resume instructions: [`2026-07-11-archive-ready.md`](2026-07-11-archive-ready.md)
- Live wait-list (⚑ SIM-001/A10, PLUG-001, KIT-001): `control/status.md`
- Shipped record, PR by PR: `control/status.md` § SHIPPED RECORD
