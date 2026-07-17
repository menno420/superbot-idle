# 2026-07-16 — overnight planning menu: consolidated idea backlog

> **Status:** `complete`
> **Branch:** `claude/overnight-planning-menu` · overnight autonomous synthesis (owner authorized silence=consent)

- **📊 Model:** Opus 4.8 · high · idea/planning — autonomous overnight synthesis of five domain idea-generator outputs into one ungroomed consolidated planning menu for owner triage · session opened 2026-07-16T21:54Z (overnight run); synthesized 2026-07-17T09:23Z (`date -u`)

**Goal:** Five READ-ONLY domain idea-generators (engine/gameplay, theme packs/content,
tooling/DX/CI, testing/quality/sim, plugin/records/process) produced ~94 grounded
proposals overnight. Synthesize them into ONE consolidated menu document —
dedup/merge genuine cross-domain overlaps, preserve every distinct proposal
(~80-90), group by the five domains, and frame it clearly as an UNGROOMED
overnight brainstorm the owner triages tomorrow. Planning docs ONLY — build
nothing, and do NOT overwrite `control/status.md` (read-only ARCHIVE).

**Baseline at HEAD `25d34f1` (before edits):**
`python3 bootstrap.py --version` → `substrate-kit 1.16.0`;
`python3 -m pytest -q` → `1381 passed, 1 skipped`.

## What happened

Read all five overnight domain idea-generator raw outputs verbatim (their final
reports, extracted from the JSONL transcripts). Ran the collision guard first:
`git fetch origin main`, read every `control/claims/` file (3 unrelated: eap-ack,
reconcile-race-fix, truth-refresh — backing work already merged), and listed open
PRs — the sibling test-coverage PR (#146, `claude/idle-test-coverage`) merged and
the draft #145 closed, leaving the clone free; no planning-menu work in flight.
Confirmed `docs/ideas/README.md` binds every file there to a per-idea
outcome-record frontmatter contract, which a flat 91-item menu does not fit, so
the menu landed under `planning/` per the task's fallback rule.

Synthesized **96 raw proposals** (18 engine · 20 theme · 20 tooling · 16 testing ·
22 plugin) into **91 distinct** by folding four cross-domain overlaps: coverage
instrumentation (TOOL-1, from two tooling items + one testing item), the
determinism/golden-corpus guard (TEST-13), claims-lifecycle hygiene (PLG-D4), and
telemetry outcome-backfill (PLG-E3). Grouped by the five domains, each proposal
keeping Title · Pitch · Effort · Risk & reversibility · Unblocks and the
generators' file/line citations. Added a Blockers section (owner-only OA-003;
host-only manifest/pin items; verdict-blocked economy numbers — feltness,
PRESTIGE 10→25, generator-purchase tuning, timed-events; the no-hypothesis policy
decision; and the live status.md kit-version drift flagged NOT-fixed) and an
honest low-risk shortlist.

All work done in an isolated git worktree off `origin/main` (a sibling git worker
shares this clone); `control/status.md` was NOT touched (read-only archive).

## Verify

- `python3 bootstrap.py check --strict` → pre-flip EXIT=1 red ONLY on this card's
  designed born-red HOLD (in-progress Status); no docs-gate finding on the
  `planning/` menu doc; the 4 `model-line-class` advisories are pre-existing on
  older 2026-07-14 cards (never exit-affecting, untouched scope). EXIT=0 after this
  close-out flip to `complete`.
- `python3 -m pytest -q` → `1381 passed, 1 skipped` (planning-docs-only change; no
  code touched).
- `python3 tools/theme_gate.py themes` → all 18 packs valid (no theme files changed).

## 💡 Session idea

The `docs/ideas/` conveyor has a strict per-idea outcome-record frontmatter
contract (`state`/`origin`/`shipped_pr`/`outcome`), which is the right home for
*groomed, individually-routed* ideas — but an ungroomed 91-item brainstorm menu
is a poor fit there (one file, not one-record-per-idea). This session landed the
menu under `planning/` instead. Follow-up worth considering: once the owner
triages the menu, promote the survivors into `docs/ideas/<slug>-YYYY-MM-DD.md`
files with proper frontmatter — turning the flat menu into the conveyor the
lifecycle was built for (this is proposal PLG-C1 on the menu itself).

## ⟲ Previous-session review

previous-session review: `.sessions/2026-07-15-truth-refresh.md` (PR #141) —
its verify block (`1381 passed, 1 skipped`; born-red hold as the only pre-flip
red) reproduced exactly this session's baseline at HEAD `25d34f1`. Its Lane-owed
note — the `control/status.md` line-5 `kit: v1.15.0` heartbeat debt still
outstanding vs the measured v1.16.0 — is CONFIRMED still live at `25d34f1` and
is surfaced (not fixed) in this menu's Blockers section, since status.md is a
read-only archive this session must not overwrite.
