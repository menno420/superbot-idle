# Timed events scoping — piecewise-exact offline, data-only skins

> **Status:** `plan` — scoping only, written 2026-07-11. **No engine code
> exists and none ships from this doc alone**: every mechanism below is a
> candidate design with its exactness analysis, and every number is
> deliberately UNREGISTERED (§ Not building yet). A build slice that
> implements any part of this doc must first re-register its shapes and
> parameters per the integrity floor (README § Integrity floor), exactly as
> [`upgrades-prestige-v0.md`](upgrades-prestige-v0.md) /
> [`economy-v1.md`](economy-v1.md) did for the base economy.

Time-boxed events — a festival weekend, a bonus window, a seasonal
celebration — are the genre's standard re-engagement lever. This doc scopes
how they could exist in THIS engine without breaking the two things this
repo exists to protect: the deterministic tick == closed-form-offline
invariant, and the CORE/SKIN split (events must be **data-only theme
content** on the noun side, identical mechanics on every server).

## 1. The hard problem, stated first

The engine's core invariant (docstring of
[`idle_engine/engine.py`](../../idle_engine/engine.py), pinned by
`tests/test_properties.py`) is:

> All arithmetic is integer arithmetic, so a single closed-form offline
> calculation equals the sum of any number of smaller ticks covering the
> same span.

That equality holds because the production rate is **constant over any span
the runtime has not punctuated with an explicit action**: the closed form is
literally `rate × elapsed`. Every multiplier shipped so far (upgrades,
prestige, milestones, theme balance) preserves this by changing the rate
only at ACTION boundaries — a purchase, a reset, an `award_milestones` call
— never inside a span.

A timed event is, by definition, a rate change that happens at a **wall-time
boundary with nobody present**. A player who goes offline Friday night and
returns Monday morning slept through the whole Saturday–Sunday festival:

- `rate × elapsed` with the *weekday* rate under-credits the festival hours;
- `rate × elapsed` with the *festival* rate (rate sampled at return time,
  mid-Monday… or worse, at a return timed inside the window) over-credits
  the weekday hours — and makes credited output depend on WHEN you check in,
  not just how long you were gone;
- either way, one closed-form multiply no longer equals the 1-second tick
  loop, and the property suite that pins the invariant goes red — or worse,
  gets weakened to accommodate the bug.

So the uniformity assumption ("rate is constant over an unpunctuated span")
is exactly what timed events break. Any design that ships events must say
where that assumption goes. Three candidate answers:

### Candidate (a) — piecewise offline integration over event boundaries

Generalize the rate from a constant to a **piecewise-constant step function
of absolute unix time**, with discontinuities only at data-declared event
boundaries. Offline credit over `[last_seen, now)` becomes a sum over
segments:

```
credit = Σ over segments [a, b) of  rate_during(a) × (b − a)
```

where the segment cuts are the event starts/ends inside the span, and
`rate_during` is the existing single-floor integer rate with one extra
`event_pct` factor (see § 2 for the fold).

