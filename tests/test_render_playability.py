"""Playability display fixes — render-layer regression guards.

Two display-only fixes off the end-to-end player review (rough edges #5 and
#3). Each test pins the CORRECTED rendered string and asserts the specific
buggy string it replaces can no longer appear. Neither fix changes any economy
number or any purchase/award MECHANIC — they are presentation only, exercised
here through the real shipped packs.
"""

from pathlib import Path

import pytest

from idle_engine import GameState, load_theme
from idle_engine.render import render_achievements, render_shop

REPO_ROOT = Path(__file__).resolve().parent.parent
THEMES_DIR = REPO_ROOT / "themes"


@pytest.fixture(scope="module")
def egg_farm():
    return load_theme(THEMES_DIR / "egg-farm.yaml")


@pytest.fixture(scope="module")
def royal_bakery():
    # A two-generator pack: tier1 (ownable) + tier2 (never ownable at base
    # seed) with boost2 targeting tier2 — the trap-buy case.
    return load_theme(THEMES_DIR / "royal-bakery.yaml")


# --- Fix #1: reached-but-unawarded milestone display -------------------------


def test_reached_but_unawarded_milestone_shows_ready_not_locked(egg_farm):
    """A milestone whose live progress meets the threshold but has not been
    AWARDED must render as ready-to-claim with the numerator capped at the
    threshold — never the past-100%-but-locked line that reads as a bug.

    BEFORE (buggy): "🔒 5,000 / 1,000" (5,000 lifetime, threshold 1,000).
    AFTER  (fixed): "⏳ 1,000 / 1,000".
    """
    # lifetime primary 5,000 >= lifetime-1 threshold 1,000; nothing awarded.
    state = GameState(lifetime={"primary": 5_000})
    embed = render_achievements(state, egg_farm)
    line = {f["name"]: f["value"] for f in embed["fields"]}[
        "🧺 first thousand eggs"
    ].split("\n")[0]

    assert line == "⏳ 1,000 / 1,000"  # corrected: ready glyph, capped
    assert line != "🔒 5,000 / 1,000"  # the exact bug this guards against
    assert "🔒" not in line  # not locked
    assert "5,000" not in line  # numerator no longer exceeds the threshold


def test_not_reached_milestone_still_locked_with_live_progress(egg_farm):
    """Below the threshold is unchanged: 🔒 with live (uncapped) progress."""
    state = GameState(lifetime={"primary": 250})  # < lifetime-1 threshold 1,000
    line = {f["name"]: f["value"] for f in render_achievements(state, egg_farm)["fields"]}[
        "🧺 first thousand eggs"
    ].split("\n")[0]
    assert line == "🔒 250 / 1,000"


def test_earned_milestone_still_shows_check_at_threshold(egg_farm):
    """An AWARDED milestone is unchanged: ✅ pinned at threshold/threshold."""
    state = GameState(milestones={"lifetime-1": 1})
    line = {f["name"]: f["value"] for f in render_achievements(state, egg_farm)["fields"]}[
        "🧺 first thousand eggs"
    ].split("\n")[0]
    assert line == "✅ 1,000 / 1,000"


def test_ready_glyph_never_appears_for_earned_or_unreached(egg_farm):
    """The ⏳ ready glyph is reserved for reached-but-unawarded slots only."""
    earned = GameState(milestones={"lifetime-1": 1})
    unreached = GameState(lifetime={"primary": 0})
    for state in (earned, unreached):
        line = {
            f["name"]: f["value"] for f in render_achievements(state, egg_farm)["fields"]
        }["🧺 first thousand eggs"].split("\n")[0]
        assert "⏳" not in line


# --- Fix #2: trap-buy annotation for 0-owned upgrade targets -----------------


def test_shop_annotates_trap_buy_for_zero_owned_target(royal_bakery):
    """boost2 targets tier2, which is never ownable at the base seed. With
    tier2 owned = 0 the upgrade is a trap buy — a purchase spends currency for
    zero observable effect — so it must render unavailable and name the
    generator it requires, not an affordable ✅.

    BEFORE (buggy): "✅ Recipe mastery 0 → 1 · 300 🥐 pastries".
    AFTER  (fixed): "⚠️ Recipe mastery 0 → 1 · 300 🥐 pastries · requires 🧱 brick oven".
    """
    # Plenty of pastries to "afford" boost2, but no brick oven owned.
    state = GameState(balances={"primary": 10_000}, owned={"tier1": 1})
    line = {f["name"]: f["value"] for f in render_shop(state, royal_bakery)["fields"]}[
        "🚪 twin hearth doors"
    ].split("\n")[0]

    assert line == "⚠️ Recipe mastery 0 → 1 · 300 🥐 pastries · requires 🧱 brick oven"
    assert not line.startswith("✅")  # no longer invites the wasted buy
    assert "requires 🧱 brick oven" in line  # names the missing generator


def test_shop_live_upgrade_with_owned_target_is_unannotated(royal_bakery):
    """boost1 targets tier1, which the player owns: normal affordability mark,
    no trap-buy annotation — the guard fires only for 0-owned targets."""
    state = GameState(balances={"primary": 10_000}, owned={"tier1": 1})
    line = {f["name"]: f["value"] for f in render_shop(state, royal_bakery)["fields"]}[
        "🌾 stone-ground flour"
    ].split("\n")[0]
    # Owned target, affordable: normal ✅ mark plus the affordability ETA — and
    # crucially NO trap-buy annotation (⚠️/requires fire only for 0-owned targets).
    assert line == "✅ Recipe mastery 0 → 1 · 60 🥐 pastries · affordable now"
    assert "⚠️" not in line
    assert "requires" not in line


def test_shop_trap_buy_annotation_independent_of_affordability(royal_bakery):
    """Even when the player cannot afford boost2, the 0-owned-target guard
    still shows the unavailable mark (not the 🔒 insufficient-funds mark) —
    the missing generator, not the balance, is the reason it does nothing."""
    state = GameState(balances={"primary": 0}, owned={"tier1": 1})
    line = {f["name"]: f["value"] for f in render_shop(state, royal_bakery)["fields"]}[
        "🚪 twin hearth doors"
    ].split("\n")[0]
    assert line.startswith("⚠️")
    assert "requires 🧱 brick oven" in line
