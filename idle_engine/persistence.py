"""SAVE FORMAT v2 — canonical, versioned GameState serialization.

:func:`dump_state` turns a :class:`~idle_engine.state.GameState` into ONE
canonical JSON string; :func:`load_state` turns that string back into an
equal ``GameState`` under strict validation. Both are pure and
deterministic: stdlib only, no I/O, no clock, no randomness — the same
state always dumps to the same bytes, so saves can be compared, hashed,
and diffed as strings. The byte-level contract is published in
``docs/persistence.md`` — each version is FROZEN once merged; any change
to what a document of the current version may contain is a version bump
routed through the migration registry, never an in-place edit. v2 added
``milestones`` (the achievements slice) and shipped WITH the v1→v2
migration in the same PR, per the version policy.

Canonical form (the only spelling :func:`dump_state` emits)::

    {"balances":{...},"last_seen":0,"lifetime":{...},"milestones":{...},
     "owned":{...},"prestige":{...},"state_version":2,"upgrades":{...}}

- keys sorted lexicographically at every level, separators ``(",", ":")``
  (no whitespace), ``ensure_ascii`` escapes — byte-identical output on
  every platform;
- every quantity is a JSON integer: the engine's math is integer-exact
  (see :mod:`idle_engine.state`), and the save format refuses floats
  ANYWHERE so no platform can smuggle drift back in;
- all eight v2 fields always present, including empty mappings — one
  state, one spelling.

:func:`load_state` is tolerant of non-canonical *JSON* spellings
(whitespace, key order — it is still just JSON) but strict about
*content*: unknown versions, missing/unknown fields, wrong types
(floats, bools, strings-for-ints), and negative quantities each raise a
distinct :class:`SaveError` subclass, never a silent guess. Round-trip
is exact both ways: ``load_state(dump_state(s)) == s`` for every valid
state, and ``dump_state(load_state(t)) == t`` for canonical ``t``
(loading then dumping any accepted document is idempotent
canonicalization).

Deliberately NOT here: where save strings live. The engine serializes;
the runtime (the future superbot-next plugin, a file, a database, a
paste) owns storage, per the CORE/SKIN seam — this module never opens a
file.
"""

from __future__ import annotations

import json
from typing import Callable

from idle_engine.state import GameState

#: The save-format version this module WRITES. Bump only alongside a
#: migration registered in :data:`_MIGRATIONS` covering the old version.
STATE_VERSION = 2

#: The exact CURRENT (v2) top-level key set (including the version field).
_CURRENT_KEYS = frozenset(
    {
        "state_version",
        "balances",
        "owned",
        "last_seen",
        "upgrades",
        "lifetime",
        "prestige",
        "milestones",
    }
)

#: v2 fields holding a ``{str: non-negative int}`` mapping, in GameState order.
_MAPPING_FIELDS = ("balances", "owned", "upgrades", "lifetime", "prestige", "milestones")


class SaveError(ValueError):
    """Base class for every save-format failure (dump or load side)."""


class InvalidStateError(SaveError):
    """Encoder input is not a serializable, well-formed GameState."""


class MalformedSaveError(SaveError):
    """The text is not a JSON object at all (or not even a string)."""


class UnknownVersionError(SaveError):
    """A well-formed document whose version has no path to v{current}."""


class FieldSetError(SaveError):
    """Wrong top-level key set: a required field missing, or extras present."""


class FieldTypeError(SaveError):
    """A field (or mapping entry) holds the wrong JSON type — incl. floats/bools."""


class NegativeValueError(SaveError):
    """A quantity is a negative integer; every save quantity is >= 0."""


def _migrate_v1_to_v2(doc: dict) -> dict:
    """v1 → v2: the achievements slice added the ``milestones`` mapping.

    Achievements did not exist before v2, so every legacy save migrates
    with an EMPTY earned set. A v1 document already carrying a
    ``milestones`` key was never a valid v1 save — refuse it loudly
    rather than silently wiping whatever it smuggled; any OTHER stray or
    missing field rides through and is caught by the current-version
    field-set validation, exactly as strict as for native saves.
    """
    if "milestones" in doc:
        raise FieldSetError(
            "v1 save already carries the v2-only field 'milestones' — "
            "not a valid v1 document"
        )
    return {**doc, "milestones": {}, "state_version": 2}


#: Migration registry: source version -> function returning the document
#: migrated to source version + 1 (bumping ``state_version`` itself).
#: Carries its first REAL entry since the v2 bump (achievements slice);
#: the dispatch is additionally proven over multiple steps by a
#: synthetic v0->v1 migration in tests/test_persistence.py. Policy: a
#: format change ships IN THE SAME PR as the migration that covers it;
#: see docs/persistence.md § Version policy.
_MIGRATIONS: dict[int, Callable[[dict], dict]] = {1: _migrate_v1_to_v2}


def _require_count(value: object, where: str) -> int:
    """Validate one integer quantity; bool is NOT an int here."""
    if isinstance(value, bool) or not isinstance(value, int):
        raise FieldTypeError(f"{where} must be a JSON integer, got {value!r}")
    if value < 0:
        raise NegativeValueError(f"{where} must be >= 0, got {value}")
    return value


