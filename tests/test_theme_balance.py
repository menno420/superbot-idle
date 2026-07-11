"""Bounded theme multipliers — the founding contract's last clause, exercised.

README § CORE/SKIN split, rule 2: theme packs are DATA ONLY … "Balance
multipliers only within schema-declared bounds." This suite pins the
MECHANISM three layers deep (defense in depth):

1. **Schema** — the bounds 90..110 are DECLARED IN the JSON schema
   (min/max on ``balance[].rate_multiplier_pct``), so the gate reds on
   out-of-bounds or wrong-typed values before any code runs.
2. **Loader** — ``idle_engine.theme.load_theme`` validates the same
   bounds independently of the gate; an out-of-bounds pack raises even
   if it somehow bypassed CI.
3. **Engine** — the multiplier folds into the single-floor integer rate
   composition: neutral (100 / absent) is BYTE-IDENTICAL to the
   pre-multiplier fold, and in-bounds 90%/110% fixtures drive tick and
   closed-form offline to exactly equal, hand-computed values.

The catalog stays NEUTRAL: no shipped pack declares a ``balance`` block —
actual non-neutral values are sim-gated (Q-0264,
docs/design/theme-balance-v0.md) and pinned so here.
"""

import json
from pathlib import Path

import pytest
import yaml

from idle_engine import GameState, GeneratorSpec, load_theme
from idle_engine.engine import (
    apply_offline_progress,
    offline_progress,
    production_per_second,
    tick,
)
from idle_engine.theme import (
    RATE_MULTIPLIER_MAX,
    RATE_MULTIPLIER_MIN,
    RATE_MULTIPLIER_NEUTRAL,
)
from tools.theme_gate import main as gate_main
from tools.theme_gate import validate_file

REPO_ROOT = Path(__file__).resolve().parent.parent
SCHEMA_PATH = REPO_ROOT / "schema" / "theme.schema.json"
THEMES_DIR = REPO_ROOT / "themes"
EGG_FARM = THEMES_DIR / "egg-farm.yaml"


def egg_farm_data() -> dict:
    return yaml.safe_load(EGG_FARM.read_text(encoding="utf-8"))


def write_pack(tmp_path: Path, data: dict) -> Path:
    path = tmp_path / f"{data['theme']['id']}.yaml"
    path.write_text(yaml.safe_dump(data, allow_unicode=True), encoding="utf-8")
    return path


def with_balance(entries: list[dict]) -> dict:
    data = egg_farm_data()
    data["balance"] = entries
    return data


# --- the bounds are SCHEMA-DECLARED (the contract's exact wording) -----------


def test_bounds_are_declared_in_the_json_schema():
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    pct = schema["properties"]["balance"]["items"]["properties"][
        "rate_multiplier_pct"
    ]
    assert pct["type"] == "integer"
    assert pct["minimum"] == RATE_MULTIPLIER_MIN == 90
    assert pct["maximum"] == RATE_MULTIPLIER_MAX == 110
    assert RATE_MULTIPLIER_NEUTRAL == 100
    assert RATE_MULTIPLIER_MIN < RATE_MULTIPLIER_NEUTRAL < RATE_MULTIPLIER_MAX


def test_balance_entries_reject_unknown_fields():
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    items = schema["properties"]["balance"]["items"]
    assert items["additionalProperties"] is False
    assert set(items["required"]) == {"generator", "rate_multiplier_pct"}


# --- gate: red on out-of-bounds or wrong type, green in bounds ---------------


def _assert_rejected(tmp_path: Path, data: dict, needle: str) -> None:
    path = write_pack(tmp_path, data)
    errors = validate_file(path)
    assert errors, f"expected red gate ({needle}), got a pass"
    assert any(needle in e for e in errors), f"{needle!r} not named in: {errors}"
    assert gate_main(["theme_gate", str(tmp_path)]) == 1


def test_gate_accepts_in_bounds_multipliers(tmp_path):
    for pct in (90, 95, 100, 105, 110):
        data = with_balance([{"generator": "tier1", "rate_multiplier_pct": pct}])
        assert validate_file(write_pack(tmp_path, data)) == [], f"pct={pct}"


def test_gate_rejects_out_of_bounds_multipliers(tmp_path):
    for pct in (89, 111, 0, -5, 200, 1_000_000):
        data = with_balance([{"generator": "tier1", "rate_multiplier_pct": pct}])
        _assert_rejected(tmp_path, data, "rate_multiplier_pct")


def test_gate_rejects_wrong_typed_multipliers(tmp_path):
    for bad in ("105", 100.5, True, None, [100], {"pct": 100}):
        data = with_balance([{"generator": "tier1", "rate_multiplier_pct": bad}])
        _assert_rejected(tmp_path, data, "rate_multiplier_pct")


def test_gate_rejects_dangling_generator_reference(tmp_path):
    data = with_balance([{"generator": "nonexistent", "rate_multiplier_pct": 105}])
    _assert_rejected(tmp_path, data, "generator")


