#!/usr/bin/env python3
"""Deterministic generator for ``tests/vectors/saves.v2.json``.

The committed JSON is the GOLDEN SAVE-FILE CORPUS for SAVE FORMAT v2
(``docs/persistence.md``): cross-version persistence vectors mirroring
the setup-code vector pattern (``tools/gen_setup_vectors.py``). The
suite (``tests/test_save_vectors.py``) asserts the committed file is
byte-identical to a fresh in-memory regeneration AND replays every
vector through the live codec — so a future format version (v3+) that
silently changes what v1/v2 documents load into reds a test instead of
corrupting player saves in production.

Every canonical string is produced BY the real ``dump_state`` and every
migration result BY the real ``load_state`` chain; nothing here is a
hand-written canonical literal. Golden STATES are driven through the
real engine functions (``tick``/``purchase_upgrade``/``apply_prestige``/
``award_milestones``) over fixed local specs — no clock, no randomness,
no catalog dependency — so the same tree always yields the same bytes
and a theme-pack tuning change can never dirty the persistence corpus.

Regenerate (after any deliberate format change — which is a version
bump per docs/persistence.md § Version policy) with::

    python3 tools/gen_save_vectors.py

Vector categories:

- ``golden_v2`` — representative GameStates (fresh, mid-run with
  upgrades, post-prestige, milestones earned, extreme magnitudes
  >= 10^300, all-zero entries, non-ASCII ids) with their canonical v2
  strings: the byte-exact ``dump_state`` contract.
- ``golden_v1_migration`` — hand-constructable LEGACY v1 documents
  (the frozen v1 field set) with their expected v2 results from the
  real v1→v2 migration: the migration pinned byte-exactly forever.
- ``errors`` — malformed / unknown-version / field-set / field-type /
  negative-value inputs, each carrying the expected error CLASS name
  from the documented taxonomy.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:  # runnable as a script from anywhere
    sys.path.insert(0, str(REPO_ROOT))

from idle_engine import persistence  # noqa: E402
from idle_engine.achievements import MilestoneSpec, award_milestones  # noqa: E402
from idle_engine.engine import tick  # noqa: E402
from idle_engine.persistence import STATE_VERSION, dump_state, load_state  # noqa: E402
from idle_engine.prestige import PrestigeSpec, apply_prestige, prestige_eligible  # noqa: E402
from idle_engine.state import GameState, GeneratorSpec  # noqa: E402
from idle_engine.upgrades import UpgradeSpec, purchase_upgrade, upgrade_cost  # noqa: E402

VECTORS_PATH = REPO_ROOT / "tests" / "vectors" / "saves.v2.json"

#: The v2 top-level key set (the module's frozen field table, including version).
V2_FIELDS = sorted(persistence._CURRENT_KEYS)

#: The FROZEN v1 field set — v2 minus ``milestones`` (docs/persistence.md
#: § Version policy: "the v1 table ... stays frozen forever as the input
#: contract of the v1→v2 migration").
V1_FIELDS = sorted(persistence._CURRENT_KEYS - {"milestones"})

#: load_state errors a consumer must reproduce, by name (the documented
#: taxonomy; ``InvalidStateError`` is dump-side and takes a GameState,
#: not text, so it cannot appear in a string-vector file).
LOAD_ERROR_CLASSES = (
    "MalformedSaveError",
    "UnknownVersionError",
    "FieldSetError",
    "FieldTypeError",
    "NegativeValueError",
)

# --- fixed engine fixtures (local constants, deliberately NOT theme packs) --------

GENERATORS = (
    GeneratorSpec(spec_id="gen-a", produces="cur-a", base_rate=1),
    GeneratorSpec(spec_id="gen-b", produces="cur-a", base_rate=7, rate_multiplier_pct=110),
)
UPGRADES = (
    UpgradeSpec(
        spec_id="up-a",
        cost_currency="cur-a",
        base_cost=10,
        cost_growth_num=3,
        cost_growth_den=2,
        target="gen-a",
        effect_percent=25,
    ),
)
PRESTIGE = PrestigeSpec(
    awards="meta", measures="cur-a", threshold=1_000, award_divisor=100, bonus_percent=10
)
MILESTONES = (
    MilestoneSpec(spec_id="owned-1", kind="owned", subject="", threshold=1, bonus_percent=5),
    MilestoneSpec(
        spec_id="lifetime-100", kind="lifetime", subject="cur-a", threshold=100, bonus_percent=5
    ),
    MilestoneSpec(
        spec_id="prestige-1", kind="prestige", subject="meta", threshold=1, bonus_percent=5
    ),
)


def _tick(state: GameState, dt: int) -> GameState:
    return tick(state, GENERATORS, dt, UPGRADES, (PRESTIGE,), MILESTONES)


def _buy(state: GameState) -> GameState:
    spec = UPGRADES[0]
    cost = upgrade_cost(spec, state.upgrades.get(spec.spec_id, 0))
    assert state.balances.get(spec.cost_currency, 0) >= cost, "fixture drift: cannot afford"
    return purchase_upgrade(state, spec)


# --- golden v2: representative states -> canonical strings ------------------------


def _mid_run_state() -> GameState:
    """A played mid-run state: buy generators' worth of ticks + two upgrades."""
    state = GameState(owned={"gen-a": 1})
    state = _tick(state, 30)
    state = _buy(state)
    state = award_milestones(state, MILESTONES)
    state = _tick(state, 45)
    state = _buy(state)
    state = GameState(  # a second generator enters play mid-run
        **{**_state_dict(state), "owned": {**state.owned, "gen-b": 2}}
    )
    return _tick(state, 17)


