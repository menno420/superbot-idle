# 2026-07-11 — timed events scoping: piecewise-exact offline, data-only skins (plan, no code)

> **Status:** `in-progress`

- **📊 Model:** fable-5 · high · idle-engine seat (timed-events scoping worker, coordinator-assigned) · 2026-07-11T18:31Z– (`date -u`)

## What is happening

The QUEUE's "NEXT: timed events (data-only) scoping" slice: a design-only
doc (`docs/design/timed-events-scoping.md`, badge `plan`, NO engine code)
after a control fast-lane claim (PR #67,
`control/claims/timed-events-scoping.md`; removed in this PR's final
commit). Scope: how time-boxed events (festivals/bonuses) could work as
data-only theme content without breaking the deterministic
tick == closed-form-offline invariant — the hard problem stated first,
candidate solutions enumerated with exactness analysis, CORE/SKIN split,
determinism + save-format constraints, Discord render-budget fit, the
sim scenarios that must be pre-registered before any bonus tuning, and
an explicit not-building-yet statement with the gated build order.
