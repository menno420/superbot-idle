# 2026-07-11 — achievements layer: threshold milestones with pre-registered bonuses

> **Status:** `complete`

- **📊 Model:** fable-5 · high · idle-engine seat (achievements-layer builder, coordinator-assigned) · 2026-07-11T17:27Z–17:5xZ (`date -u`)

## What happened

Landed the achievements/milestones layer in one build PR after a control
fast-lane claim (PR #53, `control/claims/achievements-layer.md`, merged
then removed here). TEST-FIRST: the red suite (+105 tests) was committed
before any implementation, like slice (b).

1. **Engine** (`idle_engine/achievements.py`): `MilestoneSpec` over three
   pre-registered tracks — `owned` (TOTAL generators owned), `lifetime`
   (run-lifetime earnings of the measured currency), `prestige` (units
   held). The two load-bearing semantics: **awarding is an explicit
   action-boundary step** (`award_milestones`, like a purchase — never
   implicit in tick, so tick == closed-form offline stays EXACT: the
   rate reads the span-start earned set via `milestone_percent`), and
   **earned-once-kept-forever** (`state.milestones`; `apply_prestige`
   preserves it — milestones are meta-progression like the prestige
   currency; rationale recorded in the design doc). Rate fold gains one
   factor with ONE shared floor:
   `base*count*up_pct*pr_pct*ms_pct // 1_000_000` — integer-identical
   to the old `// 10_000` fold when nothing is earned (pinned).
2. **Pre-registration** (`docs/design/achievements-v0.md`, PROVISIONAL
   pending Simulator): owned 10/100/1,000 · lifetime 1,000/100,000
   (= PRESTIGE_THRESHOLD, a deliberate double-hit)/10,000,000 · prestige
   1/5/25 · +5% global per earn (full sweep +45%, deliberately under
   prestige's pace). Doc-honesty test pins the table against
   `idle_engine/economy.py` (economy-v1.md pattern). The milestone SLOT
   SET is engine-derived (`build_milestone_specs`) — every pack runs
   identical milestone mechanics; themes cannot create, remove, or
   reprice slots.
3. **SAVE FORMAT v2** — the migration registry's FIRST REAL entry:
   `milestones` field added, `state_version` 2, v1→v2 migration in the
   SAME PR per docs/persistence.md § Version policy (legacy saves get an
   empty earned set; a v1 doc smuggling the v2-only field is refused,
   not wiped). Fresh-v2 + migrated-v1 + post-migration-strictness all
   tested; doc worked examples regenerated (md-parity test).
4. **Schema v1 additive `milestones` noun block** (md+json parity):
   entries skin canonical slot ids (enum) with name(64)/flavor(768)/
   emoji(32); numeric/mechanical fields red via additionalProperties.
   Gate semantic checks: duplicate slot ids; `prestige-*` nouns without
   a prestige block (slot doesn't exist). Loader (`ThemeMilestone`)
   stays ground truth. Filled in egg-farm + space-colony +
   potion-brewery (all nine slots each); other packs render neutral.
5. **Render**: `render_achievements` as its OWN view — the status view
   already spends up to 25 fields (5 currencies + 20 generators), so a
   status section could bust the field cap; a dedicated embed holds ≤ 9
   fields with 16 headroom. Shop-style two-tier values (number-bearing
   progress line clamps; themed flavor never truncates, > 768 raises);
   unskinned slots byte-pinned to neutral `Milestone {n}` scaffolding;
   earned slots pin `threshold / threshold` (counters may have reset —
   the earn is forever). Status /s rates now fold the earned bonus.

Tests 827 → 943 on the rebased tree (838 after the concurrent
sim-harness slice merged mid-flight; clean rebase, only
`.substrate/guard-fires.jsonl` needed the usual union care). Verify:
`python3 -m pytest -q` → 943 passed; `python3 bootstrap.py check
--strict` green with this flip; `python3 tools/theme_gate.py themes` →
all 12 packs valid.

## 💡 Session idea

`tools/simulate.py` (SIM-001 harness, merged mid-flight) drives the real
engine but knows nothing of milestones: its scenarios never call
`award_milestones`, so its pacing numbers hold only for a
zero-achievements player — once any milestone is earned, +5..45% global
shifts every arrival time it measures. Guard recipe: when the
achievements Simulator extension lands (achievements-v0.md § What the
Simulator must pin), add an `award_milestones` step to the S2/S3
check-in policy in `tools/simulate.py` and a smoke test in
`tests/test_simulate.py` pinning the first `owned-1`/`lifetime-1` earn
times against closed-form hand values; until then the provisional JSON
on record stays honest because its player literally cannot earn.

## ⟲ Previous-session review

The sim-harness card (2026-07-11-sim-harness.md) merged while this slice
was in flight — exactly the concurrency the coordinator predicted, and
the file-overlap prediction held precisely: zero source collisions, one
union-merge-shaped file (`.substrate/guard-fires.jsonl`), clean rebase.
Its A10 finding (integer-floor noise tripping a literal criterion) is a
useful warning for MY numbers: achievements-v0.md therefore words its
Simulator asks as band/target questions (arrival times, cadence bands)
rather than strict monotone gates. Its harness postdates my design
constraint that offline == tick must survive the new fold — its S3
event-scheduling optimization RELIES on the rate being constant between
actions, which is exactly the property the explicit-award design here
preserves (an implicit-award tick would have silently broken S3's
equivalence). The economy-design card's parked idea (commit the pacing
driver) was delivered by the sim-harness slice, so nothing left to
carry from it here.