def _milestones_state() -> GameState:
    """Every milestone kind earned (owned / lifetime / prestige)."""
    state = GameState(owned={"gen-a": 2, "gen-b": 1}, prestige={"meta": 1})
    state = _tick(state, 60)
    state = award_milestones(state, MILESTONES)
    assert set(state.milestones) == {m.spec_id for m in MILESTONES}, "fixture drift"
    return state

def _post_prestige_state() -> GameState:
    """A real reset: earn past the threshold, apply_prestige, play on."""
    state = GameState(owned={"gen-a": 3, "gen-b": 4})
    state = _tick(state, 40)
    state = award_milestones(state, MILESTONES)
    assert prestige_eligible(state, PRESTIGE), "fixture drift: not eligible"
    state = apply_prestige(state, PRESTIGE)
    state = GameState(**{**_state_dict(state), "owned": {"gen-a": 1}})
    return _tick(state, 10)


def _extreme_state() -> GameState:
    """Real engine output at absurd magnitude: one tick of dt = 10^300."""
    state = GameState(owned={"gen-a": 1, "gen-b": 1}, prestige={"meta": 10**9})
    state = award_milestones(state, MILESTONES)
    return _tick(state, 10**300)


def _state_dict(state: GameState) -> dict:
    return {
        "balances": dict(state.balances),
        "owned": dict(state.owned),
        "last_seen": state.last_seen,
        "upgrades": dict(state.upgrades),
        "lifetime": dict(state.lifetime),
        "prestige": dict(state.prestige),
        "milestones": dict(state.milestones),
    }


def _golden_v2_vector(name: str, state: GameState, note: str) -> dict:
    save = dump_state(state)
    # Sanity: the vector round-trips exactly, both directions, before emission.
    assert load_state(save) == state
    assert dump_state(load_state(save)) == save
    return {"name": name, "state": _state_dict(state), "save": save, "note": note}


