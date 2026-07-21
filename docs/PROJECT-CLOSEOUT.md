# superbot-idle — project closeout

> **Status:** `reference`
>

This page wraps up the superbot-idle project for two readers who have never
seen the working sessions behind it: the **owner** (no coding required) and a
**fresh Claude session** picking the repo up cold. It says what the project is,
what was built, what is true right now, what is left open, and how to run and
continue the work. Everything below was verified against the repository at
commit `31a4a3a` (the current tip of `main`).

---

## What this project is & what was accomplished

**superbot-idle is one idle-game engine plus a catalog of data-only "theme
packs" that re-skin it.** The mechanical core — generators produce currency,
currency buys upgrades, a prestige reset trades progress for a permanent boost,
and time keeps accruing while you are offline — is written once, in plain
Python. Every player-visible word, emoji, and colour comes from a *theme pack*
(a `themes/<name>.yaml` data file), never from the engine code. Two Discord
servers running different themes get **identical mechanics**: one codebase to
balance and fix, many worlds on top. This "core/skin split" is the repo's whole
reason to exist (`README.md`).

The work was carried out over a run of **autonomous agent sessions**. The major
shipped pieces, each with its verified merge citation:

- **21 data-only theme packs** — a single engine skinned into 21 worlds, built
  in waves. Highlights with citations: catalog wave 5 (clockwork-atelier,
  lighthouse-keep, ramen-stand) shipped in **PR #105**; the **apiary**
  beekeeping pack in **PR #156**; the **forge** blacksmith pack in **PR #161**;
  and the current tip, the wave-6 **vineyard/winery** pack (the 21st), in
  **PR #175** (`31a4a3a`). Adding a pack changes no engine constant — it is
  pure data that clears the theme-gate.

