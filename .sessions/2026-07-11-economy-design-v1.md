# 2026-07-11 — slice (d): ECONOMY DESIGN v1 (pre-registered targets + sim request)

> **Status:** `complete`

- **📊 Model:** fable-5 · high · idle-engine seat (slice (d) builder, coordinator-assigned) · 2026-07-11T00:30Z–00:4xZ (`date -u`)

## What happened

Shipped the ECONOMY DESIGN pre-registration BEFORE any tuning (integrity
floor), after a control fast-lane claim (PR #9,
`control/claims/economy-design-doc.md`, merged then removed here).

1. **`docs/design/economy-v1.md`** — the binding targets + provisional
   numbers contract:
   - **Pacing targets T1–T10**, each a falsifiable number ± acceptance band:
     time-to-first-upgrade (60 s, 30–180 s), first-prestige for optimal /
     idle-only / 2-h-check-in play (4 h / 24 h / 6 h with bands), active-vs-
     idle advantage ratio (7×, 4–12×), offline-return payoff (≥ 2 levels per
     pre-prestige visit), no-dead-zone stall cap (max purchase gap < 25% of
     run), reset 2–3 cadence (50–100% of prior), and T10 pre-registered
     AHEAD of the future generator-tier mechanic.
   - **Cost-curve rationale vs those targets**: why geometric ×1.15 against
     additive +25%/level (constant marginal value vs growing marginal cost =
     smooth wall, no cliff), isqrt prestige award (reset-and-regrow beats
     grinding), plus explicit "too fast" / "too slow" definitions.
   - **PROVISIONAL declaration**: all seven `idle_engine/economy.py`
     constants tabled as provisional; no tuning until SIM-001 lands; themes
     carry zero economy numbers.
   - **SIM-001 request (Q-0264)**: scenarios (idle-only; check-in N ∈
     {0.25, 2, 8, 24} h greedy; optimal 1-s speedrun; 3+ resets; 14-day
     horizon), inputs (drive the REAL engine functions at the pinned
     commit — deterministic, integer-exact, no reimplementation), outputs
     O1–O6, acceptance criteria A1–A10 each tied to a target, and verdict
     semantics (all-pass → provisional graduates sim-pinned; any-fail →
     re-register new values here before tuning).
2. **Doc-honesty tests** — `tests/test_economy_design_doc.py` (3 tests, md-
   parity pattern from `test_theme_schema.py`): sim-contract headers pinned,
   parameter-table values regex-matched against the LIVE
   `idle_engine.economy` constants (tune without re-registering = red), and
   T1–T10 / A1–A10 completeness.
3. **Targets were sanity-grounded, not guessed**: throwaway sims against the
   real engine (not committed) measured current params at first-upgrade 60 s,
   optimal prestige 3.49 h, idle-only 27.8 h, 2-h check-in 6 h, max stall gap
   9.7% of run, every pre-prestige visit affording ≥ 6 levels — all inside
   the registered bands, so SIM-001 is a real referendum, not a rigged one.
4. **⚑ SIM-001 to manager**: appended to `control/status.md` as a separate
   control fast-lane PR right after this one (control-only diffs stay out of
   build PRs).

Verify: `python3 -m pytest -q` → 79 passed; `python3 bootstrap.py check
--strict` green.

## 💡 Session idea

The throwaway pacing sim in this session (greedy player loop over
`tick`/`purchase_upgrade`) is ~30 lines and was rewritten twice from scratch
(and got `tick`'s `dt`-not-absolute-time contract wrong once). Guard recipe:
when SIM-001 results come back, commit the scenario driver as
`tools/pacing_sim.py` with a smoke test in `tests/` asserting scenario S1's
closed-form time (`PRESTIGE_THRESHOLD / base_rate` seconds) — the Simulator's
scripts and this repo's local re-checks should share one committed driver
instead of each session re-deriving it.

## ⟲ Previous-session review

Slice (b)'s card (2026-07-11-upgrades-prestige.md) promised this slice a
pre-registration home and listed three things the Simulator must pin — all
three are now formal SIM-001 criteria (pacing → A1–A5, dead zone → A8,
prestige stacking → A9/A10). Its 💡 (memoized rate table for the bot loop)
remains correctly parked for the plugin-runtime slice — nothing here touched
the hot path. The legacy theme-side `base_rate` (flagged by both prior
cards) is now explicitly scheduled in economy-v1.md's provisional section;
still theme-side today, bounded 1–1000.