def _build_golden_v2() -> list[dict]:
    return [
        _golden_v2_vector(
            "fresh", GameState(), "the empty state — a brand-new save, all defaults"
        ),
        _golden_v2_vector(
            "mid-run-upgrades",
            _mid_run_state(),
            "played via real tick/purchase_upgrade/award_milestones: two upgrade "
            "levels bought, second generator entered mid-run",
        ),
        _golden_v2_vector(
            "milestones-earned",
            _milestones_state(),
            "all three milestone kinds earned (owned/lifetime/prestige) via "
            "award_milestones",
        ),
        _golden_v2_vector(
            "post-prestige",
            _post_prestige_state(),
            "a real apply_prestige reset: run fields wiped, prestige + milestones "
            "survive, then played on",
        ),
        _golden_v2_vector(
            "extreme-magnitude",
            _extreme_state(),
            "real engine output of one dt=10^300 tick — unbounded ints serialize "
            "exactly at any magnitude",
        ),
        _golden_v2_vector(
            "all-zero-entries",
            GameState(
                balances={"cur-a": 0},
                owned={"gen-a": 0},
                last_seen=0,
                upgrades={"up-a": 0},
                lifetime={"cur-a": 0},
                prestige={"meta": 0},
                milestones={"owned-1": 0},
            ),
            "explicit zero entries are content, not absence: {'a': 0} != {} and "
            "round-trips as such",
        ),
        _golden_v2_vector(
            "non-ascii-ids",
            GameState(balances={"café": 7}, lifetime={"café": 7}, last_seen=5),
            "non-ASCII mapping keys are ensure_ascii-escaped — the save string is "
            "plain ASCII bytes on every platform",
        ),
    ]


# --- golden v1: legacy documents -> expected v2 migration results ------------------


