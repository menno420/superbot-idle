"""Theme schema v1: md/json field parity + red-gate cases.

Red-gate fixtures are built as tmp files from the shipped egg-farm pack —
never as fixture packs inside themes/ (everything there must stay green).
"""

import json
import re
from pathlib import Path

import yaml

from tools.theme_gate import main, validate_file

REPO_ROOT = Path(__file__).resolve().parent.parent
SCHEMA_PATH = REPO_ROOT / "schema" / "theme.schema.json"
DOC_PATH = REPO_ROOT / "docs" / "theme-schema.md"
EGG_FARM = REPO_ROOT / "themes" / "egg-farm.yaml"


def egg_farm_data() -> dict:
    return yaml.safe_load(EGG_FARM.read_text(encoding="utf-8"))


def write_pack(tmp_path: Path, data: dict) -> Path:
    # Named for the fixture's theme.id: the gate enforces id == filename stem,
    # and these cases must red on THEIR needle, not on a fixture-name mismatch.
    path = tmp_path / f"{data['theme']['id']}.yaml"
    path.write_text(yaml.safe_dump(data, allow_unicode=True), encoding="utf-8")
    return path


# --- doc/schema parity -----------------------------------------------------


def _schema_field_paths() -> set[str]:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    paths: set[str] = set()
    for key, sub in schema["properties"].items():
        paths.add(key)
        if "properties" in sub:
            paths.update(f"{key}.{k}" for k in sub["properties"])
        elif sub.get("type") == "array":
            paths.update(f"{key}[].{k}" for k in sub["items"]["properties"])
    return paths


def _doc_field_paths() -> set[str]:
    text = DOC_PATH.read_text(encoding="utf-8")
    section = text.split("## Fields", 1)[1].split("\n## ", 1)[0]
    return set(re.findall(r"^\|\s*`([^`]+)`\s*\|", section, flags=re.M))


def test_md_and_json_schema_field_parity():
    doc, machine = _doc_field_paths(), _schema_field_paths()
    assert doc, "docs/theme-schema.md Fields table parsed empty — parity test is vacuous"
    assert doc == machine, (
        f"doc-only fields: {sorted(doc - machine)}; schema-only fields: {sorted(machine - doc)}"
    )


def test_schema_is_draft_2020_12_and_versioned():
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    assert schema["$schema"] == "https://json-schema.org/draft/2020-12/schema"
    assert schema["properties"]["schema_version"]["const"] == 1
    assert "schema_version" in schema["required"]
    assert schema["additionalProperties"] is False


# --- the shipped pack passes -----------------------------------------------


def test_egg_farm_declares_schema_version_and_passes():
    assert egg_farm_data()["schema_version"] == 1
    assert validate_file(EGG_FARM) == []


def test_all_shipped_packs_pass_gate():
    assert main(["theme_gate", str(REPO_ROOT / "themes")]) == 0


# --- red-gate cases (each must be rejected, exit 1 through main) ------------


def _assert_rejected(tmp_path: Path, data: dict, needle: str) -> None:
    path = write_pack(tmp_path, data)
    errors = validate_file(path)
    assert errors, f"expected red gate ({needle}), got a pass"
    assert any(needle in e for e in errors), f"{needle!r} not named in: {errors}"
    assert main(["theme_gate", str(tmp_path)]) == 1


def test_oversized_title_rejected(tmp_path):
    data = egg_farm_data()
    data["theme"]["name"] = "x" * 300  # blows the 64-char name budget (256 title cap)
    _assert_rejected(tmp_path, data, "theme.name")


def test_oversized_field_value_rejected(tmp_path):
    data = egg_farm_data()
    data["theme"]["description"] = "x" * 1025  # blows the 1024-char field-value cap
    _assert_rejected(tmp_path, data, "theme.description")


def test_oversized_upgrade_description_rejected(tmp_path):
    data = egg_farm_data()
    # blows the 768-char shop-flavor budget (shop-composition arithmetic:
    # 768 + 1 newline + 139 themed cost-line text + 116 digit floor = 1024)
    data["upgrades"][0]["description"] = "x" * 769
    _assert_rejected(tmp_path, data, "upgrades[0].description")


