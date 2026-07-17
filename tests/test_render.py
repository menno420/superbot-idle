"""Render layer: engine state + theme pack -> embed-shaped payloads.

Written test-first for the render-layer slice. The render layer is the
seam superbot-next's plugin renders through: PURE presentation, plain
dicts shaped like Discord embeds, zero Discord imports. Tests here may
use theme nouns freely (they exercise the real egg-farm pack); the
module under test must contain none — `test_core_skin_guard.py` scans
`idle_engine/**/*.py`, which includes `idle_engine/render.py`.
"""

import json
import re
from pathlib import Path

import pytest

from idle_engine import GameState, load_theme
from idle_engine.render import (
    DESCRIPTION_LIMIT,
    FIELD_NAME_LIMIT,
    FIELD_VALUE_LIMIT,
    MAX_FIELDS,
    SHOP_FLAVOR_LIMIT,
    TITLE_LIMIT,
    RenderBudgetError,
    embed_color_int,
    render_achievements,
    render_prestige,
    render_shop,
    render_status,
    validate_embed,
)
from idle_engine.theme import (
    Theme,
    ThemeCurrency,
    ThemeGenerator,
    ThemeLabels,
    ThemeMilestone,
    ThemeUpgrade,
)

REPO_ROOT = Path(__file__).resolve().parent.parent
THEMES_DIR = REPO_ROOT / "themes"


@pytest.fixture(scope="module")
def egg_farm():
    return load_theme(THEMES_DIR / "egg-farm.yaml")


def _fixed_state():
    """A small deterministic save: 2 coops, some eggs, 1 upgrade level."""
    return GameState(
        balances={"primary": 1234},
        owned={"tier1": 2},
        last_seen=1_000,
        upgrades={"boost1": 1},
        lifetime={"primary": 5_000},
        prestige={"prestige": 3},
    )


def _assert_budgets(embed):
    assert len(embed["title"]) <= TITLE_LIMIT
    assert len(embed["description"]) <= DESCRIPTION_LIMIT
    assert len(embed["fields"]) <= MAX_FIELDS
    for field in embed["fields"]:
        assert 1 <= len(field["name"]) <= FIELD_NAME_LIMIT
        assert 1 <= len(field["value"]) <= FIELD_VALUE_LIMIT
        assert isinstance(field["inline"], bool)
    assert 0 <= embed["color"] <= 0xFFFFFF


# --- embed color -------------------------------------------------------------


def test_embed_color_int_parses_hex():
    assert embed_color_int("#F5C542") == 0xF5C542
    assert embed_color_int("#000000") == 0
    assert embed_color_int("#ffffff") == 0xFFFFFF


@pytest.mark.parametrize("bad", ["F5C542", "#F5C54", "#F5C5422", "#GGGGGG", "", "#12 456"])
def test_embed_color_int_rejects_malformed(bad):
    with pytest.raises(ValueError):
        embed_color_int(bad)


# --- status view -------------------------------------------------------------


def test_status_is_deterministic_and_exactly_shaped(egg_farm):
    """Pin the full payload for one fixed state: same inputs, same bytes."""
    state = _fixed_state()
    # 2 coops x base_rate 1 x (100 + 25*1 boost1)% x (100 + 10*3 prestige)% // 10_000
    # = 2 * 125 * 130 // 10_000 = 3/s; 100 s offline -> +300 eggs shown.
    embed = render_status(state, egg_farm, now=1_100)
    assert embed == render_status(state, egg_farm, now=1_100)
    assert embed == {
        "title": "🥚 Egg Farm — the morning count",
        "description": (
            "A cozy backyard farm where patient chickens fund your empire."
            "\n\nWhile you were away, the hens kept laying: +300 🥚 eggs"
        ),
        "color": 0xF5C542,
        "fields": [
            {"name": "🥚 eggs", "value": "1,234 (+3/s)", "inline": True},
            {"name": "🥇 golden eggs", "value": "3", "inline": True},
            {"name": "🐔 chicken coop", "value": "× 2 · +3/s", "inline": True},
        ],
    }


