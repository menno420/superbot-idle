"""Structural-shape guards in :func:`idle_engine.theme.load_theme`.

``load_theme`` validates a theme pack in two passes. The *semantic* pass —
unknown currency references, unknown/duplicate milestone slots, bad offline
templates, unknown label slots — is already pinned by ``tests/test_theme.py``.
This module pins the *structural* pass that runs first: the guards that reject a
pack whose SHAPE is wrong before any id can be resolved. A pack that is not a
mapping, a missing ``theme`` block, ``currencies``/``generators`` that are not
non-empty lists, non-mapping items inside the ``currencies``/``generators``/
``balance``/``upgrades``/``milestones`` blocks, a duplicate upgrade id, and the
"when present, must be a (non-empty) list/mapping" guards on the optional
``upgrades``/``prestige``/``labels``/``milestones`` blocks must all fail loud.

Every case builds the smallest malformed pack that reaches its target guard,
dumps it to a tmp YAML file, and asserts the guard's exact message fragment —
mirroring the accept/reject discipline ``tests/test_engine_guards.py`` set for
the pure-domain math. Sb-free by construction: opaque ids only, no theme nouns,
no host import.
"""

import re

import pytest
import yaml

from idle_engine import load_theme


def _base_pack() -> dict:
    """The smallest structurally valid pack: one currency, one generator."""
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


def _valid_upgrade() -> dict:
    return {
        "id": "boost1",
        "name": "up",
        "description": "d",
        "emoji": "u",
        "target": "tier1",
    }


def _load(pack, tmp_path):
    path = tmp_path / "pack.yaml"
    path.write_text(yaml.safe_dump(pack), encoding="utf-8")
    return load_theme(path)


def _load_text(text: str, tmp_path):
    """Load a pack from RAW YAML text — the only way to express a duplicate
    mapping key (``yaml.safe_dump`` of a dict cannot emit a repeated key)."""
    path = tmp_path / "pack.yaml"
    path.write_text(text, encoding="utf-8")
    return load_theme(path)


# --- top-level shape ---------------------------------------------------------


def test_rejects_non_mapping_pack(tmp_path):
    # A YAML list (not a mapping) at the document root.
    with pytest.raises(ValueError, match="theme pack must be a mapping"):
        _load(["not", "a", "mapping"], tmp_path)


def test_rejects_missing_theme_mapping(tmp_path):
    pack = _base_pack()
    del pack["theme"]
    with pytest.raises(ValueError, match="missing 'theme' mapping"):
        _load(pack, tmp_path)


# --- currencies block --------------------------------------------------------


def test_rejects_empty_currencies_list(tmp_path):
    pack = _base_pack()
    pack["currencies"] = []
    with pytest.raises(ValueError, match="'currencies' must be a non-empty list"):
        _load(pack, tmp_path)


def test_rejects_non_mapping_currency_item(tmp_path):
    pack = _base_pack()
    pack["currencies"] = ["not-a-mapping"]
    with pytest.raises(ValueError, match=re.escape("currencies[0] must be a mapping")):
        _load(pack, tmp_path)


def test_rejects_duplicate_currency_id(tmp_path):
    # Two currencies sharing an id must fail loud, not silently drop the
    # first — matching the balance/upgrades/milestones dup guards. Without
    # the guard the loader keeps only the LAST entry, so the earlier
    # name/emoji vanish with no error (silent authoring-error data loss).
    pack = _base_pack()
    pack["currencies"] = [
        {"id": "primary", "name": "first", "description": "d", "emoji": "a"},
        {"id": "primary", "name": "second", "description": "d", "emoji": "b"},
    ]
    with pytest.raises(ValueError, match="duplicate currency id"):
        _load(pack, tmp_path)


# --- generators block --------------------------------------------------------


def test_rejects_empty_generators_list(tmp_path):
    pack = _base_pack()
    pack["generators"] = []
    with pytest.raises(ValueError, match="'generators' must be a non-empty list"):
        _load(pack, tmp_path)


def test_rejects_non_mapping_generator_item(tmp_path):
    pack = _base_pack()
    pack["generators"] = ["not-a-mapping"]
    with pytest.raises(ValueError, match=re.escape("generators[0] must be a mapping")):
        _load(pack, tmp_path)


def test_rejects_duplicate_generator_id(tmp_path):
    # Two generators sharing an id must fail loud. Without the guard the
    # last entry silently wins, so the surviving generator can 'produces' a
    # DIFFERENT currency than the author's first declaration named — a
    # silent mechanics change, worse than a shape nit.
    pack = _base_pack()
    pack["currencies"].append(
        {"id": "secondary", "name": "gems", "description": "d", "emoji": "s"}
    )
    pack["generators"] = [
        {
            "id": "tier1",
            "name": "first",
            "description": "d",
            "emoji": "g",
            "produces": "primary",
            "base_rate": 1,
        },
        {
            "id": "tier1",
            "name": "second",
            "description": "d",
            "emoji": "h",
            "produces": "secondary",
            "base_rate": 5,
        },
    ]
    with pytest.raises(ValueError, match="duplicate generator id"):
        _load(pack, tmp_path)


# --- balance block (optional) ------------------------------------------------


def test_rejects_non_mapping_balance_item(tmp_path):
    pack = _base_pack()
    pack["balance"] = ["not-a-mapping"]
    with pytest.raises(ValueError, match=re.escape("balance[0] must be a mapping")):
        _load(pack, tmp_path)


# --- upgrades block (optional) -----------------------------------------------


def test_rejects_empty_upgrades_list(tmp_path):
    pack = _base_pack()
    pack["upgrades"] = []
    with pytest.raises(
        ValueError, match="'upgrades', when present, must be a non-empty list"
    ):
        _load(pack, tmp_path)


