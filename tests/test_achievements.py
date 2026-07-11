"""Achievements/milestones layer — threshold milestones, earned-set semantics.

Written test-first for the achievements-layer slice. The contract under
test (docs/design/achievements-v0.md, PROVISIONAL parameters):

- A :class:`MilestoneSpec` is pure mechanics: kind (``owned`` — total
  generators owned / ``lifetime`` — run-lifetime earnings of a currency /
  ``prestige`` — persistent prestige-currency units held), threshold, and
  a permanent global ``bonus_percent``. Player-visible nouns live in the
  theme pack's optional ``milestones`` block.
- Milestones are EARNED once and kept forever (``state.milestones``,
  meta-progression like prestige currency): a prestige reset wipes the
  run but never the earned set.
- Awarding is an EXPLICIT action-boundary step (:func:`award_milestones`),
  never implicit inside tick/offline — production within a span reads the
  earned set at span start, so the closed-form offline credit stays
  EXACTLY equal to looped ticks by construction.
- The rate fold gains one factor with one shared floor:
  ``base_rate * count * upgrade_pct * prestige_pct * milestone_pct // 1_000_000``
  — with no milestones (pct 100) this is integer-identical to the old
  ``// 10_000`` fold, so every pre-slice pin stays byte-identical.
"""

import re
from pathlib import Path
from random import Random

import pytest

from idle_engine import GameState, GeneratorSpec, load_theme
from idle_engine import economy
from idle_engine.achievements import (
    MilestoneSpec,
    award_milestones,
    milestone_earned,
    milestone_percent,
    milestone_progress,
    milestone_reached,
)
from idle_engine.engine import (
    apply_offline_progress,
    offline_progress,
    production_per_second,
    tick,
)
from idle_engine.prestige import PrestigeSpec, apply_prestige
from idle_engine.upgrades import UpgradeSpec

REPO_ROOT = Path(__file__).resolve().parent.parent
THEMES_DIR = REPO_ROOT / "themes"
DOC = REPO_ROOT / "docs" / "design" / "achievements-v0.md"


def _spec(**overrides) -> MilestoneSpec:
    base = dict(
        spec_id="ms", kind="lifetime", subject="cur-a", threshold=100, bonus_percent=5
    )
    base.update(overrides)
    return MilestoneSpec(**base)


# --- spec validation ----------------------------------------------------------


def test_spec_rejects_unknown_kind():
    with pytest.raises(ValueError):
        _spec(kind="resets")


@pytest.mark.parametrize("bad", [0, -1])
def test_spec_rejects_non_positive_threshold(bad):
    with pytest.raises(ValueError):
        _spec(threshold=bad)


@pytest.mark.parametrize("bad", [1.0, "100", True])
def test_spec_rejects_non_int_threshold(bad):
    with pytest.raises(TypeError):
        _spec(threshold=bad)


def test_spec_rejects_negative_bonus():
    with pytest.raises(ValueError):
        _spec(bonus_percent=-1)


@pytest.mark.parametrize("bad", [2.5, "5", False])
def test_spec_rejects_non_int_bonus(bad):
    with pytest.raises(TypeError):
        _spec(bonus_percent=bad)


def test_owned_kind_takes_no_subject():
    # ``owned`` measures the TOTAL generator count; a subject would imply a
    # per-generator track that v0 deliberately does not pre-register.
    with pytest.raises(ValueError):
        _spec(kind="owned", subject="gen-a")
    assert _spec(kind="owned", subject="").kind == "owned"


@pytest.mark.parametrize("kind", ["lifetime", "prestige"])
def test_currency_kinds_require_a_subject(kind):
    with pytest.raises(ValueError):
        _spec(kind=kind, subject="")


# --- progress / reached / earned ----------------------------------------------


def test_owned_progress_sums_across_all_generators():
    spec = _spec(kind="owned", subject="", threshold=10)
    state = GameState(owned={"gen-a": 4, "gen-b": 5})
    assert milestone_progress(state, spec) == 9
    assert not milestone_reached(state, spec)
    assert milestone_reached(
        GameState(owned={"gen-a": 4, "gen-b": 5, "gen-c": 1}), spec
    )


def test_lifetime_progress_reads_one_currency():
    spec = _spec(kind="lifetime", subject="cur-a", threshold=100)
    state = GameState(lifetime={"cur-a": 99, "cur-b": 10**9})
    assert milestone_progress(state, spec) == 99
    assert not milestone_reached(state, spec)
    assert milestone_reached(GameState(lifetime={"cur-a": 100}), spec)


def test_prestige_progress_reads_persistent_units():
    spec = _spec(kind="prestige", subject="meta", threshold=5)
    assert milestone_progress(GameState(prestige={"meta": 4}), spec) == 4
    assert milestone_reached(GameState(prestige={"meta": 5}), spec)


