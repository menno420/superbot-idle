# 2026-07-11 — achievements layer: threshold milestones with pre-registered bonuses

> **Status:** `in-progress`

- **📊 Model:** fable-5 · high · idle-engine seat (achievements-layer builder, coordinator-assigned) · 2026-07-11T17:27Z– (`date -u`)

## What happened

(born-red — close-out written at session end)

Plan: claim landed first (`control/claims/achievements-layer.md`, control
fast-lane PR #53), then one build PR, TEST-FIRST:

1. `idle_engine/achievements.py` — MilestoneSpec + earned-set semantics,
   awarding as an explicit action-boundary step so tick == closed-form
   offline stays EXACT.
2. Pre-registered thresholds/bonuses in `idle_engine/economy.py`,
   rationale in `docs/design/achievements-v0.md` (PROVISIONAL pending
   Simulator).
3. `state_version` 2 + v1→v2 migration in the SAME PR
   (docs/persistence.md policy — first real migration).
4. Schema v1 additive optional `milestones` noun block (md+json parity),
   filled in egg-farm + space-colony + potion-brewery; gate semantic
   checks.
5. `render_achievements` view with byte-pinned neutral fallback.

## 💡 Session idea

(at close-out)

## ⟲ Previous-session review

(at close-out)
