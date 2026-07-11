#!/usr/bin/env python3
"""Deterministic generator for ``tests/vectors/setup-codes.v1.json``.

The committed JSON is the CROSS-LANGUAGE parity file for SETUP-CODE
FORMAT v1 (``docs/provisioning.md``): a foreign implementation (the
websites lane's encoder) replays the same vectors its own way, and this
repo's suite (``tests/test_setup_vectors.py``) asserts the committed
file is byte-identical to a fresh in-memory regeneration — so contract
drift reds a test suite instead of surfacing as a live decode failure.

Every vector is produced BY the real codec (``idle_engine.provisioning``)
and sanity-checked against it before being emitted; nothing here is
hand-typed. The generator is pure and deterministic: no clock, no
randomness, no environment — the only input is the shipped catalog
(``themes/*.yaml`` filename stems, which the theme gate pins to
``theme.id``) and the codec itself, so the same tree always yields the
same bytes.

Regenerate (after any deliberate v1-additive change) with::

    python3 tools/gen_setup_vectors.py

Vector categories:

- ``valid`` — config -> canonical code for every shipped pack x a
  bounded feature-combo set (all-on, all-off, each single feature),
  WITH layer intermediates (flags byte, payload hex, crc16 hex) so a
  foreign encoder can debug layer by layer.
- ``tolerance`` — accepted non-canonical spellings (case, internal
  hyphens, surrounding whitespace, look-alike folds) mapping to the
  same config, plus the canonical spelling they normalize to.
- ``errors`` — malformed / unknown-version / checksum-mismatch /
  unknown-flag-bits / bad-payload-slug inputs, each carrying the
  expected error CLASS name from the documented taxonomy.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:  # runnable as a script from anywhere
    sys.path.insert(0, str(REPO_ROOT))

from idle_engine import provisioning  # noqa: E402
from idle_engine.provisioning import (  # noqa: E402
    SetupConfig,
    decode_setup,
    encode_setup,
)

VECTORS_PATH = REPO_ROOT / "tests" / "vectors" / "setup-codes.v1.json"
THEMES_DIR = REPO_ROOT / "themes"

#: Feature names in flags-byte bit order (the v1 contract's field table).
FEATURES = tuple(sorted(provisioning.FEATURE_BITS, key=provisioning.FEATURE_BITS.get))

#: Bounded, representative combo set — not the exhaustive 2**n product.
#: Name -> the set of features toggled ON.
FEATURE_COMBOS: dict[str, frozenset[str]] = {
    "all-on": frozenset(FEATURES),
    "all-off": frozenset(),
    **{f"only-{name}": frozenset({name}) for name in FEATURES},
}

#: decode_setup errors a foreign implementation must reproduce, by name.
DECODE_ERROR_CLASSES = (
    "MalformedCodeError",
    "UnknownVersionError",
    "ChecksumError",
    "UnknownFeatureError",
)


def catalog_theme_ids() -> list[str]:
    """Shipped theme ids, from the gate-pinned ``themes/<id>.yaml`` stems."""
    ids = sorted(path.stem for path in THEMES_DIR.glob("*.yaml"))
    if not ids:
        raise RuntimeError(f"no theme packs found under {THEMES_DIR}")
    return ids


def _make_config(theme_id: str, enabled: frozenset[str]) -> SetupConfig:
    return SetupConfig(theme_id=theme_id, **{name: name in enabled for name in FEATURES})


def _config_dict(config: SetupConfig) -> dict:
    return {"theme_id": config.theme_id, **{name: getattr(config, name) for name in FEATURES}}


def _split(code: str) -> tuple[str, str]:
    prefix, body = code.split("-", 1)
    return prefix + "-", body


def _valid_vector(name: str, config: SetupConfig) -> dict:
    payload = bytes([config.flags()]) + config.theme_id.encode("ascii")
    checksum = provisioning._checksum(payload)
    code = encode_setup(config)
    # Layer-by-layer sanity: the intermediates we publish ARE the codec's.
    assert code == provisioning.CODE_PREFIX + provisioning._crockford_encode(payload + checksum)
    assert decode_setup(code) == config
    return {
        "name": name,
        "config": _config_dict(config),
        "flags_byte": f"{config.flags():02x}",
        "payload_hex": payload.hex(),
        "crc16_hex": checksum.hex(),
        "code": code,
    }


def _build_valid() -> list[dict]:
    return [
        _valid_vector(f"{theme_id}--{combo_name}", _make_config(theme_id, enabled))
        for theme_id in catalog_theme_ids()
        for combo_name, enabled in FEATURE_COMBOS.items()
    ]


def _tolerance_vector(name: str, variant: str, config: SetupConfig, note: str) -> dict:
    assert decode_setup(variant) == config, f"tolerance vector {name!r} does not decode"
    return {
        "name": name,
        "input": variant,
        "canonical": encode_setup(config),
        "config": _config_dict(config),
        "note": note,
    }


def _build_tolerance() -> list[dict]:
    vectors: list[dict] = []
    theme_ids = catalog_theme_ids()
    for theme_id in theme_ids:
        config = _make_config(theme_id, FEATURE_COMBOS["all-on"])
        prefix, body = _split(encode_setup(config))
        grouped = "-".join(body[i : i + 4] for i in range(0, len(body), 4))
        vectors.append(
            _tolerance_vector(
                f"{theme_id}--lowercase", (prefix + body).lower(), config,
                "decoding is case-insensitive (prefix and body)",
            )
        )
        vectors.append(
            _tolerance_vector(
                f"{theme_id}--hyphen-grouped", prefix + grouped, config,
                "internal hyphens in the body are ignored",
            )
        )
        if "0" in body:
            vectors.append(
                _tolerance_vector(
                    f"{theme_id}--lookalike-O-for-0", prefix + body.replace("0", "O"),
                    config, "O folds to 0",
                )
            )
        # The all-on body may contain no "1"; fold vectors for I/L come
        # from the FIRST combo (in declaration order) whose body has one
        # — deterministically the all-off code, whose flags byte 0x00
        # makes the body start "01".
        for combo_name, enabled in FEATURE_COMBOS.items():
            fold_config = _make_config(theme_id, enabled)
            fold_prefix, fold_body = _split(encode_setup(fold_config))
            if "1" in fold_body:
                for lookalike in ("I", "L"):
                    vectors.append(
                        _tolerance_vector(
                            f"{theme_id}--{combo_name}--lookalike-{lookalike}-for-1",
                            fold_prefix + fold_body.replace("1", lookalike),
                            fold_config,
                            f"{lookalike} folds to 1 (body only — the prefix version digit is literal)",
                        )
                    )
                break
        # Folds apply to the BODY only — the prefix's version digit is literal.
        sink = prefix.lower() + grouped.lower().replace("0", "o").replace("1", "l")
        vectors.append(
            _tolerance_vector(
                f"{theme_id}--kitchen-sink", sink, config,
                "lowercase + hyphen groups + look-alike folds combined",
            )
        )
    # Surrounding whitespace is stripped (reference-impl tolerance).
    ws_config = _make_config(theme_ids[0], FEATURE_COMBOS["all-on"])
    vectors.append(
        _tolerance_vector(
            f"{theme_ids[0]}--surrounding-whitespace",
            f"  {encode_setup(ws_config)} \n",
            ws_config,
            "leading/trailing whitespace is stripped before parsing",
        )
    )
    return vectors


def _craft_code(payload: bytes) -> str:
    """A structurally valid v1 code around an arbitrary payload."""
    return "IDLE1-" + provisioning._crockford_encode(payload + provisioning._checksum(payload))


def _other_alphabet_char(ch: str) -> str:
    """First alphabet symbol decoding to a different value than ``ch``."""
    return next(
        c for c in provisioning._ALPHABET
        if provisioning._DECODE_MAP[c] != provisioning._DECODE_MAP[ch]
    )


def _error_vector(name: str, bad_input: str, error: str, note: str) -> dict:
    expected = getattr(provisioning, error)
    try:
        decode_setup(bad_input)
    except provisioning.SetupCodeError as exc:
        assert type(exc) is expected, f"error vector {name!r}: got {type(exc).__name__}, want {error}"
    else:
        raise AssertionError(f"error vector {name!r} decoded successfully")
    return {"name": name, "input": bad_input, "error": error, "note": note}


def _build_errors() -> list[dict]:
    anchor_id = catalog_theme_ids()[0]
    anchor = _make_config(anchor_id, FEATURE_COMBOS["all-on"])
    prefix, body = _split(encode_setup(anchor))
    all_on_flags = anchor.flags()

    # Tampered payload: flip the first body char to a different value.
    tampered_payload = prefix + _other_alphabet_char(body[0]) + body[1:]
    # Tampered checksum: chars 3..5 from the end sit fully inside the
    # 2 checksum bytes for any body length.
    idx = len(body) - 4
    tampered_checksum = prefix + body[:idx] + _other_alphabet_char(body[idx]) + body[idx + 1 :]
    # Non-canonical padding: the final base32 char carries the pad bits;
    # setting any of the low (5 - bit_count%5... ) pad bits is malformed.
    # For an 11-byte buffer (88 bits -> 18 chars) the last char carries
    # 2 pad bits; ORing 0b11 into it keeps it alphabet-legal but non-zero.
    last_value = provisioning._DECODE_MAP[body[-1]]
    padded = prefix + body[:-1] + provisioning._ALPHABET[last_value | 0b11]
    assert padded != prefix + body

    unknown_bit3 = _craft_code(bytes([all_on_flags | 0b0000_1000]) + anchor_id.encode())
    unknown_bit7 = _craft_code(bytes([all_on_flags | 0b1000_0000]) + anchor_id.encode())

    vectors = [
        _error_vector("empty-string", "", "MalformedCodeError", "not shaped like a code at all"),
        _error_vector("prefix-no-hyphen", "IDLE1", "MalformedCodeError", "prefix must end with a hyphen"),
        _error_vector("prefix-wrong-tag", "SETUP1-" + body, "MalformedCodeError", "tag must be IDLE"),
        _error_vector("prefix-non-numeric-version", "IDLEX-" + body, "MalformedCodeError", "version must be a decimal integer"),
        _error_vector("empty-body", "IDLE1-", "MalformedCodeError", "body must be non-empty"),
        _error_vector("illegal-char-U", "IDLE1-UUUU", "MalformedCodeError", "U is outside the Crockford alphabet — never folded"),
        _error_vector("illegal-junk-chars", "IDLE1-*!*!", "MalformedCodeError", "symbols outside the alphabet are malformed"),
        _error_vector("body-too-short", "IDLE1-07", "MalformedCodeError", "body must decode to >= flags + 1 id byte + 2 checksum bytes"),
        _error_vector("non-canonical-padding", padded, "MalformedCodeError", "trailing padding bits must be zero — one canonical spelling per payload"),
        _error_vector("unknown-version-0", "IDLE0-" + body, "UnknownVersionError", "version 0 is not v1 — rejected before body parsing"),
        _error_vector("unknown-version-2", "IDLE2-" + body, "UnknownVersionError", "future versions fail loud, never misparse"),
        _error_vector("unknown-version-42", "IDLE42-" + body, "UnknownVersionError", "any version other than 1"),
        _error_vector("checksum-tampered-payload", tampered_payload, "ChecksumError", "payload edited, checksum now disagrees"),
        _error_vector("checksum-tampered-checksum", tampered_checksum, "ChecksumError", "checksum bytes edited"),
        _error_vector("unknown-flag-bit-3", unknown_bit3, "UnknownFeatureError", "flags bit 3 is undefined in v1 (valid checksum)"),
        _error_vector("unknown-flag-bit-7", unknown_bit7, "UnknownFeatureError", "flags bit 7 is undefined in v1 (valid checksum)"),
        _error_vector("theme-id-uppercase", _craft_code(bytes([all_on_flags]) + b"UPPER"), "MalformedCodeError", "payload theme id must be a lowercase slug (valid checksum)"),
        _error_vector("theme-id-double-hyphen", _craft_code(bytes([all_on_flags]) + b"double--hyphen"), "MalformedCodeError", "single hyphens only between slug words"),
        _error_vector("theme-id-leading-hyphen", _craft_code(bytes([all_on_flags]) + b"-lead"), "MalformedCodeError", "slug cannot start with a hyphen"),
        _error_vector("theme-id-trailing-hyphen", _craft_code(bytes([all_on_flags]) + b"trail-"), "MalformedCodeError", "slug cannot end with a hyphen"),
        _error_vector("theme-id-underscore", _craft_code(bytes([all_on_flags]) + b"under_score"), "MalformedCodeError", "underscore is outside the slug charset"),
        _error_vector("theme-id-too-long", _craft_code(bytes([all_on_flags]) + b"a" * 33), "MalformedCodeError", "slug max length is 32"),
        _error_vector("theme-id-non-ascii", _craft_code(bytes([all_on_flags]) + b"\xff\xfe"), "MalformedCodeError", "payload theme id must be ASCII"),
    ]
    return vectors


def build_document() -> dict:
    valid = _build_valid()
    tolerance = _build_tolerance()
    errors = _build_errors()
    return {
        "format": "superbot-idle-setup-code-vectors",
        "format_version": 1,
        "setup_code_version": provisioning.SETUP_CODE_VERSION,
        "generated_by": "tools/gen_setup_vectors.py — DO NOT EDIT BY HAND; regenerate with: python3 tools/gen_setup_vectors.py",
        "contract": "docs/provisioning.md",
        "code_prefix": provisioning.CODE_PREFIX,
        "alphabet": provisioning._ALPHABET,
        "lookalike_folds": {"O": "0", "I": "1", "L": "1"},
        "checksum": "crc32(payload) & 0xFFFF, 2 bytes big-endian, appended to payload before base32",
        "feature_bits": dict(provisioning.FEATURE_BITS),
        "themes": catalog_theme_ids(),
        "decode_error_classes": list(DECODE_ERROR_CLASSES),
        "counts": {"valid": len(valid), "tolerance": len(tolerance), "errors": len(errors)},
        "vectors": {"valid": valid, "tolerance": tolerance, "errors": errors},
    }


def render() -> str:
    """The vector file's exact byte content (regenerate-or-red target)."""
    return json.dumps(build_document(), indent=2, ensure_ascii=True) + "\n"


def main() -> int:
    VECTORS_PATH.parent.mkdir(parents=True, exist_ok=True)
    content = render()
    VECTORS_PATH.write_text(content, encoding="utf-8")
    doc = build_document()
    print(
        f"wrote {VECTORS_PATH.relative_to(REPO_ROOT)}: "
        + ", ".join(f"{k}={v}" for k, v in doc["counts"].items())
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
