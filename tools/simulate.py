#!/usr/bin/env python3
"""SIM-001 executable harness — runs the pre-registered economy-v1 scenarios.

Executes the simulation request registered in ``docs/design/economy-v1.md``
(§ "Simulation request — SIM-001 (Q-0264)"): scenarios S1–S3 on the v1
reference world, emitting outputs O1–O6 and evaluating acceptance criteria
A1–A10 against targets T1–T10.

INTEGRITY FLOOR — what this tool is and is not:

- It drives the REAL engine functions (``tick`` / ``apply_offline_progress``,
  ``purchase_upgrade`` / ``upgrade_cost``, ``prestige_eligible`` /
  ``prestige_award`` / ``apply_prestige``, ``build_upgrade_spec`` /
  ``build_prestige_spec``). Nothing economic is reimplemented here; the only
  arithmetic this module adds is exact integer *scheduling* (when the next
  purchase/prestige becomes possible), which is provably equivalent to
  looping ``tick`` one second at a time because the engine's rates are
  constant integers between actions (tick/offline equivalence is
  test-enforced in ``tests/test_properties.py``).
- Its output is INPUT to a sim-lab verdict, NOT the verdict. The
  seven-parameter table's registered status is {TABLE_STATUS} per
  docs/design/economy-v1.md — the placeholder on this line is substituted
  into ``__doc__`` at import time from the ``TABLE_STATUS`` constant below
  (a literal docstring cannot interpolate; doc↔harness parity is
  test-enforced in ``tests/test_simulate.py``). Tuning a pinned value
  requires a fresh sim verdict (economy-v1.md § "Verdict semantics").
- It is deterministic: stdlib-only, no wall clock, no randomness. Two runs
  with the same flags produce byte-identical JSON.

Usage::

    python3 tools/simulate.py                 # full run, JSON to stdout
    python3 tools/simulate.py --out r.json    # full run, JSON to a file
    python3 tools/simulate.py --quick         # smoke mode (short horizon)

The human-readable per-criterion summary table always goes to stderr, so
stdout stays machine-clean.

Where the pre-registered spec is ambiguous, this harness implements the most
LITERAL reading and records the choice in the report's ``ambiguities`` list
(mirrored in ``docs/design/sim-harness.md``) — nothing is chosen silently.
"""

from __future__ import annotations

import argparse
import json
import sys
from bisect import bisect_right
from dataclasses import replace
from fractions import Fraction
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from idle_engine.economy import (  # noqa: E402
    PRESTIGE_AWARD_DIVISOR,
    PRESTIGE_BONUS_PERCENT,
    PRESTIGE_THRESHOLD,
    UPGRADE_BASE_COST_SECONDS,
    UPGRADE_COST_GROWTH_DEN,
    UPGRADE_COST_GROWTH_NUM,
    UPGRADE_EFFECT_PERCENT,
    build_prestige_spec,
    build_upgrade_spec,
)
from idle_engine.engine import production_per_second, tick  # noqa: E402
from idle_engine.engine import apply_offline_progress  # noqa: E402
from idle_engine.prestige import (  # noqa: E402
    apply_prestige,
    prestige_award,
    prestige_eligible,
)
from idle_engine.state import GameState, GeneratorSpec  # noqa: E402
from idle_engine.upgrades import purchase_upgrade, upgrade_cost  # noqa: E402

# --- reference world (economy-v1.md § "Reference world") ----------------------

CURRENCY = "primary"
GENERATOR_ID = "tier1"
UPGRADE_ID = "boost1"
PRESTIGE_CURRENCY = "prestige"

# --- pre-registered scenario constants (economy-v1.md § SIM-001) --------------

FULL_HORIZON_S = 14 * 86_400  # 14 simulated days
QUICK_HORIZON_S = 2 * 86_400  # smoke mode only — criteria NOT meaningful
CHECKIN_STEPS_S = {"0.25": 900, "2": 7_200, "8": 28_800, "24": 86_400}
S3_SAMPLE_S = 300  # O3: <= 5-min resolution for S3
RECORD_PURCHASES_THROUGH_RESET = 3  # O2: per run, through reset 3
FULL_O6_RESETS = 20
QUICK_O6_RESETS = 5
RESETS_HEAD = 20  # per-scenario reset detail kept in the report
MAX_EVENTS = 5_000_000  # hard safety budget; deterministic failure, not a hang

# --- ambiguity register (every non-obvious reading, mirrored in the doc) ------

