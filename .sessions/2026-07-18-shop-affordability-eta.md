# 2026-07-18 — render: surface time_to_afford ETA in the shop view (ENG-8)

> **Status:** `in-progress`

- **📊 Model:** neutral builder-agent · high · player-facing feature · shop-affordability seat · 2026-07-18T00:18Z (`date -u`)

## What / why

PR #151 shipped the pure `time_to_afford(cost, balance, rate)` helper
(`idle_engine/upgrades.py`) — whole seconds until a balance grows to a cost at
a given per-second rate, with `0` = affordable now and `None` = never (rate 0
and short). It deliberately did NOT surface the helper anywhere player-facing:
`render_shop` did not compute each generator's per-second production rate, and
the shop cost line was byte-budgeted and golden-pinned, so wiring an ETA in was
deferred until a render golden corpus existed.

That corpus now exists (`tests/vectors/render-embeds.v1.json`, TEST-2 / #157),
so a shop-render change is safe: regenerate the corpus and the embed diff is
explicitly reviewable. This slice (menu **ENG-8**, under the owner's overnight
full-autonomy order) surfaces the ETA in the shop view so a player reads WHEN
they can afford each upgrade instead of doing the arithmetic by hand.

**CONTAINED render-layer change** — no engine, mechanic, id, currency, or
shop-spec-shape change. `render_shop` gains a per-currency rate lookup by
reusing the already-imported `production_per_second` (the same rate the status
view shows) and calls the existing pure `time_to_afford` helper. Each
unaffordable upgrade's cost line gains a short ETA fragment; affordable ones
read "affordable now". The fragment rides the cost line's existing numeric-tier
clamp, so it can never bust the field-value budget. The render golden corpus is
regenerated via its blessed generator `tools/gen_render_vectors.py` as an
intentional, expected corpus change. Fully reversible.

## Verification

- `python3 -m pytest -q` — full suite green, including the render drift test
  against the regenerated corpus and the shop budget tests.
- `python3 tools/theme_gate.py themes` — passes.
- `python3 bootstrap.py check --strict` — only the born-red HOLD expected.

## Landing (born-red convention)

Card born RED (`in-progress`) in the first commit alongside
`control/claims/claude-shop-affordability-eta.md`; then the render + regenerated
corpus + test commit; card flipped `complete` as the last commit to clear the
born-red HOLD so substrate-gate goes green and the landing workflow can merge on
all-green. PR opened READY; the worker does not merge its own PR.
