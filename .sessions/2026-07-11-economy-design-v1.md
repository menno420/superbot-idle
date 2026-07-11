# 2026-07-11 — slice (d): ECONOMY DESIGN v1 (pre-registered targets + sim request)

> **Status:** `in-progress`

- **📊 Model:** fable-5 · high · idle-engine seat (slice (d) builder, coordinator-assigned) · 2026-07-11T00:30Z– (`date -u`)

## Plan

1. Control fast-lane claim (`control/claims/economy-design-doc.md`) on main FIRST.
2. `docs/design/economy-v1.md` — pre-registered, falsifiable pacing targets
   (± bands), cost-curve design rationale vs those targets, PROVISIONAL
   declaration for all current `idle_engine/economy.py` parameters, and the
   executable SIMULATION REQUEST for the fleet Simulator (Q-0264) with
   acceptance criteria. Committed BEFORE any tuning — integrity floor.
3. Doc-honesty test: `tests/test_economy_design_doc.py` pins the doc's
   section-header contract (the sim-request headers the Simulator consumes).
4. Control fast-lane ⚑ SIM-001 append to `control/status.md` (separate
   control-only PR, after the build PR).