def test_earned_means_marked_in_state_not_live_progress():
    spec = _spec(threshold=100)
    reached = GameState(lifetime={"cur-a": 10**6})
    assert milestone_reached(reached, spec)
    assert not milestone_earned(reached, spec)  # reached but never awarded
    marked = GameState(milestones={"ms": 1})
    assert milestone_earned(marked, spec)
    assert not milestone_earned(GameState(milestones={"ms": 0}), spec)  # 0 = unearned


# --- award_milestones: the explicit action-boundary step ----------------------


def test_award_marks_reached_and_skips_unreached():
    specs = [
        _spec(spec_id="hit", threshold=100),
        _spec(spec_id="miss", threshold=101),
    ]
    state = GameState(lifetime={"cur-a": 100})
    after = award_milestones(state, specs)
    assert after.milestones == {"hit": 1}
    assert milestone_earned(after, specs[0])
    assert not milestone_earned(after, specs[1])


def test_award_touches_nothing_else():
    spec = _spec(threshold=1)
    state = GameState(
        balances={"cur-a": 7},
        owned={"gen-a": 2},
        last_seen=123,
        upgrades={"up-a": 1},
        lifetime={"cur-a": 5},
        prestige={"meta": 3},
    )
    after = award_milestones(state, [spec])
    assert after.milestones == {"ms": 1}
    for field in ("balances", "owned", "last_seen", "upgrades", "lifetime", "prestige"):
        assert getattr(after, field) == getattr(state, field)


def test_award_is_idempotent_and_never_revokes():
    spec = _spec(kind="owned", subject="", threshold=10)
    rich = GameState(owned={"gen-a": 10})
    earned = award_milestones(rich, [spec])
    assert earned.milestones == {"ms": 1}
    assert award_milestones(earned, [spec]) == earned
    # Progress dropping back below the threshold never revokes the earn.
    poor = earned.with_balances(earned.balances, earned.last_seen)
    import dataclasses

    poor = dataclasses.replace(earned, owned={})
    assert award_milestones(poor, [spec]).milestones == {"ms": 1}
    assert milestone_earned(poor, spec)


def test_award_with_nothing_reached_is_a_no_op():
    spec = _spec(threshold=10**9)
    state = GameState(lifetime={"cur-a": 1})
    assert award_milestones(state, [spec]) == state


# --- milestone_percent: earned set only, additive ------------------------------


def test_percent_is_100_with_no_specs():
    assert milestone_percent(GameState(), []) == 100


def test_percent_counts_earned_only_never_live_progress():
    specs = [_spec(spec_id=f"m{i}", threshold=1, bonus_percent=5) for i in range(3)]
    reached_unearned = GameState(lifetime={"cur-a": 10**9})
    assert milestone_percent(reached_unearned, specs) == 100  # reached ≠ earned
    two_earned = GameState(milestones={"m0": 1, "m2": 1})
    assert milestone_percent(two_earned, specs) == 110


def test_percent_rejects_negative_marks():
    spec = _spec()
    with pytest.raises(ValueError):
        milestone_percent(GameState(milestones={"ms": -1}), [spec])


# --- rate fold: one shared floor, exact no-milestone compatibility -------------


def _roster():
    gen = GeneratorSpec(spec_id="gen-a", produces="cur-a", base_rate=7)
    up = UpgradeSpec(
        spec_id="up-a",
        cost_currency="cur-a",
        base_cost=1,
        cost_growth_num=115,
        cost_growth_den=100,
        target="gen-a",
        effect_percent=25,
    )
    pr = PrestigeSpec(
        awards="meta", measures="cur-a", threshold=100, award_divisor=100, bonus_percent=10
    )
    ms = _spec(spec_id="m1", kind="owned", subject="", threshold=1, bonus_percent=15)
    return gen, up, pr, ms


def test_rate_folds_milestone_percent_with_a_single_floor():
    gen, up, pr, ms = _roster()
    # upgrade_pct 125 (level 1 × 25), prestige_pct 130 (3 held × 10), milestone_pct 115.
    state = GameState(
        owned={"gen-a": 1},
        upgrades={"up-a": 1},
        prestige={"meta": 3},
        milestones={"m1": 1},
    )
    rates = production_per_second(state, [gen], [up], [pr], [ms])
    # SINGLE floor: 7*1*125*130*115 // 10**6 = 13; a second floor after the
    # old //10_000 fold would give (7*125*130//10_000=11)*115//100 = 12.
    assert 7 * 125 * 130 * 115 // 10**6 == 13
    assert rates == {"cur-a": 13}


def test_rate_without_milestone_specs_is_integer_identical():
    gen, up, pr, _ = _roster()
    state = GameState(owned={"gen-a": 3}, upgrades={"up-a": 2}, prestige={"meta": 1})
    old_fold = 7 * 3 * 150 * 110 // 10_000
    assert production_per_second(state, [gen], [up], [pr]) == {"cur-a": old_fold}
    assert production_per_second(state, [gen], [up], [pr], []) == {"cur-a": old_fold}