def test_status_nouns_all_resolve_from_pack(egg_farm):
    embed = render_status(_fixed_state(), egg_farm, now=1_100)
    names = [f["name"] for f in embed["fields"]]
    assert "🥚 eggs" in names
    assert "🥇 golden eggs" in names
    assert "🐔 chicken coop" in names
    assert embed["title"] == "🥚 Egg Farm — the morning count"  # labels.status_title
    _assert_budgets(embed)


def test_status_no_offline_line_when_caught_up(egg_farm):
    state = _fixed_state()
    embed = render_status(state, egg_farm, now=state.last_seen)
    assert embed["description"] == egg_farm.description
    # Clock skew (now < last_seen) accrues nothing rather than going negative.
    skewed = render_status(state, egg_farm, now=state.last_seen - 50)
    assert skewed["description"] == egg_farm.description


def test_status_prestige_currency_reads_persistent_balance(egg_farm):
    """The pack's prestige currency shows state.prestige, not run balances."""
    state = GameState(prestige={"prestige": 7})
    embed = render_status(state, egg_farm, now=0)
    by_name = {f["name"]: f["value"] for f in embed["fields"]}
    assert by_name["🥇 golden eggs"] == "7"
    assert by_name["🥚 eggs"] == "0"


# --- upgrade shop view -------------------------------------------------------


def test_shop_costs_and_affordability(egg_farm):
    # boost1 level 0 costs base_rate 1 * 60 s = 60 eggs (economy v0 table).
    # Own a coop so boost1 is a live buy (its target generator is non-zero):
    # a 0-owned target is annotated as a trap buy, tested separately.
    broke = GameState(balances={"primary": 59}, owned={"tier1": 1})
    rich = GameState(balances={"primary": 60}, owned={"tier1": 1})
    shop_broke = render_shop(broke, egg_farm)
    shop_rich = render_shop(rich, egg_farm)
    (field_broke,) = shop_broke["fields"]
    (field_rich,) = shop_rich["fields"]
    assert field_broke["name"] == "🏠 bigger henhouse"
    assert "60 🥚 eggs" in field_broke["value"]
    assert field_broke["value"].startswith("🔒")
    assert field_rich["value"].startswith("✅")
    assert "Coop size 0 → 1" in field_rich["value"]  # labels.level
    # Shop composition: cost line first, themed flavor on the line below.
    assert field_rich["value"] == (
        "✅ Coop size 0 → 1 · 60 🥚 eggs"
        "\nA roomier henhouse; every hen in the coop lays that bit faster."
    )
    assert shop_rich["title"] == "🧺 The Farm Supply Shed"  # labels.shop_title
    assert shop_rich["description"] == "Trade fresh eggs for a busier, happier farm."
    _assert_budgets(shop_rich)


def test_shop_cost_tracks_current_level(egg_farm):
    # Level 3 -> 4 costs 60 * 115**3 // 100**3 = 91 (exact integer curve).
    state = GameState(balances={"primary": 10_000}, upgrades={"boost1": 3})
    (field,) = render_shop(state, egg_farm)["fields"]
    assert "Coop size 3 → 4" in field["value"]
    assert "91 🥚 eggs" in field["value"]


def test_shop_is_none_without_upgrade_block(egg_farm):
    bare = Theme(
        theme_id="bare",
        name="Bare",
        description="No shop here.",
        emoji="🔹",
        embed_color="#123456",
        currencies={"primary": ThemeCurrency("primary", "points", "points.", "🔹")},
        generators={
            "tier1": ThemeGenerator("tier1", "maker", "makes points.", "⚙️", "primary", 1)
        },
    )
    assert render_shop(GameState(), bare) is None
    assert render_prestige(GameState(), bare) is None


# --- prestige view -----------------------------------------------------------


