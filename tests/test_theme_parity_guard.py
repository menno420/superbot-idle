"""Durable loader↔schema PARITY GUARD — the capstone of the schema-enforcement
class of fixes (#164 embed_color format, #166/#167 duplicate YAML keys, #168
base_rate ceiling).

Those slices closed a whole family of bug: a constraint the schema *declares*
and the CI gate (``tools/theme_gate.py``) *enforces*, but that
``idle_engine.theme.load_theme`` — the engine's RUNTIME ground truth — did not
re-check, so a pack loaded outside the gate (a live server reading an unvetted
pack, any direct ``load_theme`` caller) silently corrupted or smuggled balance.
The loader now re-checks every value/format/uniqueness/reference/numeric-bound
constraint in that class, and per-constraint violation tests pin that each
KNOWN constraint stays enforced (base_rate both ends —
``tests/test_theme_loader_guards.py``; rate_multiplier both ends —
``tests/test_theme_balance.py``; embed_color format, ``produces`` reference,
duplicate keys/ids — ``tests/test_theme.py`` + the guards module).

What NONE of those catch is a NEW schema constraint added WITHOUT matching
loader enforcement — the exact way this class would silently regress. This
module closes that meta-gap two ways:

1. :func:`_schema_constraints` introspects ``schema/theme.schema.json`` and
   emits one token ``<path>:<keyword>`` per constraint-bearing keyword. A total
   classifier (:func:`_classify`) sorts every token into ``"loader"`` (the
   loader re-checks it) or ``"gate"`` (a reviewed gate-only / structural-sugar
   allow-list). The *dangerous* families — numeric bounds, ``pattern``,
   ``enum``, ``const``, unknown-key rejection — are pinned to EXACT paths, so a
   new occurrence on a new field lands in neither bucket and REDS
   :func:`test_every_schema_constraint_is_loader_enforced_or_reviewed_gate_only`,
   forcing a human to wire a loader guard or consciously mark it gate-only.

2. Four concrete loader violation tests for the reference-integrity guards that
   existed in the loader but had NO loader-level test (only gate coverage):
   dangling ``upgrades[].target`` / ``prestige.currency`` / ``prestige.measures``
   and the prestige ``currency == measures`` "differ" rule. These give the suite
   direct teeth against a loosened loader guard and close a real coverage gap.

Sb-free by construction: opaque ids only, no theme nouns, no host import.
TEST-ONLY — this module asserts existing behavior; it changes none.
"""

import json
from pathlib import Path

import pytest
import yaml

from idle_engine import load_theme

REPO_ROOT = Path(__file__).resolve().parent.parent
SCHEMA_PATH = REPO_ROOT / "schema" / "theme.schema.json"


# --------------------------------------------------------------------------- #
# Schema introspection: every constraint the schema declares, as a flat token  #
# set ``<json-path>:<keyword>`` (path "" is the document root).                 #
# --------------------------------------------------------------------------- #

# The keywords that express a real value/shape constraint (as opposed to
# annotations like "description" / "title"). additionalProperties is handled
# separately because only the ``false`` form is a constraint.
_CONSTRAINT_KEYWORDS = frozenset(
    {
        "type",
        "pattern",
        "minimum",
        "maximum",
        "minItems",
        "maxItems",
        "minLength",
        "maxLength",
        "minProperties",
        "const",
        "enum",
    }
)


def _resolve(schema: dict, node: dict) -> dict:
    """Resolve a ``$ref`` one level into ``$defs``, merging any sibling keys.

    JSON-Schema 2020-12 allows keywords alongside ``$ref``; merging siblings
    over the ``$defs`` target means a constraint added NEXT TO a ``$ref`` (e.g.
    a tighter ``maxLength`` on one field that otherwise reuses ``slug``) is
    still seen by the walk rather than silently dropped.
    """
    if "$ref" not in node:
        return node
    key = node["$ref"].split("/")[-1]
    target = schema["$defs"][key]
    merged = dict(target)
    merged.update({k: v for k, v in node.items() if k != "$ref"})
    return merged


