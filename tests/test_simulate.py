"""SIM-001 harness tests: determinism, closed-form spot checks, criteria logic.

The harness (``tools/simulate.py``) computes and reports; it never tunes and
never declares the Q-0264 verdict. These tests pin that the computation is
deterministic, that it agrees with hand arithmetic where hand arithmetic is
possible, and that the A1–A10 evaluation logic goes red and green on the
right synthetic inputs.
"""

import ast
import json
import re
import subprocess
import sys
from pathlib import Path

from idle_engine.economy import (
    PRESTIGE_THRESHOLD,
    UPGRADE_BASE_COST_SECONDS,
    UPGRADE_COST_GROWTH_DEN,
    UPGRADE_COST_GROWTH_NUM,
)
import tools.simulate
from tools.simulate import (
    A10_CRITERION_VERSION,
    QUICK_HORIZON_S,
    TABLE_STATUS,
    evaluate_criteria,
    render_summary,
    run_report,
    to_json,
)

REPO_ROOT = Path(__file__).resolve().parent.parent


# --- shared quick run (one in-process simulation for the whole module) ---------

_QUICK = run_report(quick=True)


# --- determinism ----------------------------------------------------------------


def test_two_cli_runs_are_byte_identical(tmp_path):
    """The committed-results contract: same flags -> byte-identical JSON."""
    outs = []
    for name in ("a.json", "b.json"):
        out = tmp_path / name
        proc = subprocess.run(
            [sys.executable, "tools/simulate.py", "--quick", "--out", str(out)],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=True,
        )
        assert "SIM-001" in proc.stderr  # human summary goes to stderr
        assert proc.stdout == ""  # --out keeps stdout machine-clean
        outs.append(out.read_bytes())
    assert outs[0] == outs[1]


def test_in_process_report_matches_cli_bytes(tmp_path):
    """run_report + to_json is exactly what the CLI writes."""
    out = tmp_path / "cli.json"
    subprocess.run(
        [sys.executable, "tools/simulate.py", "--quick", "--out", str(out)],
        cwd=REPO_ROOT,
        capture_output=True,
        check=True,
    )
    assert out.read_text(encoding="utf-8") == to_json(_QUICK)


# --- S1 closed-form spot check ---------------------------------------------------


def test_s1_idle_only_matches_hand_computation():
    """S1 at base_rate 1/s: pure accrual is fully hand-computable.

    lifetime(t) = t, so the threshold crossing is exactly PRESTIGE_THRESHOLD
    seconds (100000 s = ~27.78 h) and the horizon balance equals the horizon.
    """
    s1 = _QUICK["scenarios"]["S1"]
    assert s1["rate_per_s"] == 1
    assert s1["first_purchase_t"] is None  # AMB-1: S1 never purchases
    assert s1["first_upgrade_affordable_t"] == UPGRADE_BASE_COST_SECONDS  # 60 s
    if PRESTIGE_THRESHOLD <= QUICK_HORIZON_S:
        assert s1["threshold_crossing_t"] == PRESTIGE_THRESHOLD  # exactly 100000 s
    assert s1["balance_at_horizon"] == QUICK_HORIZON_S
    assert s1["lifetime_at_horizon"] == QUICK_HORIZON_S
    assert s1["trajectory"][0] == [0, 0, 0]
    assert s1["trajectory"][-1] == [QUICK_HORIZON_S, QUICK_HORIZON_S, QUICK_HORIZON_S]


def test_s3_first_purchases_match_cost_curve_hand_values():
    """The first S3 purchases are hand-checkable against the exact curve.

    At rate 1/s: cost(0) = 60 -> bought at t=60 with balance 0 after; the
    next purchase lands when the balance regrows to cost(1) = 60*115//100 = 69.
    """
    purchases = _QUICK["scenarios"]["S3"]["purchases_through_reset_3"]
    t0, reset0, level0, cost0, bal0 = purchases[0]
    assert (t0, reset0, level0, cost0, bal0) == (60, 1, 1, 60, 0)
    cost1 = 60 * UPGRADE_COST_GROWTH_NUM // UPGRADE_COST_GROWTH_DEN
    t1, _, level1, cost1_seen, _ = purchases[1]
    assert level1 == 2 and cost1_seen == cost1 == 69