def test_prestige_ineligible_then_eligible(egg_farm):
    ineligible = GameState(lifetime={"primary": 99_999})
    embed = render_prestige(ineligible, egg_farm)
    assert embed["title"] == "🌟 sell the farm"
    assert embed["description"] == egg_farm.prestige.action_description
    by_name = {f["name"]: f["value"] for f in embed["fields"]}
    assert by_name["🥚 eggs"].startswith("🔒")
    assert "lifetime eggs toward the sale:" in by_name["🥚 eggs"]  # labels.prestige_progress
    assert "99,999 / 100,000" in by_name["🥚 eggs"]
    assert "(+0)" in by_name["🥇 golden eggs"]

    eligible = GameState(lifetime={"primary": 400_000}, prestige={"prestige": 2})
    embed = render_prestige(eligible, egg_farm)
    by_name = {f["name"]: f["value"] for f in embed["fields"]}
    assert by_name["🥚 eggs"].startswith("✅")
    assert by_name["🥇 golden eggs"] == "2 (+2)"  # isqrt(400_000 // 100_000) = 2
    _assert_budgets(embed)


# --- every shipped pack renders within budget --------------------------------


@pytest.mark.parametrize("pack", sorted(THEMES_DIR.glob("*.yaml")), ids=lambda p: p.stem)
def test_all_shipped_packs_render_within_budget(pack):
    theme = load_theme(pack)
    owned = {gid: 5 for gid in theme.generators}
    upgrades = {uid: 2 for uid in theme.upgrades}
    balances = {cid: 123_456 for cid in theme.currencies}
    state = GameState(
        balances=balances,
        owned=owned,
        last_seen=0,
        upgrades=upgrades,
        lifetime=dict(balances),
        prestige={theme.prestige.currency: 4} if theme.prestige else {},
    )
    _assert_budgets(render_status(state, theme, now=86_400))
    shop = render_shop(state, theme)
    if shop is not None:
        _assert_budgets(shop)
    prestige = render_prestige(state, theme)
    if prestige is not None:
        _assert_budgets(prestige)


# --- budget enforcement: numeric overflow clamps, themed overflow raises -----


def test_extreme_values_stay_within_budget(egg_farm):
    """Property-ish sweep: absurd balances/levels/counts never break caps."""
    for magnitude in (10**6, 10**60, 10**200, 10**400):
        state = GameState(
            balances={"primary": magnitude},
            owned={"tier1": magnitude},
            last_seen=0,
            upgrades={"boost1": 25},  # keeps the exact cost curve tractable
            lifetime={"primary": magnitude},
            prestige={"prestige": magnitude},
        )
        for embed in (
            render_status(state, egg_farm, now=10**9),
            render_shop(state, egg_farm),
            render_prestige(state, egg_farm),
        ):
            _assert_budgets(embed)


def test_numeric_overflow_truncates_with_ellipsis(egg_farm):
    huge = 10**2000  # ~2,668 chars formatted with separators: must clamp
    state = GameState(balances={"primary": huge}, prestige={"prestige": huge})
    embed = render_status(state, egg_farm, now=0)
    by_name = {f["name"]: f["value"] for f in embed["fields"]}
    assert len(by_name["🥚 eggs"]) == FIELD_VALUE_LIMIT
    assert by_name["🥚 eggs"].endswith("…")


def test_offline_block_clamps_not_raises(egg_farm):
    huge = 10**1000
    state = GameState(owned={"tier1": huge}, last_seen=0)
    embed = render_status(state, egg_farm, now=10**6)
    assert len(embed["description"]) <= DESCRIPTION_LIMIT


def _theme_with(name="Okay", emoji="🔹", description="Fine.", currency_name="points"):
    return Theme(
        theme_id="rogue",
        name=name,
        description=description,
        emoji=emoji,
        embed_color="#123456",
        currencies={"primary": ThemeCurrency("primary", currency_name, "flat.", "🔹")},
        generators={
            "tier1": ThemeGenerator("tier1", "maker", "makes points.", "⚙️", "primary", 1)
        },
    )


def test_theme_sourced_title_overflow_raises(egg_farm):
    """A pack the gate would reject must raise, never silently truncate."""
    rogue = _theme_with(name="x" * 300)
    with pytest.raises(RenderBudgetError):
        render_status(GameState(), rogue, now=0)


def test_theme_sourced_field_name_overflow_raises():
    rogue = _theme_with(currency_name="y" * 300)
    with pytest.raises(RenderBudgetError):
        render_status(GameState(), rogue, now=0)


