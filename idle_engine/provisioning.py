"""SETUP-CODE FORMAT v1 — the versioned provisioning contract.

A setup code is one short, paste-able string that provisions an
idle-game instance for a server: which theme pack to load and which
engine features to enable. The websites lane BUILDS codes with
:func:`encode_setup`; superbot-next's plugin CONSUMES them with
:func:`decode_setup`. The byte-level contract is published in
``docs/provisioning.md`` — v1 is FROZEN once merged; anything beyond
additive is v2 behind a new version prefix, so v1 consumers never break.

Code shape (see the doc for the byte-by-byte grammar)::

    IDLE1-<body>

where ``<body>`` is Crockford base32 of ``payload ++ checksum``:
one feature-flags byte, then the theme id in ASCII, then a 2-byte
big-endian CRC-32 truncated to 16 bits so typos fail loud instead of
provisioning the wrong game. Decoding is case-insensitive, ignores
internal hyphens, and folds the classic base32 look-alikes
(``O``->``0``, ``I``/``L``->``1``).

:func:`encode_setup` and :func:`decode_setup` are pure and
deterministic: stdlib only, no I/O, no clock, no randomness — the same
config always yields the same code, byte for byte. Resolving a decoded
theme id against the shipped catalog is deliberately a SEPARATE step,
:func:`validate_against_catalog` (which reads ``themes/``), so the
plugin can decode at its trust boundary and resolve at load time.

Feature toggles are honest: every v1 flag maps to a mechanic the engine
actually ships (:mod:`idle_engine.engine` offline progress,
:mod:`idle_engine.upgrades`, :mod:`idle_engine.prestige`). Unknown flag
bits are a distinct error, never silently ignored — that is what makes
v2 detectable instead of misread.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING
from zlib import crc32

if TYPE_CHECKING:  # imported lazily at runtime; decode stays I/O-free
    from idle_engine.theme import Theme

#: The format version this module speaks, as carried by the code prefix.
SETUP_CODE_VERSION = 1

#: Canonical prefix emitted by the encoder.
CODE_PREFIX = f"IDLE{SETUP_CODE_VERSION}-"

#: v1 feature flags: name -> bit position in the flags byte.
#: Every entry is a mechanic the engine ships TODAY — no vaporware bits.
FEATURE_BITS: dict[str, int] = {
    "offline_progress": 0,
    "upgrades": 1,
    "prestige": 2,
}

_KNOWN_FLAGS_MASK = sum(1 << bit for bit in FEATURE_BITS.values())

#: Theme ids are schema-v1 slugs (docs/theme-schema.md § Fields).
_SLUG_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
_SLUG_MAX = 32

#: Crockford base32: 32 symbols, no I/L/O/U (docs/provisioning.md § Grammar).
_ALPHABET = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"
_DECODE_MAP = {ch: i for i, ch in enumerate(_ALPHABET)}
_DECODE_MAP.update({"O": 0, "I": 1, "L": 1})  # look-alike folding

_PREFIX_RE = re.compile(r"^IDLE([0-9]+)-(.*)$", re.IGNORECASE | re.DOTALL)

_CHECKSUM_BYTES = 2


class SetupCodeError(ValueError):
    """Base class for every setup-code failure (encode or decode side)."""


class InvalidConfigError(SetupCodeError):
    """Encoder input is not a representable v1 config."""


class MalformedCodeError(SetupCodeError):
    """The string is not shaped like a setup code at all."""


class UnknownVersionError(SetupCodeError):
    """Valid shape, but a format version this decoder does not speak."""


class ChecksumError(SetupCodeError):
    """Well-formed body whose checksum does not match — typo or tampering."""


class UnknownFeatureError(SetupCodeError):
    """Flag bits set that v1 does not define (a from-the-future config)."""


class UnknownThemeError(SetupCodeError):
    """Decoded theme id is not in the shipped catalog."""


class FeatureUnavailableError(SetupCodeError):
    """A toggled-on feature has no skin in the resolved theme pack."""


@dataclass(frozen=True)
class SetupConfig:
    """One provisioned instance: a theme id plus v1 feature toggles.

    ``theme_id`` names a pack; whether it resolves is checked against a
    catalog by :func:`validate_against_catalog`, not here. Toggles
    default to on — a bare ``SetupConfig(theme_id=...)`` is the full
    game — and each maps 1:1 to a bit in the code's flags byte.
    """

    theme_id: str
    offline_progress: bool = True
    upgrades: bool = True
    prestige: bool = True

    def flags(self) -> int:
        """The v1 flags byte for this config."""
        value = 0
        for name, bit in FEATURE_BITS.items():
            if getattr(self, name):
                value |= 1 << bit
        return value


def _crockford_encode(data: bytes) -> str:
    """Crockford base32, canonical: zero-bit padded, no separators."""
    bits = 0
    bit_count = 0
    out: list[str] = []
    for byte in data:
        bits = (bits << 8) | byte
        bit_count += 8
        while bit_count >= 5:
            bit_count -= 5
            out.append(_ALPHABET[(bits >> bit_count) & 0x1F])
    if bit_count:
        out.append(_ALPHABET[(bits << (5 - bit_count)) & 0x1F])
    return "".join(out)


def _crockford_decode(body: str) -> bytes:
    """Inverse of :func:`_crockford_encode`, tolerant per the grammar.

    Case-insensitive, folds ``O``->``0`` and ``I``/``L``->``1``; any
    other symbol outside the alphabet — including ``U`` — is malformed.
    Trailing padding bits must be zero (one canonical spelling per
    payload, so codes compare as strings).
    """
    bits = 0
    bit_count = 0
    out = bytearray()
    for ch in body.upper():
        value = _DECODE_MAP.get(ch)
        if value is None:
            raise MalformedCodeError(f"invalid setup-code character {ch!r}")
        bits = (bits << 5) | value
        bit_count += 5
        if bit_count >= 8:
            bit_count -= 8
            out.append((bits >> bit_count) & 0xFF)
    if bit_count and bits & ((1 << bit_count) - 1):
        raise MalformedCodeError("non-canonical setup code (padding bits set)")
    return bytes(out)


def _checksum(payload: bytes) -> bytes:
    """CRC-32 of the payload, truncated to its low 16 bits, big-endian."""
    return (crc32(payload) & 0xFFFF).to_bytes(_CHECKSUM_BYTES, "big")


def _require_slug(theme_id: object) -> str:
    if not isinstance(theme_id, str) or not _SLUG_RE.fullmatch(theme_id) or len(theme_id) > _SLUG_MAX:
        raise InvalidConfigError(
            f"theme_id {theme_id!r} is not a schema-v1 slug "
            f"(lowercase a-z0-9 words joined by single hyphens, <= {_SLUG_MAX} chars)"
        )
    return theme_id


def encode_setup(config: SetupConfig) -> str:
    """Encode a v1 config into its one canonical setup code.

    Pure and deterministic: the same config always returns the same
    string. Raises :class:`InvalidConfigError` if the config cannot be
    represented in v1 (bad theme-id slug).
    """
    theme_id = _require_slug(config.theme_id)
    payload = bytes([config.flags()]) + theme_id.encode("ascii")
    return CODE_PREFIX + _crockford_encode(payload + _checksum(payload))


def decode_setup(code: str) -> SetupConfig:
    """Decode and strictly validate a setup code's SHAPE.

    Returns the carried config. Catalog resolution (does this theme id
    ship?) is the separate :func:`validate_against_catalog` step.

    Error taxonomy (all subclass :class:`SetupCodeError`, all distinct):

    - :class:`MalformedCodeError` — no ``IDLE<n>-`` prefix, illegal
      body character, truncated body, non-canonical padding, or a
      payload whose theme id is not a slug.
    - :class:`UnknownVersionError` — prefix version other than 1.
    - :class:`ChecksumError` — body decodes but the checksum disagrees
      (typo/tampering). Checked BEFORE any payload semantics.
    - :class:`UnknownFeatureError` — flag bits v1 does not define.
    """
    if not isinstance(code, str):
        raise MalformedCodeError("setup code must be a string")
    match = _PREFIX_RE.fullmatch(code.strip())
    if not match:
        raise MalformedCodeError(
            f"setup code must look like {CODE_PREFIX}<base32-body> (got {code!r})"
        )
    version = int(match.group(1))
    if version != SETUP_CODE_VERSION:
        raise UnknownVersionError(
            f"setup-code version {version} — this decoder speaks only v{SETUP_CODE_VERSION}"
        )
    body = match.group(2).replace("-", "")
    if not body:
        raise MalformedCodeError("setup code has an empty body")
    raw = _crockford_decode(body)
    if len(raw) < 1 + 1 + _CHECKSUM_BYTES:  # flags + >=1 id byte + checksum
        raise MalformedCodeError("setup-code body is too short")
    payload, checksum = raw[:-_CHECKSUM_BYTES], raw[-_CHECKSUM_BYTES:]
    if checksum != _checksum(payload):
        raise ChecksumError("setup-code checksum mismatch (mistyped or tampered)")
    flags = payload[0]
    if flags & ~_KNOWN_FLAGS_MASK:
        raise UnknownFeatureError(
            f"unknown v1 feature bits set in flags byte 0b{flags:08b}"
        )
    try:
        theme_id = payload[1:].decode("ascii")
    except UnicodeDecodeError as exc:
        raise MalformedCodeError("theme id in payload is not ASCII") from exc
    if not _SLUG_RE.fullmatch(theme_id) or len(theme_id) > _SLUG_MAX:
        raise MalformedCodeError(f"theme id in payload is not a slug: {theme_id!r}")
    return SetupConfig(
        theme_id=theme_id,
        **{name: bool(flags & (1 << bit)) for name, bit in FEATURE_BITS.items()},
    )


def validate_against_catalog(config: SetupConfig, themes_dir: str | Path) -> "Theme":
    """Resolve a decoded config against a shipped theme catalog.

    Loads every ``*.yaml`` pack under ``themes_dir`` (a broken pack
    propagates its own loader error — the catalog is gate-clean by
    contract) and returns the resolved :class:`~idle_engine.theme.Theme`.

    Raises :class:`UnknownThemeError` if no pack declares the config's
    theme id, and :class:`FeatureUnavailableError` if a toggled-on
    feature has no skin in the resolved pack (upgrades toggled with no
    ``upgrades`` block, or prestige toggled with no ``prestige`` block —
    the engine would have nothing to render). ``offline_progress`` is
    pure engine mechanics and needs no skin.
    """
    from idle_engine.theme import load_theme  # keep decode_setup import-light

    themes_dir = Path(themes_dir)
    catalog = {theme.theme_id: theme for theme in map(load_theme, sorted(themes_dir.glob("*.yaml")))}
    theme = catalog.get(config.theme_id)
    if theme is None:
        raise UnknownThemeError(
            f"theme id {config.theme_id!r} is not in the catalog "
            f"({sorted(catalog) or 'empty'})"
        )
    if config.upgrades and not theme.upgrades:
        raise FeatureUnavailableError(
            f"config enables upgrades but pack {config.theme_id!r} declares no upgrade skins"
        )
    if config.prestige and theme.prestige is None:
        raise FeatureUnavailableError(
            f"config enables prestige but pack {config.theme_id!r} declares no prestige skin"
        )
    return theme
