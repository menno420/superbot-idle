#!/usr/bin/env python3
"""A runnable, text-only way to actually PLAY superbot-idle.

The engine ships with rigorous tests and a deterministic economy but no
player-facing entrypoint (end-to-end review, rough edge #11: "No CLI / REPL /
demo entrypoint exists for a player"). This tool is that entrypoint — a small
REPL that seeds a :class:`~idle_engine.state.GameState` from a shipped theme
pack (optionally decoded from a setup code), advances wall-clock time between
commands, and renders every view through the existing ``render_*`` functions.

NEW FILE, zero engine change: it only *drives* the public engine + render API.
It reimplements no mechanics — production is ``tick`` /
``apply_offline_progress``, purchases are ``purchase_upgrade`` / ``upgrade_cost``,
resets are ``prestige_eligible`` / ``apply_prestige``, milestone banking is
``award_milestones``. The one runtime choice local to this file is a starting
grant of generators (``--start-count``, default 1): the engine has no generator
purchase verb yet (a separate, economy-number-bearing slice), so without a
starting grant a fresh save produces nothing and there is no loop to watch.

Commands (type ``help`` in the loop):

    status            balances, generator rates, offline gains
    shop              the upgrade shop (cost lines + trap-buy warnings)
    buy <id>          buy one level of upgrade <id>
    prestige          show the prestige view; ``prestige do`` performs the reset
    offline <secs>    credit <secs> of offline production, then show status
    pack <id>         switch to another shipped theme pack (fresh save)
    wait <secs>       advance the clock by <secs> without other action
    achievements      the milestone view
    help / quit

Usage::

    python3 tools/play.py                       # default pack (egg-farm)
    python3 tools/play.py --pack royal-bakery    # a two-generator pack
    python3 tools/play.py --code IDLE1-...        # provision from a setup code
    python3 tools/play.py --start-count 4         # start with 4 generators

Import-safe: the interactive loop runs only under ``if __name__ == "__main__"``.
The pure helpers (:func:`new_session`, :func:`advance`, :func:`dispatch`,
:func:`demo_step`) take an explicit clock and never touch stdin/stdout, so they
are unit-testable without spawning the REPL.
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass, field
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:  # allow `python3 tools/play.py` from anywhere
    sys.path.insert(0, str(REPO_ROOT))

from idle_engine import (  # noqa: E402  (path shim must precede the import)
    GameState,
    apply_prestige,
    award_milestones,
    load_theme,
    prestige_eligible,
    purchase_upgrade,
    render_achievements,
    render_prestige,
    render_shop,
    render_status,
    tick,
)
from idle_engine.engine import apply_offline_progress  # noqa: E402
from idle_engine.provisioning import decode_setup, validate_against_catalog  # noqa: E402
from idle_engine.theme import Theme  # noqa: E402

THEMES_DIR = REPO_ROOT / "themes"


@dataclass(frozen=True)
class Session:
    """One in-progress play session: the loaded pack, the save, the clock."""

    theme: Theme
    state: GameState
    now: int = 0
    log: tuple[str, ...] = field(default_factory=tuple)


class QuitGame(Exception):
    """Raised by :func:`dispatch` to unwind the interactive loop cleanly."""


# --- session construction ----------------------------------------------------


def available_packs() -> list[str]:
    """Theme ids of every shipped pack, sorted (the ``pack`` command menu)."""
    return sorted(p.stem for p in THEMES_DIR.glob("*.yaml"))


def load_pack(theme_id: str) -> Theme:
    """Load a shipped pack by theme id, or raise ``ValueError`` with the menu."""
    path = THEMES_DIR / f"{theme_id}.yaml"
    if not path.exists():
        raise ValueError(
            f"unknown pack {theme_id!r} (available: {', '.join(available_packs())})"
        )
    return load_theme(path)


def new_session(theme: Theme, start_count: int = 1, now: int = 0) -> Session:
    """Seed a fresh save: ``start_count`` of every declared generator.

    The starting grant is a RUNTIME entrypoint choice (see the module
    docstring) — it lives entirely in this tool and touches no economy
    constant. ``start_count`` 0 is legal (an empty, zero-production save).
    """
    if start_count < 0:
        raise ValueError("start_count must be >= 0")
    owned = {gid: start_count for gid in theme.generators} if start_count else {}
    state = GameState(owned=owned, last_seen=now)
    return Session(theme=theme, state=state, now=now)


def session_from_code(code: str, start_count: int = 1, now: int = 0) -> Session:
    """Provision a session from a setup code, resolved against the catalog."""
    config = decode_setup(code)
    theme = validate_against_catalog(config, THEMES_DIR)
    return new_session(theme, start_count=start_count, now=now)


# --- pure engine advance -----------------------------------------------------


def _spec_bundle(theme: Theme):
    return (
        theme.generator_specs(),
        theme.upgrade_specs(),
        [s for s in (theme.prestige_spec(),) if s is not None],
        theme.milestone_specs(),
    )


def advance(session: Session, seconds: int) -> Session:
    """Advance the clock by ``seconds``, crediting production and banking any
    newly reached milestones — the between-actions engine step.

    Uses the real engine ``tick`` (production) then ``award_milestones`` (the
    explicit action-boundary), exactly as a runtime would; the offline path is
    integer-identical (property-pinned) and is exercised by the ``offline``
    command instead.
    """
    if seconds < 0:
        raise ValueError("seconds must be >= 0")
    gens, upgrades, prestige, milestones = _spec_bundle(session.theme)
    state = tick(session.state, gens, seconds, upgrades, prestige, milestones)
    state = award_milestones(state, milestones)
    return Session(
        theme=session.theme, state=state, now=session.now + seconds, log=session.log
    )


def go_offline(session: Session, seconds: int) -> Session:
    """Credit ``seconds`` of offline production via the closed-form engine path."""
    if seconds < 0:
        raise ValueError("seconds must be >= 0")
    gens, upgrades, prestige, milestones = _spec_bundle(session.theme)
    now = session.now + seconds
    state = apply_offline_progress(session.state, gens, now, upgrades, prestige, milestones)
    state = award_milestones(state, milestones)
    return Session(theme=session.theme, state=state, now=now, log=session.log)


# --- rendering embeds to plain text ------------------------------------------


def format_embed(embed: dict) -> str:
    """Render one embed dict (title/description/fields) as readable text."""
    lines = [f"=== {embed['title']} ===", embed["description"], ""]
    for f in embed["fields"]:
        value = f["value"].replace("\n", "\n    ")
        lines.append(f"  {f['name']}: {value}")
    return "\n".join(lines).rstrip()


def view_status(session: Session) -> str:
    return format_embed(render_status(session.state, session.theme, session.now))


def view_shop(session: Session) -> str:
    embed = render_shop(session.state, session.theme)
    if embed is None:
        return "This pack has no upgrade shop."
    return format_embed(embed)


def view_prestige(session: Session) -> str:
    embed = render_prestige(session.state, session.theme)
    if embed is None:
        return "This pack has no prestige track."
    return format_embed(embed)


def view_achievements(session: Session) -> str:
    return format_embed(render_achievements(session.state, session.theme))


# --- command dispatch --------------------------------------------------------

_HELP = """Commands:
  status                 balances, generator rates, offline gains
  shop                   the upgrade shop (cost lines + trap-buy warnings)
  buy <id>               buy one level of upgrade <id>
  prestige [do]          show the prestige view; 'prestige do' performs a reset
  offline <secs>         credit <secs> of offline production, then show status
  wait <secs>            advance the clock by <secs>
  achievements           the milestone view
  pack <id>              switch to another shipped theme pack (fresh save)
  help                   this message
  quit                   leave the game"""


def _buy(session: Session, upgrade_id: str) -> tuple[Session, str]:
    specs = {s.spec_id: s for s in session.theme.upgrade_specs()}
    spec = specs.get(upgrade_id)
    if spec is None:
        valid = ", ".join(specs) or "(none)"
        return session, f"No upgrade {upgrade_id!r}. Valid: {valid}"
    try:
        state = purchase_upgrade(session.state, spec)
    except ValueError as exc:
        return session, f"Cannot buy {upgrade_id!r}: {exc}"
    _, _, _, milestones = _spec_bundle(session.theme)
    state = award_milestones(state, milestones)
    bought = Session(theme=session.theme, state=state, now=session.now, log=session.log)
    return bought, f"Bought a level of {upgrade_id!r}.\n" + view_shop(bought)


def _prestige(session: Session, arg: str) -> tuple[Session, str]:
    if session.theme.prestige is None:
        return session, "This pack has no prestige track."
    if arg != "do":
        return session, view_prestige(session)
    spec = session.theme.prestige_spec()
    if not prestige_eligible(session.state, spec):
        return session, "Not eligible to prestige yet.\n" + view_prestige(session)
    state = apply_prestige(session.state, spec)
    reset = Session(theme=session.theme, state=state, now=session.now, log=session.log)
    return reset, "Prestiged — run reset, bonus banked.\n" + view_status(reset)


def _pack(session: Session, theme_id: str, start_count: int) -> tuple[Session, str]:
    try:
        theme = load_pack(theme_id)
    except ValueError as exc:
        return session, str(exc)
    fresh = new_session(theme, start_count=start_count, now=session.now)
    return fresh, f"Switched to {theme_id!r}.\n" + view_status(fresh)


def dispatch(
    session: Session, command: str, start_count: int = 1
) -> tuple[Session, str]:
    """Apply one command, returning the (possibly new) session and its output.

    Pure: no stdin/stdout, no wall clock. ``start_count`` is the grant used
    when the ``pack`` command starts a fresh save. Raises :class:`QuitGame`
    for ``quit``/``exit`` so the loop can unwind.
    """
    parts = command.strip().split()
    if not parts:
        return session, ""
    verb, args = parts[0].lower(), parts[1:]
    arg = args[0] if args else ""

    if verb in ("quit", "exit", "q"):
        raise QuitGame
    if verb in ("help", "?"):
        return session, _HELP
    if verb == "status":
        return session, view_status(session)
    if verb == "shop":
        return session, view_shop(session)
    if verb in ("achievements", "milestones"):
        return session, view_achievements(session)
    if verb == "buy":
        if not arg:
            return session, "Usage: buy <upgrade-id>"
        return _buy(session, arg)
    if verb == "prestige":
        return _prestige(session, arg)
    if verb in ("offline", "wait"):
        try:
            seconds = int(arg)
        except ValueError:
            return session, f"Usage: {verb} <seconds>"
        moved = (go_offline if verb == "offline" else advance)(session, seconds)
        return moved, view_status(moved)
    if verb == "pack":
        if not arg:
            return session, "Available packs: " + ", ".join(available_packs())
        return _pack(session, arg, start_count)
    return session, f"Unknown command {verb!r}. Type 'help'."


# --- self-contained smoke step (imported by tests) ---------------------------


def demo_step(theme_id: str = "egg-farm") -> str:
    """Build a default session, advance one second, and render status.

    A single self-contained tick+render, no interactive loop and no I/O — the
    smoke-test hook that proves the entrypoint's core path runs end to end.
    """
    session = new_session(load_pack(theme_id))
    session = advance(session, 1)
    return view_status(session)


# --- interactive loop (only under __main__) ----------------------------------


def _build_session(args: argparse.Namespace) -> Session:
    if args.code:
        return session_from_code(args.code, start_count=args.start_count)
    return new_session(load_pack(args.pack), start_count=args.start_count)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="play",
        description="Play superbot-idle in a text REPL (drives the real engine).",
    )
    parser.add_argument(
        "--pack", default="egg-farm", help="theme pack id (default: egg-farm)"
    )
    parser.add_argument("--code", default=None, help="provision from a setup code")
    parser.add_argument(
        "--start-count",
        type=int,
        default=1,
        help="starting generator count per generator (runtime grant; default 1)",
    )
    parser.add_argument(
        "--list-packs", action="store_true", help="print the pack menu and exit"
    )
    args = parser.parse_args(argv)

    if args.list_packs:
        print("\n".join(available_packs()))
        return 0

    try:
        session = _build_session(args)
    except Exception as exc:  # bad pack / bad code — report, don't traceback
        print(f"Could not start: {exc}", file=sys.stderr)
        return 2

    import time  # local: keeps the pure helpers wall-clock-free

    print(f"superbot-idle — {session.theme.name}. Type 'help' or 'quit'.\n")
    print(view_status(session))
    last = time.monotonic()
    while True:
        try:
            raw = input("\n> ")
        except (EOFError, KeyboardInterrupt):
            print()
            break
        # Advance the game clock by the real seconds elapsed while the player
        # was thinking, so idle production actually accrues between commands.
        elapsed = int(time.monotonic() - last)
        if elapsed > 0:
            session = advance(session, elapsed)
            last = time.monotonic()
        try:
            session, out = dispatch(session, raw, start_count=args.start_count)
        except QuitGame:
            break
        if out:
            print(out)
    print("Bye.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