def _schema_constraints() -> set[str]:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    out: set[str] = set()

    def walk(node: dict, path: str) -> None:
        node = _resolve(schema, node)
        for kw in _CONSTRAINT_KEYWORDS:
            if kw in node:
                out.add(f"{path}:{kw}")
        for req in node.get("required", []):
            out.add(f"{path}.{req}:required" if path else f"{req}:required")
        if node.get("additionalProperties") is False:
            out.add(f"{path}:additionalProperties")
        for key, sub in node.get("properties", {}).items():
            walk(sub, f"{path}.{key}" if path else key)
        if "items" in node:
            walk(node["items"], f"{path}[]")

    walk(schema, "")
    return out


# --------------------------------------------------------------------------- #
# The reviewed classification.                                                  #
#                                                                               #
# DANGEROUS families are pinned to EXACT paths: a numeric bound / format        #
# pattern / value enum / unknown-key rejection on ANY field the loader does not #
# re-check is exactly how a pack silently corrupts or smuggles balance, so a    #
# NEW occurrence must fall through to "unclassified" and red the test.          #
# --------------------------------------------------------------------------- #

# Numeric bounds the loader re-checks (idle_engine/theme.py: BASE_RATE_MIN/MAX
# and RATE_MULTIPLIER_MIN/MAX). A ``minimum``/``maximum`` on any other field is
# unreviewed → red.
_LOADER_NUMERIC_BOUND_PATHS = frozenset(
    {"generators[].base_rate", "balance[].rate_multiplier_pct"}
)

# The ONE format ``pattern`` the loader re-checks (the _HEX_COLOR regex).
_LOADER_PATTERN_PATHS = frozenset({"theme.embed_color"})

# Slug charset ``pattern``s — GATE ONLY. An out-of-charset id cannot smuggle
# mechanics (the worst case is a cosmetically odd id string); referential
# integrity for the reference-bearing slugs IS loader-enforced, but that is a
# procedural check, not a schema keyword, so it never appears in this token set.
_GATE_SLUG_PATTERN_PATHS = frozenset(
    {
        "theme.id",
        "currencies[].id",
        "generators[].id",
        "generators[].produces",
        "upgrades[].id",
        "upgrades[].target",
        "prestige.currency",
        "prestige.measures",
        "balance[].generator",
    }
)

# The ONE ``enum`` the loader re-checks (milestone slot ids — the loader rejects
# any id outside the engine-derived slot set for the pack's roster).
_LOADER_ENUM_PATHS = frozenset({"milestones[].id"})

# The ONE ``additionalProperties: false`` the loader re-checks: the labels block
# actively rejects unknown slots ("unknown label slot"). Every OTHER block's
# unknown-key rejection is gate-only, and safely so — the loader reads only the
# keys it knows, so a smuggled unknown key is inert (it never reaches the
# engine). (This is the "data-only discipline: no smuggled mechanics" gate line;
# the loader's inertness is the runtime half of the same guarantee.)
_LOADER_UNKNOWN_KEY_PATHS = frozenset({"labels"})

# Inert / structural-sugar keywords — GATE ONLY wherever they appear. These
# cannot silently change mechanics: array caps and string budgets are
# render-embed limits (overflow is a red gate, never a live render bug), never
# an economy number.
_GATE_ONLY_KEYWORDS = frozenset({"maxItems", "maxLength"})

# Presence / type / non-empty keywords the loader re-checks generically via
# _require_str (non-empty string), the "non-empty list"/"non-empty mapping"
# block guards, and its isinstance() type checks. Classified by rule rather than
# by path: a NEW field under one of these is low-risk — a missing/empty/
# wrong-typed value on a field the loader ignores is inert, it cannot smuggle an
# economy number. (schema_version is the one exception, handled first below.)
_LOADER_PRESENCE_KEYWORDS = frozenset(
    {"required", "type", "minLength", "minItems", "minProperties"}
)