def test_boundary_upgrade_description_passes(tmp_path):
    data = egg_farm_data()
    data["upgrades"][0]["description"] = "x" * 768  # exactly the shop-flavor budget
    assert validate_file(write_pack(tmp_path, data)) == []


def test_more_than_25_fields_worth_rejected(tmp_path):
    data = egg_farm_data()
    tier1 = data["generators"][0]
    data["generators"] = [dict(tier1, id=f"tier{i}") for i in range(1, 22)]  # 21 > 20
    _assert_rejected(tmp_path, data, "generators")


def test_too_many_currencies_rejected(tmp_path):
    data = egg_farm_data()
    primary = data["currencies"][0]
    data["currencies"] = [dict(primary, id=f"cur{i}") for i in range(1, 7)]  # 6 > 5
    data["generators"][0]["produces"] = "cur1"
    _assert_rejected(tmp_path, data, "currencies")


def test_bad_embed_color_rejected(tmp_path):
    for bad in ("gold", "#F5C54", "F5C542", "#F5C5421"):
        data = egg_farm_data()
        data["theme"]["embed_color"] = bad
        _assert_rejected(tmp_path, data, "embed_color")


def test_unknown_top_level_key_rejected(tmp_path):
    data = egg_farm_data()
    data["mechanics"] = {"autoclick": True}  # data-only discipline: no smuggled mechanics
    _assert_rejected(tmp_path, data, "mechanics")


def test_unknown_nested_key_rejected(tmp_path):
    data = egg_farm_data()
    data["generators"][0]["cost_curve"] = "exponential"
    _assert_rejected(tmp_path, data, "cost_curve")


def test_missing_schema_version_rejected(tmp_path):
    data = egg_farm_data()
    del data["schema_version"]
    _assert_rejected(tmp_path, data, "schema_version")


def test_wrong_schema_version_rejected(tmp_path):
    data = egg_farm_data()
    data["schema_version"] = 2
    _assert_rejected(tmp_path, data, "schema_version")


def test_base_rate_out_of_bounds_rejected(tmp_path):
    for bad in (0, 1001, -5):
        data = egg_farm_data()
        data["generators"][0]["base_rate"] = bad
        _assert_rejected(tmp_path, data, "base_rate")


def test_dangling_produces_rejected(tmp_path):
    data = egg_farm_data()
    data["generators"][0]["produces"] = "nonexistent"
    _assert_rejected(tmp_path, data, "produces")


def test_duplicate_generator_ids_rejected(tmp_path):
    data = egg_farm_data()
    data["generators"].append(dict(data["generators"][0]))
    _assert_rejected(tmp_path, data, "duplicate")


# --- upgrades + prestige slots (slice (b), optional additive v1 fields) ------


def test_egg_farm_ships_upgrade_and_prestige_slots():
    data = egg_farm_data()
    assert data["upgrades"], "egg-farm must fill the upgrades slot"
    assert data["prestige"], "egg-farm must fill the prestige slot"
    assert validate_file(EGG_FARM) == []


def test_pack_without_upgrades_or_prestige_still_passes(tmp_path):
    # both slots are OPTIONAL — a minimal v1 pack stays valid (additive change)
    data = egg_farm_data()
    del data["upgrades"]
    del data["prestige"]
    # dropping the prestige track removes its milestone slots too — keep
    # only the noun skins whose slots still exist for this roster
    data["milestones"] = [
        m for m in data["milestones"] if not m["id"].startswith("prestige-")
    ]
    path = write_pack(tmp_path, data)
    assert validate_file(path) == []


def test_dangling_upgrade_target_rejected(tmp_path):
    data = egg_farm_data()
    data["upgrades"][0]["target"] = "nonexistent"
    _assert_rejected(tmp_path, data, "target")


def test_duplicate_upgrade_ids_rejected(tmp_path):
    data = egg_farm_data()
    data["upgrades"].append(dict(data["upgrades"][0]))
    _assert_rejected(tmp_path, data, "duplicate")


def test_upgrade_cannot_smuggle_economy_numbers(tmp_path):
    # cost curves / effect sizes live ENGINE-side; a numeric field in the
    # theme's upgrade entry is exactly the smuggling the schema must red
    for smuggled in ("base_cost", "effect_percent", "cost_multiplier"):
        data = egg_farm_data()
        data["upgrades"][0][smuggled] = 9999
        _assert_rejected(tmp_path, data, smuggled)


