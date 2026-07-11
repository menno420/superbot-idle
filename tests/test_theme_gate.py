"""theme-gate v0: validator passes real packs, fails broken ones, exits right."""

import shutil
from pathlib import Path

from tools.theme_gate import main, validate_file

REPO_ROOT = Path(__file__).resolve().parent.parent
EGG_FARM = REPO_ROOT / "themes" / "egg-farm.yaml"


def test_all_shipped_packs_pass(capsys):
    assert main(["theme_gate", str(REPO_ROOT / "themes")]) == 0
    out = capsys.readouterr().out
    assert "PASS" in out and "FAIL" not in out


def test_empty_themes_dir_is_an_error(tmp_path):
    assert main(["theme_gate", str(tmp_path)]) == 2


def test_broken_pack_fails_gate(tmp_path, capsys):
    shutil.copy(EGG_FARM, tmp_path / "egg-farm.yaml")
    broken = EGG_FARM.read_text(encoding="utf-8").replace("name: eggs", "name: ''")
    (tmp_path / "broken.yaml").write_text(
        broken.replace("id: egg-farm", "id: broken"), encoding="utf-8"
    )
    assert main(["theme_gate", str(tmp_path)]) == 1
    out = capsys.readouterr().out
    assert "FAIL" in out and "PASS" in out


def test_string_budget_enforced(tmp_path):
    oversized = EGG_FARM.read_text(encoding="utf-8").replace(
        "name: Egg Farm", "name: " + "x" * 300
    )
    path = tmp_path / "oversized.yaml"
    path.write_text(oversized, encoding="utf-8")
    errors = validate_file(path)
    assert errors and "theme.name" in errors[0]


def test_bad_embed_color_rejected(tmp_path):
    bad = EGG_FARM.read_text(encoding="utf-8").replace('"#F5C542"', '"gold"')
    path = tmp_path / "badcolor.yaml"
    path.write_text(bad, encoding="utf-8")
    errors = validate_file(path)
    assert errors and "embed_color" in errors[0]


def test_unparseable_yaml_fails_not_crashes(tmp_path):
    path = tmp_path / "garbage.yaml"
    path.write_text("just a string, not a mapping", encoding="utf-8")
    errors = validate_file(path)
    assert errors and "mapping" in errors[0]


# --- theme.id <-> filename-stem convention (red both directions, green match)


def test_valid_pack_under_wrong_filename_reds_gate(tmp_path, capsys):
    # direction 1: untouched valid pack, WRONG filename
    shutil.copy(EGG_FARM, tmp_path / "renamed-pack.yaml")
    errors = validate_file(tmp_path / "renamed-pack.yaml")
    assert errors and "filename stem" in errors[0]
    assert "'egg-farm'" in errors[0] and "'renamed-pack'" in errors[0]
    assert main(["theme_gate", str(tmp_path)]) == 1
    assert "filename stem" in capsys.readouterr().out


def test_edited_theme_id_under_right_filename_reds_gate(tmp_path):
    # direction 2: RIGHT filename, theme.id edited away from it
    drifted = EGG_FARM.read_text(encoding="utf-8").replace(
        "id: egg-farm", "id: drifted-id"
    )
    path = tmp_path / "egg-farm.yaml"
    path.write_text(drifted, encoding="utf-8")
    errors = validate_file(path)
    assert errors and "filename stem" in errors[0]
    assert "'drifted-id'" in errors[0] and "'egg-farm'" in errors[0]


def test_theme_id_matching_filename_stem_passes(tmp_path, capsys):
    shutil.copy(EGG_FARM, tmp_path / "egg-farm.yaml")
    assert validate_file(tmp_path / "egg-farm.yaml") == []
    assert main(["theme_gate", str(tmp_path)]) == 0
    assert "filename stem" not in capsys.readouterr().out