def test_unearned_milestones_leave_the_rate_alone():
    gen, up, pr, ms = _roster()
    state = GameState(owned={"gen-a": 5})  # milestone reached (5 ≥ 1) but unearned
    with_specs = production_per_second(state, [gen], milestone_specs=[ms])
    without = production_per_second(state, [gen])
    assert with_specs == without


# --- tick == closed-form offline stays EXACT with milestones -------------------


@pytest.mark.parametrize("seed", range(10))
def test_partitioned_ticks_equal_offline_with_earned_milestones(seed):
    rng = Random(30_000 + seed)
    gen, up, pr, ms = _roster()
    specs = [
        _spec(spec_id=f"m{i}", kind="owned", subject="", threshold=1, bonus_percent=rng.randint(0, 20))
        for i in range(3)
    ]
    earned = {f"m{i}": 1 for i in range(3) if rng.random() < 0.5}
    state = GameState(
        owned={"gen-a": rng.randint(1, 50)},
        upgrades={"up-a": rng.randint(0, 10)},
        prestige={"meta": rng.randint(0, 10)},
        milestones=earned,
        last_seen=rng.randint(0, 10**9),
    )
    total = rng.randint(0, 500_000)
    closed = offline_progress(
        state, [gen], state.last_seen, state.last_seen + total, [up], [pr], specs
    )
    cuts = sorted(rng.randint(0, total) for _ in range(3))
    walked = state
    for a, b in zip([0, *cuts], [*cuts, total]):
        walked = tick(walked, [gen], b - a, [up], [pr], specs)
    for currency, amount in closed.items():
        assert walked.balances.get(currency, 0) == state.balances.get(currency, 0) + amount
    via_offline = apply_offline_progress(
        state, [gen], state.last_seen + total, [up], [pr], specs
    )
    assert via_offline == tick(state, [gen], total, [up], [pr], specs)


