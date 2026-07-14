"""Cross-language setup-code test vectors — regenerate-or-red + replay.

``tests/vectors/setup-codes.v1.json`` is the machine-readable parity
file a foreign implementation (the websites lane's encoder) consumes;
``tools/gen_setup_vectors.py`` generates it FROM the real codec. Two
duties here:

1. **Regenerate-or-red** (the repo's md-parity pattern, applied to
   JSON): the committed file must be byte-identical to a fresh
   in-memory regeneration — edit the codec, the catalog, or the file
   alone and this reds until ``python3 tools/gen_setup_vectors.py``
   is re-run and committed.
2. **Consumer replay**: every committed vector is replayed through the
   live codec exactly the way a foreign suite would replay it through
   its own — valid vectors encode AND decode to their stated values
   (intermediates recomputed independently via ``zlib.crc32``, not the
   module's helper), tolerance vectors decode to the same config, and
   error vectors raise EXACTLY their stated taxonomy class.
"""

import json
import zlib
from pathlib import Path

import pytest

from idle_engine import provisioning
from idle_engine.provisioning import SetupConfig, decode_setup, encode_setup
from tools.gen_setup_vectors import DRIFT_HINT, VECTORS_PATH, render

REPO_ROOT = Path(__file__).resolve().parent.parent
THEMES_DIR = REPO_ROOT / "themes"

DOC = json.loads(VECTORS_PATH.read_text(encoding="utf-8"))
VALID = DOC["vectors"]["valid"]
TOLERANCE = DOC["vectors"]["tolerance"]
ERRORS = DOC["vectors"]["errors"]

_ids = lambda vectors: [v["name"] for v in vectors]  # noqa: E731


def _config(vector) -> SetupConfig:
    return SetupConfig(**vector["config"])


# --- regenerate-or-red ---------------------------------------------------------


def _assert_byte_identical_to_regeneration(committed: str) -> None:
    assert committed == render(), DRIFT_HINT


def test_committed_vector_file_is_byte_identical_to_regeneration():
    _assert_byte_identical_to_regeneration(VECTORS_PATH.read_text(encoding="utf-8"))


def test_drift_red_names_the_catalog_question_and_the_regen_command():
    # The hint is the developer-facing contract of a drift red: it must
    # name the likely cause (a catalog change) and the exact fix.
    with pytest.raises(AssertionError) as excinfo:
        _assert_byte_identical_to_regeneration(render() + "# drifted\n")
    message = str(excinfo.value)
    assert "Did the catalog change" in message
    assert "themes/*.yaml" in message
    assert "python3 tools/gen_setup_vectors.py" in message


# --- file shape: what a foreign consumer relies on -------------------------------


def test_document_pins_the_v1_contract_constants():
    assert DOC["format"] == "superbot-idle-setup-code-vectors"
    assert DOC["format_version"] == 1
    assert DOC["setup_code_version"] == provisioning.SETUP_CODE_VERSION
    assert DOC["code_prefix"] == provisioning.CODE_PREFIX
    assert DOC["alphabet"] == provisioning._ALPHABET
    assert DOC["feature_bits"] == provisioning.FEATURE_BITS
    assert DOC["lookalike_folds"] == {"O": "0", "I": "1", "L": "1"}


def test_counts_match_the_vector_arrays():
    assert DOC["counts"] == {
        "valid": len(VALID),
        "tolerance": len(TOLERANCE),
        "errors": len(ERRORS),
    }
    assert len(VALID) and len(TOLERANCE) and len(ERRORS)


def test_every_shipped_pack_has_valid_vectors():
    # This is the red a pack add/remove hits first — carry the same hint.
    shipped = sorted(path.stem for path in THEMES_DIR.glob("*.yaml"))
    assert shipped == DOC["themes"], DRIFT_HINT
    assert {v["config"]["theme_id"] for v in VALID} == set(shipped), DRIFT_HINT


def test_valid_vectors_cover_all_on_all_off_and_each_single_feature():
    combos_per_theme = {}
    for vector in VALID:
        combo = tuple(sorted(k for k, v in vector["config"].items() if k != "theme_id" and v))
        combos_per_theme.setdefault(vector["config"]["theme_id"], set()).add(combo)
    features = sorted(provisioning.FEATURE_BITS)
    expected = {tuple(features), ()} | {(f,) for f in features}
    for theme_id, combos in combos_per_theme.items():
        assert combos == expected, f"{theme_id} vector combos drifted"


def test_error_vectors_use_only_documented_decode_error_classes():
    documented = set(DOC["decode_error_classes"])
    assert documented == {
        "MalformedCodeError", "UnknownVersionError", "ChecksumError", "UnknownFeatureError",
    }
    assert {v["error"] for v in ERRORS} == documented  # every class exercised
    for name in documented:
        assert issubclass(getattr(provisioning, name), provisioning.SetupCodeError)


# --- consumer replay: valid vectors ----------------------------------------------


@pytest.mark.parametrize("vector", VALID, ids=_ids(VALID))
def test_valid_vector_encodes_to_its_code(vector):
    assert encode_setup(_config(vector)) == vector["code"]


@pytest.mark.parametrize("vector", VALID, ids=_ids(VALID))
def test_valid_vector_decodes_to_its_config(vector):
    assert decode_setup(vector["code"]) == _config(vector)


@pytest.mark.parametrize("vector", VALID, ids=_ids(VALID))
def test_valid_vector_intermediates_recompute_from_the_published_grammar(vector):
    # Independent recomputation — zlib.crc32 straight off the doc's field
    # table, not the module's private helpers — so the intermediates a
    # foreign implementation debugs against are contract-true.
    config = vector["config"]
    flags = sum(
        1 << bit for name, bit in provisioning.FEATURE_BITS.items() if config[name]
    )
    assert f"{flags:02x}" == vector["flags_byte"]
    payload = bytes([flags]) + config["theme_id"].encode("ascii")
    assert payload.hex() == vector["payload_hex"]
    crc16 = (zlib.crc32(payload) & 0xFFFF).to_bytes(2, "big")
    assert crc16.hex() == vector["crc16_hex"]
    body = provisioning._crockford_decode(vector["code"].split("-", 1)[1])
    assert body == payload + crc16, "code body is not payload ++ checksum"


# --- consumer replay: tolerance vectors -------------------------------------------


@pytest.mark.parametrize("vector", TOLERANCE, ids=_ids(TOLERANCE))
def test_tolerance_vector_decodes_to_the_same_config(vector):
    config = _config(vector)
    assert decode_setup(vector["input"]) == config
    assert vector["canonical"] == encode_setup(config)
    assert vector["input"] != vector["canonical"], "tolerance vector is not a variant"


# --- consumer replay: error vectors ------------------------------------------------


@pytest.mark.parametrize("vector", ERRORS, ids=_ids(ERRORS))
def test_error_vector_raises_exactly_its_stated_class(vector):
    expected = getattr(provisioning, vector["error"])
    with pytest.raises(expected) as excinfo:
        decode_setup(vector["input"])
    # EXACT class, not a subclass — the taxonomy stays distinct.
    assert type(excinfo.value) is expected