def test_theme_sourced_description_overflow_raises():
    rogue = _theme_with(description="z" * 5000)
    with pytest.raises(RenderBudgetError):
        render_status(GameState(), rogue, now=0)


def test_offline_line_dropped_when_description_leaves_no_room(egg_farm):
    """Neutral path (no themed ``offline_return`` slot), description at the
    budget edge: the offline-gain line is DROPPED, not silently truncated or
    over-budget. This pins branch ``render.py`` 240->243 — the ``room < 1``
    arm — as intentional budget protection, not a swallow of player earnings.

    A themed description 4094 chars long leaves ``room = 4096 - 4094 - 2 = 0``,
    so the ``if room >= 1`` gate is False and the formatted gains are not
    appended. The offline earnings are DISPLAY-only here (crediting is the
    engine's job), and the same state DOES surface the line under a short
    description — proving this is the near-full path, not a no-gain case.
    """
    state = GameState(owned={"tier1": 1}, last_seen=0)

    # Same state, short description: the offline line IS shown -> gains are real.
    shown = render_status(state, _theme_with(description="Fine."), now=100)
    assert "+100" in shown["description"]  # the neutral offline line is present

    # Now saturate the description budget so room == 0: the line is dropped.
    near_full = "z" * 4094
    theme = _theme_with(description=near_full)
    embed = render_status(state, theme, now=100)

    # The offline flavor line is omitted -> description is the theme's, unchanged.
    assert embed["description"] == near_full
    assert "+100" not in embed["description"]
    # ...and the rest of the payload stays valid within the 4096 cap.
    assert len(embed["description"]) <= DESCRIPTION_LIMIT
    _assert_budgets(embed)
    assert [f["name"] for f in embed["fields"]] == ["🔹 points", "⚙️ maker"]


def test_validate_embed_rejects_too_many_fields():
    embed = {
        "title": "t",
        "description": "",
        "color": 0,
        "fields": [{"name": "n", "value": "v", "inline": True}] * 26,
    }
    with pytest.raises(RenderBudgetError):
        validate_embed(embed)


def test_validate_embed_rejects_empty_field_strings():
    embed = {
        "title": "t",
        "description": "",
        "color": 0,
        "fields": [{"name": "", "value": "v", "inline": True}],
    }
    with pytest.raises(RenderBudgetError):
        validate_embed(embed)


# --- themed label slots: themed path, fallback path, budget composition ------


@pytest.fixture(scope="module")
def egg_farm_unlabelled(tmp_path_factory):
    """The shipped egg-farm pack with its labels block stripped — the
    fallback path must render exactly the pre-labels neutral scaffolding."""
    src = (THEMES_DIR / "egg-farm.yaml").read_text(encoding="utf-8")
    stripped, sep, _ = src.partition("\nlabels:")
    assert sep, "egg-farm.yaml must carry a labels block"
    path = tmp_path_factory.mktemp("packs") / "egg-farm.yaml"
    path.write_text(stripped, encoding="utf-8")
    return load_theme(path)


def test_fallback_without_labels_renders_neutral_scaffolding(egg_farm_unlabelled):
    """A pack without the labels block pins the original neutral output."""
    state = _fixed_state()
    status = render_status(state, egg_farm_unlabelled, now=1_100)
    assert status["title"] == "🥚 Egg Farm"
    assert status["description"] == (
        "A cozy backyard farm where patient chickens fund your empire."
        "\n\n+300 🥚 eggs"
    )
    shop = render_shop(state, egg_farm_unlabelled)
    assert shop["title"] == "🥚 Egg Farm"
    assert shop["description"] == egg_farm_unlabelled.description
    assert "Lv 1 → 2" in shop["fields"][0]["value"]
    prestige = render_prestige(state, egg_farm_unlabelled)
    by_name = {f["name"]: f["value"] for f in prestige["fields"]}
    assert by_name["🥚 eggs"] == "🔒 5,000 / 100,000"


