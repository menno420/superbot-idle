# 2026-07-13 — playability fixes (display/UX/new-entrypoint slice)

> **Status:** `complete`

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

**Reproduce-then-fix (driver against the real render layer):**

Fix #1 (`render_achievements`, egg-farm, lifetime 5,000 ≥ threshold 1,000, unawarded):
- BEFORE: `🔒 5,000 / 1,000` (lifetime-1), `🔒 3 / 1` (prestige-1) — past 100%, locked.
- AFTER:  `⏳ 1,000 / 1,000` (lifetime-1), `⏳ 1 / 1` (prestige-1) — ready glyph, capped.

Fix #2 (`render_shop`, royal-bakery, boost2 → tier2 with tier2 0-owned):
- BEFORE: `✅ Recipe mastery 0 → 1 · 300 🥐 pastries` — affordable, invites a wasted buy.
- AFTER:  `⚠️ Recipe mastery 0 → 1 · 300 🥐 pastries · requires 🧱 brick oven`.
- boost1 → tier1 (owned) stays `✅ Recipe mastery 0 → 1 · 60 🥐 pastries` (unannotated).

**Green gates:**
- `python3 -m pytest -q` → **1157 passed** (baseline 1131 + 7 render-playability
  + 19 play-entrypoint = 1157; 4 pre-existing render pins updated to the
  corrected strings).
- `python3 tools/theme_gate.py themes` → all **12 pack(s) valid (schema v1)**,
  unchanged (no theme file touched).
- `python3 bootstrap.py check --require-session-log --session-log <this card>`
  → complete (post-flip).
- `python3 tools/play.py --help` runs clean; `demo_step()` renders one
  tick+render without error.

**Economy safety:** zero economy constant changed — no cost curve, `base_rate`,
prestige threshold/award, offline factor, `PRESTIGE_BONUS_PERCENT`, or engine
rate floor. `idle_engine/economy.py`, `engine.py`, `upgrades.py`, `prestige.py`,
`achievements.py`, and every `themes/*.yaml` are untouched; the diff is
`render.py` (display), `tools/play.py` (new entrypoint), tests, and README.

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
