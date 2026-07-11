"""SETUP-CODE FORMAT v1 — contract tests (slice (e)).

Covers the full published contract in ``docs/provisioning.md``:
round-trips across every shipped theme x every v1 feature combination,
determinism, paste tolerance (case, hyphens, look-alikes), the distinct
error taxonomy (malformed / unknown version / checksum / unknown feature
bits / unknown theme / feature-unavailable), and doc honesty — the
literal example codes in the doc must decode to their stated configs AND
re-encode to the exact literal (regenerate-or-red, the repo's md-parity
pattern from ``tests/test_theme_schema.py``).
"""

import itertools
import re
import zlib
from pathlib import Path

import pytest

from idle_engine import provisioning
from idle_engine.provisioning import (
    ChecksumError,
    FeatureUnavailableError,
    InvalidConfigError,
    MalformedCodeError,
    SetupCodeError,
    SetupConfig,
    UnknownFeatureError,
    UnknownThemeError,
    UnknownVersionError,
    decode_setup,
    encode_setup,
    validate_against_catalog,
)

REPO_ROOT = Path(__file__).resolve().parent.parent
THEMES_DIR = REPO_ROOT / "themes"
DOC = REPO_ROOT / "docs" / "provisioning.md"

SHIPPED_THEME_IDS = ("egg-farm", "space-colony", "potion-brewery")
FLAG_COMBOS = list(itertools.product((False, True), repeat=3))


def _make_config(theme_id, combo):
    offline, upgrades, prestige = combo
    return SetupConfig(
        theme_id=theme_id, offline_progress=offline, upgrades=upgrades, prestige=prestige
    )


def _split(code: str) -> tuple[str, str]:
    prefix, body = code.split("-", 1)
    return prefix + "-", body


# --- round-trip + determinism ------------------------------------------------


@pytest.mark.parametrize("theme_id", SHIPPED_THEME_IDS)
@pytest.mark.parametrize("combo", FLAG_COMBOS)
def test_round_trip_every_shipped_theme_and_feature_combo(theme_id, combo):
    config = _make_config(theme_id, combo)
    code = encode_setup(config)
    assert code.startswith("IDLE1-")
    assert decode_setup(code) == config


@pytest.mark.parametrize("theme_id", SHIPPED_THEME_IDS)
def test_same_config_always_yields_the_same_code(theme_id):
    config = SetupConfig(theme_id=theme_id)
    codes = {encode_setup(config) for _ in range(5)}
    assert len(codes) == 1
    # equal configs built independently agree too
    assert encode_setup(SetupConfig(theme_id=theme_id)) in codes


def test_codes_are_short_and_pasteable():
    for theme_id in SHIPPED_THEME_IDS:
        code = encode_setup(SetupConfig(theme_id=theme_id))
        assert len(code) <= 40
        assert re.fullmatch(r"IDLE1-[0-9A-HJKMNP-TV-Z]+", code), code


def test_config_defaults_are_all_features_on():
    assert SetupConfig(theme_id="egg-farm") == _make_config("egg-farm", (True, True, True))


# --- paste tolerance ----------------------------------------------------------


def test_decode_is_case_insensitive():
    config = SetupConfig(theme_id="egg-farm")
    code = encode_setup(config)
    assert decode_setup(code.lower()) == config
    assert decode_setup(code.swapcase()) == config


def test_decode_tolerates_internal_hyphens_and_whitespace():
    config = SetupConfig(theme_id="space-colony")
    prefix, body = _split(encode_setup(config))
    grouped = "-".join(body[i : i + 4] for i in range(0, len(body), 4))
    assert decode_setup(f"  {prefix}{grouped} \n") == config


def test_decode_folds_lookalike_characters():
    config = SetupConfig(theme_id="egg-farm")
    prefix, body = _split(encode_setup(config))
    assert "0" in body  # the fixture exercises the fold for real
    folded = body.replace("0", "O").replace("1", "L")
    assert decode_setup(prefix + folded) == config


# --- error taxonomy: decode side ----------------------------------------------