# --- criteria evaluation logic: red/green on synthetic measures ------------------


def _green_measures():
    """A synthetic all-PASS measures dict (hand-picked mid-band values)."""
    return {
        "s3_first_purchase_t": 60,
        "s3_purchases_by_900s": 8,
        "s3_first_prestige_t": 14_400,
        "s1_threshold_crossing_t": 100_000,
        "s2_2h_first_prestige_t": 21_600,
        "s2_2h_min_levels_per_early_visit": 5,
        "s2_8h_min_levels_per_early_visit": 5,
        "s3_max_purchase_gap": 1_000,
        "s3_reset_durations": [14_400, 10_000, 8_000],
        # Harmonic decay d_k = lcm(1..20)/k: consecutive ratios k/(k+1) are
        # exactly representable and strictly rise toward 1 -> A10 green.
        "o6_durations": [232_792_560 // k for k in range(1, 21)],
    }


def _result(criteria, cid):
    return next(c for c in criteria if c["id"] == cid)


def test_synthetic_green_measures_pass_everything():
    criteria = evaluate_criteria(_green_measures())
    assert [c["id"] for c in criteria] == [f"A{i}" for i in range(1, 11)]
    assert all(c["pass"] for c in criteria), [c for c in criteria if not c["pass"]]


def test_each_criterion_reds_on_its_own_violation():
    violations = {
        "A1": {"s3_first_purchase_t": 181},  # above T1 band
        "A2": {"s3_purchases_by_900s": 4},  # below T2 floor
        "A3": {"s3_first_prestige_t": 7_199},  # under T3 band
        "A4": {"s1_threshold_crossing_t": 129_601},  # over T4 band
        "A5": {"s2_2h_first_prestige_t": 43_201},  # over T5 band
        "A6": {"s3_first_prestige_t": 26_000},  # ratio 100000/26000 < 4
        "A7": {"s2_8h_min_levels_per_early_visit": 1},  # a 1-level visit
        "A8": {"s3_max_purchase_gap": 3_600},  # 3600/14400 = 25%, not < 25%
        "A9": {"s3_reset_durations": [14_400, 7_199, 6_000]},  # d2 < 50% of d1
        # v2 TREND violation: every step dips only 0.01 (inside the wiggle
        # band) but the ratio sequence 0.95, 0.94, 0.93 FALLS overall —
        # final consecutive ratio < first.
        "A10": {"o6_durations": [1_000_000, 950_000, 893_000, 830_490]},
    }
    for cid, patch in violations.items():
        measures = {**_green_measures(), **patch}
        criteria = evaluate_criteria(measures)
        assert not _result(criteria, cid)["pass"], cid
        if cid not in ("A3", "A6"):  # A3's patch legitimately moves A6 too
            others = [c for c in criteria if c["id"] not in (cid, "A6")]
            assert all(c["pass"] for c in others), (cid, [c for c in others if not c["pass"]])


def test_a10_v2_trend_form_semantics():
    """A10 v2 (TREND form, VERDICT 038 re-registration) pinned red/green.

    v2's registered delta from v1's strict per-step gate: a single-step
    ratio decrease within the 0.02 wiggle band no longer fails on its own —
    the gate is the TREND (final consecutive ratio >= first).
    """
    def a10(o6):
        measures = {**_green_measures(), "o6_durations": o6}
        return _result(evaluate_criteria(measures), "A10")["pass"]

    # In-band dip (0.90 -> 0.89), trend rises to 0.95: v1 FAILED this
    # shape, v2 passes it — the exact shape VERDICT 038 graduated on.
    assert a10([100_000, 90_000, 80_100, 76_095])
    # Same rising trend but the dip is 0.03 > the 0.02 band: FAIL.
    assert not a10([100_000, 90_000, 78_300, 76_734])
    # Dip of exactly 0.02 (0.90 -> 0.88), trend recovers to 0.90: "within
    # a 0.02 wiggle band" is inclusive, and final == first satisfies >=.
    assert a10([100_000, 90_000, 79_200, 71_280])
    # Fewer than 2 resets: unmeasurable fails loud, never skips.
    assert not a10([1_000])


def test_a10_criterion_version_matches_registered_doc_form():
    """Doc↔harness criterion-version parity guard.

    docs/design/economy-v1.md registers A10 with a version token in its
    acceptance-criteria row ("| A10 | O6 — v2, TREND form ..."); the
    harness exposes the version it implements as A10_CRITERION_VERSION.
    Re-register the criterion without syncing tools/simulate.py (or bump
    the harness without re-registering) and this goes red — same pattern
    as the parameter-table mirror in tests/test_economy_design_doc.py.
    """
    doc = REPO_ROOT / "docs" / "design" / "economy-v1.md"
    text = doc.read_text(encoding="utf-8")
    match = re.search(r"^\|\s*A10\s*\|\s*O6\s*—\s*(v\d+)\b", text, re.M)
    assert match, "economy-v1.md lost its versioned A10 acceptance-criteria row"
    assert match.group(1) == A10_CRITERION_VERSION, (
        f"criterion drift: economy-v1.md registers A10 {match.group(1)} but "
        f"tools/simulate.py implements {A10_CRITERION_VERSION} — bump both "
        "sides in the same PR"
    )


def test_table_status_matches_registered_doc_badge():
    """Doc↔harness parameter-table status parity guard.

    docs/design/economy-v1.md carries the table's registered status as the
    badge on its Status line ("**SIM-PINNED** (every numeric parameter ...",
    graduated by VERDICT 038); the harness derives run_report's label wording
    from TABLE_STATUS. Re-grade the table without syncing tools/simulate.py
    (or bump the harness without re-registering) and this goes red — same
    pattern as the A10 criterion-version guard above.
    """
    doc = REPO_ROOT / "docs" / "design" / "economy-v1.md"
    text = doc.read_text(encoding="utf-8")
    match = re.search(r"·\s*\*\*([A-Z][A-Z-]+)\*\*\s*\(every numeric", text)
    assert match, "economy-v1.md lost its parameter-table status badge"
    assert match.group(1) == TABLE_STATUS, (
        f"table-status drift: economy-v1.md registers {match.group(1)} but "
        f"tools/simulate.py reports {TABLE_STATUS} — bump both sides in the "
        "same PR"
    )
    assert TABLE_STATUS in _QUICK["label"], (
        "run_report's label no longer derives from TABLE_STATUS — the parity "
        "guard cannot protect a hard-coded status sentence"
    )
    # The two human-facing surfaces derive from the same constant: the module
    # docstring's INTEGRITY FLOOR bullet (placeholder substituted into
    # __doc__ at import) and render_summary's stderr header.
    assert TABLE_STATUS in tools.simulate.__doc__, (
        "the module docstring's INTEGRITY FLOOR bullet no longer carries "
        "TABLE_STATUS — the {TABLE_STATUS} placeholder substitution broke"
    )
    assert TABLE_STATUS in render_summary(_QUICK).splitlines()[0], (
        "render_summary's stderr header no longer derives its status wording "
        "from TABLE_STATUS"
    )
    # And the derivation is real, not a re-hard-coded literal: the RAW
    # docstring (pre-substitution) must still contain the placeholder, so a
    # future re-grade of TABLE_STATUS propagates without a docstring edit.
    raw_doc = ast.get_docstring(
        ast.parse((REPO_ROOT / "tools" / "simulate.py").read_text(encoding="utf-8"))
    )
    assert "{TABLE_STATUS}" in raw_doc, (
        "tools/simulate.py's raw module docstring lost its {TABLE_STATUS} "
        "placeholder — a hard-coded status there will silently go stale on "
        "the next re-grade"
    )


def test_report_stamps_criteria_versions_from_parity_pinned_constant():
    """Run-artifact provenance: the report records the criterion version it
    was judged under, sourced from the SAME constant the parity guard above
    pins — committed runs stay self-describing across re-registrations
    (the v1-era run on record carries the retro-stamp {"A10": "v1"})."""
    assert _QUICK["criteria_versions"] == {"A10": A10_CRITERION_VERSION}
    v1_run = REPO_ROOT / "docs" / "design" / "sim-results-2026-07-11-provisional.json"
    stamped = json.loads(v1_run.read_text(encoding="utf-8"))["criteria_versions"]
    assert stamped == {"A10": "v1"}


def test_band_endpoints_are_inclusive_and_a8_is_strict():
    """AMB-9 pinned: closed bands at both ends; A8 strictly below 25%."""
    measures = {
        **_green_measures(),
        "s3_first_purchase_t": 30,
        "s1_threshold_crossing_t": 129_600,
        "s3_first_prestige_t": 28_800,
        "s2_2h_first_prestige_t": 14_400,
        "s3_reset_durations": [28_800, 14_400, 14_400],  # exactly 50% then 100%
        "s3_max_purchase_gap": 7_199,  # one below the 25% line of 28800
    }
    criteria = evaluate_criteria(measures)
    for cid in ("A1", "A3", "A4", "A5", "A8", "A9"):
        assert _result(criteria, cid)["pass"], cid
    # A6: 129600/28800 = 4.5, still in band.
    assert _result(criteria, "A6")["pass"]
    # Nudge the gap to exactly 25%: strict '<' must fail it.
    measures["s3_max_purchase_gap"] = 7_200
    assert not _result(evaluate_criteria(measures), "A8")["pass"]


def test_unmeasured_values_fail_loud_never_skip():
    measures = {**_green_measures(), "s3_first_prestige_t": None}
    criteria = evaluate_criteria(measures)
    for cid in ("A3", "A6", "A8"):
        assert not _result(criteria, cid)["pass"], cid


# --- smoke: the quick report is complete and internally consistent ----------------


def test_quick_report_shape_and_labels():
    report = _QUICK
    assert report["report"] == "SIM-001"
    assert TABLE_STATUS in report["label"] and "not the verdict" in report["label"]
    assert report["mode"] == "quick"
    assert report["quick_mode_warning"] is not None
    for key in ("O1_time_to_first_upgrade_s", "O2_purchase_timelines",
                "O3_trajectories", "O4_prestige_times", "O5_payback_curve",
                "O6_prestige_stacking"):
        assert key in report["outputs"], key
    assert [c["id"] for c in report["criteria"]] == [f"A{i}" for i in range(1, 11)]
    assert report["all_pass"] == all(c["pass"] for c in report["criteria"])
    # The report is valid JSON and round-trips.
    assert json.loads(to_json(report)) == report
    # Ambiguities are declared, never silent.
    assert {a["id"] for a in report["ambiguities"]} >= {"AMB-1", "AMB-3", "AMB-6"}


def test_s2_visits_land_exactly_on_the_checkin_grid():
    for label, step in (("0.25", 900), ("2", 7_200), ("8", 28_800), ("24", 86_400)):
        visits = _QUICK["scenarios"]["S2"][label]["visits"]
        assert [v[0] for v in visits] == list(range(step, QUICK_HORIZON_S + 1, step))


def test_o5_payback_matches_hand_formula():
    """payback(L) = cost(L) / (base_rate * 25/100) s -> cost(0)=60 -> 240 s."""
    rows = _QUICK["outputs"]["O5_payback_curve"]["rows"]
    assert rows[0]["level"] == 0 and rows[0]["cost"] == 60
    assert rows[0]["payback_hours"]["exact"] == "1/15"  # 240 s = 1/15 h
