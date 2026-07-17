# 2026-07-17 — tests: cover render.py offline-gain drop branch (240->243)

> **Status:** `complete`

- **📊 Model:** neutral builder-agent · high · test writing · render-layer seat (offline-gain drop) · 2026-07-17T23:19Z (`date -u`)

## What / why

`idle_engine/render.py` is the pure render layer that turns engine state + a
theme pack into embed-shaped payloads. End-to-end branch coverage measured it at
**99%** with a single uncovered partial branch: `240->243` — the neutral
(no themed `offline_return` label) offline-return path where, after the offline
gains are formatted, the byte budget is checked:

```python
room = DESCRIPTION_LIMIT - len(description) - 2
if room >= 1:
    description = description + "\n\n" + _clamp(gains_text, room)
```

The uncovered edge is the FALSE arm (`room < 1`): when the theme's own
`description` sits at or near the 4096-char cap, there is no room to append the
offline-earnings line, so it is dropped. No existing test forces the near-full
description on the neutral path, so whether that drop is intentional
budget-trimming or a silent swallow of player-visible earnings was unverified.

This slice (menu **TEST**, under the owner's overnight full-autonomy order)
closes that gap with a **test-only** case that saturates the description budget
(`room == 0`) with a labels-less pack and a state that DOES accrue offline gains,
then asserts the documented behavior: the flavor line is omitted and the rest of
the payload stays valid within budget.

**By-design verdict.** The drop is intentional budget protection, not a bug: the
module docstring is explicit that offline production is DISPLAYED, never credited
(crediting is `engine.apply_offline_progress`), so dropping the flavor line loses
no player money — the earnings are still credited by the engine and current
balances still render in the payload fields. The sibling test
`test_offline_template_that_cannot_fit_raises` already documents the same edge
from the themed side, noting "the neutral path would just skip the line." This
test pins that skip.

**No product code changes** — `render.py` behavior is untouched; this slice only
drives the existing near-full path that was previously exercised only in theory.

## Verification

- `python3 -m pytest -q` — full suite, green.
- New case forces `room == 0` (description length 4094: `4096 - 4094 - 2`) on the
  labels-less neutral path with a state that accrues offline gains, and asserts
  the offline line is dropped (`description == theme.description`), the payload
  stays within the 4096 cap, and the fields still render. A companion assertion
  shows the SAME state DOES surface the offline line under a short description —
  proving the drop is the near-full path, not a no-gain case.
- `python3 -m coverage run --branch --source=idle_engine.render` shows
  `render.py` rising from 99% (branch `240->243`) to 100%.
- `python3 bootstrap.py check --strict` (only the born-red HOLD expected).

## Landing (born-red convention)

Card born RED (`in-progress`) in the first commit alongside
`control/claims/claude-test-render-offline-dropline.md`; then the test; card
flipped `complete` as the last commit to clear the born-red HOLD so
substrate-gate goes green and the landing workflow can merge on all-green. PR
opened READY; the worker does not merge its own PR.

## 💡 Session idea

The render layer's budget arithmetic is now fully branch-covered. A natural
follow-up is a property-style test that sweeps description lengths across the
`room` boundary (4093 → 4096) and asserts monotonic behavior: the offline line
appears until room drops below 1, then vanishes, with the payload never
exceeding the 4096 cap at any point — a tripwire on the budget edge itself.

## ⟲ Previous-session review

The prior overnight slices hardened the manual-verify entrypoint (`tools/play.py`
`main()` REPL, TEST-11) and grew the engine surface (prestige-preview, ENG-9).
This slice is the render-side sibling: instead of a helper or a loop it pins a
budget-boundary drop in the pure presentation layer, closing the last branch gap
end-to-end review flagged in `render.py`. It keeps the same born-red session-gate
discipline (card red until the final flip) and the same no-economy-pinning test
convention — stable structural assertions, never brittle economy numbers.