@pytest.mark.parametrize(
    "bad",
    [
        "",
        "IDLE1",  # no hyphen
        "IDLE1-",  # empty body
        "SETUP1-AAAA",  # wrong tag
        "IDLEX-AAAA",  # non-numeric version
        "IDLE1-UUUU",  # U is outside the Crockford alphabet
        "IDLE1-*!*!",  # junk characters
        "IDLE1-07",  # decodes to too few bytes
    ],
)
def test_malformed_codes_raise_malformed(bad):
    with pytest.raises(MalformedCodeError):
        decode_setup(bad)


def test_non_string_input_is_malformed():
    with pytest.raises(MalformedCodeError):
        decode_setup(12345)


def test_non_canonical_padding_bits_are_malformed():
    prefix, body = _split(encode_setup(SetupConfig(theme_id="egg-farm")))
    # Last char carries 2 padding bits (11 bytes -> 88 bits -> 18 chars);
    # bump them to a non-zero pad while keeping every char alphabet-legal.
    last_value = provisioning._DECODE_MAP[body[-1]]
    tweaked = body[:-1] + provisioning._ALPHABET[last_value | 0b11]
    assert tweaked != body
    with pytest.raises(MalformedCodeError):
        decode_setup(prefix + tweaked)


@pytest.mark.parametrize("version", [0, 2, 9, 42])
def test_unknown_version_raises_before_body_parsing(version):
    with pytest.raises(UnknownVersionError):
        decode_setup(f"IDLE{version}-THIS-BODY-IS-NOT-EVEN-VALID*")


def test_tampered_payload_raises_checksum_error():
    prefix, body = _split(encode_setup(SetupConfig(theme_id="egg-farm")))
    original = body[0]
    replacement = next(
        ch
        for ch in provisioning._ALPHABET
        if provisioning._DECODE_MAP[ch] != provisioning._DECODE_MAP[original]
    )
    with pytest.raises(ChecksumError):
        decode_setup(prefix + replacement + body[1:])


def test_tampered_checksum_raises_checksum_error():
    prefix, body = _split(encode_setup(SetupConfig(theme_id="potion-brewery")))
    # Chars 3..5 from the end sit fully inside the 2 checksum bytes.
    idx = len(body) - 4
    original = body[idx]
    replacement = next(
        ch
        for ch in provisioning._ALPHABET
        if provisioning._DECODE_MAP[ch] != provisioning._DECODE_MAP[original]
    )
    with pytest.raises(ChecksumError):
        decode_setup(prefix + body[:idx] + replacement + body[idx + 1 :])


def _craft_code(payload: bytes) -> str:
    """A structurally valid v1 code around an arbitrary payload."""
    checksum = (zlib.crc32(payload) & 0xFFFF).to_bytes(2, "big")
    return "IDLE1-" + provisioning._crockford_encode(payload + checksum)


def test_unknown_feature_bits_raise_distinctly():
    code = _craft_code(bytes([0b0000_1111]) + b"egg-farm")  # bit 3 undefined in v1
    with pytest.raises(UnknownFeatureError):
        decode_setup(code)


@pytest.mark.parametrize("bad_id", [b"UPPER", b"double--hyphen", b"-lead", b"a" * 33, b"\xff\xfe"])
def test_non_slug_theme_id_in_payload_is_malformed(bad_id):
    with pytest.raises(MalformedCodeError):
        decode_setup(_craft_code(bytes([0b0000_0111]) + bad_id))


def test_every_error_is_a_setup_code_error_and_a_value_error():
    for exc in (
        InvalidConfigError,
        MalformedCodeError,
        UnknownVersionError,
        ChecksumError,
        UnknownFeatureError,
        UnknownThemeError,
        FeatureUnavailableError,
    ):
        assert issubclass(exc, SetupCodeError) and issubclass(exc, ValueError)


# --- error taxonomy: encode side ----------------------------------------------


@pytest.mark.parametrize(
    "bad_id", ["", "UPPER", "double--hyphen", "-lead", "trail-", "under_score", "a" * 33, None]
)
def test_encoder_rejects_non_slug_theme_ids(bad_id):
    with pytest.raises(InvalidConfigError):
        encode_setup(SetupConfig(theme_id=bad_id))


# --- catalog resolution --------------------------------------------------------


