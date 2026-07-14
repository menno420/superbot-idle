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


def test_dispatch_buy_count_buys_n_levels_in_one_command():
    """`buy <id> 3` climbs 3 levels via the engine's atomic bulk purchase."""
    session = play.new_session(play.load_pack("egg-farm"), start_count=1)
    session = play.advance(session, 2000)  # earn enough eggs for several levels
    bought, out = play.dispatch(session, "buy boost1 3")
    assert bought.state.upgrades.get("boost1", 0) == 3
    assert "3 levels" in out and "boost1" in out
    # `buy <id> 1` is the single-level buy, same wording as the bare verb.
    one_more, out = play.dispatch(bought, "buy boost1 1")
    assert one_more.state.upgrades.get("boost1", 0) == 4
    assert "a level" in out


def test_dispatch_buy_max_buys_exactly_all_affordable():
    """`buy <id> max` buys every affordable level — and afterwards not even
    one more level is affordable (the defining property of the argmax)."""
    session = play.new_session(play.load_pack("egg-farm"), start_count=1)
    session = play.advance(session, 600)
    bought, out = play.dispatch(session, "buy boost1 max")
    assert bought.state.upgrades.get("boost1", 0) >= 1
    assert out.startswith("Bought")
    # Maxed means maxed: an immediate repeat (no time passed, no new income)
    # must afford nothing, and must say so gracefully without changing state.
    same, out = play.dispatch(bought, "buy boost1 max")
    assert same is bought
    assert "cannot afford a single level" in out


def test_dispatch_buy_bad_count_is_graceful():
    """`buy <id> 0/-3/garbage` must not traceback or spend anything."""
    session = play.new_session(play.load_pack("egg-farm"), start_count=1)
    session = play.advance(session, 200)
    for bad in ("0", "-3", "banana", "2.5"):
        same, out = play.dispatch(session, f"buy boost1 {bad}")
        assert same is session  # nothing bought, nothing spent
        assert "Usage: buy" in out


def test_dispatch_buy_more_than_affordable_is_graceful_and_atomic():
    """A count beyond the budget spends NOTHING (atomic refusal) and answers
    instantly even for an absurd count (no pricing of 10^9 levels)."""
    session = play.new_session(play.load_pack("egg-farm"), start_count=1)
    same, out = play.dispatch(session, "buy boost1 1000000000")
    assert same is session
    assert "Cannot buy 1000000000 levels" in out
    assert "cannot afford a single level" in out
    # And `max` on a zero-egg fresh save is the same graceful refusal.
    same, out = play.dispatch(session, "buy boost1 max")
    assert same is session
    assert "cannot afford a single level" in out


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


def test_dispatch_save_prints_one_canonical_loadable_line():
    """`save` prints exactly the persistence-v2 canonical blob: one line,
    copy-pasteable, and loadable back into an equal state."""
    from idle_engine.persistence import dump_state, load_state

    session = play.new_session(play.load_pack("egg-farm"), start_count=1)
    session = play.advance(session, 60)
    same, blob = play.dispatch(session, "save")
    assert same is session  # save is read-only
    assert blob == dump_state(session.state)
    assert "\n" not in blob
    assert load_state(blob) == session.state


def test_dispatch_save_load_round_trip_preserves_state_and_rate():
    """save -> (fresh, diverged session) -> load restores the exact state,
    and production resumes at the saved run's rate, not the fresh one's."""
    original = play.new_session(play.load_pack("egg-farm"), start_count=1)
    original = play.advance(original, 2000)
    original, _ = play.dispatch(original, "buy boost1 3")  # a run worth keeping
    _, blob = play.dispatch(original, "save")

    fresh = play.new_session(play.load_pack("egg-farm"), start_count=1)
    restored, out = play.dispatch(fresh, f"load {blob}")
    assert out.startswith("Save loaded.")
    assert restored.state == original.state
    # Rate correct: the same wait credits the same production on both.
    a, _ = play.dispatch(original, "wait 10")
    b, _ = play.dispatch(restored, "wait 10")
    assert b.state.balances == a.state.balances
    # And an immediate re-save round-trips to the identical blob.
    _, blob_again = play.dispatch(restored, "save")
    assert blob_again == blob


def test_dispatch_load_malformed_blob_is_graceful():
    """Garbage, wrong versions, mutant field sets, floats, negatives, and
    hostile deeply-nested input all refuse with a message — same session
    object back, no traceback (the persistence error taxonomy, caught)."""
    session = play.new_session(play.load_pack("egg-farm"), start_count=1)
    _, blob = play.dispatch(session, "save")
    for bad in (
        "banana",  # not JSON at all
        "[1,2,3]",  # JSON, not an object
        '{"state_version":99}',  # unknown version
        '{"state_version":2}',  # missing fields
        blob.replace('"last_seen":', '"last_seen_x":'),  # mutant field set
        blob.replace('"last_seen":0', '"last_seen":0.5'),  # float smuggling
        blob.replace('"tier1":1', '"tier1":-1'),  # negative quantity
        "[" * 50000,  # hostile oversized/deep nesting
    ):
        same, out = play.dispatch(session, f"load {bad}")
        assert same is session
        assert out.startswith("Cannot load save:")
    # A bare `load` is a usage message, matching the house style.
    same, out = play.dispatch(session, "load")
    assert same is session
    assert "Usage: load" in out


def test_dispatch_load_then_status_renders_without_phantom_offline():
    """A loaded session renders: `status` works, the clock sits at the
    save's own last_seen, so no phantom offline time is shown or credited."""
    original = play.new_session(play.load_pack("egg-farm"), start_count=1)
    original = play.advance(original, 120)
    _, blob = play.dispatch(original, "save")
    late = play.advance(play.new_session(play.load_pack("egg-farm")), 5000)
    restored, _ = play.dispatch(late, f"load {blob}")
    assert restored.now == restored.state.last_seen == 120  # clock rebased
    _, status = play.dispatch(restored, "status")
    assert "Egg Farm" in status
    # `offline 0` at the rebased clock credits nothing (no phantom time).
    same_balances, _ = play.dispatch(restored, "offline 0")
    assert same_balances.state.balances == restored.state.balances


def test_dispatch_load_does_not_regrant_anything():
    """The blob is authoritative: loading an empty-owned save into a granted
    session must NOT re-seed the starting grant (unlike fresh/prestige)."""
    empty = play.new_session(play.load_pack("egg-farm"), start_count=0)
    _, blob = play.dispatch(empty, "save")
    granted = play.new_session(play.load_pack("egg-farm"), start_count=3)
    restored, _ = play.dispatch(granted, f"load {blob}")
    assert restored.state.owned == {}  # not re-granted
    assert restored.state == empty.state


@pytest.mark.parametrize(
    "pack", sorted(p.stem for p in (REPO_ROOT / "themes").glob("*.yaml"))
)
def test_every_pack_starts_and_renders_all_views(pack):
    session = play.new_session(play.load_pack(pack), start_count=1)
    session = play.advance(session, 60)
    for verb in ("status", "shop", "prestige", "achievements"):
        _, out = play.dispatch(session, verb)
        assert isinstance(out, str) and out.strip()
