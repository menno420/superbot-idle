# 2026-07-11 — render layer: pure embed-payload builder

> **Status:** `in-progress`

- **📊 Model:** fable-5 · high · idle-engine seat (render-layer builder, coordinator-assigned) · 2026-07-11T01:03Z– (`date -u`)

## Plan

Claimed via `control/claims/render-layer.md` (PR #18, control fast lane).
Build PR delivers, test-first:

1. `idle_engine/render.py` — pure, stdlib-only-at-runtime, zero
   chat-platform imports: status / upgrade-shop / prestige views as plain
   embed-shaped dicts. Every player-visible noun from the theme pack.
2. Hard budget enforcement (title 256 / field name 256 / field value 1024
   / description 4096 / 25 fields) via one validator; theme-sourced
   overflow raises, numeric overflow clamps with ellipsis.
3. `tests/test_render.py` — per-view noun resolution on egg-farm,
   determinism, extreme-value budget safety; core/skin guard covers
   render.py automatically (glob).
4. `docs/render-layer.md` + orientation cross-link — the plugin contract.

Schema-slot decision: NO schema/themes edits this slice (concurrent
workers own themes/, schema/, tools/theme_gate.py) — neutral scaffolding
labels only, optional labeled slots parked as a follow-up.

## 💡 Session idea

(placeholder — filled at close)

## ⟲ Previous-session review

(placeholder — filled at close)