def test_award_between_spans_is_the_action_boundary():
    """The published semantics: production reads the earned set at span
    start; awarding happens BETWEEN spans (like a purchase), and the two
    halves recompose exactly."""
    gen, up, pr, ms = _roster()
    state = GameState(owned={"gen-a": 1}, last_seen=0)
    first = tick(state, [gen], 100, milestone_specs=[ms])
    awarded = award_milestones(first, [ms])
    assert awarded.milestones == {"m1": 1}
    second = tick(awarded, [gen], 100, milestone_specs=[ms])
    # First span at pct 100 (unearned), second at pct 115 (earned): the
    # boundary is explicit and deterministic.
    assert second.balances["cur-a"] == 7 * 100 + (7 * 100 * 100 * 115 // 10**6) * 100


# --- prestige interaction: milestones are meta-progression ---------------------


def test_apply_prestige_preserves_earned_milestones():
    pr = PrestigeSpec(
        awards="meta", measures="cur-a", threshold=100, award_divisor=100, bonus_percent=10
    )
    state = GameState(
        balances={"cur-a": 500},
        owned={"gen-a": 12},
        upgrades={"up-a": 3},
        lifetime={"cur-a": 400},
        prestige={"meta": 1},
        milestones={"owned-1": 1, "lifetime-1": 1},
        last_seen=777,
    )
    after = apply_prestige(state, pr)
    assert after.milestones == {"owned-1": 1, "lifetime-1": 1}
    assert after.balances == {} and after.owned == {} and after.lifetime == {}
    assert after.last_seen == 777


# --- pre-registered builders (economy) ------------------------------------------


def test_builder_emits_the_nine_preregistered_slots():
    specs = economy.build_milestone_specs("cur-a", "meta")
    assert [s.spec_id for s in specs] == [
        "owned-1",
        "owned-2",
        "owned-3",
        "lifetime-1",
        "lifetime-2",
        "lifetime-3",
        "prestige-1",
        "prestige-2",
        "prestige-3",
    ]
    by_id = {s.spec_id: s for s in specs}
    for i, threshold in enumerate(economy.MILESTONE_OWNED_THRESHOLDS, 1):
        spec = by_id[f"owned-{i}"]
        assert (spec.kind, spec.subject, spec.threshold) == ("owned", "", threshold)
    for i, threshold in enumerate(economy.MILESTONE_LIFETIME_THRESHOLDS, 1):
        spec = by_id[f"lifetime-{i}"]
        assert (spec.kind, spec.subject, spec.threshold) == ("lifetime", "cur-a", threshold)
    for i, threshold in enumerate(economy.MILESTONE_PRESTIGE_THRESHOLDS, 1):
        spec = by_id[f"prestige-{i}"]
        assert (spec.kind, spec.subject, spec.threshold) == ("prestige", "meta", threshold)
    assert all(s.bonus_percent == economy.MILESTONE_BONUS_PERCENT for s in specs)


def test_builder_ladders_are_strictly_increasing():
    for ladder in (
        economy.MILESTONE_OWNED_THRESHOLDS,
        economy.MILESTONE_LIFETIME_THRESHOLDS,
        economy.MILESTONE_PRESTIGE_THRESHOLDS,
    ):
        assert list(ladder) == sorted(set(ladder)), "ladder rungs must strictly increase"


def test_builder_without_prestige_track_emits_six_slots():
    specs = economy.build_milestone_specs("cur-a", None)
    assert [s.spec_id for s in specs] == [
        "owned-1",
        "owned-2",
        "owned-3",
        "lifetime-1",
        "lifetime-2",
        "lifetime-3",
    ]


def test_theme_milestone_specs_bind_the_prestige_track():
    theme = load_theme(THEMES_DIR / "egg-farm.yaml")
    specs = theme.milestone_specs()
    assert len(specs) == 9
    by_id = {s.spec_id: s for s in specs}
    assert by_id["lifetime-1"].subject == theme.prestige.measures
    assert by_id["prestige-1"].subject == theme.prestige.currency


def test_theme_milestone_specs_without_prestige_fall_back(tmp_path):
    src = (THEMES_DIR / "egg-farm.yaml").read_text(encoding="utf-8")
    stripped, sep, rest = src.partition("\nprestige:")
    assert sep
    _, _, tail = rest.partition("\nlabels:")
    stripped = stripped + "\nlabels:" + tail
    # also drop the milestones block if present (it may name prestige slots)
    head, sep2, _ = stripped.partition("\nmilestones:")
    if sep2:
        stripped = head
    path = tmp_path / "egg-farm.yaml"
    path.write_text(stripped, encoding="utf-8")
    theme = load_theme(path)
    assert theme.prestige is None
    specs = theme.milestone_specs()
    assert len(specs) == 6
    by_id = {s.spec_id: s for s in specs}
    # Deterministic fallback: lifetime track measures the FIRST declared
    # generator's produced currency.
    first_generator = next(iter(theme.generators.values()))
    assert by_id["lifetime-1"].subject == first_generator.produces


@pytest.mark.parametrize("path", sorted(THEMES_DIR.glob("*.yaml")), ids=lambda p: p.stem)
def test_every_pack_gets_identical_milestone_mechanics(path):
    """CORE/SKIN: the milestone SET is engine-derived — every pack with a
    prestige track gets the same nine slots, same thresholds, same bonuses."""
    specs = load_theme(path).milestone_specs()
    assert [s.spec_id for s in specs] == [
        f"{kind}-{i}" for kind in ("owned", "lifetime", "prestige") for i in (1, 2, 3)
    ]
    assert [s.threshold for s in specs] == list(
        economy.MILESTONE_OWNED_THRESHOLDS
        + economy.MILESTONE_LIFETIME_THRESHOLDS
        + economy.MILESTONE_PRESTIGE_THRESHOLDS
    )


def test_milestone_specs_carry_no_display_data():
    for spec in load_theme(THEMES_DIR / "egg-farm.yaml").milestone_specs():
        assert not hasattr(spec, "name")
        assert not hasattr(spec, "emoji")
        assert not hasattr(spec, "description")


# --- doc honesty: pre-registration contract ------------------------------------

PINNED_SCALARS = ["MILESTONE_BONUS_PERCENT"]
PINNED_LADDERS = [
    "MILESTONE_OWNED_THRESHOLDS",
    "MILESTONE_LIFETIME_THRESHOLDS",
    "MILESTONE_PRESTIGE_THRESHOLDS",
]


def test_design_doc_exists_and_is_provisional():
    assert DOC.is_file(), f"{DOC} missing — the pre-registered achievements design doc"
    text = DOC.read_text(encoding="utf-8")
    assert "PROVISIONAL" in text
    assert "prestige" in text  # the persistence-through-prestige decision is recorded


def test_design_doc_parameter_table_mirrors_engine_values():
    text = DOC.read_text(encoding="utf-8")
    stale = []
    for name in PINNED_SCALARS:
        value = getattr(economy, name)
        if not re.search(rf"\|\s*`{name}`\s*\|\s*{value}\s*\|", text):
            stale.append(f"{name}={value}")
    for name in PINNED_LADDERS:
        values = ", ".join(f"{v:,}" for v in getattr(economy, name))
        if not re.search(rf"\|\s*`{name}`\s*\|\s*{re.escape(values)}\s*\|", text):
            stale.append(f"{name}=({values})")
    assert not stale, (
        "achievements-v0.md parameter table out of sync with idle_engine/economy.py "
        f"(tune + re-register in the SAME PR): {stale}"
    )
