# 2026-07-13 fleet cleanup audit — superbot-idle

> **Status:** `audit` — a point-in-time snapshot, not a binding doc. Written by an
> external auditor session, not this repo's own coordinator lane. Source code and
> live GitHub state win over anything below if they disagree.

**Audit window:** 2026-07-13 ~22:50Z–23:15Z, local clone fast-forwarded to
`origin/main` @ `a6906b9` (PR #109) before any check was run. Trigger: fleet-wide
EAP final-night cleanup pass (owner ORDER 045), dispatched as a complementary
audit — no feature work, no control-bus edits to files other repos own.

## What this repo is

`superbot-idle` is the idle-game **engine + theme-pack catalog** for the
menno420 Discord-bot fleet (README.md, `docs/AGENT_ORIENTATION.md`). One
mechanical core (`idle_engine/`: generators → currency → upgrades → prestige →
collections, with closed-form offline progress) is skinned per Discord server by
**data-only theme packs** (`themes/*.yaml` against a published JSON Schema,
`schema/theme.schema.json`). The non-negotiable contract (README.md § "The
CORE/SKIN split") is that the engine never hard-codes theme content and theme
packs are data-only, gated by CI (`theme-gate`) so a green pack is safe to enable
on a live server unreviewed. It is not yet wired to Discord — no live bot runtime
exists in this repo; a thin `plugin/` adapter exports a `SubsystemManifest`
against superbot-next's plugin contract, consumed host-side elsewhere.

## Structure

- `idle_engine/` — pure-domain engine (state, tick/offline math, upgrades,
  prestige, economy, theme loader, render, provisioning/setup-codes,
  persistence). Enforced core/skin boundary via
  `tests/test_core_skin_guard.py`.
- `themes/*.yaml` — **18 theme packs** at HEAD `a6906b9` (README/current-state.md
  says 15 — see Inconsistencies below).
- `plugin/` — the superbot-next plugin adapter (`SubsystemManifest`, commands,
  panels, settings, events); has its own `plugin/pyproject.toml`.
- `schema/` — machine-twin JSON Schema for theme packs.
- `tools/`, `scripts/` — theme-gate validator, setup-code vector generator,
  simulate.py (economy simulation harness), `tools/play.py` text REPL.
- `tests/` — unit + property/invariant suite.
- `docs/` — binding contracts (`architecture.md`, `ownership.md`,
  `runtime_contracts.md`, `AGENT_ORIENTATION.md`, `current-state.md`,
  `question-router.md`, …) plus `docs/design/` (economy-v1, achievements-v0,
  sim-harness, timed-events-scoping) and `docs/retro/`.
- `control/` — the fleet-coordination bus: `inbox.md` (manager-written orders),
  `status.md` (this repo's own heartbeat, sole writer = this repo),
  `outbox.md` (lane→manager append-only channel), `claims/` (per-file work
  claims).
- `.sessions/` — 50 per-session log cards (newest: `2026-07-13-eap-wave5-packs.md`,
  `2026-07-13-eap-wave4-milestones.md`, `2026-07-13-eap-ci-skip-hole.md`).
- `bootstrap.py` (828 KB, vendored substrate-kit CLI), `substrate.config.json`,
  `project.index.json`, `.substrate/` — the fleet-kit tooling this repo was
  seeded from (per README, seeded 2026-07-10).
- `CONSTITUTION.md`, `CONVENTIONS.md`, `PLATFORM-LIMITS.md` — repo-local binding
  docs (kit-generated, then hand-extended).

## CI setup and health

Four workflows in `.github/workflows/`:

1. **`substrate-gate.yml`** — kit-owned structural/heartbeat gate (born-red
   session-card check, kit `check --strict`, etc.).
2. **`theme-gate.yml`** — validates every `themes/*.yaml` against the schema
   plus referential checks (id uniqueness, `produces`/`target` resolution,
   `theme.id` == filename stem). Merge-on-green is safe by design for
   data-only theme packs.
3. **`pytest.yml`** — added by PR #74 (ORDER 003, closing a real CI gap: before
   it, no workflow ran the test suite at all — "GREEN ≠ TESTED"). Extended by
   **PR #107** (merged 2026-07-13T22:56:19Z) with a second job,
   `pytest-with-host`, that checks out `menno420/superbot-next` at a pinned
   commit (`9634e81748363184bf13abf1485e80262e19e8cb`) and fails loudly if any
   test still shows `N skipped` — this closes the "1 skipped" hole that was
   item 3 on this repo's own EAP night worklist (`control/inbox.md` ORDER 007).
4. **`auto-merge-enabler.yml`** — arms squash auto-merge on every non-draft
   `claude/*` PR (PR #77).

**Verified live:** PR #109's check runs (`get_check_runs`, queried
2026-07-13T23:0X Z) — `theme-gate`, `substrate-gate`, `pytest`,
`pytest-with-host`, `enable-auto-merge` — **all 5 green**, all completed within
~30 s of each other around 23:03:0X–23:03:22Z.

**Verified locally** (fresh clone at `a6906b9`, `python3.10 -m pip install
pytest pyyaml jsonschema` then `python3.10 -m pytest -q`): **1363 passed, 1
skipped** (23 s). The 1 skip is expected for the plain `pytest` job — it comes
from `plugin/tests/test_manifest.py`'s `importorskip("sb.spec.manifest")` when
the `sb` host package isn't on `PYTHONPATH`; the new `pytest-with-host` CI job
supplies the host and enforces 0 skips there, and that job was green on #109.
`python3.10 bootstrap.py check --strict` also passed clean
(`check: all checks passed.`).

CI is healthy and the gap this repo itself identified (untested-but-green
merges, then the manifest-test skip) has now been closed by its own recent
work — nothing outstanding on the CI front.

## Doc quality

Documentation is extensive and structurally strong: binding contracts
(`architecture.md`, `ownership.md`, `runtime_contracts.md`) plus a "living
ledger" (`docs/current-state.md`) that explicitly declares itself a dated
snapshot to be verified against source, per-session cards in `.sessions/`, and
a `docs/design/` trail of pre-registered, sim-gated economy parameters
(`economy-v1.md`) with an evidenced graduation record (PROVISIONAL →
SIM-PINNED via PR #93, citing sim-lab VERDICT 038). This is a genuinely
disciplined process on paper.

In practice, two of this repo's own living documents are **stale relative to
its own git history** as of this audit — see below. Given the commit velocity
tonight (9 PRs merged between 22:05Z and 23:03Z alone), this is expected lag
rather than a one-off defect, but it is real drift a reader would hit right
now.

## Open PRs — what we found and did

**Zero open PRs at audit time** (`list_pull_requests(state=open)` on
`menno420/superbot-idle`, queried 2026-07-13T~22:5X Z and re-queried after
fast-forwarding the local clone — both returned `[]`). This matches the
worklist claim of "0 open PRs." **No merge, close, or fix action was taken or
needed** — there was nothing open to act on.

However, "0 open PRs" should not be read as "dormant tonight." The 20 most
recently closed PRs (`list_pull_requests(state=closed, sort=updated)`) are
**all merged**, running from #90 (14:25:56Z) through **#109 (23:03:18Z)** — the
newest merge landed 8 seconds before this audit's own `date -u` check
(23:03:10Z). Nine of those PRs (#101–#109) merged inside the final hour of the
audit window alone, each following the repo's claim → build → merge rhythm
(a `control/claims/<slug>.md` fast-lane PR immediately followed by the build
PR). This is a **live, fast-moving coordinator loop, not a dark repo** — see
Activity assessment below.

## Inconsistencies found

**1. The heartbeat (`control/status.md`) is stale by 16 merged PRs, not "0
orders outstanding."** `control/status.md` line 2 reads `updated:
2026-07-13T17:43Z` and line 9 reads `orders: acked=000-005 done=000-005` — no
mention of ORDER 006 or ORDER 007. But `control/inbox.md` shows **ORDER 006**
(owner batching directive, 2026-07-13T22:03:39Z) and **ORDER 007** (EAP
final-night worklist, 2026-07-13T22:14Z) both landed and are actively being
worked: PR #101 ("control: land owner ORDER 006 … + batching note to
manager", merged 22:05:45Z) and PR #104 ("control: ack ORDER 007 + claim EAP
night slices 1-3", merged 22:38:54Z) both modified `control/inbox.md` /
`control/outbox.md` / `control/claims/*` but **neither touched
`control/status.md`** (verified via `get_commit` file lists for both SHAs).
Three more PRs then shipped concrete ORDER 007 worklist items — #105 (catalog
wave 5), #106 (SIM-REQUEST: min-visible-delta feltness floor), #107 (CI
skip-hole close), #108/#109 (wave-4 milestone flavoring) — **all without a
`control/status.md` overwrite**. This is a direct deviation from this repo's
own binding process: `CONVENTIONS.md` line 11–13 ("overwrite `control/status.md`
as the deliberate last step") and `control/README.md` § "Per-session ritual"
("LAST (deliberate final step): overwrite `control/status.md` … You report
order progress ONLY here"). Net effect: an external reader of the heartbeat
right now (as this audit's own dispatch brief was) sees "3h47m-old fresh
heartbeat, all orders done, 0 open PRs" and reasonably concludes the lane is
idle — when in fact 9 more PRs have landed and 2 more orders are in progress.
Per `control/README.md`'s own words, a stale heartbeat is exactly the signal
"the manager treats the Project as dark," which is the wrong read here.
**Not fixed by this audit** (see method note below) — flagged for this repo's
own next wake to correct with its next status overwrite.

**2. `docs/current-state.md` reports counts and roadmap state that are one
graduation-plus-several-waves behind HEAD.** It is dated "Groomed 2026-07-13
against main `05a99f5`" and states "Theme catalog: 15 packs" and "Test suite:
1260 passing, 1 skipped," with roadmap item 1 ("Economy parameter graduation")
marked "UNBLOCKED, next up" and item 3 ("Catalog wave 5") marked "optional
volume." At HEAD `a6906b9`: there are **18** theme packs on disk (`ls
themes/*.yaml | wc -l`), the suite is **1363 passed, 1 skipped** (locally
verified), the economy graduation already shipped (PR #93, `cf59d02`, per
`control/status.md`'s own ORDER 005 section), and catalog wave 5 already
shipped (PR #105, merged 22:50:48Z). The doc itself is explicit that it is a
"dated snapshot" to verify against source (line 106), so this is disclosed
drift rather than a false claim, but it is currently wrong on every headline
number.

**3. Minor: the dispatching brief's "heartbeat ~3h47m old" was accurate at
issue time, not at audit time.** `21:34Z` (fm ORDER 045) + 3h47m ≈ 21:30Z; by
the time this audit ran (`date -u` → 23:03:10Z), the same `17:43Z` heartbeat
was **5h20m old**. Not a repo defect — a reminder that any fleet-wide snapshot
decays fast on a repo running a live wake loop, and this audit's own numbers
will be stale within the hour too.

## Activity assessment for tonight

**ACTIVE, not dark.** Nine PRs merged in the hour before this audit
(#101–#109, 22:05:45Z–23:03:18Z), the newest 8 seconds before this session's
own clock check. `control/claims/` is currently empty except its README —
consistent with a fast claim→build→merge→claim-delete loop still running, not
an abandoned one. This repo's own night worklist (relayed via ORDER 007) is
partway executed: item 1 (catalog wave 5) done via #105, item 3 (CI skip-hole)
done via #107, item 4 (wave-4 milestone flavoring, a related follow-on) done
via #108/#109; item 2 (min-visible-delta feltness SIM-REQUEST) was filed to
the manager via #106 (a request, correctly not a code change — the value is
sim-governed). **No PR fell inside this audit's do-not-touch window because
none was open** — there was nothing to hold back from.

## Method note — why the report doesn't fix finding #1 or #2 directly

Both stale-doc findings are inside this repo's own `control/status.md` /
`docs/current-state.md` update loop, which is that lane's sole-writer
territory by explicit convention (`control/README.md`: "One writer:
this Project" for `status.md`). This audit is an external, complementary pass
per its own brief (no redispatch of work, no touching another lane's
in-progress control surface), and the repo is demonstrably an active lane
mid-loop tonight — the correct next overwrite of `control/status.md` will come
from that lane's own next wake, which already has the evidence in hand
(PRs #101–#109 all exist on `main`). Flagging here rather than hand-editing
avoids racing a live coordinator on the one file it's the sole writer of.

## Suggestions

1. **Add a heartbeat-staleness self-check to the coordinator's own session
   ritual, not just the kit's advisory check.** `control/README.md` already
   says `check` "warns when the heartbeat goes stale," but tonight's gap
   (16 PRs across ~1h20m with zero `status.md` touches) shows that a warning
   that isn't blocking gets skipped under fast batch-mode work. Consider
   making the fast-lane "claim" commit *also* stamp a one-line `status.md`
   `last-shipped:` bump (cheap, no risk of conflicting with a concurrent
   build PR since claims already serialize on `main`), so the heartbeat can
   never drift more than one claim-cycle behind reality even mid-batch.
2. **Fleet-wide: a "heartbeat age" figure quoted in a cross-repo dispatch
   should be time-stamped against the query time, not assumed static.** This
   repo's own case (3h47m at dispatch → 5h20m at audit, in a single evening)
   shows how fast that number rots on any repo running a live wake/pacemaker
   loop. A cheap fix: fleet-status tooling that reports heartbeat age should
   also report "PRs merged since that heartbeat" (a single `list_pull_requests`
   diff) so a reader doesn't need a full audit to tell fresh-and-idle apart
   from fresh-timestamp-but-stale-content.
3. **`docs/current-state.md`'s "groom every session" cadence is falling
   behind burst-mode velocity.** This is disclosed and by design (the doc
   says to verify against source), but during a night like tonight's
   (9 merges/hour) a doc groomed once at the start of a burst is wrong within
   20 minutes. Consider decoupling "current-state groom" from every session
   and instead running it as its own periodic pass (e.g. every N merged
   PRs, mirroring the parent `superbot` repo's 30-PR reconciliation cadence)
   so a groom doesn't get skipped simply because faster sessions keep
   outrunning it.
4. **Minor, low-risk:** `README.md` and `docs/current-state.md` both still say
   "15 packs" (README's `docs/theme-schema.md` chain isn't checked here, but
   the catalog count claim recurs in two places) — worth a single source of
   truth (`len(themes/*.yaml)` computed at doc-generation time rather than
   hand-typed in prose) the next time either file is touched, to stop this
   specific class of drift recurring every catalog wave.

## Evidence index

- PRs verified via `mcp__github__list_pull_requests` /
  `mcp__github__pull_request_read` / `mcp__github__get_commit` against
  `menno420/superbot-idle`, queried 2026-07-13 ~22:50Z–23:10Z.
- Local verification: `git fetch origin main` (`952aa9e..a6906b9`, 6 commits),
  `python3.10 -m pytest -q` → `1363 passed, 1 skipped`, `python3.10 bootstrap.py
  check --strict` → `all checks passed`, `ls themes/*.yaml | wc -l` → `18`.
- Key SHAs: `952aa9e` (PR #103, ORDER 007 landing), `a6906b9` (PR #109, latest
  merge), `58061e8` (PR #101, ORDER 006 landing — no `status.md` touch),
  `c99057c` (PR #104, ORDER 007 ack — no `status.md` touch).