def test_more_than_20_upgrades_rejected(tmp_path):
    data = egg_farm_data()
    first = data["upgrades"][0]
    data["upgrades"] = [dict(first, id=f"boost{i}") for i in range(1, 22)]  # 21 > 20
    _assert_rejected(tmp_path, data, "upgrades")


def test_prestige_currency_must_be_declared(tmp_path):
    data = egg_farm_data()
    data["prestige"]["currency"] = "nonexistent"
    _assert_rejected(tmp_path, data, "currency")


def test_prestige_measures_must_be_declared(tmp_path):
    data = egg_farm_data()
    data["prestige"]["measures"] = "nonexistent"
    _assert_rejected(tmp_path, data, "measures")


def test_prestige_currency_equal_to_measures_rejected(tmp_path):
    data = egg_farm_data()
    data["prestige"]["measures"] = data["prestige"]["currency"]
    _assert_rejected(tmp_path, data, "differ")


def test_prestige_cannot_smuggle_threshold(tmp_path):
    data = egg_farm_data()
    data["prestige"]["threshold"] = 1
    _assert_rejected(tmp_path, data, "threshold")


# --- labels slots (themed-label-slots slice, optional additive v1 fields) ----

LABEL_SLOTS = (
    "offline_return",
    "status_title",
    "shop_title",
    "shop_description",
    "level",
    "prestige_progress",
)


def test_all_shipped_packs_fill_labels():
    for pack in sorted((REPO_ROOT / "themes").glob("*.yaml")):
        data = yaml.safe_load(pack.read_text(encoding="utf-8"))
        assert data.get("labels"), f"{pack.stem} must fill the labels slot"
        assert set(data["labels"]) == set(LABEL_SLOTS), (
            f"{pack.stem} should fill every label slot"
        )


def test_pack_without_labels_still_passes(tmp_path):
    # the whole block is OPTIONAL — a pre-labels pack stays valid (additive)
    data = egg_farm_data()
    del data["labels"]
    path = write_pack(tmp_path, data)
    assert validate_file(path) == []


def test_every_label_slot_individually_optional(tmp_path):
    # EVERY slot inside the block is optional too — one slot alone is valid
    for slot in LABEL_SLOTS:
        data = egg_farm_data()
        data["labels"] = {slot: data["labels"][slot]}
        path = write_pack(tmp_path, data)
        assert validate_file(path) == [], f"labels with only {slot!r} must pass"


def test_empty_labels_block_rejected(tmp_path):
    data = egg_farm_data()
    data["labels"] = {}
    _assert_rejected(tmp_path, data, "labels")


def test_unknown_label_slot_rejected(tmp_path):
    data = egg_farm_data()
    data["labels"]["click_sound"] = "cluck"
    _assert_rejected(tmp_path, data, "click_sound")


def test_label_budget_boundaries_pass(tmp_path):
    data = egg_farm_data()
    data["labels"] = {
        "offline_return": "x" * 249 + "{gains}",  # 256 incl. the 7-char token
        "status_title": "t" * 256,
        "shop_title": "s" * 256,
        "shop_description": "d" * 1024,
        "level": "l" * 32,
        "prestige_progress": "p" * 64,
    }
    path = write_pack(tmp_path, data)
    assert validate_file(path) == []


def test_oversized_label_slots_rejected(tmp_path):
    for slot, limit in (
        ("offline_return", 256),
        ("status_title", 256),
        ("shop_title", 256),
        ("shop_description", 1024),
        ("level", 32),
        ("prestige_progress", 64),
    ):
        data = egg_farm_data()
        filler = "x" * (limit + 1)
        if slot == "offline_return":
            filler = "{gains}" + "x" * (limit + 1 - len("{gains}"))
        data["labels"][slot] = filler
        _assert_rejected(tmp_path, data, f"labels.{slot}")


def test_non_string_label_rejected(tmp_path):
    data = egg_farm_data()
    data["labels"]["level"] = 42
    _assert_rejected(tmp_path, data, "labels.level")


# --- milestones slots (achievements slice, optional additive v1 field) -------

