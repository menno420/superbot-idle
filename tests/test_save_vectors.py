"""Golden save-file corpus — regenerate-or-red + consumer replay.

``tests/vectors/saves.v2.json`` is the machine-readable persistence
corpus that pins SAVE FORMAT v2 and the v1→v2 migration byte-exactly;
``tools/gen_save_vectors.py`` generates it FROM the real codec. Two
duties here, mirroring ``tests/test_setup_vectors.py``:

1. **Regenerate-or-red**: the committed file must be byte-identical to
   a fresh in-memory regeneration — edit the codec, a migration, or the
   file alone and this reds until ``python3 tools/gen_save_vectors.py``
   is re-run and committed. A v3 bump that changes what v1/v2 documents
   load into therefore CANNOT land silently.
2. **Consumer replay**: every committed vector is replayed through the
   live codec — golden v2 vectors dump AND load to their stated values
   (canonical form recomputed independently via ``json`` off the doc's
   published grammar, not the module's own dump), golden v1 vectors
   migrate byte-exactly to their stated v2 results, and error vectors
   raise EXACTLY their stated taxonomy class.
"""

import json

import pytest

from idle_engine import GameState, persistence
from idle_engine.persistence import STATE_VERSION, SaveError, dump_state, load_state
from tools.gen_save_vectors import VECTORS_PATH, render

DOC = json.loads(VECTORS_PATH.read_text(encoding="utf-8"))
GOLDEN_V2 = DOC["vectors"]["golden_v2"]
GOLDEN_V1 = DOC["vectors"]["golden_v1_migration"]
ERRORS = DOC["vectors"]["errors"]

_ids = lambda vectors: [v["name"] for v in vectors]  # noqa: E731


def _state(vector) -> GameState:
    return GameState(**vector["state"])