def _classify(token: str) -> str:
    """Return ``"loader"``, ``"gate"``, or ``"unclassified"`` for one token."""
    path, _, keyword = token.rpartition(":")

    # schema_version is gate-owned pack versioning — the loader never reads it,
    # so its type/required/const are ALL gate-only. Checked first so the
    # presence-keyword rule below does not sweep it into "loader".
    if path == "schema_version":
        return "gate"

    if keyword in _GATE_ONLY_KEYWORDS:
        return "gate"

    if keyword == "additionalProperties":
        return "loader" if path in _LOADER_UNKNOWN_KEY_PATHS else "gate"

    if keyword == "pattern":
        if path in _LOADER_PATTERN_PATHS:
            return "loader"
        if path in _GATE_SLUG_PATTERN_PATHS:
            return "gate"
        return "unclassified"

    if keyword in ("minimum", "maximum"):
        return "loader" if path in _LOADER_NUMERIC_BOUND_PATHS else "unclassified"

    if keyword == "enum":
        return "loader" if path in _LOADER_ENUM_PATHS else "unclassified"

    if keyword == "const":
        # The only const in v1 is schema_version (handled above); a const on any
        # other field is a value pin the loader would need to re-check.
        return "unclassified"

    if keyword in _LOADER_PRESENCE_KEYWORDS:
        return "loader"

    return "unclassified"


# --------------------------------------------------------------------------- #
# The capstone assertions.                                                       #
# --------------------------------------------------------------------------- #


def test_schema_introspection_is_not_vacuous():
    """Guard the guard: if the walk ever returns empty (a schema move renamed
    ``properties``/``$defs``), the partition test below would pass vacuously."""
    constraints = _schema_constraints()
    assert len(constraints) > 100, (
        f"schema introspection found only {len(constraints)} constraints — "
        "the walk is probably broken; the parity guard would be vacuous"
    )
    # Every token is well-formed (has a keyword) and no $ref leaked through
    # unresolved (an unresolved ref would surface as a ':$ref' style token).
    assert all(":" in t for t in constraints)
    assert not any(t.endswith(":$ref") for t in constraints)


def test_every_schema_constraint_is_loader_enforced_or_reviewed_gate_only():
    """THE parity guard.

    Every constraint the schema declares must be either re-checked by the
    loader or listed as a reviewed gate-only / structural-sugar constraint. A
    constraint in NEITHER bucket is unclassified — which happens exactly when
    someone adds a NEW schema constraint (a numeric bound, a format pattern, a
    value enum, an unknown-key rule) without wiring the matching
    ``load_theme`` guard. That is the silent-regression this whole class of
    fixes exists to prevent, so it must red here and force a human decision.
    """
    unclassified = sorted(t for t in _schema_constraints() if _classify(t) == "unclassified")
    assert not unclassified, (
        "New schema constraint(s) with no matching loader enforcement and no "
        "reviewed gate-only entry:\n  "
        + "\n  ".join(unclassified)
        + "\n\nDecide for each: either re-check it in "
        "idle_engine/theme.py::load_theme and pin the exact path in the "
        "loader allow-list in this module, OR — if it genuinely cannot "
        "silently change mechanics (a render budget, a cosmetic slug shape) — "
        "add it to the reviewed gate-only allow-list with a one-line rationale."
    )


def test_loader_allow_lists_have_no_stale_entries():
    """The pinned loader-enforced paths must all still exist in the schema, so
    REMOVING a constraint (or renaming its field) reds here too — the guard
    stays honest in both directions, not just against additions."""
    constraints = _schema_constraints()
    paths = {t.rpartition(":")[0] for t in constraints}
    pinned = (
        _LOADER_NUMERIC_BOUND_PATHS
        | _LOADER_PATTERN_PATHS
        | _GATE_SLUG_PATTERN_PATHS
        | _LOADER_ENUM_PATHS
        | _LOADER_UNKNOWN_KEY_PATHS
    )
    stale = sorted(p for p in pinned if p not in paths)
    assert not stale, (
        f"parity allow-list names path(s) the schema no longer declares: {stale} "
        "— the schema changed; re-review the classification."
    )


