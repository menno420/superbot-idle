# 2026-07-17 — engine: add a pure `time_to_afford()` affordability-ETA helper (ENG-8)

> **Status:** `in-progress`

- **📊 Model:** neutral builder-agent · high · engine · idle-engine seat (economy helpers) · 2026-07-17T22:55Z (`date -u`)

## What / why

The shop view shows an upgrade's cost and the player's income rate, but never
answers the question a player actually asks — *when* can I afford this? The
engine has the dual already (`max_affordable_levels` — "how many can I buy with
budget X now"), but nothing computes the seconds-to-afford the next purchase.

This slice adds a pure `time_to_afford(cost, balance, rate)` to
`idle_engine/upgrades.py` (menu **ENG-8**, under the owner's overnight
full-autonomy order). It computes the whole seconds until `balance` grows to
`cost` at `rate` units/second: `0` when already affordable, the "never"
sentinel `None` when nothing is produced (`rate == 0`) and not yet affordable,
otherwise exact integer ceil-division of the shortfall — big-int arithmetic,
single floor, no float, so every platform agrees to the second (the engine's
integer-exact convention). Exported from `idle_engine.__init__` next to its
dual `max_affordable_levels`.

Engine-only this slice: the render shop does not currently compute
`production_per_second`, so surfacing an ETA line there would mean new spec
plumbing plus a change to the byte-budgeted, golden-pinned cost line — out of
scope and a risk to the render vectors. The helper is landed pure and ready;
wiring it into `render_shop` is a clean follow-up when the shop view already
holds a rate.

## Verification

- `python3 -m pytest -q` — full sb-free suite (recorded in the flip commit).
- New `tests/test_time_to_afford.py`: already-affordable (→0), exact boundary,
  ceil rounds up, `rate == 0` not-affordable (→None/never), and
  integer-exactness (no float leakage), plus the input guards.
- `python3 bootstrap.py check --strict`.

## Landing (born-red convention)

Card born RED (`in-progress`) in the first commit alongside
`control/claims/claude-eng-time-to-afford.md`; then the helper + tests; card
flipped `complete` as the last commit to clear the born-red HOLD so
substrate-gate goes green and the landing workflow can merge on all-green. PR
opened READY; the worker does not merge its own PR.

## 💡 Session idea

`time_to_afford` is the engine half of a shop ETA. The natural next slice is the
SKIN half: teach `render_shop` to compute the cost-currency rate (it already has
the state and specs the status view uses) and append an "affordable in Ns /
affordable now" tail to the cost line — behind the render budget with its own
golden vector, so the ETA text is pinned the same way the cost line is.
