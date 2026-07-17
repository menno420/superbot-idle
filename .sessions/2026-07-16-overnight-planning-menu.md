# 2026-07-16 — overnight planning menu: consolidated idea backlog

> **Status:** `in-progress`
> **Branch:** `claude/overnight-planning-menu` · overnight autonomous synthesis (owner authorized silence=consent)

- **📊 Model:** Opus 4.8 · autonomous project planning · synthesis — consolidate five domain idea-generator outputs into one ungroomed overnight planning menu for owner triage · session opened 2026-07-16T21:54Z (overnight run); synthesized 2026-07-17T09:23Z (`date -u`)

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

(in progress — filled at close-out flip)

## Verify

(filled at close-out flip)

## 💡 Session idea

The `docs/ideas/` conveyor has a strict per-idea outcome-record frontmatter
contract (`state`/`origin`/`shipped_pr`/`outcome`), which is the right home for
*groomed, individually-routed* ideas — but an ungroomed 89-item brainstorm menu
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
