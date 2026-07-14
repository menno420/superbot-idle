"""Smoke tests for the tools/play.py player entrypoint.

The point of these tests is that the runnable entrypoint's CORE path — seed a
session, advance a tick, render — executes without error, and the command
dispatcher handles the documented verbs. They import the pure helpers and never
spawn the interactive loop (no stdin/stdout, no wall clock). They assert
structure, not economy numbers, so they stay green across any (out-of-scope)
economy retune.
"""

import importlib.util
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent


def _load_play():
    spec = importlib.util.spec_from_file_location(
        "tools_play", REPO_ROOT / "tools" / "play.py"
    )
    module = importlib.util.module_from_spec(spec)
    # Register before exec: the frozen dataclass's annotation resolution reads
    # sys.modules[cls.__module__] at class-creation time.
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


play = _load_play()


def test_demo_step_runs_one_tick_and_render():
    """The self-contained smoke hook: one tick + render, no loop, no I/O."""
    out = play.demo_step()
    assert isinstance(out, str) and out.strip()
    assert "Egg Farm" in out  # the default pack rendered its status title


def test_new_session_grants_starting_generators():
    theme = play.load_pack("egg-farm")
    session = play.new_session(theme, start_count=3)
    assert session.state.owned == {"tier1": 3}
    # A zero grant is legal (an empty save).
    assert play.new_session(theme, start_count=0).state.owned == {}


def test_advance_credits_production_via_engine():
    theme = play.load_pack("egg-farm")
    session = play.new_session(theme, start_count=1, now=0)
    moved = play.advance(session, 10)
    assert moved.now == 10
    # 1 coop at base_rate 1/s for 10 s -> 10 eggs (drives the real tick).
    assert moved.state.balances.get("primary", 0) == 10


def test_dispatch_core_commands_return_text():
    session = play.new_session(play.load_pack("egg-farm"))
    for verb in ("status", "shop", "achievements", "help", "prestige"):
        _, out = play.dispatch(session, verb)
        assert isinstance(out, str) and out.strip()


def test_dispatch_quit_raises_quitgame():
    session = play.new_session(play.load_pack("egg-farm"))
    with pytest.raises(play.QuitGame):
        play.dispatch(session, "quit")


def test_dispatch_buy_then_offline_flow():
    session = play.new_session(play.load_pack("egg-farm"), start_count=1)
    session = play.advance(session, 200)  # earn enough eggs to afford boost1
    bought, out = play.dispatch(session, "buy boost1")
    assert bought.state.upgrades.get("boost1", 0) == 1
    assert "boost1" in out
    moved, status = play.dispatch(bought, "offline 3600")
    assert moved.now == bought.now + 3600
    assert "eggs" in status


def test_dispatch_unknown_and_bad_buy_are_graceful():
    session = play.new_session(play.load_pack("egg-farm"))
    _, out = play.dispatch(session, "frobnicate")
    assert "Unknown command" in out
    _, out = play.dispatch(session, "buy nonesuch")
    assert "No upgrade" in out


def test_dispatch_negative_seconds_is_graceful():
    """`wait -5` / `offline -5` must not escape as a ValueError traceback."""
    session = play.new_session(play.load_pack("egg-farm"))
    for verb in ("wait", "offline"):
        same, out = play.dispatch(session, f"{verb} -5")
        assert same is session  # no time moved, no state change
        assert f"Usage: {verb} <seconds>" in out


def test_prestige_do_regrants_starting_generators():
    """A prestige reset must re-seed the runtime starting grant, or the run
    is unrecoverable (the engine has no generator purchase verb yet)."""
    session = play.new_session(play.load_pack("egg-farm"), start_count=1)
    spec = session.theme.prestige_spec()
    session = play.advance(session, spec.threshold + 1)  # cross eligibility
    reset, out = play.dispatch(session, "prestige do")
    assert "starting generators re-granted" in out
    assert reset.state.owned == {"tier1": 1}  # grant re-applied, not 0-owned
    moved, _ = play.dispatch(reset, "wait 10")
    assert moved.state.balances.get("primary", 0) > 0  # production accrues again


@pytest.mark.parametrize(
    "pack", sorted(p.stem for p in (REPO_ROOT / "themes").glob("*.yaml"))
)
def test_every_pack_starts_and_renders_all_views(pack):
    session = play.new_session(play.load_pack(pack), start_count=1)
    session = play.advance(session, 60)
    for verb in ("status", "shop", "prestige", "achievements"):
        _, out = play.dispatch(session, verb)
        assert isinstance(out, str) and out.strip()
