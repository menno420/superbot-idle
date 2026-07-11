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
        ('emoji: "🥇"', "currencies"),             # removed a currency's emoji
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


# --- labels block (optional, every slot optional) ----------------------------


def test_loader_maps_labels_block():
    theme = load_theme(EGG_FARM)
    assert theme.labels is not None
    assert theme.labels.level == "Coop size"
    assert theme.labels.status_title == "🥚 Egg Farm — the morning count"
    assert theme.labels.shop_title == "🧺 The Farm Supply Shed"
    assert theme.labels.shop_description == "Trade fresh eggs for a busier, happier farm."
    assert theme.labels.prestige_progress == "lifetime eggs toward the sale:"
    assert theme.labels.offline_return.count("{gains}") == 1


def test_loader_defaults_labels_to_none(tmp_path):
    stripped, sep, _ = EGG_FARM.read_text(encoding="utf-8").partition("\nlabels:")
    assert sep, "egg-farm.yaml must carry a labels block"
    path = tmp_path / "egg-farm.yaml"
    path.write_text(stripped, encoding="utf-8")
    assert load_theme(path).labels is None


def test_loader_rejects_unknown_label_slot(tmp_path):
    broken = EGG_FARM.read_text(encoding="utf-8").replace(
        "  level: Coop size", "  level: Coop size\n  click_sound: cluck"
    )
    path = tmp_path / "broken.yaml"
    path.write_text(broken, encoding="utf-8")
    with pytest.raises(ValueError, match="unknown label slot"):
        load_theme(path)


@pytest.mark.parametrize(
    "bad_template, fragment",
    [
        ('"no token here"', "exactly once"),
        ('"{gains} twice {gains}"', "exactly once"),
        ('"{gains} and a {smuggled} token"', "unknown placeholder"),
        ('"{gains} then a stray } brace"', "unknown placeholder"),
    ],
)
def test_loader_rejects_bad_offline_template(tmp_path, bad_template, fragment):
    broken = EGG_FARM.read_text(encoding="utf-8").replace(
        '"While you were away, the hens kept laying: {gains}"', bad_template
    )
    assert broken != EGG_FARM.read_text(encoding="utf-8")
    path = tmp_path / "broken.yaml"
    path.write_text(broken, encoding="utf-8")
    with pytest.raises(ValueError, match=fragment):
        load_theme(path)


# --- milestones block (optional noun skins for the engine-derived slots) -----


def test_loader_maps_milestones_block():
    theme = load_theme(EGG_FARM)
    assert set(theme.milestones) == {
        f"{kind}-{i}" for kind in ("owned", "lifetime", "prestige") for i in (1, 2, 3)
    }
    first = theme.milestones["owned-1"]
    assert first.milestone_id == "owned-1"
    assert first.name == "first flock"
    assert first.description and first.emoji


def test_loader_defaults_milestones_to_empty(tmp_path):
    src = EGG_FARM.read_text(encoding="utf-8")
    head, sep, _ = src.partition("\nmilestones:")
    assert sep, "egg-farm.yaml must carry a milestones block"
    path = tmp_path / "egg-farm.yaml"
    path.write_text(head, encoding="utf-8")
    theme = load_theme(path)
    assert theme.milestones == {}
    assert len(theme.milestone_specs()) == 9  # slots exist regardless of nouns


def test_loader_rejects_unknown_milestone_slot(tmp_path):
    broken = EGG_FARM.read_text(encoding="utf-8").replace(
        "- id: owned-1", "- id: owned-9"
    )
    path = tmp_path / "broken.yaml"
    path.write_text(broken, encoding="utf-8")
    with pytest.raises(ValueError, match="not an engine milestone slot"):
        load_theme(path)


def test_loader_rejects_duplicate_milestone_slot(tmp_path):
    broken = EGG_FARM.read_text(encoding="utf-8").replace(
        "- id: owned-2", "- id: owned-1"
    )
    path = tmp_path / "broken.yaml"
    path.write_text(broken, encoding="utf-8")
    with pytest.raises(ValueError, match="duplicate milestone"):
        load_theme(path)


def test_loader_rejects_prestige_slot_nouns_without_prestige_track(tmp_path):
    src = EGG_FARM.read_text(encoding="utf-8")
    head, sep, rest = src.partition("\nprestige:")
    assert sep
    _, _, tail = rest.partition("\nlabels:")
    path = tmp_path / "egg-farm.yaml"
    path.write_text(head + "\nlabels:" + tail, encoding="utf-8")
    with pytest.raises(ValueError, match="not an engine milestone slot"):
        load_theme(path)  # prestige-1..3 nouns skin slots that do not exist