def test_gate_rejects_duplicate_generator_entries(tmp_path):
    data = with_balance(
        [
            {"generator": "tier1", "rate_multiplier_pct": 105},
            {"generator": "tier1", "rate_multiplier_pct": 95},
        ]
    )
    _assert_rejected(tmp_path, data, "duplicate")


def test_gate_rejects_empty_balance_list(tmp_path):
    _assert_rejected(tmp_path, with_balance([]), "balance")


def test_gate_rejects_smuggled_balance_fields(tmp_path):
    # the block tunes ONE bounded knob; any other economy field is smuggling
    for smuggled in ("base_rate", "cost_multiplier", "threshold"):
        data = with_balance(
            [{"generator": "tier1", "rate_multiplier_pct": 105, smuggled: 9}]
        )
        _assert_rejected(tmp_path, data, smuggled)


def test_pack_without_balance_block_still_passes(tmp_path):
    # the block is OPTIONAL — every pre-slice pack stays valid (additive v1)
    data = egg_farm_data()
    assert "balance" not in data
    assert validate_file(write_pack(tmp_path, data)) == []


# --- loader: validates bounds INDEPENDENTLY of the gate (defense in depth) ---


def test_loader_maps_balance_block_onto_generator_specs(tmp_path):
    data = with_balance([{"generator": "tier1", "rate_multiplier_pct": 110}])
    theme = load_theme(write_pack(tmp_path, data))
    assert theme.generators["tier1"].rate_multiplier_pct == 110
    (spec,) = theme.generator_specs()
    assert spec.rate_multiplier_pct == 110


def test_loader_defaults_to_neutral_when_block_absent():
    theme = load_theme(EGG_FARM)
    assert all(
        g.rate_multiplier_pct == RATE_MULTIPLIER_NEUTRAL
        for g in theme.generators.values()
    )
    assert all(
        s.rate_multiplier_pct == RATE_MULTIPLIER_NEUTRAL
        for s in theme.generator_specs()
    )


def test_loader_defaults_unlisted_generators_to_neutral(tmp_path):
    # a pack may tune a subset; every unlisted generator stays neutral
    data = with_balance([{"generator": "tier1", "rate_multiplier_pct": 90}])
    data["generators"].append(
        dict(data["generators"][0], id="tier2", name="second maker")
    )
    theme = load_theme(write_pack(tmp_path, data))
    assert theme.generators["tier1"].rate_multiplier_pct == 90
    assert theme.generators["tier2"].rate_multiplier_pct == RATE_MULTIPLIER_NEUTRAL


def test_loader_rejects_out_of_bounds_multipliers(tmp_path):
    for pct in (89, 111, 0, -5):
        data = with_balance([{"generator": "tier1", "rate_multiplier_pct": pct}])
        with pytest.raises(ValueError, match="90..110"):
            load_theme(write_pack(tmp_path, data))


def test_loader_accepts_the_exact_bounds(tmp_path):
    for pct in (RATE_MULTIPLIER_MIN, RATE_MULTIPLIER_MAX):
        data = with_balance([{"generator": "tier1", "rate_multiplier_pct": pct}])
        theme = load_theme(write_pack(tmp_path, data))
        assert theme.generators["tier1"].rate_multiplier_pct == pct


def test_loader_rejects_wrong_typed_multipliers(tmp_path):
    for bad in ("105", 100.5, True, None):
        data = with_balance([{"generator": "tier1", "rate_multiplier_pct": bad}])
        with pytest.raises(ValueError, match="rate_multiplier_pct"):
            load_theme(write_pack(tmp_path, data))


def test_loader_rejects_dangling_generator_reference(tmp_path):
    data = with_balance([{"generator": "ghost", "rate_multiplier_pct": 105}])
    with pytest.raises(ValueError, match="not a declared generator"):
        load_theme(write_pack(tmp_path, data))


def test_loader_rejects_duplicate_generator_entries(tmp_path):
    data = with_balance(
        [
            {"generator": "tier1", "rate_multiplier_pct": 105},
            {"generator": "tier1", "rate_multiplier_pct": 95},
        ]
    )
    with pytest.raises(ValueError, match="duplicate"):
        load_theme(write_pack(tmp_path, data))


def test_loader_rejects_empty_balance_list(tmp_path):
    data = with_balance([])
    with pytest.raises(ValueError, match="balance"):
        load_theme(write_pack(tmp_path, data))


# --- engine: single-floor fold, neutral byte-identity, exactness -------------


def _spec(base_rate: int, pct: int | None = None) -> GeneratorSpec:
    if pct is None:
        return GeneratorSpec(spec_id="g", produces="c", base_rate=base_rate)
    return GeneratorSpec(
        spec_id="g", produces="c", base_rate=base_rate, rate_multiplier_pct=pct
    )


def test_generator_spec_defaults_to_neutral_multiplier():
    assert _spec(3).rate_multiplier_pct == RATE_MULTIPLIER_NEUTRAL


