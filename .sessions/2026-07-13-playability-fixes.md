# 2026-07-13 — playability fixes (display/UX/new-entrypoint slice)

> **Status:** `in-progress`

- **📊 Model:** opus-4.8 · high · feature build · 2026-07-13 · display/render/entrypoint only (NO economy tuning)

## What this session is doing

An ENGINE-SAFE playability slice off the end-to-end player review
(`scratchpad/idle-player-review.md`, rough-edge inventory #3/#5/#11). Three
fixes that make idle *read* and *play* like a finished game, with ZERO economy
tuning: no cost curve, no `base_rate`, no prestige threshold/award, no offline
factor, no `PRESTIGE_BONUS_PERCENT`, no engine rate floor touched. Display /
render / new-file only.

1. **Reached-but-locked milestone display** (`idle_engine/render.py`
   `render_achievements`, ~L377-381). A milestone whose live progress already
   meets its threshold but has not yet been awarded rendered as
   `🔒 5,000 / 1,000` — past 100%, still locked, which reads as a bug.
   Display-only fix: when reached-but-unearned, cap the shown numerator at the
   threshold and use a distinct "ready" glyph (⏳) instead of 🔒. The runtime
   awarding path (`award_milestones`) is untouched — WHEN a milestone is earned
   is unchanged; only how a ready-to-claim one looks.
2. **Trap-buy guard** (`idle_engine/render.py` `render_shop`, ~L282-308). An
   upgrade whose target generator is 0-owned (e.g. `boost2` → `tier2`, never
   ownable at base seed) rendered a normal affordable ✅ line — spending
   currency for zero observable effect. Display-only fix: when the target is
   0-owned, mark the row unavailable and annotate `requires <generator>`.
   Purchase logic and costs are untouched (render/annotation only — the
   annotation cannot itself prevent the spend, which is acceptable per the
   task's "prefer render annotation" call).
3. **Playable entrypoint** (`tools/play.py`, NEW FILE). A real text loop: seed
   a `GameState` from a theme pack (+ optional setup code), then a REPL that
   ticks wall time and accepts `status / shop / buy <id> / prestige /
   offline <seconds> / pack <id> / help / quit`, rendering through the existing
   `render_*` functions. Zero engine change; import-safe under
   `if __name__ == "__main__"`.

## Verify

_(filled at close-out — reproduce-then-fix strings, full pytest, theme_gate,
bootstrap --require-session-log, play.py smoke.)_

## 💡 Session idea

The review's headline gap is structural (no generator purchase verb — a real
economy-number change, out of scope here). The cheap, honest win adjacent to it
is *legibility*: two of the three fixes cost nothing mechanically yet remove the
two displays a fresh player most reliably misreads as broken (past-100% lock,
and a green "buy me" on an inert upgrade). Guard recipe for the next session
that DOES add the generator economy: the trap-buy annotation in `render_shop`
(target-0-owned branch) is the natural place to *also* surface "buy a
<generator> first" once buying generators exists — keep the annotation string
and the future purchase CTA co-located so they can't drift.

## ⟲ Previous-session review

The `2026-07-12-install-auto-merge-enabler` session (fable-5, ORDER 029)
installed `.github/workflows/auto-merge-enabler.yml` but left it correctly INERT
— main has zero required status-check contexts, so the enabler refuses to arm
until the owner wires `pytest` + `substrate-gate` as required checks. That is
exactly the landing surface this session's PR parks against: this PR is left
READY + green, NOT armed, so it rides the same owner clickset that unparks
#75/#76. One thing that session did well and this one copies: it shipped the
repo-settings ask paste-ready in its PR body rather than as a follow-up. Carried
forward: this session keeps its economy-safety claim explicit and paste-checkable
in the PR body so a reviewer can confirm "no economy number moved" without
diffing every file.