MILESTONE_SLOT_IDS = tuple(
    f"{kind}-{i}" for kind in ("owned", "lifetime", "prestige") for i in (1, 2, 3)
)


def test_egg_farm_fills_every_milestone_slot():
    data = egg_farm_data()
    assert [m["id"] for m in data["milestones"]] == list(MILESTONE_SLOT_IDS)
    assert validate_file(EGG_FARM) == []


def test_three_shipped_packs_fill_the_milestones_slot():
    filled = [
        pack.stem
        for pack in sorted((REPO_ROOT / "themes").glob("*.yaml"))
        if yaml.safe_load(pack.read_text(encoding="utf-8")).get("milestones")
    ]
    assert {"egg-farm", "space-colony", "potion-brewery"} <= set(filled)


def test_pack_without_milestones_still_passes(tmp_path):
    # the whole block is OPTIONAL — a pre-achievements pack stays valid
    data = egg_farm_data()
    del data["milestones"]
    assert validate_file(write_pack(tmp_path, data)) == []


def test_unknown_milestone_slot_id_rejected(tmp_path):
    data = egg_farm_data()
    data["milestones"][0]["id"] = "owned-9"
    _assert_rejected(tmp_path, data, "milestones[0].id")


def test_duplicate_milestone_slot_ids_rejected(tmp_path):
    data = egg_farm_data()
    data["milestones"][1]["id"] = data["milestones"][0]["id"]
    _assert_rejected(tmp_path, data, "duplicate")


def test_prestige_milestone_nouns_require_prestige_block(tmp_path):
    data = egg_farm_data()
    del data["prestige"]
    _assert_rejected(tmp_path, data, "prestige")


def test_milestone_cannot_smuggle_economy_numbers(tmp_path):
    # thresholds and bonus percents live ENGINE-side (pre-registered in
    # docs/design/achievements-v0.md) — numeric fields here must red
    for smuggled in ("threshold", "bonus_percent", "kind", "target"):
        data = egg_farm_data()
        data["milestones"][0][smuggled] = 9999
        _assert_rejected(tmp_path, data, smuggled)


def test_oversized_milestone_strings_rejected(tmp_path):
    for field, limit in (("name", 64), ("description", 768), ("emoji", 32)):
        data = egg_farm_data()
        data["milestones"][0][field] = "x" * (limit + 1)
        _assert_rejected(tmp_path, data, f"milestones[0].{field}")


def test_boundary_milestone_description_passes(tmp_path):
    data = egg_farm_data()
    data["milestones"][0]["description"] = "x" * 768
    assert validate_file(write_pack(tmp_path, data)) == []


def test_partial_milestone_fill_passes(tmp_path):
    # a pack may skin any SUBSET of the slots; unfilled slots render neutral
    data = egg_farm_data()
    data["milestones"] = data["milestones"][:2]
    assert validate_file(write_pack(tmp_path, data)) == []


def test_empty_milestones_list_rejected(tmp_path):
    data = egg_farm_data()
    data["milestones"] = []
    _assert_rejected(tmp_path, data, "milestones")


def test_more_than_nine_milestones_rejected(tmp_path):
    data = egg_farm_data()
    data["milestones"].append(dict(data["milestones"][0]))
    _assert_rejected(tmp_path, data, "milestones")


def test_offline_return_missing_placeholder_rejected(tmp_path):
    data = egg_farm_data()
    data["labels"]["offline_return"] = "The generators were busy."
    _assert_rejected(tmp_path, data, "labels.offline_return")


def test_offline_return_duplicate_placeholder_rejected(tmp_path):
    data = egg_farm_data()
    data["labels"]["offline_return"] = "{gains} and then {gains} again"
    _assert_rejected(tmp_path, data, "exactly once")


def test_offline_return_unknown_placeholder_rejected(tmp_path):
    for bad in (
        "Back with {loot}!",  # unknown token instead of {gains}
        "{gains} plus a {bonus}",  # unknown token alongside the real one
        "stray } brace with {gains}",  # unbalanced brace
        "{gains} then {",  # dangling opener
    ):
        data = egg_farm_data()
        data["labels"]["offline_return"] = bad
        _assert_rejected(tmp_path, data, "labels.offline_return")
