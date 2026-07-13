"""NON-gated forwarding checks — run in idle's sb-free CI.

Unlike ``test_manifest.py`` (which needs the host ``sb`` package and skips
cleanly without it), this module exercises the PURE render-forwarding path
against the REAL ``idle_engine`` — no ``sb`` import anywhere — so idle CI
actually PROVES the forwarding works (returns the engine's embed dict verbatim),
not merely that the adapter imports. ``plugin/conftest.py`` puts both the
plugin package and the repo root on ``sys.path``.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from idle_engine import GameState, load_theme
from idle_engine.render import render_prestige, render_shop, render_status
from superbot_idle_plugin.render_forward import (
    IdleRenderState,
    forward_prestige,
    forward_shop,
    forward_status,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
THEMES_DIR = REPO_ROOT / "themes"


@pytest.fixture(scope="module")
def egg_farm():
    return load_theme(THEMES_DIR / "egg-farm.yaml")


def _fixed_state() -> GameState:
    """A small deterministic save (mirrors tests/test_render.py)."""
    return GameState(
        balances={"primary": 1234},
        owned={"tier1": 2},
        last_seen=1_000,
        upgrades={"boost1": 1},
        lifetime={"primary": 5_000},
        prestige={"prestige": 3},
    )


def test_forward_status_returns_render_status_dict_unchanged(egg_farm) -> None:
    state = _fixed_state()
    now = 2_000
    handle = IdleRenderState(game_state=state, theme=egg_farm, now=now)
    forwarded = forward_status(handle)
    assert forwarded == render_status(state, egg_farm, now)
    # And it IS a real embed dict (title/description/color/fields), not a stub.
    assert set(forwarded) >= {"title", "description", "color", "fields"}
    assert isinstance(forwarded["color"], int)


def test_forward_shop_returns_render_shop_output_verbatim(egg_farm) -> None:
    state = _fixed_state()
    assert forward_shop(IdleRenderState(state, egg_farm, 0)) == render_shop(state, egg_farm)


def test_forward_prestige_returns_render_prestige_output_verbatim(egg_farm) -> None:
    state = _fixed_state()
    assert forward_prestige(IdleRenderState(state, egg_farm, 0)) == render_prestige(
        state, egg_farm
    )


def test_forwarders_add_no_formatting(egg_farm) -> None:
    """The forwarders are pure pass-throughs: the SAME object identity the
    engine returns, never a re-shaped copy (zero adapter-side formatting)."""
    state = _fixed_state()
    handle = IdleRenderState(game_state=state, theme=egg_farm, now=5_000)
    engine_status = render_status(state, egg_farm, 5_000)
    forwarded = forward_status(handle)
    # Identical value; and byte-identical field ordering (verbatim forward).
    assert forwarded == engine_status
    assert list(forwarded["fields"]) == list(engine_status["fields"])
