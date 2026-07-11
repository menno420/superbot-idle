# 2026-07-11 — timed events scoping: piecewise-exact offline, data-only skins (plan, no code)

> **Status:** `complete`

- **📊 Model:** fable-5 · high · idle-engine seat (timed-events scoping worker, coordinator-assigned) · 2026-07-11T18:31Z–18:4xZ (`date -u`)

## What happened

Shipped the QUEUE's "NEXT: timed events (data-only) scoping" slice: a
design-only doc, NO engine code, after a control fast-lane claim (PR #67,
`control/claims/timed-events-scoping.md`, auto-merge armed at creation,
merged 18:32:20Z; claim removed in this PR's final commit).

1. **`docs/design/timed-events-scoping.md`** (badge `plan`) — the hard
   problem stated FIRST: timed events are rate changes at wall-time
   boundaries with nobody present, which breaks the closed-form offline
   uniformity assumption ("rate is constant over an unpunctuated span").
   Three candidates analyzed for exactness: (a) **piecewise offline
   integration over event boundaries** — rate generalized to a
   piecewise-constant step function of absolute unix time, exact by the
   same argument as today (both paths evaluate the same step function;
   today's invariant is the zero-boundary special case), segment count
   bounded ≤ 2K+1 (~105 segments for a YEAR offline on a weekly calendar)
   — **RECOMMENDED**; (b) online-only bonuses — rejected (forks the
   invariant per caller identity, rewards no-life play against T5/T7's
   registered feel); (c) side-pool event currency — deferred (relocates
   the piecewise problem or dodges it into check-in grants, adds save
   state + a sink first). Plus: CORE/SKIN ownership (calendar/bonus/caps
   engine-side pre-registered; nouns theme-side via a milestone-style
   engine-derived slot set; clause 4 stated plainly — a theme can NEVER
   declare windows or bonuses); determinism constraints (schedules as
   data — absolute UTC windows or integer-arithmetic recurrence, UTC
   only, randomness structurally excluded; v0 shape needs NO new save
   state — caps/claims/history are the v3 trigger, governed by the
   golden-corpus same-PR policy); Discord surface inside the existing
   two-tier budget policy (clamping status-description line +
   labels-pattern `event_active` template with the `{gains}`-style
   exactly-once token check); SIM-002 scenario sketches SE-1..SE-5 to
   register BEFORE any bonus value — incl. SE-4's A10 interaction (an
   event multiplier amplifies reset spam exactly where the provisional
   run's ~80,796-resets auxiliary signal already awaits a Q-0264 ruling;
   isqrt dampens awards to ~sqrt(bonus) but reset FREQUENCY scales with
   rate directly); explicit NOT-BUILDING-YET statement + the ordered
   build plan (schema slot → engine piecewise fold → render → packs →
   values), each step naming its gate.
2. **`docs/AGENT_ORIENTATION.md`** — doc cross-linked from § Lane-layer
   docs (read-path reachable, no strict-check orphan).

No engine, schema, theme, or tool files touched — design only, per the
slice contract. Every number deliberately UNREGISTERED: a build slice
citing this doc still owes its own pre-registration.

Verify: `python3 -m pytest -q` → 1131 passed; `python3 bootstrap.py
check --strict` green after this flip.

## 💡 Session idea

The piecewise-fold slice, when green-lit, should land the shared
span-segmenting function as the ONLY caller-visible change to both
progress paths (`tick` and `offline_progress` both calling one
`segments(last_seen, now, calendar)` helper), with a property test that
the zero-boundary calendar reproduces today's trajectories
byte-for-byte across the whole golden corpus — that single test turns
the § 1(a) "special case" claim from prose into a pin before any
non-neutral window exists. Guard recipe: helper in
`idle_engine/engine.py` beside `production_per_second`, pin in
`tests/test_properties.py` against `tests/vectors/saves.v2.json`
trajectories.

## ⟲ Previous-session review

The golden-save-corpus card (2026-07-11-golden-save-corpus.md) fed this
slice twice: its binding "any state_version bump MUST extend the corpus
in the same PR" policy is exactly what § 3 leans on to price event
caps honestly (v3 trigger, not a footnote), and its `_FROZEN_FIELDS`
💡 is cited as the companion hardening for that future bump. Its
gitattributes prediction held again — `.substrate/guard-fires.jsonl`
picked up appends from this session's verify runs and rode the rebase
with zero content conflicts (one mechanical stash/pop around
`git rebase`, nothing hand-resolved). One friction its card didn't
warn about: `bootstrap.py check --strict` exits 1 on a born-red card
mid-session (missing enders), so the mid-build verify is expected-red
on that single line until the flip — worth one clarifying word in
`.sessions/README.md` some grooming pass.
