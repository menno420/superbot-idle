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
    shutil.copy(EGG_FARM, tmp_path / "good.yaml")
    broken = EGG_FARM.read_text(encoding="utf-8").replace("name: eggs", "name: ''")
    (tmp_path / "broken.yaml").write_text(broken, encoding="utf-8")
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
