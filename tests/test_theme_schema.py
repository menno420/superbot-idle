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
    path = tmp_path / "pack.yaml"
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