def test_generator_spec_rejects_invalid_multiplier_types():
    for bad in ("105", 100.5, True):
        with pytest.raises(TypeError):
            GeneratorSpec(
                spec_id="g", produces="c", base_rate=1, rate_multiplier_pct=bad
            )
    with pytest.raises(ValueError):
        GeneratorSpec(spec_id="g", produces="c", base_rate=1, rate_multiplier_pct=-1)


def test_neutral_multiplier_is_byte_identical_to_absent():
    """The pin: explicit 100 == absent field, across awkward magnitudes."""
    state = GameState(owned={"g": 7}, last_seen=0)
    for base_rate in (1, 3, 7, 999, 1_000):
        implicit = production_per_second(state, [_spec(base_rate)])
        explicit = production_per_second(state, [_spec(base_rate, 100)])
        assert implicit == explicit
        assert all(isinstance(v, int) for v in explicit.values())


def test_hand_computed_rates_at_90_and_110():
    # 110%: 3 * 4 * 100 * 100 * 100 * 110 // 10^8 = 13.2 -> 13 (one floor)
    state = GameState(owned={"g": 4}, last_seen=0)
    assert production_per_second(state, [_spec(3, 110)]) == {"c": 13}
    # 90%: 3 * 4 * 100 * 100 * 100 * 90 // 10^8 = 10.8 -> 10
    assert production_per_second(state, [_spec(3, 90)]) == {"c": 10}
    # neutral control: 3 * 4 = 12
    assert production_per_second(state, [_spec(3, 100)]) == {"c": 12}


def test_tick_equals_closed_form_offline_with_multipliers():
    """The flagship invariant survives the new factor, exactly."""
    specs = [
        GeneratorSpec("t1", "c", 3, rate_multiplier_pct=110),
        GeneratorSpec("t2", "c", 7, rate_multiplier_pct=90),
    ]
    state = GameState(owned={"t1": 5, "t2": 2}, last_seen=1_000)
    span = 3_607  # awkward, non-round
    closed = offline_progress(state, specs, 1_000, 1_000 + span)
    walked = state
    for _ in range(span):
        walked = tick(walked, specs, 1)
    assert walked.balances == closed
    applied = apply_offline_progress(state, specs, 1_000 + span)
    assert applied.balances == closed
    # hand value: rate = (5*3*110 + 2*7*90)//100-fold = 16 + 12 = 28/s
    assert closed == {"c": 28 * span}


def test_theme_fixture_at_110_drives_tick_and_offline_exactly(tmp_path):
    data = with_balance([{"generator": "tier1", "rate_multiplier_pct": 110}])
    theme = load_theme(write_pack(tmp_path, data))
    specs = theme.generator_specs()
    state = GameState(owned={"tier1": 10}, last_seen=0)
    # base_rate 1, count 10, pct 110 -> 1*10*110*10^6 // 10^8 = 11/s
    assert production_per_second(state, specs) == {"primary": 11}
    assert tick(state, specs, 60).balances == {"primary": 660}
    assert offline_progress(state, specs, 0, 60) == {"primary": 660}


def test_theme_fixture_at_90_drives_tick_and_offline_exactly(tmp_path):
    data = with_balance([{"generator": "tier1", "rate_multiplier_pct": 90}])
    theme = load_theme(write_pack(tmp_path, data))
    specs = theme.generator_specs()
    state = GameState(owned={"tier1": 10}, last_seen=0)
    # base_rate 1, count 10, pct 90 -> 1*10*90*10^6 // 10^8 = 9/s
    assert production_per_second(state, specs) == {"primary": 9}
    assert tick(state, specs, 60).balances == {"primary": 540}
    assert offline_progress(state, specs, 0, 60) == {"primary": 540}


def test_neutral_fold_identity_holds_across_magnitudes():
    """(x * 100) // 10^8 == x // 10^6 — the exact identity the extension
    rides on, checked over adversarial integer-floor territory."""
    for x in (0, 1, 999_999, 1_000_000, 1_000_001, 10**8 - 1, 10**8, 7**20):
        assert (x * 100) // 100_000_000 == x // 1_000_000


# --- catalog stays neutral: non-neutral values are sim-gated ------------------


def test_no_shipped_pack_declares_a_balance_block():
    """MECHANISM shipped, VALUES sim-gated (Q-0264): every shipped pack is
    neutral until the Simulator blesses a non-neutral tuning —
    docs/design/theme-balance-v0.md is the pre-registered statement."""
    for pack in sorted(THEMES_DIR.glob("*.yaml")):
        data = yaml.safe_load(pack.read_text(encoding="utf-8"))
        assert "balance" not in data, (
            f"{pack.stem} declares a balance block — non-neutral values "
            f"require Q-0264 approval (docs/design/theme-balance-v0.md)"
        )


def test_sim_gating_addendum_is_on_record():
    doc = REPO_ROOT / "docs" / "design" / "theme-balance-v0.md"
    text = doc.read_text(encoding="utf-8")
    assert "Q-0264" in text
    assert "90" in text and "110" in text


def test_all_shipped_packs_still_pass_the_gate():
    assert gate_main(["theme_gate", str(THEMES_DIR)]) == 0