def _require_mapping(value: object, name: str) -> dict[str, int]:
    """Validate one ``{str: non-negative int}`` mapping field."""
    if not isinstance(value, dict):
        raise FieldTypeError(f"{name!r} must be a JSON object, got {value!r}")
    out: dict[str, int] = {}
    for key, count in value.items():
        if not isinstance(key, str):  # unreachable via json.loads; guards dump side
            raise FieldTypeError(f"{name!r} keys must be strings, got {key!r}")
        out[key] = _require_count(count, f"{name}[{key!r}]")
    return out


def _validated_document(state: GameState) -> dict:
    """The current-version document for ``state``, validating on the way out.

    Dumping refuses what loading would refuse, so every emitted string is
    loadable by construction and the round-trip guarantee has no blind
    side. A GameState hand-built with negative counts or non-int values
    is :class:`InvalidStateError`, not a save.
    """
    doc: dict = {"state_version": STATE_VERSION}
    try:
        for name in _MAPPING_FIELDS:
            doc[name] = _require_mapping(getattr(state, name), name)
        doc["last_seen"] = _require_count(state.last_seen, "last_seen")
    except SaveError as exc:
        raise InvalidStateError(f"state is not serializable: {exc}") from exc
    return doc


def dump_state(state: GameState) -> str:
    """Serialize a GameState to its ONE canonical current-version JSON string.

    Pure and deterministic: sorted keys, no whitespace, ASCII escapes,
    integers only — the same state always returns byte-identical text.
    Raises :class:`InvalidStateError` if ``state`` is not a well-formed
    GameState (non-int or negative quantities, non-string ids).
    """
    if not isinstance(state, GameState):
        raise InvalidStateError(f"dump_state takes a GameState, got {type(state).__name__}")
    return json.dumps(
        _validated_document(state), sort_keys=True, separators=(",", ":"), ensure_ascii=True
    )


def _reject_constant(token: str) -> None:
    raise MalformedSaveError(f"save contains a non-JSON constant: {token}")


def _read_version(doc: dict) -> int:
    if "state_version" not in doc:
        raise FieldSetError("save has no 'state_version' field")
    version = doc["state_version"]
    if isinstance(version, bool) or not isinstance(version, int):
        raise FieldTypeError(f"'state_version' must be a JSON integer, got {version!r}")
    return version


def _migrate(doc: dict, version: int) -> dict:
    """Walk ``doc`` up the migration chain to :data:`STATE_VERSION`.

    Versions NEWER than this module (from the future) and old versions
    with no registered chain both fail with the same actionable error:
    this loader does not speak that version.
    """
    while version != STATE_VERSION:
        step = _MIGRATIONS.get(version) if version < STATE_VERSION else None
        if step is None:
            raise UnknownVersionError(
                f"save version {version} — this loader speaks v{STATE_VERSION} "
                f"and can migrate from: {sorted(_MIGRATIONS) or 'nothing'}"
            )
        doc = step(doc)
        if not isinstance(doc, dict):
            raise MalformedSaveError(
                f"migration from v{version} returned {type(doc).__name__}, not a document"
            )
        migrated = _read_version(doc)
        if migrated != version + 1:
            raise UnknownVersionError(
                f"migration from v{version} produced v{migrated}, expected v{version + 1}"
            )
        version = migrated
    return doc


def load_state(text: str) -> GameState:
    """Parse and strictly validate a save string back into a GameState.

    Accepts any JSON spelling of a valid document (whitespace and key
    order are not content) and canonicalizes on the way in:
    ``dump_state(load_state(t)) == t`` whenever ``t`` is canonical.

    Error taxonomy (all subclass :class:`SaveError`, all distinct):

    - :class:`MalformedSaveError` — not a string, not parseable JSON,
      non-JSON constants (``NaN``/``Infinity``), or a top level that is
      not an object.
    - :class:`FieldSetError` — ``state_version`` missing, a current-
      version field missing, or unknown extra fields present (checked as
      a SET, so the message names every offender at once).
    - :class:`FieldTypeError` — a present field or mapping entry has the
      wrong JSON type; floats and booleans are wrong types EVERYWHERE
      (``1.0`` and ``true`` are not counts).
    - :class:`UnknownVersionError` — an integer version this loader
      cannot reach v{current} from (checked before field validation, so
      a future format is never misread as a broken current document).
    - :class:`NegativeValueError` — a well-typed quantity below zero.
    """
    if not isinstance(text, str):
        raise MalformedSaveError(f"load_state takes str, got {type(text).__name__}")
    try:
        doc = json.loads(text, parse_constant=_reject_constant)
    except json.JSONDecodeError as exc:
        raise MalformedSaveError(f"save is not valid JSON: {exc}") from exc
    if not isinstance(doc, dict):
        raise MalformedSaveError(
            f"save must be a JSON object, got {type(doc).__name__}"
        )
    doc = _migrate(doc, _read_version(doc))

    present = set(doc)
    missing, unknown = _CURRENT_KEYS - present, present - _CURRENT_KEYS
    if missing or unknown:
        raise FieldSetError(
            f"v{STATE_VERSION} save fields are wrong: "
            f"missing {sorted(missing) or '{}'}, unknown {sorted(unknown) or '{}'}"
        )
    return GameState(
        last_seen=_require_count(doc["last_seen"], "last_seen"),
        **{name: _require_mapping(doc[name], name) for name in _MAPPING_FIELDS},
    )
