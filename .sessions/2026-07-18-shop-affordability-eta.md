# 2026-07-18 — render: surface time_to_afford ETA in the shop view (ENG-8)

> **Status:** `complete`

- **📊 Model:** neutral builder-agent · high · feature build · shop-affordability seat · 2026-07-18T00:18Z (`date -u`)

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
all-green. PR opened READY (#160); the worker does not merge its own PR.

## Result

`render_shop` now surfaces the ENG-8 `time_to_afford` helper that #151 shipped
but left invisible. The change is fully contained to `idle_engine/render.py`:
the shop loop computes the same per-currency `production_per_second` rates the
status view already shows (reusing the one rate seam — no forked formula), and
each non-trap upgrade's cost line gains a short affordability fragment read off
the pure helper — `0 → · affordable now`, a positive shortfall → `· buy in Ns`,
and the never sentinel (rate 0 while still short) → nothing, since 🔒 already
reads "locked". Trap-buys (0-owned target) keep their `· requires X` annotation
and show no ETA, so the shop never invites a wasted buy with a countdown.

Before → after (egg-farm, affordable):

    ✅ Coop size 0 → 1 · 60 🥚 eggs
    ✅ Coop size 0 → 1 · 60 🥚 eggs · affordable now

The fragment appends to the numeric-tier cost line, which already clamps into
its budgeted room, so it can never bust the 1024-char field-value cap — no
budget-arithmetic change needed. `tests/vectors/render-embeds.v1.json` was
regenerated via `tools/gen_render_vectors.py` as an intentional delta: the diff
is exactly the ETA additions (19 packs, one affordable line each), nothing else.

Verification: `python3 -m pytest -q` green (1527 passed, 1 skipped) including the
render drift test against the regenerated corpus and the shop budget tests;
`python3 tools/theme_gate.py themes` PASS (19/19); `python3 bootstrap.py check
--strict` showed only the expected born-red HOLD. Two pinned exact-byte shop
assertions in `tests/test_render.py`, one bare-line assertion, and one live-buy
assertion in `tests/test_render_playability.py` were updated to the new ETA-
carrying line, and a dedicated `test_shop_affordability_eta_reads_off_time_to_afford`
pins the "affordable now" / "buy in Ns" / trap-buy-shows-no-ETA branches.

## 💡 Session idea

The ETA reads off the current instantaneous rate, which ignores the compounding
a player gets by buying cheaper upgrades first — the displayed "buy in Ns" is an
upper bound, not the true optimal-path time. A follow-up could annotate the ETA
as a ceiling (or compute a greedy buy-order-aware estimate) so the shop's
countdown matches how an optimizing player actually reaches the purchase.

## ⟲ Previous-session review

The immediately prior slices leaned on the render golden corpus
(`test-render-golden-corpus`, TEST-2, #157) to make player-facing render changes
self-documenting — the flavor-depth (#159) and color-distinctness (#158) slices
each regenerated the corpus as an intentional, reviewed delta. This slice is the
first to change rendered *structure* (a new cost-line fragment) rather than pack
*data* against that corpus, and the same discipline held: the drift test reds
until the corpus is regenerated, so the added ETA is an explicit, reviewed diff
rather than a silent shift. It also completes the arc TEST-2 was partly built to
unblock — #151 deferred surfacing `time_to_afford` precisely because no render
corpus existed to make a shop-line change safely reviewable; now it does.