def test_rejects_non_mapping_upgrade_item(tmp_path):
    pack = _base_pack()
    pack["upgrades"] = ["not-a-mapping"]
    with pytest.raises(ValueError, match=re.escape("upgrades[0] must be a mapping")):
        _load(pack, tmp_path)


def test_rejects_duplicate_upgrade_id(tmp_path):
    pack = _base_pack()
    pack["upgrades"] = [_valid_upgrade(), _valid_upgrade()]
    with pytest.raises(ValueError, match="duplicate upgrade id"):
        _load(pack, tmp_path)


# --- prestige block (optional) -----------------------------------------------


def test_rejects_non_mapping_prestige_block(tmp_path):
    pack = _base_pack()
    pack["prestige"] = ["not", "a", "mapping"]
    with pytest.raises(
        ValueError, match="'prestige', when present, must be a mapping"
    ):
        _load(pack, tmp_path)


# --- labels block (optional) -------------------------------------------------


def test_rejects_empty_labels_mapping(tmp_path):
    pack = _base_pack()
    pack["labels"] = {}
    with pytest.raises(
        ValueError, match="'labels', when present, must be a non-empty mapping"
    ):
        _load(pack, tmp_path)


# --- milestones block (optional) ---------------------------------------------


def test_rejects_empty_milestones_list(tmp_path):
    pack = _base_pack()
    pack["milestones"] = []
    with pytest.raises(
        ValueError, match="'milestones', when present, must be a non-empty list"
    ):
        _load(pack, tmp_path)


def test_rejects_non_mapping_milestone_item(tmp_path):
    pack = _base_pack()
    pack["milestones"] = ["not-a-mapping"]
    with pytest.raises(ValueError, match=re.escape("milestones[0] must be a mapping")):
        _load(pack, tmp_path)


# --- base_rate numeric bounds (schema minimum 1, maximum 1000) ---------------
#
# The schema declares ``generators[].base_rate`` an integer bounded 1..1000
# ("Bounded 1-1000 in v1 so a theme cannot smuggle economy balance"). The gate
# (jsonschema) enforces both ends. The loader — the engine's runtime ground
# truth — re-checks the LOWER bound (positivity) as defense in depth, but the
# UPPER bound must be re-checked too: without it a pack with ``base_rate:
# 999999``, loaded directly via ``load_theme`` OUTSIDE the gate, loads clean and
# carries an out-of-bounds rate straight into the engine economy (no crash, no
# error — the exact balance-smuggling the schema bound exists to prevent).
# Mirror the balance-bounds re-check: both ends enforced at load with a
# where-anchored ValueError.


@pytest.mark.parametrize("bad_rate", [1001, 5000, 999999])
def test_rejects_base_rate_above_schema_max(tmp_path, bad_rate):
    pack = _base_pack()
    pack["generators"][0]["base_rate"] = bad_rate
    with pytest.raises(ValueError, match="base_rate"):
        _load(pack, tmp_path)


def test_accepts_base_rate_at_schema_max(tmp_path):
    # The boundary value 1000 is IN-bounds — the guard is inclusive and must
    # not over-reject a valid pack.
    pack = _base_pack()
    pack["generators"][0]["base_rate"] = 1000
    theme = _load(pack, tmp_path)
    assert theme.generators["tier1"].base_rate == 1000


# --- duplicate YAML mapping keys (document-structure ambiguity) ---------------
#
# PyYAML's ``safe_load`` SILENTLY accepts a repeated mapping key and keeps the
# LAST value, so a pack with an accidental duplicate key (a stray second
# ``name:``, a copy-pasted ``base_rate:``) parses clean with the author's
# intended value dropped — every downstream check then validates corrupted
# data. The loader is the runtime ground truth, so it must reject the ambiguous
# document loud, at any nesting depth. Runtime twin of the CI-time gate check
# in tools/theme_gate.py (kept loader-local, not imported — same cross-layer
# discipline as the _HEX_COLOR / GAINS_PLACEHOLDER copies).


def test_rejects_duplicate_top_level_key(tmp_path):
    # A stray second ``theme.name``: under safe_load the pack loads with
    # name == 'SHADOW NAME' and the author's 'Real Name' vanishes silently.
    text = (
        "theme:\n"
        "  id: t\n"
        "  name: Real Name\n"
        "  name: SHADOW NAME\n"
        "  description: d\n"
        "  emoji: x\n"
        "  embed_color: '#000000'\n"
        "currencies:\n"
        "  - id: primary\n"
        "    name: coins\n"
        "    description: d\n"
        "    emoji: c\n"
        "generators:\n"
        "  - id: tier1\n"
        "    name: gen\n"
        "    description: d\n"
        "    emoji: g\n"
        "    produces: primary\n"
        "    base_rate: 1\n"
    )
    with pytest.raises(ValueError, match="duplicate key"):
        _load_text(text, tmp_path)


def test_rejects_duplicate_nested_key(tmp_path):
    # A duplicated leaf inside a list item (generators[0].base_rate): proves
    # detection reaches arbitrary nesting depth, not just the document root.
    text = (
        "theme:\n"
        "  id: t\n"
        "  name: T\n"
        "  description: d\n"
        "  emoji: x\n"
        "  embed_color: '#000000'\n"
        "currencies:\n"
        "  - id: primary\n"
        "    name: coins\n"
        "    description: d\n"
        "    emoji: c\n"
        "generators:\n"
        "  - id: tier1\n"
        "    name: gen\n"
        "    description: d\n"
        "    emoji: g\n"
        "    produces: primary\n"
        "    base_rate: 1\n"
        "    base_rate: 999\n"
    )
    with pytest.raises(ValueError, match="duplicate key"):
        _load_text(text, tmp_path)
