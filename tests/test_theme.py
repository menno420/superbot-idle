"""Theme loading: the egg-farm pack supplies every player-visible noun."""

from pathlib import Path

import pytest

from idle_engine import load_theme

REPO_ROOT = Path(__file__).resolve().parent.parent
EGG_FARM = REPO_ROOT / "themes" / "egg-farm.yaml"


def test_egg_farm_nouns_map_onto_engine_ids():
    theme = load_theme(EGG_FARM)
    assert theme.theme_id == "egg-farm"
    assert theme.name == "Egg Farm"
    assert theme.currency_name("primary") == "eggs"
    assert theme.generator_name("tier1") == "chicken coop"
    assert theme.emoji and theme.embed_color.startswith("#")
    gen = theme.generators["tier1"]
    assert gen.produces == "primary"
    assert gen.base_rate == 1
    assert gen.emoji
    assert theme.currencies["primary"].description


def test_generator_specs_carry_no_display_data():
    theme = load_theme(EGG_FARM)
    (spec,) = theme.generator_specs()
    assert spec.spec_id == "tier1"
    assert spec.produces == "primary"
    assert spec.base_rate == 1
    assert not hasattr(spec, "name")
    assert not hasattr(spec, "emoji")


@pytest.mark.parametrize(
    "mutation, message_fragment",
    [
        ("name: Egg Farm", "name"),                # removed theme name
        ("- id: primary", "currencies"),           # removed only currency
        ("base_rate: 1", "base_rate"),             # removed generator rate
    ],
)
def test_loader_rejects_missing_required_fields(tmp_path, mutation, message_fragment):
    broken = EGG_FARM.read_text(encoding="utf-8").replace(mutation, "")
    path = tmp_path / "broken.yaml"
    path.write_text(broken, encoding="utf-8")
    with pytest.raises(ValueError) as excinfo:
        load_theme(path)
    assert message_fragment in str(excinfo.value)


def test_loader_rejects_produces_pointing_at_unknown_currency(tmp_path):
    broken = EGG_FARM.read_text(encoding="utf-8").replace("produces: primary", "produces: nonexistent")
    path = tmp_path / "broken.yaml"
    path.write_text(broken, encoding="utf-8")
    with pytest.raises(ValueError, match="not a declared currency"):
        load_theme(path)
