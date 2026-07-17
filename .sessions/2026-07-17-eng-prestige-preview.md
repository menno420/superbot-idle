# 2026-07-17 — engine: add pure prestige-preview helpers (ENG-9)

> **Status:** `complete`

- **📊 Model:** neutral builder-agent · high · feature build · idle-engine seat (prestige helpers) · 2026-07-17T23:03Z (`date -u`)

## What / why

The prestige view can show a player's held prestige currency and the reset
action, but never answers the question a player actually weighs before pulling
the lever — *how much would a reset pay out right now, and how long until the
payout ticks up again?* Today that means eyeballing lifetime totals against the
award curve by hand. The award mechanic (`prestige_award` —
`isqrt(lifetime // award_divisor)`) and the eligibility gate
(`prestige_eligible`) already exist; nothing exposes a read-only *preview* over
them.

This slice adds pure preview helpers to `idle_engine/prestige.py` (menu
**ENG-9**, under the owner's overnight full-autonomy order). They are read-only
over the EXISTING prestige model — no award formula changes, no tunable-number
changes:

- `prestige_award_if_reset(state, spec)` — the prestige currency a reset would
  bank right now. Delegates to `prestige_award` (the mechanic is not forked),
  giving the UI a discoverable *preview* verb distinct from the reset path.
- `seconds_to_prestige_eligible(state, spec, rate)` — whole seconds until this
  run's lifetime earnings reach the eligibility threshold at the current
  measured-currency production `rate`: `0` at/over the threshold, the `None`
  never-sentinel at `rate == 0` below it.
- `seconds_to_next_prestige_award(state, spec, rate)` — whole seconds until the
  award increments by one whole unit (lifetime reaching `(award+1)**2 *
  award_divisor`), same sentinel convention.

The two ETA helpers reuse the engine's affordability primitive
`time_to_afford` — its integer-exact ceil-division dual applied to a lifetime
target — so the previews inherit the engine's no-float, agrees-to-the-second
convention for free.

Engine-only this slice: the render prestige view does not currently compute
`production_per_second`, so surfacing an ETA line there would mean new spec
plumbing plus a change to a byte-budgeted, golden-pinned view — out of scope
and a risk to the render vectors. The helpers land pure and ready; wiring them
into `render_prestige` is a clean follow-up when that view already holds a rate.

## Verification

- `python3 -m pytest -q` — full sb-free suite (recorded in the flip commit).
- New `tests/test_prestige_preview.py`: award-now matches the real award path,
  monotonicity (waiting never decreases the previewed award), threshold
  boundary (→0 seconds), `rate == 0` below threshold (→None/never), and
  integer-exactness at big-int scale.
- `python3 bootstrap.py check --strict`.

## Landing (born-red convention)

Card born RED (`in-progress`) in the first commit alongside
`control/claims/claude-eng-prestige-preview.md`; then the helpers + tests; card
flipped `complete` as the last commit to clear the born-red HOLD so
substrate-gate goes green and the landing workflow can merge on all-green. PR
opened READY; the worker does not merge its own PR.

## 💡 Session idea

These preview helpers are the engine half of a prestige ETA line. The natural
next slice is the SKIN half: teach `render_prestige` to compute the measured
currency's rate (it already has the state and specs the status view uses) and
append an "award now: N · +1 in Ms" tail — behind the render budget with its
own golden vector, so the preview text is pinned the same way the rest of the
view is.

## ⟲ Previous-session review

The prior overnight slice (`engine: add time_to_afford() helper`, ENG-8, PR on
`claude/eng-time-to-afford`) added the affordability time dimension to the
shop-side surface. This slice is its prestige-side sibling: it reuses that very
`time_to_afford` primitive to answer the reset-timing question, and adds the
award-now preview over the existing prestige mechanic. Both keep the CORE/SKIN
wall intact — the helpers carry zero theme vocabulary — and both land born-red
under the same session-gate discipline.