def _v1_text(*, balances={}, owned={}, last_seen=0, upgrades={}, lifetime={}, prestige={}) -> str:
    """A LEGACY v1 document, spelled canonically (sorted keys, no whitespace).

    Hand-constructable per the frozen v1 field set — v1 documents can no
    longer be produced by the live encoder (it writes v2), which is
    exactly why the corpus must pin them.
    """
    doc = {
        "state_version": 1,
        "balances": balances,
        "owned": owned,
        "last_seen": last_seen,
        "upgrades": upgrades,
        "lifetime": lifetime,
        "prestige": prestige,
    }
    assert sorted(doc) == V1_FIELDS
    return json.dumps(doc, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _golden_v1_vector(name: str, v1_text: str, note: str) -> dict:
    migrated = load_state(v1_text)  # the REAL v1→v2 migration chain
    expected_v2 = dump_state(migrated)
    # Sanity: migrated saves are first-class v2 citizens.
    assert load_state(expected_v2) == migrated
    assert json.loads(expected_v2)["milestones"] == {}  # achievements post-date v1
    return {"name": name, "v1": v1_text, "expected_v2": expected_v2, "note": note}


def _build_golden_v1() -> list[dict]:
    return [
        _golden_v1_vector(
            "v1-empty",
            _v1_text(),
            "the canonical empty v1 save migrates to the canonical empty v2 save",
        ),
        _golden_v1_vector(
            "v1-mid-run",
            _v1_text(
                balances={"cur-a": 42},
                owned={"gen-a": 3},
                last_seen=1_700_000_000,
                upgrades={"up-a": 2},
                lifetime={"cur-a": 999},
                prestige={"meta": 1},
            ),
            "a populated legacy save: every v1 field carried through unchanged, "
            "milestones arrives empty",
        ),
        _golden_v1_vector(
            "v1-zero-entries",
            _v1_text(balances={"cur-a": 0}, owned={"gen-a": 0}, upgrades={"up-a": 0}),
            "explicit zero entries survive migration — never pruned",
        ),
        _golden_v1_vector(
            "v1-prestige-veteran",
            _v1_text(
                balances={"cur-a": 12},
                owned={"gen-a": 25, "gen-b": 10},
                last_seen=1_800_000_000,
                upgrades={"up-a": 9},
                lifetime={"cur-a": 123_456_789},
                prestige={"meta": 40},
            ),
            "a many-reset legacy player migrates with prestige intact and ZERO "
            "milestones — earning starts post-migration",
        ),
        _golden_v1_vector(
            "v1-extreme-magnitude",
            _v1_text(
                balances={"cur-a": 10**300},
                lifetime={"cur-a": 10**300 + 1},
                last_seen=2**63,
            ),
            "magnitude survives migration exactly — no precision loss at 10^300",
        ),
        _golden_v1_vector(
            "v1-non-ascii-ids",
            _v1_text(balances={"café": 7}, lifetime={"café": 7}),
            "escaped non-ASCII ids migrate byte-exactly",
        ),
    ]


# --- error vectors ------------------------------------------------------------------


def _doc(**overrides) -> str:
    """A valid v2 document text, tweakable per error vector."""
    base = {
        "state_version": 2,
        "balances": {"cur-a": 42},
        "owned": {"gen-a": 3},
        "last_seen": 1_700_000_000,
        "upgrades": {"up-a": 2},
        "lifetime": {"cur-a": 999},
        "prestige": {"meta": 1},
        "milestones": {"owned-1": 1},
    }
    base.update(overrides)
    return json.dumps(
        {k: v for k, v in base.items() if v is not ...},
        sort_keys=True,
        separators=(",", ":"),
    )


def _error_vector(name: str, bad_input: str, error: str, note: str) -> dict:
    expected = getattr(persistence, error)
    try:
        load_state(bad_input)
    except persistence.SaveError as exc:
        assert type(exc) is expected, (
            f"error vector {name!r}: got {type(exc).__name__}, want {error}"
        )
    else:
        raise AssertionError(f"error vector {name!r} loaded successfully")
    return {"name": name, "input": bad_input, "error": error, "note": note}


def _build_errors() -> list[dict]:
    v1_smuggle = json.loads(_doc(state_version=1))
    # keep milestones present: a v1 doc carrying the v2-only field.
    return [
        # -- MalformedSaveError: not a JSON object at all ---------------------------
        _error_vector("empty-string", "", "MalformedSaveError", "not JSON at all"),
        _error_vector("not-json", "not json", "MalformedSaveError", "unparseable text"),
        _error_vector(
            "truncated", _doc()[:-10], "MalformedSaveError", "a cut-off save is unparseable"
        ),
        _error_vector(
            "top-level-array", "[" + _doc() + "]", "MalformedSaveError",
            "a save is a JSON object, never an array",
        ),
        _error_vector("top-level-string", '"a string"', "MalformedSaveError", "not an object"),
        _error_vector("top-level-number", "42", "MalformedSaveError", "not an object"),
        _error_vector(
            "nan-constant", '{"state_version":NaN}', "MalformedSaveError",
            "NaN is not JSON — rejected by the constant hook",
        ),
        _error_vector(
            "infinity-in-field", _doc().replace('"last_seen":1700000000', '"last_seen":Infinity'),
            "MalformedSaveError", "Infinity is not JSON — floats appear NOWHERE in a save",
        ),
        # -- FieldSetError: wrong top-level key set ---------------------------------
        _error_vector("no-state-version", "{}", "FieldSetError", "version field is mandatory"),
        _error_vector(
            "v2-missing-field", _doc(owned=...), "FieldSetError",
            "all eight v2 fields are required — 'owned' missing",
        ),
        _error_vector(
            "v2-extra-field", _doc(surplus={"x": 1}), "FieldSetError",
            "unknown extra fields are refused, never ignored",
        ),
        _error_vector(
            "v2-missing-and-extra", _doc(prestige=..., surplus=1), "FieldSetError",
            "field-set check is a SET diff: every offender named at once",
        ),
        _error_vector(
            "v1-smuggles-milestones",
            json.dumps(v1_smuggle, sort_keys=True, separators=(",", ":")),
            "FieldSetError",
            "a v1 doc carrying the v2-only 'milestones' field was never a valid v1 "
            "save — refused loudly, never silently wiped",
        ),
        _error_vector(
            "v1-extra-field",
            json.dumps(
                {**json.loads(_v1_text()), "surplus": 1},
                sort_keys=True, separators=(",", ":"),
            ),
            "FieldSetError",
            "stray v1 fields ride through migration and red on v2 validation",
        ),
        _error_vector(
            "v1-missing-field",
            json.dumps(
                {k: v for k, v in json.loads(_v1_text()).items() if k != "owned"},
                sort_keys=True, separators=(",", ":"),
            ),
            "FieldSetError",
            "an incomplete v1 doc migrates, then fails the v2 field-set check",
        ),
        # -- FieldTypeError: wrong JSON types ---------------------------------------
        _error_vector(
            "version-string", _doc(state_version="2"), "FieldTypeError",
            "'2' is not an integer version",
        ),
        _error_vector(
            "version-bool", _doc(state_version=True), "FieldTypeError",
            "true is not an integer version (bools are not ints anywhere)",
        ),
        _error_vector(
            "version-float", _doc(state_version=2.0), "FieldTypeError",
            "2.0 is not an integer version — floats refused even when integral",
        ),
        _error_vector(
            "float-count", _doc(balances={"cur-a": 1.0}), "FieldTypeError",
            "1.0 is not a count — float drift can never enter through a save",
        ),
        _error_vector(
            "bool-count", _doc(owned={"gen-a": True}), "FieldTypeError",
            "true is not a count",
        ),
        _error_vector(
            "string-count", _doc(upgrades={"up-a": "2"}), "FieldTypeError",
            "'2' is not a count — no type coercion",
        ),
        _error_vector(
            "null-count", _doc(milestones={"owned-1": None}), "FieldTypeError",
            "null is not a count",
        ),
        _error_vector(
            "mapping-not-object", _doc(lifetime=[1, 2]), "FieldTypeError",
            "mapping fields must be JSON objects",
        ),
        _error_vector(
            "last-seen-float", _doc(last_seen=1.5), "FieldTypeError",
            "timestamps are integer seconds",
        ),
        # -- UnknownVersionError: no path to the current version --------------------
        _error_vector(
            "version-0", _doc(state_version=0), "UnknownVersionError",
            "v0 never existed — no registered migration",
        ),
        _error_vector(
            "version-negative", _doc(state_version=-1), "UnknownVersionError",
            "negative versions have no path",
        ),
        _error_vector(
            "version-3-future", _doc(state_version=3), "UnknownVersionError",
            "a FUTURE version fails loud ('update the plugin'), never misreads as "
            "the current format",
        ),
        _error_vector(
            "version-99-future", _doc(state_version=99), "UnknownVersionError",
            "any unknown future version",
        ),
        # -- NegativeValueError: well-typed quantities below zero --------------------
        _error_vector(
            "negative-balance", _doc(balances={"cur-a": -1}), "NegativeValueError",
            "every save quantity is >= 0",
        ),
        _error_vector(
            "negative-last-seen", _doc(last_seen=-1), "NegativeValueError",
            "timestamps are non-negative",
        ),
        _error_vector(
            "negative-astronomical", _doc(lifetime={"cur-a": -(10**40)}), "NegativeValueError",
            "negativity is checked at any magnitude",
        ),
        _error_vector(
            "v1-negative-migrated",
            _v1_text(balances={"cur-a": -7}),
            "NegativeValueError",
            "migrated documents face exactly the same strictness as native saves",
        ),
    ]


def build_document() -> dict:
    golden_v2 = _build_golden_v2()
    golden_v1 = _build_golden_v1()
    errors = _build_errors()
    return {
        "format": "superbot-idle-save-vectors",
        "format_version": 1,
        "state_version": STATE_VERSION,
        "generated_by": (
            "tools/gen_save_vectors.py — DO NOT EDIT BY HAND; "
            "regenerate with: python3 tools/gen_save_vectors.py"
        ),
        "contract": "docs/persistence.md",
        "canonical_form": (
            "JSON object, keys sorted lexicographically at every level, "
            "separators (',', ':'), ensure_ascii escapes, integers only"
        ),
        "v2_fields": V2_FIELDS,
        "v1_fields": V1_FIELDS,
        "load_error_classes": list(LOAD_ERROR_CLASSES),
        "counts": {
            "golden_v2": len(golden_v2),
            "golden_v1_migration": len(golden_v1),
            "errors": len(errors),
        },
        "vectors": {
            "golden_v2": golden_v2,
            "golden_v1_migration": golden_v1,
            "errors": errors,
        },
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