**Exactness analysis — exact, by the same argument as today.** Within each
segment the rate is a constant integer, so segment credit is exact; the
1-second tick loop crossing a boundary switches to the new rate at exactly
the boundary second, because both paths evaluate the SAME step function of
absolute time (`tick` already knows absolute time — it advances
`state.last_seen`, which is unix seconds). Partition-equivalence
generalizes: any partition of the span into ticks yields the same total,
because every path is summing the same per-second step function. The
current invariant becomes a special case (zero boundaries in the span ⇒ one
segment ⇒ today's single multiply, byte-identical).

**Cost analysis — bounded segment count, small.** The number of segments is
`≤ 2K + 1` for `K` event windows overlapping the span. With any sane
pre-registered calendar (say, one weekend window per week), a player
offline a full YEAR produces ~105 segments — trivially cheap, and the bound
is enumerable up front from the schedule data, so a hostile/degenerate
schedule is a data-validation failure, not a runtime surprise. The sim
harness's exact event-scheduling trick ("jump to the next action moment")
survives with one amendment: the next jump target is
`min(next_action_time, next_event_boundary)`.

**Blast radius — the production fold and both progress paths.** `tick` and
`offline_progress` must both become boundary-aware (they must split spans
identically — best done by ONE shared segmenting function both call), and
`production_per_second` grows a seventh factor. The property suite grows
boundary-crossing cases. No new save state in the v0 shape (§ 3).

### Candidate (b) — events apply to online ticks only

Keep `offline_progress` untouched; fold the event bonus only into ticks the
runtime performs while a player is "present".

**Exactness analysis — exact only by forking the invariant.** The engine
has NO online/offline concept — `tick` and `offline_progress` are two
spellings of the same math, and that sameness IS the tested invariant. To
make (b) coherent, the equality test would have to be conditioned on caller
identity ("offline equals looped ticks *except when the runtime decided a
human was watching*"), which demotes the invariant from an algebraic
property to a policy. Every future property test, golden trajectory, and
sim run would need an online/offline annotation to be meaningful.

**Design analysis — rewards no-life play, punishes the genre's promise.**
The economy's registered feel is explicit: "coming back must feel like
opening a present, never like being punished for leaving"
([`economy-v1.md`](economy-v1.md) § session-length intent, targets T5/T7).
An event that only pays while you actively watch inverts that — the
festival becomes a screen-time tax, and the T4/T6 idle-vs-active ratios
silently change during every window. Simple to build, wrong for this
game. **Rejected.**

### Candidate (c) — event currency earned separately (side pool)

Leave the main production loop untouched; events grant a separate
event-scoped currency into a side pool, spent in an event shop or converted
at event end.

**Exactness analysis — exact, but only by relocating or dodging the
problem.** Two sub-shapes:

- *(c1) time-accrual side pool*: the event currency accrues per second
  during the window — which is the SAME piecewise-over-wall-time problem as
  (a), now duplicated in a second accrual path, PLUS a new balance that
  must persist (save-format bump) PLUS a sink (an event shop is a whole new
  pre-registered mechanic surface). Strictly more scope than (a) for less
  coherence.
- *(c2) action-boundary grant*: checking in during the window grants a flat
  bonus — exact trivially (it is an action, like `award_milestones`), but a
  repeatable grant incentivizes check-in spam, and a once-per-event grant
  needs per-event participation state (save-format bump) — and a flat
  drop is the least "idle" event shape there is.

**Verdict — a possible LATER layer, not the foundation.** A side pool never
answers what players most expect from a festival ("my farm runs faster this
weekend"); it adds state and a sink before it adds the core feeling.

### Recommendation: (a), piecewise-exact offline integration

Candidate (a) is the recommendation because it is the only shape that
**keeps one production loop** — it preserves the tick == closed-form
invariant by *generalizing* it (rate as a step function of absolute time,
provable with the same property-test machinery, with today's behavior as
the zero-boundary special case) rather than by forking it per caller (b) or
dodging it into a second accrual system (c). It is the only candidate whose
v0 shape needs **zero new save state** (§ 3), its cost is provably bounded
by the schedule data, and it directly produces the thing an event is FOR:
the world visibly runs richer during the window, for idlers and actives
alike, in the exact T6 proportion the economy already registered. (c2)-style
extras can stack on later if a ruling ever wants them; (b) stays rejected.

## 2. CORE/SKIN split — mechanics engine-side, nouns theme-side

Identical to the achievements precedent
([`achievements-v0.md`](achievements-v0.md) § Ownership): the event SLOT
SET is engine-derived, the nouns are theme data.

**Engine-owned (pre-registered numbers, `idle_engine/economy.py` when
built):**

- the **calendar** — which canonical event slots exist and their schedule
  (recurrence rule or absolute UTC windows, § 3);
- the **bonus structure** — what an active event multiplies (production
  rates only, via one `event_pct` factor in the existing single-floor
  fold), and by how much;
- any **caps** (maximum simultaneous events, maximum bonus, per-event
  earning ceilings if ever wanted — § 3 on their state cost).

The fold extends the established pattern — one more integer percent, still
ONE floor division per generator per second (per segment):

```
rate(generator) = base_rate * count * upgrade_pct * prestige_pct
                    * milestone_pct * theme_pct * event_pct // 10_000_000_000
```

with the neutral identity `(x * 100) // 10_000_000_000 == x // 100_000_000`
making no-event spans byte-for-byte identical to today's outputs — the same
graduation test every prior fold factor passed
([`theme-balance-v0.md`](theme-balance-v0.md)).

**Theme-owned (nouns only, optional block, schema addition):** per
canonical event slot id — event name, flavor description, emoji, and an
optional themed announcement line (§ 4). The schema rejects any numeric or
mechanical field in the block (`additionalProperties: false`, as
everywhere), and skinning is optional per slot with neutral scaffolding
fallback — a pack without the block renders byte-stable neutral output,
exactly like `milestones`/`labels`.

**Clause-4 consequence (README rule 4), stated plainly:** the calendar and
bonuses are GLOBAL and identical on every server. Two servers on different
themes run the same festival at the same UTC seconds with the same
multiplier; one calls it Harvest Moon and the other calls it Meteor Shower.
A theme can NEVER declare its own windows, lengths, or bonus sizes — a
theme-declared schedule would be progression-defining balance in the data
lane, which the founding contract caps at the ±10% `balance` block and
nothing more. Per-server event opt-out, if ever wanted, is a runtime
(setup-code v2?) question, not a theme field — and it is out of scope here.

## 3. Determinism constraints — schedules are data, state stays minimal

**Schedules must be data, never sampled randomness.** Two admissible
encodings, both pure functions of integer unix seconds (no wall-clock
reads inside the engine — callers pass `now`, as everywhere today):

- **Absolute UTC windows**: an explicit list of `(start_unix, end_unix)`
  half-open integer intervals per event slot. Trivially deterministic,
  trivially enumerable, expires (a one-shot festival).
- **Deterministic recurrence**: a rule evaluable in integer arithmetic on
  unix seconds — e.g. a weekly window as "day-of-week via
  `(t // 86_400 + 4) % 7` (epoch was a Thursday), UTC only". No local
  timezones, no DST, no locale: UTC is the only clock, which also keeps
  "same festival, same seconds, every server" true by construction.
  Boundary enumeration between two instants must be closed-form or
  strictly bounded iteration so the § 1 segment bound is checkable.

"Random surprise events" are structurally excluded: any randomness would
either read a wall clock/RNG inside the engine (banned — same inputs must
give same outputs, byte for byte) or push the sampling to the runtime,
where two servers would diverge (clause-4 violation) and replayed
trajectories would stop being comparable. If surprise is ever wanted, it is
a deterministic function of published calendar data (e.g. seeded from the
window's start second) — announced-but-unread is as surprising as random,
and it keeps determinism.

**Save-format impact — v0 shape needs NONE; caps are the v3 trigger.** The
recommended v0 event shape (uncapped rate-multiplier windows) derives
`event_pct` entirely from schedule data + the absolute time both progress
paths already carry (`last_seen`, `now`). No participation record, no new
field: `state_version` stays 2, and the golden save corpus is untouched.

The moment any of these is wanted, per-event state appears and **save
format v3** happens:

- earning **ceilings** per event ("at most X bonus units this festival");
- **once-per-event** claims/grants (any (c2)-style layer);
- event **participation history** (an "attended N festivals" milestone
  track).

That bump is governed by the binding corpus policy
([`persistence.md`](../persistence.md) § Golden save corpus): the v3 PR
ships the v2→v3 migration AND extends
`tests/vectors/saves.v2.json` with the migrated-golden expectations **in
the same PR** — what old saves become is pinned byte-exactly before the
bump can merge. (The golden-save-corpus session card's `_FROZEN_FIELDS`
guard recipe is the natural companion hardening for that PR.) Scoping
stance: ship v0 WITHOUT state, and treat "do events need caps?" as a
question SIM-002 answers (§ 5) — not one we pre-pay a format bump for.

## 4. Discord surface — inside the existing budget policy

No new embed and no new view for v0. Events render as **optional additions
to the status view**, following the two patterns the render layer already
enforces ([`render-layer.md`](../render-layer.md),
[`theme-schema.md`](../theme-schema.md) § labels):

- **Neutral scaffolding, always available**: while a window is active,
  `render_status` appends one line to the description — event emoji/name
  (themed if the pack skins the slot, neutral `Event` scaffolding
  otherwise), the multiplier, and the UTC end. The line is number-bearing,
  so it sits in the CLAMPING tier; the status description budget has
  thousands of chars of headroom after the offline-return arithmetic
  (theme-schema budget table: ≥ 2821 free in the worst case today). A
  title suffix variant also fits (≥ 159 chars of title headroom) but the
  description line is the cheaper first claim on shared headroom — the
  budget-table row must be re-derived in the schema PR either way.
- **Labels-pattern themed announcement (optional)**: a
  `labels.event_active` template slot, 1–256 chars, containing an
  `{event}` token **exactly once and no other braces** — the exact
  `offline_return` gate check, substitution semantics, and two-tier budget
  split (themed template never truncates, raises on overflow; substituted
  text clamps). Plus the nouns block itself: `events[].id` (canonical slot
  enum, like `milestones[].id`), `name` ≤ 64, `description` ≤ 768 (if
  composed into a field value — provenance arithmetic due in the schema
  PR), `emoji` ≤ 32.

Render stays pure: the caller passes `now`, so whether an event line
appears is a deterministic function of inputs — same state, same theme,
same `now`, same payload, event or no event. Announcement *pushes*
("the festival started!") are a runtime/plugin concern (the layer that owns
Discord I/O), out of engine scope, and blocked with everything else behind
PLUG-001.

Field-count pressure: v0 adds zero fields (a description line), so the
25-field ledger in the theme-schema budget table is untouched. An
event-history or multi-event view would need its own embed (the
achievements-embed precedent) — deferred until a mechanic wants it.

## 5. Sim implications — pre-register BEFORE tuning any bonus

Per the [`economy-v1.md`](economy-v1.md) pattern, the scenarios and
acceptance criteria below (sketch form) must be REGISTERED — an executable
SIM-002 request with bands, in a revision of the design doc that the build
slice ships — **before** any non-neutral event bonus value exists anywhere.
The harness ([`sim-harness.md`](sim-harness.md)) needs one mechanical
extension first: its exact event scheduler must jump to
`min(next_action, next_event_boundary)` (§ 1a), and its reference world
gains a pre-registered test calendar.

Scenario sketches to register:

- **SE-1 — exactness over boundaries** (property-suite, but sim-visible):
  offline spans that start before / end inside / straddle / exactly abut
  event windows equal the looped-tick trajectory byte-for-byte. This is
  the gate for the engine slice, independent of any tuning.
- **SE-2 — sleep-through equity**: S1/S2-style players offline across a
  full window get credited exactly the window bonus, independent of WHEN
  they return (return-time invariance is the whole point of (a)).
- **SE-3 — pacing displacement**: rerun S2 (N ∈ {2, 8, 24}) and S3 across
  a calendar week containing one event window; T1–T9 must stay inside
  their registered bands in the WEEKLY aggregate, with the in-window
  deviation itself banded (an event that moves time-to-first-prestige
  outside T3's band for players who START during a window is a tuning
  fail).
- **SE-4 — event-aligned optimal play**: an S3 variant that deliberately
  times prestige resets to window starts. Two things to band: (i) the
  advantage of event-aligned play over event-ignorant S3 (some advantage
  is the feature; a hard requirement to schedule your life around UTC
  windows is the failure mode); (ii) **the A10/reset-spam interaction** —
  the provisional SIM-001 run recorded ~80,796 resets in 14 days with late
  resets shrinking to ~13 s (auxiliary signal,
  [`sim-results-2026-07-11-provisional.json`](sim-results-2026-07-11-provisional.json)).
  An event multiplier feeds lifetime accrual, and lifetime feeds prestige
  awards through `isqrt` — the award only scales like the square root of
  the bonus (×2 rate ≈ ×1.41 award per run), but reset *frequency* scales
  with the rate directly, so a bonus window is a reset-spam amplifier
  precisely where A10 already needs a Q-0264 ruling. SE-4 must be
  registered TOGETHER with whatever reset-cadence criterion that ruling
  produces; tuning an event bonus before the A10 question is settled would
  be tuning into a known open wound.
- **SE-5 — fold interactions**: sweep the event bonus against earned
  milestone stacks (+5..45%) and the theme `balance` extremes (90/110) to
  confirm band edges don't flip in composition — the same reason
  [`theme-balance-v0.md`](theme-balance-v0.md) gates its values, now with
  one more factor multiplied in (SIM-001's harness models a
  zero-achievements player; SIM-002 must not).

Only after SE-1..SE-5 are registered with bands does a bonus VALUE get
proposed, and it graduates exactly like every other economy number:
pre-registered rationale → Simulator verdict → value, through the Q-0264
pipeline.

## 6. NOT BUILDING YET — and the ordered plan when we do

**Explicit statement: nothing in this doc is built, scheduled, or
parameter-bearing.** No schema field, no engine factor, no render line, no
calendar, no bonus number exists. This doc is `plan`-badged scoping: it
records the recommended shape and the exactness argument so the build
slices don't re-derive them, and it registers NO values — a build slice
citing this doc still owes its own pre-registration. The lane is in
steady-state hold; this slice exists because the QUEUE asked for the
scoping, not because a build was green-lit.

Ordered build plan, each step gated:

1. **Schema slot** — optional `events` nouns block + `labels.event_active`
   (v1-additive per the compatibility promise, gate checks + budget-table
   rows re-derived). *Gated on*: a coordinator/manager ruling adopting
   recommendation (a) and fixing the canonical slot-id set; pointless
   before the engine slice is agreed, since the slot ids are engine-derived.
2. **Engine piecewise fold** — shared span-segmenting function used by
   `tick` AND `offline_progress`, `event_pct` as the seventh single-floor
   factor, calendar constants in `idle_engine/economy.py`, neutral-identity
   + boundary-crossing property tests in the same PR (SE-1 is the merge
   gate). Shapes + calendar pre-registered in a `timed-events-v0.md`
   revision in the same PR; **all bonus values neutral (100)** at merge.
   *Gated on*: step 1's ruling; save format untouched (any capped/stateful
   variant additionally gates on the v3 + golden-corpus same-PR policy,
   § 3).
3. **Render** — status-description event line (clamping tier) +
   `labels.event_active` consumption with pinned neutral fallback
   (byte-identical output when no window is active or no pack skins it).
   *Gated on*: step 2 (there is nothing true to render before the engine
   knows what "active" means).
4. **Packs** — skin the event slots across the catalog; theme-gate green
   is the only merge bar (data-only, clause 3). *Gated on*: steps 1–3
   shipped.
5. **Non-neutral bonus values** — the first real festival. *Gated on*:
   SIM-002 registered and run, the A10/reset-cadence ruling from Q-0264,
   and value graduation through the same pipeline as every economy number.

## Cross-links

Reachable from [`AGENT_ORIENTATION.md`](../AGENT_ORIENTATION.md) § Lane-layer
docs. Related: [`economy-v1.md`](economy-v1.md) (targets T1–T10, SIM-001),
[`sim-harness.md`](sim-harness.md) (exact event scheduling, A10 ambiguity),
[`achievements-v0.md`](achievements-v0.md) (engine-derived slot precedent),
[`theme-balance-v0.md`](theme-balance-v0.md) (fold-factor graduation
pattern), [`../persistence.md`](../persistence.md) (version + golden-corpus
policy), [`../render-layer.md`](../render-layer.md) +
[`../theme-schema.md`](../theme-schema.md) (budget tiers, labels pattern),
[`../../README.md`](../../README.md) (CORE/SKIN split, integrity floor).