AMBIGUITIES = [
    {
        "id": "AMB-1",
        "where": "O1 x S1",
        "reading": (
            "S1 never purchases, so time-to-first-upgrade is reported as null "
            "for S1; the time the first upgrade first becomes AFFORDABLE is "
            "reported separately as s1_first_upgrade_affordable_t."
        ),
    },
    {
        "id": "AMB-2",
        "where": "O3 x S1 ('at every visit')",
        "reading": (
            "S1 has no visits (never returns). Its trajectory is reported as "
            "three exact points: t=0, the prestige-threshold crossing, and "
            "the horizon."
        ),
    },
    {
        "id": "AMB-3",
        "where": "apply_prestige wipes state.owned",
        "reading": (
            "The reference world fixes tier1 count at 1 with no purchase "
            "path, so after every reset the harness re-seeds owned to "
            "{'tier1': 1} (a fresh save 'starts owning it'). Without the "
            "re-seed, production would be zero forever after reset 1."
        ),
    },
    {
        "id": "AMB-4",
        "where": "A7 'every visit before first prestige'",
        "reading": (
            "Qualifying visits are those STRICTLY earlier than the visit at "
            "which the first prestige fires (that visit is the boundary, not "
            "'before'). The minimum including the prestige visit's own "
            "pre-reset purchases is also reported as an auxiliary value."
        ),
    },
    {
        "id": "AMB-5",
        "where": "A8 'gap between consecutive purchases'",
        "reading": (
            "Measured between consecutive purchase events only; the spans "
            "t=0 -> first purchase and last purchase -> prestige are NOT "
            "gaps between purchases, but both are reported as auxiliary "
            "values."
        ),
    },
    {
        "id": "AMB-6",
        "where": "A10 v1 'each reset's duration ratio non-decreasing toward 1'",
        "reading": (
            "RESOLVED by the v2 TREND re-registration (economy-v1.md § A10 "
            "re-registration record, VERDICT 038): the gate is now final "
            "consecutive ratio >= first (exact rationals, r_k = duration_k "
            "/ duration_(k-1)), with any single-step ratio decrease "
            "tolerated within a 0.02 wiggle band of its predecessor. v1's "
            "strict per-step gate was the ambiguity; kept on this list as "
            "the record of the choice and its resolution."
        ),
    },
    {
        "id": "AMB-11",
        "where": "O6 'flag if reset-duration shrinkage is super-geometric'",
        "reading": (
            "The flag is set when the ratio TREND falls (final consecutive "
            "ratio < first) — accelerating shrinkage. This is deliberately "
            "distinct from A10's strict non-decreasing gate, which also "
            "trips on single-step integer-floor wiggles."
        ),
    },
    {
        "id": "AMB-7",
        "where": "S2/S3 policy order at a prestige moment",
        "reading": (
            "The doc's visit order is credit -> greedy-buy -> prestige iff "
            "eligible; purchases made at the same visit/second as a reset "
            "are executed and recorded in O2 even though the reset "
            "immediately wipes them (the doc explicitly blesses "
            "buy-then-prestige)."
        ),
    },
    {
        "id": "AMB-8",
        "where": "A2 'by t = 15 min'",
        "reading": "Purchases with t <= 900 s count (boundary inclusive).",
    },
    {
        "id": "AMB-9",
        "where": "band endpoints",
        "reading": (
            "All acceptance bands are inclusive at both endpoints except "
            "A8's explicitly strict '< 25%'."
        ),
    },
    {
        "id": "AMB-10",
        "where": "O3 sample values at action times",
        "reading": (
            "Samples record the post-action state (what the player leaves "
            "with after the visit's/second's purchases and any reset)."
        ),
    },
]


def _world() -> tuple[GeneratorSpec, object, object]:
    gen = GeneratorSpec(spec_id=GENERATOR_ID, produces=CURRENCY, base_rate=1)
    up = build_upgrade_spec(UPGRADE_ID, gen)
    pres = build_prestige_spec(awards=PRESTIGE_CURRENCY, measures=CURRENCY)
    return gen, up, pres


def _fresh_state() -> GameState:
    return GameState(owned={GENERATOR_ID: 1}, last_seen=0)


