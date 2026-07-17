"""REPL-loop tests for the tools/play.py player entrypoint.

The pure helpers of ``tools/play.py`` (``new_session``, ``advance``,
``dispatch``, ``_buy``, ``_load`` ...) are covered by
``tests/test_play_entrypoint.py``; those tests never spawn the interactive
loop. THIS file covers the interactive ``main()`` REPL itself — the argparse
front, the ``--list-packs`` short-circuit, the bad-pack startup guard, and the
read-eval-print ``while True`` body with its between-command clock advance and
EOF/quit unwind — the biggest coverage hole in game-facing code (measured 72%,
menu TEST-11).

The loop reads stdin via ``input()`` and prints to stdout, so it is driven by
monkeypatching ``builtins.input`` to replay a scripted command sequence and
capturing the printed transcript with ``capsys``; ``time.monotonic`` is
monkeypatched so the between-command clock advance is deterministic. Assertions
are on stable transcript substrings (never brittle economy numbers) and on
``main()``'s integer return code, so they stay green across any (out-of-scope)
economy retune. These tests only DRIVE the existing ``main()`` — no product
code is changed.
"""

import builtins
import importlib.util
import itertools
import sys
import time
from pathlib import Path

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


def _scripted_input(commands):
    """A fake ``input()`` that replays ``commands`` then raises ``EOFError``.

    The trailing ``EOFError`` models the end of stdin, which the loop treats
    as a clean quit — matching a real piped/heredoc session.
    """
    it = iter(commands)

    def fake_input(prompt=""):
        try:
            return next(it)
        except StopIteration:
            raise EOFError

    return fake_input


def _freeze_clock(monkeypatch):
    """Pin ``time.monotonic`` so the between-command advance credits 0 seconds.

    ``main()`` does ``import time`` locally, binding the shared ``sys.modules``
    module object we patch here, so the pin takes effect inside the loop.
    """
    monkeypatch.setattr(time, "monotonic", lambda: 1000.0)


def test_main_list_packs_exits_zero(capsys):
    """``--list-packs`` prints the pack menu and returns 0 without a loop."""
    rc = play.main(["--list-packs"])
    assert rc == 0
    out = capsys.readouterr().out
    assert "egg-farm" in out


def test_main_bad_pack_reports_and_exits_two(capsys):
    """A bad pack is reported to stderr and exits 2 — no traceback, no loop."""
    rc = play.main(["--pack", "no-such-pack"])
    assert rc == 2
    err = capsys.readouterr().err
    assert "Could not start" in err


def test_main_scripted_session_drives_repl(monkeypatch, capsys):
    """One scripted session drives the loop through the documented verbs:
    status, offline (earn), buy, save, load, help, an invalid command, then a
    clean ``quit`` (exit 0). Asserts on the transcript and the return code."""
    _freeze_clock(monkeypatch)
    # A concrete, loadable persistence-v2 blob to exercise the `load` verb.
    blob = play.dump_state(
        play.new_session(play.load_pack("egg-farm"), start_count=2).state
    )
    commands = [
        "status",  # render the opening view again
        "offline 3600",  # credit offline production so a buy can afford
        "buy boost1",  # spend earned eggs on a real upgrade level
        "save",  # emit the canonical save line
        f"load {blob}",  # restore a run from a save line
        "help",  # the help text
        "frobnicate",  # an invalid command (graceful)
        "quit",  # clean unwind -> exit 0
    ]
    monkeypatch.setattr(builtins, "input", _scripted_input(commands))

    rc = play.main(["--pack", "egg-farm"])

    assert rc == 0
    out = capsys.readouterr().out
    assert "superbot-idle" in out  # startup banner
    assert "Egg Farm" in out  # status view rendered
    assert "Bought" in out  # buy path took
    assert "Save loaded." in out  # load path took
    assert "Commands:" in out  # help printed
    assert "Unknown command" in out  # invalid command handled
    assert "Bye." in out  # clean loop unwind


def test_main_eof_exits_zero(monkeypatch, capsys):
    """Empty stdin (immediate EOF) unwinds the loop cleanly and returns 0."""
    _freeze_clock(monkeypatch)
    monkeypatch.setattr(builtins, "input", _scripted_input([]))

    rc = play.main(["--pack", "egg-farm"])

    assert rc == 0
    out = capsys.readouterr().out
    assert "Bye." in out


def test_main_credits_idle_time_between_commands(monkeypatch, capsys):
    """A monotonic clock that steps forward every read makes ``elapsed > 0``,
    so the loop credits real idle seconds between commands (the
    advance-between-commands branch) before dispatching each verb."""
    # count(step=5) => each monotonic() read is +5s, so every iteration sees a
    # positive elapsed and takes the advance branch; itertools.count never
    # exhausts, keeping the clock deterministic and traceback-free.
    ticks = itertools.count(start=0, step=5)
    monkeypatch.setattr(time, "monotonic", lambda: float(next(ticks)))
    monkeypatch.setattr(builtins, "input", _scripted_input(["status", "status", "quit"]))

    rc = play.main(["--pack", "egg-farm"])

    assert rc == 0
    out = capsys.readouterr().out
    assert "Egg Farm" in out
    assert "Bye." in out