def test_themed_labels_consume_every_slot(egg_farm):
    """The shipped labels block reaches every view: all six slots pinned."""
    state = _fixed_state()
    status = render_status(state, egg_farm, now=1_100)
    assert status["title"] == "🥚 Egg Farm — the morning count"
    assert status["description"].endswith(
        "\n\nWhile you were away, the hens kept laying: +300 🥚 eggs"
    )
    shop = render_shop(state, egg_farm)
    assert shop["title"] == "🧺 The Farm Supply Shed"
    assert shop["description"] == "Trade fresh eggs for a busier, happier farm."
    assert "Coop size 1 → 2" in shop["fields"][0]["value"]
    prestige = render_prestige(state, egg_farm)
    by_name = {f["name"]: f["value"] for f in prestige["fields"]}
    assert by_name["🥚 eggs"] == "🔒 lifetime eggs toward the sale: 5,000 / 100,000"


def _theme_with_labels(labels, description="Fine."):
    return Theme(
        theme_id="rogue",
        name="Okay",
        description=description,
        emoji="🔹",
        embed_color="#123456",
        currencies={"primary": ThemeCurrency("primary", "points", "flat.", "🔹")},
        generators={
            "tier1": ThemeGenerator("tier1", "maker", "makes points.", "⚙️", "primary", 1)
        },
        labels=labels,
    )


def test_offline_template_clamps_gains_never_the_template():
    """Max-budget template + max-budget description + absurd gains: the
    substituted gains clamp (numeric tier); the themed template survives
    intact and the description stays within the 4096 cap."""
    template = ("x" * 249) + "{gains}"  # 256 chars incl. the 7-char token
    theme = _theme_with_labels(
        ThemeLabels(offline_return=template), description="d" * 1024
    )
    state = GameState(owned={"tier1": 10**3000}, last_seen=0)
    embed = render_status(state, theme, now=10**6)
    assert len(embed["description"]) <= DESCRIPTION_LIMIT
    assert ("x" * 249) in embed["description"]  # template never truncated
    assert embed["description"].endswith("…")  # gains clamped with ellipsis


def test_offline_template_that_cannot_fit_raises():
    """A hand-built theme the gate would reject (description far over the
    flavor budget): the themed template is theme-sourced — it must raise,
    never silently truncate (the neutral path would just skip the line)."""
    theme = _theme_with_labels(
        ThemeLabels(offline_return="y" * 100 + "{gains}"), description="d" * 4090
    )
    state = GameState(owned={"tier1": 1}, last_seen=0)
    with pytest.raises(RenderBudgetError):
        render_status(state, theme, now=100)


def test_themed_status_title_overflow_raises():
    theme = _theme_with_labels(ThemeLabels(status_title="t" * 300))
    with pytest.raises(RenderBudgetError):
        render_status(GameState(), theme, now=0)


def test_shop_and_prestige_label_budgets_at_extremes(egg_farm):
    """Max-length level + progress labels with 10^400..10^2000 numbers:
    composed values stay within every cap, labels render (they lead the
    value, so the trailing numeric clamp never eats them)."""
    from dataclasses import replace

    themed = replace(
        egg_farm, labels=ThemeLabels(level="L" * 32, prestige_progress="P" * 64)
    )
    state = GameState(
        balances={"primary": 10**400},
        owned={"tier1": 10**400},
        last_seen=0,
        upgrades={"boost1": 25},
        lifetime={"primary": 10**2000},
        prestige={"prestige": 10**2000},
    )
    shop = render_shop(state, themed)
    _assert_budgets(shop)
    assert ("L" * 32) in shop["fields"][0]["value"]
    prestige = render_prestige(state, themed)
    _assert_budgets(prestige)
    assert any(("P" * 64) in f["value"] for f in prestige["fields"])


# --- shop composition: themed upgrade flavor in the field value ---------------