def _canonicalize(doc) -> str:
    """The published canonical grammar, recomputed independently of dump_state."""
    return json.dumps(doc, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


# --- regenerate-or-red ---------------------------------------------------------


def test_committed_vector_file_is_byte_identical_to_regeneration():
    committed = VECTORS_PATH.read_text(encoding="utf-8")
    assert committed == render(), (
        "tests/vectors/saves.v2.json drifted from the live save codec — "
        "regenerate with: python3 tools/gen_save_vectors.py (regenerate-or-red). "
        "If this red comes from a format change: that is a state_version bump, "
        "and the corpus must gain migrated-golden vectors in the SAME PR "
        "(docs/persistence.md § Golden save corpus)."
    )


# --- file shape: what a consumer relies on -----------------------------------------


def test_document_pins_the_contract_constants():
    assert DOC["format"] == "superbot-idle-save-vectors"
    assert DOC["format_version"] == 1
    assert DOC["state_version"] == STATE_VERSION == 2
    assert DOC["contract"] == "docs/persistence.md"
    assert DOC["v2_fields"] == sorted(persistence._CURRENT_KEYS)
    # The FROZEN v1 field set: v2 minus the milestones field added at v2.
    assert DOC["v1_fields"] == sorted(persistence._CURRENT_KEYS - {"milestones"})


def test_counts_match_the_vector_arrays():
    assert DOC["counts"] == {
        "golden_v2": len(GOLDEN_V2),
        "golden_v1_migration": len(GOLDEN_V1),
        "errors": len(ERRORS),
    }
    assert len(GOLDEN_V2) and len(GOLDEN_V1) and len(ERRORS)


def test_golden_v2_covers_the_representative_categories():
    names = set(_ids(GOLDEN_V2))
    assert {
        "fresh",
        "mid-run-upgrades",
        "milestones-earned",
        "post-prestige",
        "extreme-magnitude",
        "all-zero-entries",
        "non-ascii-ids",
    } <= names


def test_error_vectors_use_only_documented_load_error_classes():
    documented = set(DOC["load_error_classes"])
    assert documented == {
        "MalformedSaveError",
        "UnknownVersionError",
        "FieldSetError",
        "FieldTypeError",
        "NegativeValueError",
    }
    assert {v["error"] for v in ERRORS} == documented  # every class exercised
    for name in documented:
        assert issubclass(getattr(persistence, name), SaveError)


# --- consumer replay: golden v2 -----------------------------------------------------


@pytest.mark.parametrize("vector", GOLDEN_V2, ids=_ids(GOLDEN_V2))
def test_golden_v2_state_dumps_to_its_save(vector):
    assert dump_state(_state(vector)) == vector["save"]


@pytest.mark.parametrize("vector", GOLDEN_V2, ids=_ids(GOLDEN_V2))
def test_golden_v2_save_loads_to_its_state(vector):
    assert load_state(vector["save"]) == _state(vector)


@pytest.mark.parametrize("vector", GOLDEN_V2, ids=_ids(GOLDEN_V2))
def test_golden_v2_save_is_a_canonical_fixed_point(vector):
    # dump(load(t)) == t, and the spelling matches the PUBLISHED grammar
    # recomputed independently (sorted keys, compact separators, ASCII).
    assert dump_state(load_state(vector["save"])) == vector["save"]
    assert _canonicalize(json.loads(vector["save"])) == vector["save"]
    assert vector["save"].isascii()


@pytest.mark.parametrize("vector", GOLDEN_V2, ids=_ids(GOLDEN_V2))
def test_golden_v2_document_shape_is_the_frozen_v2_field_table(vector):
    doc = json.loads(vector["save"])
    assert sorted(doc) == DOC["v2_fields"]
    assert doc["state_version"] == 2


def test_extreme_magnitude_vector_really_is_extreme():
    vector = next(v for v in GOLDEN_V2 if v["name"] == "extreme-magnitude")
    assert max(vector["state"]["balances"].values()) >= 10**300
    assert vector["state"]["last_seen"] >= 10**300


def test_all_zero_vector_pins_zero_entries_as_content():
    vector = next(v for v in GOLDEN_V2 if v["name"] == "all-zero-entries")
    state = load_state(vector["save"])
    assert state.balances == {"cur-a": 0}  # {'a': 0} != {} — never pruned
    assert state != GameState()


# --- consumer replay: golden v1 migration -------------------------------------------


@pytest.mark.parametrize("vector", GOLDEN_V1, ids=_ids(GOLDEN_V1))
def test_golden_v1_document_has_the_frozen_v1_field_set(vector):
    doc = json.loads(vector["v1"])
    assert sorted(doc) == DOC["v1_fields"]
    assert doc["state_version"] == 1


@pytest.mark.parametrize("vector", GOLDEN_V1, ids=_ids(GOLDEN_V1))
def test_golden_v1_migrates_byte_exactly_to_its_expected_v2(vector):
    # THE pin: the v1→v2 migration result, frozen forever. A v3 that
    # changes what old saves become must regenerate this file in the
    # same PR — regenerate-or-red makes the change loud and reviewed.
    assert dump_state(load_state(vector["v1"])) == vector["expected_v2"]


@pytest.mark.parametrize("vector", GOLDEN_V1, ids=_ids(GOLDEN_V1))
def test_golden_v1_migrated_state_is_a_first_class_v2_citizen(vector):
    migrated = load_state(vector["v1"])
    assert load_state(vector["expected_v2"]) == migrated
    assert dump_state(load_state(vector["expected_v2"])) == vector["expected_v2"]


@pytest.mark.parametrize("vector", GOLDEN_V1, ids=_ids(GOLDEN_V1))
def test_golden_v1_migration_adds_exactly_an_empty_milestones_field(vector):
    v1_doc = json.loads(vector["v1"])
    v2_doc = json.loads(vector["expected_v2"])
    assert v2_doc["milestones"] == {}  # achievements post-date v1
    assert v2_doc["state_version"] == 2
    # Every other field rides through unchanged — migration invents nothing.
    for field in DOC["v1_fields"]:
        if field != "state_version":
            assert v2_doc[field] == v1_doc[field], field


# --- consumer replay: error vectors --------------------------------------------------


@pytest.mark.parametrize("vector", ERRORS, ids=_ids(ERRORS))
def test_error_vector_raises_exactly_its_stated_class(vector):
    expected = getattr(persistence, vector["error"])
    with pytest.raises(expected) as excinfo:
        load_state(vector["input"])
    # EXACT class, not a subclass — the taxonomy stays distinct.
    assert type(excinfo.value) is expected