def _ceil_div(numerator: int, denominator: int) -> int:
    return -(-numerator // denominator)


# --- shared policy pieces (S2 and S3 use the identical action order) -----------


def _greedy_buy(state, up, purchases, reset_index, record_through):
    """Repeat-buy while affordable, recording O2 rows through reset 3."""
    t = state.last_seen
    bought = 0
    while True:
        level = state.upgrades.get(up.spec_id, 0)
        cost = upgrade_cost(up, level)
        if state.balances.get(up.cost_currency, 0) < cost:
            return state, bought
        state = purchase_upgrade(state, up)
        bought += 1
        if reset_index <= record_through:
            purchases.append(
                [t, reset_index, level + 1, cost, state.balances.get(up.cost_currency, 0)]
            )


def _maybe_prestige(state, gen, up, pres, resets, reset_start, reset_index):
    """Prestige iff eligible; re-seed the fixed generator (AMB-3)."""
    if not prestige_eligible(state, pres):
        return state, reset_start, reset_index, False
    t = state.last_seen
    entry = {
        "index": reset_index,
        "t": t,
        "duration": t - reset_start,
        "award": prestige_award(state, pres),
        "level_at_reset": state.upgrades.get(up.spec_id, 0),
        "lifetime_at_reset": state.lifetime.get(CURRENCY, 0),
    }
    state = apply_prestige(state, pres)
    state = replace(state, owned={gen.spec_id: 1})  # AMB-3
    entry["prestige_after"] = state.prestige.get(pres.awards, 0)
    resets.append(entry)
    return state, t, reset_index + 1, True


# --- scenarios -----------------------------------------------------------------


def simulate_s1(gen, up, pres, horizon):
    """S1 — idle-only: never purchases, never prestiges. Pure accrual."""
    gens, ups, prs = (gen,), (up,), (pres,)
    state = _fresh_state()
    rate = production_per_second(state, gens, ups, prs).get(CURRENCY, 0)
    crossing = _ceil_div(pres.threshold, rate) if rate > 0 else None
    afford_t = _ceil_div(upgrade_cost(up, 0), rate) if rate > 0 else None
    if crossing is not None and crossing <= horizon:
        # Exactness check via the REAL engine: crossed at t, not at t-1.
        at = tick(state, gens, crossing, ups, prs)
        before = tick(state, gens, crossing - 1, ups, prs)
        assert at.lifetime.get(CURRENCY, 0) >= pres.threshold
        assert before.lifetime.get(CURRENCY, 0) < pres.threshold
    else:
        crossing = crossing if crossing is not None and crossing <= horizon else None
    end = tick(state, gens, horizon, ups, prs)
    trajectory = [[0, 0, 0]]
    if crossing is not None:
        mid = tick(state, gens, crossing, ups, prs)
        trajectory.append(
            [crossing, mid.balances.get(CURRENCY, 0), mid.lifetime.get(CURRENCY, 0)]
        )
    trajectory.append(
        [horizon, end.balances.get(CURRENCY, 0), end.lifetime.get(CURRENCY, 0)]
    )
    return {
        "policy": "idle-only: never purchases, never prestiges",
        "horizon_s": horizon,
        "rate_per_s": rate,
        "first_purchase_t": None,  # AMB-1
        "first_upgrade_affordable_t": afford_t,
        "threshold_crossing_t": crossing,
        "balance_at_horizon": end.balances.get(CURRENCY, 0),
        "lifetime_at_horizon": end.lifetime.get(CURRENCY, 0),
        "trajectory": trajectory,  # AMB-2: [t, balance, lifetime]
    }


def simulate_s2(gen, up, pres, step, horizon, record_through=RECORD_PURCHASES_THROUGH_RESET):
    """S2 — check-in every ``step`` seconds: credit, greedy-buy, prestige iff eligible."""
    gens, ups, prs = (gen,), (up,), (pres,)
    state = _fresh_state()
    purchases: list[list[int]] = []
    resets: list[dict] = []
    visits: list[list[int]] = []  # [t, levels_bought, prestiged(0/1), balance_after, lifetime_after]
    reset_start, reset_index = 0, 1
    for now in range(step, horizon + 1, step):
        state = apply_offline_progress(state, gens, now, ups, prs)
        state, bought = _greedy_buy(state, up, purchases, reset_index, record_through)
        state, reset_start, reset_index, prestiged = _maybe_prestige(
            state, gen, up, pres, resets, reset_start, reset_index
        )
        visits.append(
            [
                now,
                bought,
                1 if prestiged else 0,
                state.balances.get(CURRENCY, 0),
                state.lifetime.get(CURRENCY, 0),
            ]
        )
    return _run_dict(
        f"check-in every {step} s: credit, greedy-buy, prestige iff eligible",
        horizon,
        purchases,
        resets,
        visits=visits,
    )


def simulate_s3(
    gen,
    up,
    pres,
    horizon=None,
    max_resets=None,
    record_through=RECORD_PURCHASES_THROUGH_RESET,
):
    """S3 — optimal-play speedrun: S2's policy at 1-second granularity.

    Implemented as exact event scheduling: between actions the engine rate is
    a constant integer, so the first whole second at which the next purchase
    (or prestige eligibility) is possible is ``ceil(need / rate)`` seconds
    away; jumping there with one ``tick`` is EXACTLY equal to looping 1-second
    ticks (engine equivalence is test-enforced). Policy per second matches
    S2's visit order: credit, greedy-buy, prestige iff eligible.
    """
    if horizon is None and max_resets is None:
        raise ValueError("need a horizon or a reset cap")
    gens, ups, prs = (gen,), (up,), (pres,)
    state = _fresh_state()
    purchases: list[list[int]] = []
    resets: list[dict] = []
    segments: list[tuple[int, int, int, int]] = []  # (t, balance, lifetime, rate)
    reset_start, reset_index = 0, 1
    events = 0
    while True:
        t = state.last_seen
        rate = production_per_second(state, gens, ups, prs).get(CURRENCY, 0)
        segments.append(
            (t, state.balances.get(CURRENCY, 0), state.lifetime.get(CURRENCY, 0), rate)
        )
        if horizon is not None and t >= horizon:
            break
        if max_resets is not None and len(resets) >= max_resets:
            break
        if rate <= 0:  # unreachable in the reference world; loud, not silent
            raise RuntimeError(f"production stalled at rate 0 (t={t})")
        need_buy = upgrade_cost(up, state.upgrades.get(up.spec_id, 0)) - state.balances.get(
            CURRENCY, 0
        )
        need_pre = pres.threshold - state.lifetime.get(CURRENCY, 0)
        dt = min(_ceil_div(max(need_buy, 1), rate), _ceil_div(max(need_pre, 1), rate))
        if horizon is not None and t + dt > horizon:
            state = tick(state, gens, horizon - t, ups, prs)
            continue  # loop top records the horizon segment, then breaks
        state = tick(state, gens, dt, ups, prs)
        state, _ = _greedy_buy(state, up, purchases, reset_index, record_through)
        state, reset_start, reset_index, _ = _maybe_prestige(
            state, gen, up, pres, resets, reset_start, reset_index
        )
        events += 1
        if events > MAX_EVENTS:
            raise RuntimeError("event budget exceeded — scenario did not terminate")
    run = _run_dict(
        "optimal speedrun: S2's policy at 1-second granularity (greedy proxy)",
        horizon,
        purchases,
        resets,
    )
    run["samples"] = _sample_segments(segments, horizon) if horizon is not None else []
    return run


def _sample_segments(segments, horizon, every=S3_SAMPLE_S):
    """O3 for S3: exact [t, balance, lifetime] at <= 5-min resolution.

    Between recorded action points the rate is constant, so intermediate
    samples are exact linear interpolations in integer arithmetic — the same
    value a 1-second tick loop would hold at that second.
    """
    starts = [seg[0] for seg in segments]
    samples = []
    for s in range(0, horizon + 1, every):
        i = bisect_right(starts, s) - 1
        t0, bal, life, rate = segments[i]
        samples.append([s, bal + rate * (s - t0), life + rate * (s - t0)])
    return samples


def _run_dict(policy, horizon, purchases, resets, visits=None):
    first_prestige = resets[0]["t"] if resets else None
    run = {
        "policy": policy,
        "horizon_s": horizon,
        "first_purchase_t": purchases[0][0] if purchases else None,
        "purchases_through_reset_3": purchases,
        "purchase_columns": ["t", "reset_index", "level_after", "cost", "balance_after"],
        "first_prestige_t": first_prestige,
        "resets_total": len(resets),
        "resets_head": resets[:RESETS_HEAD],
        "reset_durations_1_to_3": [r["duration"] for r in resets[:3]],
    }
    if visits is not None:
        run["visits"] = visits
        run["visit_columns"] = [
            "t",
            "levels_bought",
            "prestiged",
            "balance_after",
            "lifetime_after",
        ]
    return run


# --- output post-processing -----------------------------------------------------


def _fraction_fields(fr: Fraction) -> dict:
    return {"exact": f"{fr.numerator}/{fr.denominator}", "approx": float(fr)}


def _purchase_gaps(purchases, first_prestige_t):
    """A8 helpers: gaps between consecutive first-run purchases (AMB-5)."""
    first_run = [p[0] for p in purchases if p[1] == 1]
    if first_prestige_t is not None:
        first_run = [t for t in first_run if t <= first_prestige_t]
    gaps = [b - a for a, b in zip(first_run, first_run[1:])]
    return {
        "max_gap_between_purchases": max(gaps) if gaps else None,
        "lead_in_gap_t0_to_first_purchase": first_run[0] if first_run else None,
        "tail_gap_last_purchase_to_prestige": (
            first_prestige_t - first_run[-1]
            if first_prestige_t is not None and first_run
            else None
        ),
    }


def _s2_visit_burst_minima(run):
    """A7 helpers: min levels bought per visit before the first prestige."""
    visits = run["visits"]
    first_prestige = run["first_prestige_t"]
    if first_prestige is None:
        return {"strictly_before": None, "including_prestige_visit": None}
    strictly = [v[1] for v in visits if v[0] < first_prestige]  # AMB-4
    inclusive = [v[1] for v in visits if v[0] <= first_prestige]
    return {
        "strictly_before": min(strictly) if strictly else None,
        "including_prestige_visit": min(inclusive) if inclusive else None,
    }


def _payback_rows(up, gen, s3_resets):
    """O5: payback per level in hours, annotated with S3 hold levels."""
    held = {str(r["index"]): r["level_at_reset"] for r in s3_resets[:3]}
    top = max(list(held.values()) + [40]) + 5
    denominator = gen.base_rate * UPGRADE_EFFECT_PERCENT  # units/s * pct
    rows = []
    for level in range(top + 1):
        cost = upgrade_cost(up, level)
        payback_s = Fraction(cost * 100, denominator)
        rows.append(
            {
                "level": level,
                "cost": cost,
                "payback_hours": _fraction_fields(payback_s / 3600),
                "s3_holds_at_prestige": sorted(
                    (idx for idx, lvl in held.items() if lvl == level), key=int
                ),
            }
        )
    return {"rows": rows, "s3_level_at_each_prestige": held}


def _o6_table(o6_resets):
    """O6: per-reset duration + cumulative bonus across the reset ladder."""
    rows = []
    prev = None
    ratios = []
    for r in o6_resets:
        ratio = None
        if prev is not None and prev > 0:
            fr = Fraction(r["duration"], prev)
            ratios.append(fr)
            ratio = _fraction_fields(fr)
        rows.append(
            {
                "index": r["index"],
                "duration": r["duration"],
                "award": r["award"],
                "cum_prestige_units": r["prestige_after"],
                "cum_bonus_pct": 100 + PRESTIGE_BONUS_PERCENT * r["prestige_after"],
                "ratio_to_prev": ratio,
            }
        )
        prev = r["duration"]
    trend_rises, max_step_decrease, _ = _a10_v2_gate(ratios)
    return {
        "rows": rows,
        # A10's v2 TREND gate (economy-v1.md § A10 re-registration record,
        # VERDICT 038): the ratio trend rises toward 1, and single-step
        # decreases stay within the registered 0.02 wiggle band.
        "a10_trend_rises_toward_1": trend_rises,
        "a10_max_step_decrease": _fraction_fields(max_step_decrease),
        "a10_steps_within_wiggle_band": max_step_decrease <= A10_WIGGLE_BAND,
        # O6's requested flag: shrinkage is super-geometric when the ratio
        # TREND falls (each reset shrinks proportionally more than the last);
        # measured as final ratio < first ratio. Same trend reading A10 v2
        # gates on, kept as its own reported flag per the O6 spec.
        "super_geometric_shrinkage_flag": bool(ratios) and ratios[-1] < ratios[0],
        "first_ratio": _fraction_fields(ratios[0]) if ratios else None,
        "final_ratio": _fraction_fields(ratios[-1]) if ratios else None,
    }


# --- acceptance criteria (pure — unit-testable with synthetic measures) ---------

#: Implemented A10 criterion version — MUST match the version token in the
#: registered A10 row of docs/design/economy-v1.md § "Acceptance criteria"
#: ("O6 — v2, TREND form ..."); doc↔harness parity is test-enforced
#: (tests/test_simulate.py), so re-registering the criterion without syncing
#: this harness (or vice versa) goes red. Bump BOTH sides in the same PR.
A10_CRITERION_VERSION = "v2"

#: Registered status of the seven-parameter table — MUST match the
#: parameter-status badge on docs/design/economy-v1.md's Status line
#: ("**SIM-PINNED** (every numeric parameter ..."); doc↔harness parity is
#: test-enforced (tests/test_simulate.py), so a future re-grade of the table
#: without syncing the report label (or vice versa) goes red instead of the
#: report silently emitting a stale status. Bump BOTH sides in the same PR.
#: (VERDICT 038 graduated the table PROVISIONAL → SIM-PINNED 2026-07-13,
#: PR #93.)
TABLE_STATUS = "SIM-PINNED"

# The module docstring's INTEGRITY FLOOR bullet carries the table status via
# a literal {TABLE_STATUS} placeholder (a docstring literal cannot
# interpolate); substitute it here so the rendered ``__doc__`` derives from
# the single constant above — the parity guard in tests/test_simulate.py
# pins both the substituted docstring and the raw placeholder.
__doc__ = (__doc__ or "").replace("{TABLE_STATUS}", TABLE_STATUS)

#: v2's registered single-step tolerance: a ratio decrease is a tolerated
#: wiggle iff it stays within 0.02 of its predecessor (exact rational; the
#: VERDICT 038 evidence run's worst step was 0.0166 ≈ 83% of this band).
A10_WIGGLE_BAND = Fraction(2, 100)


def _a10_v2_gate(ratios: list[Fraction]) -> tuple[bool, Fraction, bool]:
    """A10 v2 TREND form on consecutive duration ratios (exact rationals).

    Returns (trend_rises_toward_1, max_step_decrease, steps_within_band):
    the trend rises iff the final consecutive ratio >= the first, and every
    single-step decrease must stay within A10_WIGGLE_BAND (inclusive) of
    its predecessor.
    """
    trend_rises = bool(ratios) and ratios[-1] >= ratios[0]
    max_step_decrease = max(
        (a - b for a, b in zip(ratios, ratios[1:]) if b < a), default=Fraction(0)
    )
    return trend_rises, max_step_decrease, max_step_decrease <= A10_WIGGLE_BAND


def evaluate_criteria(measures: dict) -> list[dict]:
    """Evaluate A1–A10 from a flat measures dict; exact arithmetic throughout.

    ``measures`` keys (None = not measurable within the run's horizon, which
    evaluates as FAIL with an explanatory detail — never as a silent skip):
    s3_first_purchase_t, s3_purchases_by_900s, s3_first_prestige_t,
    s1_threshold_crossing_t, s2_2h_first_prestige_t,
    s2_2h_min_levels_per_early_visit, s2_8h_min_levels_per_early_visit,
    s3_max_purchase_gap, s3_reset_durations (list), o6_durations (list).
    """
    results = []

    def add(cid, target, band, measured, ok, detail=""):
        results.append(
            {
                "id": cid,
                "target": target,
                "band": band,
                "measured": measured,
                "pass": bool(ok),
                "detail": detail,
            }
        )

    def in_band(value, lo, hi):
        return value is not None and lo <= value <= hi

    m = measures

    v = m.get("s3_first_purchase_t")
    add("A1", "T1", "30–180 s", v, in_band(v, 30, 180), "S3 time-to-first-upgrade")

    v = m.get("s3_purchases_by_900s")
    add("A2", "T2", ">= 5 by t=900 s", v, v is not None and v >= 5,
        "S3 purchases with t <= 900 s (AMB-8)")

    v = m.get("s3_first_prestige_t")
    add("A3", "T3", "7200–28800 s", v, in_band(v, 7_200, 28_800), "S3 first prestige")

    v = m.get("s1_threshold_crossing_t")
    add("A4", "T4", "64800–129600 s", v, in_band(v, 64_800, 129_600),
        "S1 lifetime crosses PRESTIGE_THRESHOLD")

    v = m.get("s2_2h_first_prestige_t")
    add("A5", "T5", "14400–43200 s", v, in_band(v, 14_400, 43_200),
        "S2(N=2) first prestige")

    t4, t3 = m.get("s1_threshold_crossing_t"), m.get("s3_first_prestige_t")
    if t4 is not None and t3:
        ratio = Fraction(t4, t3)
        add("A6", "T6", "4–12x", _fraction_fields(ratio),
            Fraction(4) <= ratio <= Fraction(12), "A4 time / A3 time, exact rational")
    else:
        add("A6", "T6", "4–12x", None, False, "A4 or A3 unmeasured")

    lo2, lo8 = m.get("s2_2h_min_levels_per_early_visit"), m.get(
        "s2_8h_min_levels_per_early_visit"
    )
    ok7 = lo2 is not None and lo8 is not None and lo2 >= 2 and lo8 >= 2
    add("A7", "T7", ">= 2 levels per visit", {"N=2": lo2, "N=8": lo8}, ok7,
        "min levels bought per visit strictly before first prestige (AMB-4)")

    gap, dur = m.get("s3_max_purchase_gap"), m.get("s3_first_prestige_t")
    if gap is not None and dur:
        share = Fraction(gap, dur)
        add("A8", "T8", "< 25% of run duration",
            {"max_gap_s": gap, "share_of_run": _fraction_fields(share)},
            share < Fraction(1, 4), "gap between consecutive purchases (AMB-5)")
    else:
        add("A8", "T8", "< 25% of run duration", None, False, "gap or duration unmeasured")

    durations = m.get("s3_reset_durations") or []
    if len(durations) >= 3 and durations[0] > 0 and durations[1] > 0:
        checks = []
        for prev, cur in ((durations[0], durations[1]), (durations[1], durations[2])):
            checks.append(2 * cur >= prev and cur <= prev)  # 50–100% of prior
        add("A9", "T9", "resets 2 and 3 each 50–100% of prior",
            {"d1": durations[0], "d2": durations[1], "d3": durations[2]},
            all(checks), "exact integer comparison, band inclusive (AMB-9)")
    else:
        add("A9", "T9", "resets 2 and 3 each 50–100% of prior",
            {"durations": durations}, False, "fewer than 3 resets reached")
    o6 = m.get("o6_durations") or []
    ratios = [
        Fraction(b, a) for a, b in zip(o6, o6[1:]) if a > 0
    ]
    trend_rises, max_step_decrease, within_band = _a10_v2_gate(ratios)
    ok10 = len(o6) >= 2 and trend_rises and within_band
    detail10 = (
        f"{len(o6)} resets; {A10_CRITERION_VERSION} TREND form (VERDICT 038 "
        "re-registration): final consecutive ratio >= first, single-step "
        "decreases within the 0.02 wiggle band (AMB-6 resolved)"
        + ("" if len(o6) >= FULL_O6_RESETS else " — fewer than 20 resets simulated")
    )
    add("A10", "O6",
        "trend rises toward 1 (final ratio >= first); step decreases <= 0.02",
        {
            "resets": len(o6),
            "first_ratio": _fraction_fields(ratios[0]) if ratios else None,
            "final_ratio": _fraction_fields(ratios[-1]) if ratios else None,
            "max_step_decrease": _fraction_fields(max_step_decrease),
        },
        ok10, detail10)

    return results


# --- report assembly -------------------------------------------------------------


def run_report(quick: bool = False) -> dict:
    gen, up, pres = _world()
    horizon = QUICK_HORIZON_S if quick else FULL_HORIZON_S
    o6_cap = QUICK_O6_RESETS if quick else FULL_O6_RESETS

    s1 = simulate_s1(gen, up, pres, horizon)
    s2 = {
        label: simulate_s2(gen, up, pres, step, horizon)
        for label, step in CHECKIN_STEPS_S.items()
    }
    s3 = simulate_s3(gen, up, pres, horizon=horizon)
    o6_run = simulate_s3(gen, up, pres, max_resets=o6_cap)

    gaps = _purchase_gaps(s3["purchases_through_reset_3"], s3["first_prestige_t"])
    burst_2h = _s2_visit_burst_minima(s2["2"])
    burst_8h = _s2_visit_burst_minima(s2["8"])
    o6 = _o6_table(o6_run["resets_head"][:o6_cap])

    measures = {
        "s3_first_purchase_t": s3["first_purchase_t"],
        "s3_purchases_by_900s": sum(
            1 for p in s3["purchases_through_reset_3"] if p[1] == 1 and p[0] <= 900
        ),
        "s3_first_prestige_t": s3["first_prestige_t"],
        "s1_threshold_crossing_t": s1["threshold_crossing_t"],
        "s2_2h_first_prestige_t": s2["2"]["first_prestige_t"],
        "s2_2h_min_levels_per_early_visit": burst_2h["strictly_before"],
        "s2_8h_min_levels_per_early_visit": burst_8h["strictly_before"],
        "s3_max_purchase_gap": gaps["max_gap_between_purchases"],
        "s3_reset_durations": [r["duration"] for r in s3["resets_head"][:3]],
        "o6_durations": [r["duration"] for r in o6_run["resets_head"][:o6_cap]],
    }
    criteria = evaluate_criteria(measures)

    return {
        "report": "SIM-001",
        "label": (
            "UNOFFICIAL — harness output is INPUT to the Q-0264 verdict, not "
            f"the verdict. The seven-parameter table is {TABLE_STATUS} per "
            "docs/design/economy-v1.md (VERDICT 038; tuning a pinned value "
            "requires a fresh sim verdict)."
        ),
        "spec": "docs/design/economy-v1.md § Simulation request — SIM-001 (Q-0264)",
        "harness": "tools/simulate.py",
        "mode": "quick" if quick else "full",
        "quick_mode_warning": (
            "quick mode shortens the horizon for smoke testing; criteria "
            "results are NOT meaningful in quick mode"
            if quick
            else None
        ),
        "parameters": {
            "UPGRADE_BASE_COST_SECONDS": UPGRADE_BASE_COST_SECONDS,
            "UPGRADE_COST_GROWTH_NUM": UPGRADE_COST_GROWTH_NUM,
            "UPGRADE_COST_GROWTH_DEN": UPGRADE_COST_GROWTH_DEN,
            "UPGRADE_EFFECT_PERCENT": UPGRADE_EFFECT_PERCENT,
            "PRESTIGE_THRESHOLD": PRESTIGE_THRESHOLD,
            "PRESTIGE_AWARD_DIVISOR": PRESTIGE_AWARD_DIVISOR,
            "PRESTIGE_BONUS_PERCENT": PRESTIGE_BONUS_PERCENT,
        },
        "world": {
            "generator": {"spec_id": GENERATOR_ID, "produces": CURRENCY, "base_rate": 1},
            "owned": {GENERATOR_ID: 1},
            "upgrade": UPGRADE_ID,
            "prestige": {"awards": PRESTIGE_CURRENCY, "measures": CURRENCY},
        },
        "scenarios": {"S1": s1, "S2": s2, "S3": s3},
        "outputs": {
            "O1_time_to_first_upgrade_s": {
                "S1": s1["first_purchase_t"],
                "S1_first_upgrade_affordable_t": s1["first_upgrade_affordable_t"],
                **{f"S2(N={n})": s2[n]["first_purchase_t"] for n in CHECKIN_STEPS_S},
                "S3": s3["first_purchase_t"],
            },
            "O2_purchase_timelines": {
                "columns": ["t", "reset_index", "level_after", "cost", "balance_after"],
                **{f"S2(N={n})": s2[n]["purchases_through_reset_3"] for n in CHECKIN_STEPS_S},
                "S3": s3["purchases_through_reset_3"],
            },
            "O3_trajectories": {
                "S1": {"columns": ["t", "balance", "lifetime"], "points": s1["trajectory"]},
                **{
                    f"S2(N={n})": {
                        "columns": s2[n]["visit_columns"],
                        "visits": s2[n]["visits"],
                    }
                    for n in CHECKIN_STEPS_S
                },
                "S3": {
                    "columns": ["t", "balance", "lifetime"],
                    "sample_every_s": S3_SAMPLE_S,
                    "points": s3["samples"],
                },
            },
            "O4_prestige_times": {
                "first_prestige_t": {
                    "S1": None,
                    **{f"S2(N={n})": s2[n]["first_prestige_t"] for n in CHECKIN_STEPS_S},
                    "S3": s3["first_prestige_t"],
                },
                "S1_threshold_crossing_t": s1["threshold_crossing_t"],
                "reset_durations_1_to_3": {
                    **{f"S2(N={n})": s2[n]["reset_durations_1_to_3"] for n in CHECKIN_STEPS_S},
                    "S3": s3["reset_durations_1_to_3"],
                },
            },
            "O5_payback_curve": _payback_rows(up, gen, s3["resets_head"]),
            "O6_prestige_stacking": o6,
        },
        "auxiliary": {
            "s3_purchase_gaps": gaps,
            "s2_visit_burst_minima": {"N=2": burst_2h, "N=8": burst_8h},
            "s3_resets_total": s3["resets_total"],
            "o6_resets_simulated": len(o6["rows"]),
        },
        "measures": measures,
        "criteria": criteria,
        # Run-artifact provenance: which criterion version each row above was
        # judged under, sourced from the SAME constants the doc↔harness parity
        # guard pins (tests/test_simulate.py) — a committed run stays
        # self-describing across re-registrations, so v1-era evidence can
        # never silently pass as v2-era (and vice versa).
        "criteria_versions": {"A10": A10_CRITERION_VERSION},
        "all_pass": all(c["pass"] for c in criteria),
        "ambiguities": AMBIGUITIES,
    }


def render_summary(report: dict) -> str:
    lines = [
        "SIM-001 harness — per-criterion summary "
        f"(table {TABLE_STATUS}: harness output is input to a verdict, "
        "not the verdict)",
        f"mode: {report['mode']}",
        f"{'id':<4} {'verdict':<8} {'band':<38} measured",
        "-" * 78,
    ]
    for c in report["criteria"]:
        measured = c["measured"]
        if isinstance(measured, dict) and "exact" in measured:
            measured = f"{measured['approx']:.4g} ({measured['exact']})"
        lines.append(
            f"{c['id']:<4} {'PASS' if c['pass'] else 'FAIL':<8} {c['band']:<38} {measured}"
        )
    lines.append("-" * 78)
    lines.append("ALL PASS" if report["all_pass"] else "NOT ALL PASS")
    if report["mode"] == "quick":
        lines.append("quick mode — criteria results are NOT meaningful (smoke only)")
    return "\n".join(lines)


def to_json(report: dict) -> str:
    return json.dumps(report, sort_keys=True, separators=(",", ": "), indent=1) + "\n"


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        prog="simulate",
        description="SIM-001 executable harness (deterministic; see module docstring)",
    )
    parser.add_argument("--quick", action="store_true", help="short-horizon smoke mode")
    parser.add_argument("--out", type=Path, default=None, help="write JSON report here")
    args = parser.parse_args(argv)

    report = run_report(quick=args.quick)
    payload = to_json(report)
    if args.out is not None:
        args.out.write_text(payload, encoding="utf-8")
    else:
        sys.stdout.write(payload)
    print(render_summary(report), file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