def test_known_dangerous_constraints_classify_as_loader():
    """Positive anchor: the specific constraints this class of fixes closed are
    still classified loader-enforced (so a bad edit to the allow-list that drops
    one is caught, not silently downgraded to gate-only)."""
    for token in (
        "generators[].base_rate:minimum",
        "generators[].base_rate:maximum",
        "balance[].rate_multiplier_pct:minimum",
        "balance[].rate_multiplier_pct:maximum",
        "theme.embed_color:pattern",
        "milestones[].id:enum",
        "labels:additionalProperties",
    ):
        assert token in _schema_constraints(), f"{token} vanished from the schema"
        assert _classify(token) == "loader", f"{token} must stay loader-enforced"


# --------------------------------------------------------------------------- #
# Gap-closing loader violation tests — reference-integrity guards that existed  #
# in load_theme but had no loader-level coverage (only gate coverage). These    #
# give the suite direct teeth against a loosened loader guard.                  #
# --------------------------------------------------------------------------- #


def _base_pack() -> dict:
    """Smallest structurally valid pack with two currencies + a prestige track
    (opaque ids only — sb-free)."""
    return {
        "theme": {
            "id": "t",
            "name": "T",
            "description": "d",
            "emoji": "x",
            "embed_color": "#000000",
        },
        "currencies": [
            {"id": "primary", "name": "coins", "description": "d", "emoji": "c"},
            {"id": "secondary", "name": "gems", "description": "d", "emoji": "s"},
        ],
        "generators": [
            {
                "id": "tier1",
                "name": "gen",
                "description": "d",
                "emoji": "g",
                "produces": "primary",
                "base_rate": 1,
            },
        ],
    }


def _valid_prestige() -> dict:
    return {
        "currency": "secondary",
        "measures": "primary",
        "action_name": "reset",
        "action_description": "d",
        "action_emoji": "r",
    }


def _load(pack: dict, tmp_path) -> object:
    path = tmp_path / "pack.yaml"
    path.write_text(yaml.safe_dump(pack), encoding="utf-8")
    return load_theme(path)


def test_loader_rejects_dangling_upgrade_target(tmp_path):
    # load_theme checks upgrades[].target against the declared generators, but
    # only the GATE had a dangling-target test until now. Without the loader
    # guard, upgrade_specs() would KeyError deep at build time (by_id[u.target]).
    pack = _base_pack()
    pack["upgrades"] = [
        {
            "id": "boost1",
            "name": "up",
            "description": "d",
            "emoji": "u",
            "target": "nonexistent",
        }
    ]
    with pytest.raises(ValueError, match="not a declared generator"):
        _load(pack, tmp_path)


def test_loader_rejects_dangling_prestige_currency(tmp_path):
    pack = _base_pack()
    pack["prestige"] = {**_valid_prestige(), "currency": "nonexistent"}
    with pytest.raises(ValueError, match="not a declared currency"):
        _load(pack, tmp_path)


def test_loader_rejects_dangling_prestige_measures(tmp_path):
    pack = _base_pack()
    pack["prestige"] = {**_valid_prestige(), "measures": "nonexistent"}
    with pytest.raises(ValueError, match="not a declared currency"):
        _load(pack, tmp_path)


def test_loader_rejects_prestige_currency_equal_to_measures(tmp_path):
    # A track cannot measure the currency it awards. The loader enforces this
    # ("must differ"); only the gate had a test until now.
    pack = _base_pack()
    pack["prestige"] = {**_valid_prestige(), "currency": "primary", "measures": "primary"}
    with pytest.raises(ValueError, match="differ"):
        _load(pack, tmp_path)


def test_prestige_base_pack_actually_loads(tmp_path):
    # Anchor: the _base_pack + _valid_prestige fixture is itself valid, so the
    # rejection tests above red on THEIR guard, not on an unrelated defect.
    pack = _base_pack()
    pack["prestige"] = _valid_prestige()
    theme = _load(pack, tmp_path)
    assert theme.prestige is not None
    assert theme.prestige.currency == "secondary"
    assert theme.prestige.measures == "primary"