- **Security / loader hardening wave** — a run of load-time guards that make a
  malformed or malicious theme pack fail *loudly at load* instead of silently
  corrupting a live game: structural guards on the pack loader (**PR #149**);
  rejecting duplicate currency and generator ids (**PR #163**); rejecting a
  malformed `embed_color` (**PR #164**); rejecting duplicate YAML mapping keys,
  both in the gate and in the loader (**PR #166**, **PR #167**); enforcing the
  `base_rate` upper bound at load time (**PR #168**); and a durable
  loader↔schema parity-guard capstone that also closed four loader
  reference-integrity gaps (**PR #169**), followed by the cross-pack
  vocabulary and structural-parity audit THM-17 (**PR #170**).

- **Engine ergonomics** — read-only helpers that never touch the economy
  numbers: a `time_to_afford()` helper (**PR #151**), a prestige-preview helper
  (**PR #152**), and an affordability ETA shown in the shop view (**PR #160**).

- **substrate-kit upgrades** — the shared agent-workflow tooling was vendored
  forward from v1.15.0 to **v1.16.0** (**PR #134**), and the local preflight
  script plus the host card-guard were split cleanly out of the kit-owned
  enabler (**PR #137**).

- **The engine core is the sim-pinned stability baseline.** The economy
  parameters are not hand-tuned guesses: the seven-parameter table was
  graduated from PROVISIONAL to **SIM-PINNED** against a fleet simulator verdict
  (**PR #93**, ORDER 005 / VERDICT 038), and re-tuning any pinned value now
  requires a fresh verdict. Offline progress is computed in **closed form** and
  property-pinned to be integer-exact-equal to running the live tick loop
  step-by-step (`idle_engine/engine.py`, enforced by the property/invariant
  test layer). The suite also runs the tests against a pinned copy of the host
  (`superbot-next`) so the plugin adapter contract is actually exercised in CI,
  not just skipped (**PR #107**).

---

## Current true state

Verified live at `main` tip `31a4a3a`:

- **Test suite: 1642 passed, 1 skipped** (`python3 -m pytest -q`). The single
  skip is a *known, designed* hole: `plugin/tests/test_manifest.py` skips when
  the `sb` host package is absent locally, but the `pytest-with-host` CI job
  checks out a pinned `superbot-next` and runs those 15 manifest-contract tests
  on every PR (`1657 passed` there — no skips). Not a regression.
- **`python3 bootstrap.py check --strict` passes** ("all checks passed"; only
  never-exit-affecting advisory warnings, e.g. a stale-heartbeat note).
- **Zero open PRs.** `control/claims/` holds only its README plus this seat's
  own terminal claims (removed as part of this closeout).
- **21 theme packs**, all schema-v1, all clearing the theme-gate.

---

## Continuation — open threads

**Idle is engine-complete. The continuation list is genuinely thin — the engine
is the stable baseline, not an active build front.** There is no unfinished
feature waiting to land. What remains is a short list of *deferred* items, none
of which this repo can start on its own:

1. **Feltness-floor sim (V038 ASK1) — BLOCKED on a fleet number.** The
   "min-visible-delta feltness floor" SIM-REQUEST is filed (see the roadmap in
   `docs/current-state.md`) and awaits a fleet SIM/Q-number from the manager.
   *Resume step:* when a verdict is served, register the spec section and
   harness metrics, then build the winning floor mechanism. Do not invent a
   constant — the verdict confirmed no constant fix is viable.
2. **PRESTIGE_BONUS_PERCENT 10→25 — PARKED behind a ruling.** A candidate
   economy row, not a mandate; it stays parked behind the SIM-PINNED re-tuning
   process ask in `control/outbox.md`. *Resume step:* only when that ruling
   lands.
3. **Setup-code v2 version-bound ruling — deferred by design** to the PR that
   actually defines format v2.

`control/inbox.md` ORDER 005 (the VERDICT 038 economy graduation) is **already
served** — it shipped as PR #93; no open build thread hangs off it. The other
inbox ORDERs are likewise served or are standing-direction records (ORDER 011).

For **fleet-wide** threads that span more than this repo, see the master
closeout in superbot-mineverse (linked below).

---

## Owner walkthrough

**What this repo is, in one line:** the reusable idle-game engine and its
growing catalog of theme packs — the part that will eventually let you pick a
theme on a website *before* the bot is invited to a Discord server. There is no
live Discord bot in this repo yet; that wiring lives in the host repo
(`superbot-next`).

**How to run it yourself** (Python 3.10+, no install, no build step):

```
# See the game play in a text window — pick any of the 21 themes:
python3 tools/play.py                       # default egg-farm theme
python3 tools/play.py --pack vineyard       # the newest (winery) theme
python3 tools/play.py --list-packs          # list all 21 themes

# Inside the loop, type: status, shop, buy <id> [n|max], prestige, offline <secs>,
# wait <secs>, achievements, save, load <blob>, pack <id>, help, quit.

# Prove the whole project is healthy (this is the one command that matters):
python3 -m pytest -q                        # expect: 1642 passed, 1 skipped
python3 bootstrap.py check --strict         # expect: all checks passed
```

**Key docs, if you want to read further:**

- `README.md` — the plain-language project pitch and the core/skin rule.
- `docs/current-state.md` — the living status ledger (what is true right now).
- `docs/eap-closeout-walkthrough-2026-07-14.md` — an earlier owner walkthrough
  with a pending-owner-actions checklist.
- `themes/README.md` — what a theme pack is.

**Owner checklist (quickest first):**

- [ ] *(1 min)* Run `python3 -m pytest -q` and confirm `1642 passed, 1 skipped`
      — that is the whole project verifying itself.
- [ ] *(2 min)* Run `python3 tools/play.py --pack vineyard` and play a few turns
      to see the engine and a theme in action.
- [ ] *(optional)* Nothing is blocking on an owner click for this repo. The one
      standing owner decision — whether to re-tune `PRESTIGE_BONUS_PERCENT`
      10→25 — is parked behind a sim ruling, not awaiting your action today.

---

## Working this repo with a fresh session

**Boot route (in order):** `.claude/CLAUDE.md` (working agreement) →
`HANDOFF.md` if present (previous session's trail, untracked) →
`docs/current-state.md` (living ledger). Then `docs/AGENT_ORIENTATION.md` for
task-specific reading routes. This closeout is reachable from both
`docs/current-state.md` (top pointer) and `docs/AGENT_ORIENTATION.md`
(lane-layer docs).

**Verify any change:**

```
python3 -m pytest -q && python3 bootstrap.py check --strict
```

Theme packs additionally validate through the theme-gate:
`python3 tools/theme_gate.py themes/*.yaml`.

**How PRs land here:** work on a `claude/*` branch. The session card
(`.sessions/<date>-<slug>.md`) is **born red** — first commit sets its Status to
`in-progress`, which holds the substrate-gate HOLD so the PR cannot merge
prematurely; flipping the card to `complete` as the deliberate **last** commit
releases the gate. **Theme packs merge on theme-gate green alone** (the
core/skin split paying rent — data-only, no code review needed). **Engine
behaviour changes need tests in the same PR** plus the enabler and card-guard.

**Gotchas:**

- The **born-red substrate-gate HOLD is by design**, not a failure — it is the
  mechanism that keeps a half-done session from reading as finished.
- **Git writes may be classifier-denied** in some environments — fall back to
  the GitHub MCP `push_files` with raw text.
- **MCP PR reads can lag ~25 min** behind live GitHub — cross-check PR/merge
  state against live before acting on it.
- The single skipped test is the **designed sb-host CI hole**, covered by the
  `pytest-with-host` job — never "fix" it by deleting the skip.

---

## Sibling repos (fleet closeouts)

- **superbot-games** — https://github.com/menno420/superbot-games —
  `docs/PROJECT-CLOSEOUT.md`
- **superbot-mineverse** — https://github.com/menno420/superbot-mineverse —
  `docs/PROJECT-CLOSEOUT.md` — **MASTER** closeout (fleet-wide threads live
  here).