def _shop_theme(flavor, currency_name="points", currency_emoji="🔹", level_label=None):
    labels = ThemeLabels(level=level_label) if level_label else None
    return Theme(
        theme_id="rogue",
        name="Okay",
        description="Fine.",
        emoji="🔹",
        embed_color="#123456",
        currencies={
            "primary": ThemeCurrency("primary", currency_name, "flat.", currency_emoji)
        },
        generators={
            "tier1": ThemeGenerator("tier1", "maker", "makes points.", "⚙️", "primary", 1)
        },
        upgrades={"boost1": ThemeUpgrade("boost1", "sharpener", flavor, "🗡", "tier1")},
        labels=labels,
    )


def test_shop_flavor_limit_matches_schema_budget():
    """SHOP_FLAVOR_LIMIT and $defs.shop_flavor_text carry the same number —
    the composition arithmetic anchor cannot drift on either side alone."""
    schema = json.loads(
        (REPO_ROOT / "schema" / "theme.schema.json").read_text(encoding="utf-8")
    )
    assert schema["$defs"]["shop_flavor_text"]["maxLength"] == SHOP_FLAVOR_LIMIT == 768


def test_shop_composes_description_below_cost_line(egg_farm):
    """The composed value is exactly: cost line, newline, themed flavor."""
    (field,) = render_shop(_fixed_state(), egg_farm)["fields"]
    cost_line, _, flavor = field["value"].partition("\n")
    assert cost_line == "✅ Coop size 1 → 2 · 69 🥚 eggs"
    assert flavor == egg_farm.upgrades["boost1"].description


def test_shop_without_description_pins_pre_composition_bytes():
    """Absent flavor (hand-built themes only — the gate requires the field)
    renders the bare cost line BYTE-IDENTICALLY to the pre-composition layer:
    no newline, no trailing scaffolding."""
    theme = _shop_theme("")
    # Own the target generator so the row is a live buy (a 0-owned target is
    # annotated as a trap buy — covered by test_shop_annotates_trap_buy).
    owned = {"tier1": 1}
    (field,) = render_shop(GameState(balances={"primary": 60}, owned=owned), theme)["fields"]
    assert field["value"] == "✅ Lv 0 → 1 · 60 🔹 points"
    (field,) = render_shop(GameState(owned=owned), theme)["fields"]
    assert field["value"] == "🔒 Lv 0 → 1 · 60 🔹 points"


def test_shop_composition_budget_at_worst_case_extremes():
    """Max-budget flavor (768) × max level label (32) × max currency label
    (32 + 64) × an astronomical cost: the value spends the 1024 cap exactly,
    the flavor survives verbatim, the number-bearing cost line clamps."""
    flavor = "D" * SHOP_FLAVOR_LIMIT
    theme = _shop_theme(
        flavor, currency_name="c" * 64, currency_emoji="e" * 32, level_label="L" * 32
    )
    state = GameState(upgrades={"boost1": 10_000})  # cost ~10^607: must clamp
    embed = render_shop(state, theme)
    _assert_budgets(embed)
    (field,) = embed["fields"]
    cost_line, _, tail = field["value"].partition("\n")
    assert tail == flavor  # themed flavor never truncated
    assert len(field["value"]) == FIELD_VALUE_LIMIT  # 255 + 1 + 768 = 1024
    assert ("L" * 32) in cost_line  # the leading themed label survives the clamp
    assert cost_line.endswith("…")  # the numeric tail clamped with ellipsis


def test_shop_description_overflowing_its_slot_raises():
    """A flavor past 768 chars is theme-sourced overflow (gate-illegal pack):
    it must raise, never silently starve the cost line."""
    theme = _shop_theme("z" * (SHOP_FLAVOR_LIMIT + 1))
    with pytest.raises(RenderBudgetError):
        render_shop(GameState(), theme)


def test_shop_boundary_description_never_raises():
    """Exactly 768 chars — the budget boundary — renders within every cap."""
    theme = _shop_theme("b" * SHOP_FLAVOR_LIMIT)
    for magnitude in (0, 10**6, 10**400, 10**2000):
        embed = render_shop(
            GameState(balances={"primary": magnitude}, upgrades={"boost1": 25}), theme
        )
        _assert_budgets(embed)
        assert embed["fields"][0]["value"].endswith("b" * SHOP_FLAVOR_LIMIT)


# --- achievements view: themed pins, neutral fallback pins, budgets ----------