@pytest.mark.parametrize("theme_id", SHIPPED_THEME_IDS)
def test_every_shipped_pack_resolves_with_all_features_on(theme_id):
    config = decode_setup(encode_setup(SetupConfig(theme_id=theme_id)))
    theme = validate_against_catalog(config, THEMES_DIR)
    assert theme.theme_id == theme_id


def test_unknown_theme_id_raises_at_catalog_resolution():
    config = decode_setup(encode_setup(SetupConfig(theme_id="no-such-pack")))
    with pytest.raises(UnknownThemeError):
        validate_against_catalog(config, THEMES_DIR)


MINIMAL_PACK = """\
schema_version: 1
theme:
  id: min-pack
  name: Minimal Pack
  description: The schema doc's minimal pack; no upgrades, no prestige.
  emoji: "M"
  embed_color: "#112233"
currencies:
  - id: primary
    name: units
    description: The only currency.
    emoji: "U"
generators:
  - id: tier1
    name: unit maker
    description: Makes units.
    emoji: "G"
    produces: primary
    base_rate: 1
"""


@pytest.mark.parametrize("toggle", ["upgrades", "prestige"])
def test_enabled_feature_without_pack_skin_is_unavailable(tmp_path, toggle):
    (tmp_path / "min-pack.yaml").write_text(MINIMAL_PACK, encoding="utf-8")
    kwargs = {"upgrades": False, "prestige": False, toggle: True}
    config = SetupConfig(theme_id="min-pack", **kwargs)
    with pytest.raises(FeatureUnavailableError):
        validate_against_catalog(config, tmp_path)
    # and with the feature off, the same pack resolves fine
    ok = SetupConfig(theme_id="min-pack", upgrades=False, prestige=False)
    assert validate_against_catalog(ok, tmp_path).theme_id == "min-pack"


def test_empty_catalog_is_an_unknown_theme(tmp_path):
    with pytest.raises(UnknownThemeError):
        validate_against_catalog(SetupConfig(theme_id="egg-farm"), tmp_path)


# --- doc honesty (docs/provisioning.md) -----------------------------------------

EXAMPLE_ROW = re.compile(
    r"^\|\s*\d+\s*\|\s*`([a-z0-9-]+)`\s*"
    r"\|\s*(on|off)\s*\|\s*(on|off)\s*\|\s*(on|off)\s*"
    r"\|\s*`(IDLE[0-9]+-[0-9A-Z-]+)`\s*\|$",
    re.M,
)


def doc_text() -> str:
    assert DOC.is_file(), f"{DOC} missing — the published provisioning contract"
    return DOC.read_text(encoding="utf-8")


def test_doc_ships_an_example_for_every_shipped_theme():
    themes_with_examples = {row[0] for row in EXAMPLE_ROW.findall(doc_text())}
    assert set(SHIPPED_THEME_IDS) <= themes_with_examples


def test_doc_examples_decode_and_reencode_exactly():
    rows = EXAMPLE_ROW.findall(doc_text())
    assert len(rows) >= 3, "worked-examples table lost its rows"
    for theme_id, offline, upgrades, prestige, literal_code in rows:
        stated = SetupConfig(
            theme_id=theme_id,
            offline_progress=offline == "on",
            upgrades=upgrades == "on",
            prestige=prestige == "on",
        )
        assert decode_setup(literal_code) == stated, f"doc code for {theme_id} decodes off-spec"
        assert encode_setup(stated) == literal_code, (
            f"doc code for {theme_id} is not what the real encoder emits — "
            "regenerate the table (regenerate-or-red)"
        )


def test_doc_worked_bytes_walkthrough_matches_the_implementation():
    text = doc_text()
    payload = bytes([0b0000_0111]) + b"egg-farm"
    crc16 = zlib.crc32(payload) & 0xFFFF
    assert payload.hex(" ") in text, "worked-bytes payload row drifted"
    assert f"0x{crc16:04x}" in text, "worked-bytes checksum value drifted"
    assert crc16.to_bytes(2, "big").hex(" ") in text, "worked-bytes checksum row drifted"


def test_doc_pins_the_flag_bit_assignments():
    text = doc_text()
    for name, bit in provisioning.FEATURE_BITS.items():
        row = rf"\|\s*`flags` bit {bit}\s*\|.*`{name}`"
        assert re.search(row, text), f"doc field table lost flag bit {bit} ({name})"