@pytest.fixture(scope="module")
def egg_farm_no_milestones(tmp_path_factory):
    """The shipped egg-farm pack with its milestones block stripped — the
    fallback path must render the neutral scaffolding, byte-pinned."""
    src = (THEMES_DIR / "egg-farm.yaml").read_text(encoding="utf-8")
    head, sep, rest = src.partition("\nmilestones:")
    assert sep, "egg-farm.yaml must carry a milestones block"
    # keep everything after the milestones block (the next top-level key)
    tail = re.search(r"\n(?=[a-z_]+:)", rest[1:])
    remainder = rest[1 + tail.start() :] if tail else ""
    path = tmp_path_factory.mktemp("packs") / "egg-farm.yaml"
    path.write_text(head + remainder, encoding="utf-8")
    theme = load_theme(path)
    assert not theme.milestones
    return theme


def test_achievements_is_deterministic_and_exactly_shaped(egg_farm):
    """Pin the full themed payload for one fixed state (nothing earned)."""
    state = _fixed_state()
    embed = render_achievements(state, egg_farm)
    assert embed == render_achievements(state, egg_farm)
    assert embed["title"] == "🥚 Egg Farm"
    assert embed["description"] == egg_farm.description
    assert embed["color"] == 0xF5C542
    assert len(embed["fields"]) == 9
    first = embed["fields"][0]
    assert first["name"] == "🐣 first flock"
    line, _, flavor = first["value"].partition("\n")
    assert line == "🔒 2 / 10"  # owned total 2 vs pre-registered threshold 10
    assert flavor == egg_farm.milestones["owned-1"].description
    by_name = {f["name"]: f["value"] for f in embed["fields"]}
    # lifetime-1 (threshold 1,000) is REACHED (5,000) but not yet AWARDED:
    # the mark reflects the earned set, never live progress. Display shows the
    # "ready to claim" glyph with the numerator CAPPED at the threshold, so it
    # never reads as a past-100%-but-locked bug (was "🔒 5,000 / 1,000").
    assert by_name["🧺 first thousand eggs"].startswith("⏳ 1,000 / 1,000")
    assert by_name["🥇 first golden egg"].startswith("⏳ 1 / 1")
    _assert_budgets(embed)


def test_achievements_earned_pins_at_threshold(egg_farm):
    """An earned milestone shows threshold/threshold with the earned mark,
    even after the live counter reset (e.g. post-prestige owned = 0)."""
    state = GameState(milestones={"owned-1": 1})
    embed = render_achievements(state, egg_farm)
    by_name = {f["name"]: f["value"] for f in embed["fields"]}
    assert by_name["🐣 first flock"].startswith("✅ 10 / 10")
    assert by_name["🐥 hundred-hen farmstead"].startswith("🔒 0 / 100")


def test_achievements_neutral_fallback_is_byte_pinned(egg_farm_no_milestones):
    """A pack without the milestones noun block renders pure neutral
    scaffolding: numbered milestone slots, bare progress lines."""
    state = _fixed_state()
    embed = render_achievements(state, egg_farm_no_milestones)
    assert [f["name"] for f in embed["fields"]] == [
        f"Milestone {i}" for i in range(1, 10)
    ]
    assert embed["fields"][0] == {
        "name": "Milestone 1",
        "value": "🔒 2 / 10",
        "inline": True,
    }
    # Reached-but-unawarded slots render the "ready" glyph, numerator capped
    # at the threshold (not the past-100% "🔒 5,000 / 1,000" that read as a bug).
    assert embed["fields"][3]["value"] == "⏳ 1,000 / 1,000"
    assert embed["fields"][6]["value"] == "⏳ 1 / 1"
    assert "\n" not in embed["fields"][0]["value"]  # no flavor line composed
    assert embed["title"] == "🥚 Egg Farm"
    assert embed["description"] == egg_farm_no_milestones.description
    _assert_budgets(embed)


def test_achievements_mechanics_identical_with_and_without_nouns(
    egg_farm, egg_farm_no_milestones
):
    """The noun block skins slots, never creates them: same slot count,
    same marks, same numbers either way."""
    state = GameState(owned={"tier1": 15}, milestones={"owned-1": 1})
    themed = render_achievements(state, egg_farm)
    neutral = render_achievements(state, egg_farm_no_milestones)
    assert len(themed["fields"]) == len(neutral["fields"]) == 9
    themed_lines = [f["value"].partition("\n")[0] for f in themed["fields"]]
    neutral_lines = [f["value"] for f in neutral["fields"]]
    assert themed_lines == neutral_lines


@pytest.mark.parametrize("pack", sorted(THEMES_DIR.glob("*.yaml")), ids=lambda p: p.stem)
def test_all_shipped_packs_render_achievements_within_budget(pack):
    theme = load_theme(pack)
    state = GameState(
        owned={gid: 500 for gid in theme.generators},
        lifetime={cid: 10**6 for cid in theme.currencies},
        prestige={theme.prestige.currency: 30} if theme.prestige else {},
        milestones={spec.spec_id: 1 for spec in theme.milestone_specs()[:4]},
    )
    _assert_budgets(render_achievements(state, theme))


def _milestone_theme(flavor):
    """A hand-built single-currency, no-prestige theme (6 slots) with one
    themed milestone noun."""
    return Theme(
        theme_id="rogue",
        name="Okay",
        description="Fine.",
        emoji="🔹",
        embed_color="#123456",
        currencies={"primary": ThemeCurrency("primary", "points", "flat.", "🔹")},
        generators={
            "tier1": ThemeGenerator("tier1", "maker", "makes points.", "⚙️", "primary", 1)
        },
        milestones={"owned-1": ThemeMilestone("owned-1", "starter", flavor, "🗿")},
    )


def test_achievements_without_prestige_track_has_six_slots():
    embed = render_achievements(GameState(), _milestone_theme("keep going."))
    assert len(embed["fields"]) == 6
    assert embed["fields"][0]["name"] == "🗿 starter"
    assert embed["fields"][1]["name"] == "Milestone 2"  # partial fill falls back


def test_achievements_flavor_overflowing_its_slot_raises():
    theme = _milestone_theme("z" * (SHOP_FLAVOR_LIMIT + 1))
    with pytest.raises(RenderBudgetError):
        render_achievements(GameState(), theme)


def test_achievements_boundary_flavor_and_extreme_numbers_stay_in_budget():
    theme = _milestone_theme("b" * SHOP_FLAVOR_LIMIT)
    for magnitude in (0, 10**6, 10**400, 10**2000):
        state = GameState(
            owned={"tier1": magnitude}, lifetime={"primary": magnitude}
        )
        embed = render_achievements(state, theme)
        _assert_budgets(embed)
        assert embed["fields"][0]["value"].endswith("b" * SHOP_FLAVOR_LIMIT)


def test_status_rates_include_earned_milestone_bonus(egg_farm):
    """The status view shows the rate the engine would actually credit:
    milestone_pct folds into the displayed /s numbers."""
    base = GameState(owned={"tier1": 100})
    earned = GameState(owned={"tier1": 100}, milestones={"owned-1": 1})
    plain = render_status(base, egg_farm, now=0)
    boosted = render_status(earned, egg_farm, now=0)
    by_name = {f["name"]: f["value"] for f in plain["fields"]}
    boosted_by_name = {f["name"]: f["value"] for f in boosted["fields"]}
    # 100 coops × 1/s: +5% milestone bonus -> 105/s (single shared floor).
    assert by_name["🥚 eggs"].endswith("(+100/s)")
    assert boosted_by_name["🥚 eggs"].endswith("(+105/s)")


# --- purity: the render module imports no chat-platform SDK ------------------


def test_render_module_is_pure_presentation():
    source = (REPO_ROOT / "idle_engine" / "render.py").read_text(encoding="utf-8")
    assert not re.search(r"\bimport\s+discord\b|\bfrom\s+discord\b", source)
    assert not re.search(r"\bimport\s+yaml\b|\bfrom\s+yaml\b", source)
    assert "requests" not in source and "aiohttp" not in source
