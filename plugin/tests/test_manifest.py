"""Authoring-time checks for the idle manifest (needs the host `sb` package —
`pip install -e .[host]` or run inside a host checkout).

The whole module SKIPS cleanly when superbot-next is not installed, so idle's
sb-free CI stays green — the manifest imports `sb.spec.manifest`, so gating on
it is the exact availability signal. The pure render-forwarding behavior is
proven by the SEPARATE, NON-gated `test_render_forward.py`, which runs against
the real `idle_engine` without `sb` (so CI executes the forwarding path, not
just imports it)."""

import pytest

pytest.importorskip("sb.spec.manifest")

from superbot_idle_plugin import manifest as m  # noqa: E402


# --- slice-1 shape (unchanged) ------------------------------------------------


def test_manifest_shape() -> None:
    assert m.MANIFEST.key == "idle"
    # slice command + the three inc2 render-forwarding view commands.
    assert [c.name for c in m.MANIFEST.commands] == ["idle", "status", "shop", "prestige"]
    assert [p.panel_id for p in m.MANIFEST.panels] == [m.PANEL_ID]
    assert m.PANEL_ID == "idle.status"


def test_idle_command_routes_to_the_panel() -> None:
    (cmd,) = [c for c in m.MANIFEST.commands if c.name == "idle" and not c.group]
    assert cmd.route is not None and cmd.route.name == m.PANEL_ID


def test_v1_contract_facets_only() -> None:
    # stores / data_invariants / wizard_sections are host-owned in v1.
    assert m.MANIFEST.stores == ()
    assert m.MANIFEST.data_invariants == ()
    assert m.MANIFEST.wizard_sections == ()


def test_capabilities() -> None:
    assert m.MANIFEST.capabilities == ("idle",)


def test_panel_ref_registered_on_import() -> None:
    from sb.spec.refs import PanelRef, is_registered

    m.ENSURE_REFS()
    assert is_registered(PanelRef(m.PANEL_ID))


# --- inc2: settings facet (the decoded SetupConfig knobs) ---------------------


def test_settings_declared_with_binding_keys() -> None:
    from sb.spec.settings import Activation, SettingSpec

    specs = {s.name: s for s in m.MANIFEST.settings}
    assert set(specs) == {"pack", "offline_progress", "upgrades", "prestige"}
    assert all(isinstance(s, SettingSpec) for s in specs.values())
    # `settings_key` is each spec's binding (the canonical persisted key).
    assert {s.key for s in m.MANIFEST.settings} == {
        "idle.pack",
        "idle.offline_progress",
        "idle.upgrades",
        "idle.prestige",
    }
    # pack is the str theme-id selector; the toggles are §4.4 bools.
    assert specs["pack"].python_type() is str
    assert specs["pack"].activation is None  # non-bool leaves activation unset
    for name in ("offline_progress", "upgrades", "prestige"):
        assert specs[name].is_bool
        assert specs[name].activation is Activation.ON_BY_DEFAULT


def test_settings_facets_validate_clean() -> None:
    # The §2.5/§4.4 conscious-choice fences must pass (no bool without an
    # activation, no non-bool with one, etc.).
    from sb.spec.settings import validate_settings_facets

    assert validate_settings_facets(m.MANIFEST) == []


def test_no_host_owned_binding_fabricated() -> None:
    # The engine is platform-free: no Discord-pointer BindingSpec is declared
    # (would invent a channel/role target the engine doesn't have).
    from sb.spec.settings import BindingSpec

    assert not any(isinstance(s, BindingSpec) for s in m.MANIFEST.settings)


# --- inc2: events facet (the idle lifecycle) ----------------------------------


def test_events_declared() -> None:
    from sb.spec.events import EventSpec

    by_name = {e.name: e for e in m.MANIFEST.events}
    assert set(by_name) == {"idle.tick", "idle.offline_return"}
    assert all(isinstance(e, EventSpec) for e in by_name.values())
    for e in by_name.values():
        assert e.owner_subsystem == "idle"
        assert e.observability_only is True
        assert len(e.payload_schema) >= 1
    # offline-return carries the credited gains + the timing window.
    fields = {f.name for f in by_name["idle.offline_return"].payload_schema}
    assert {"last_seen", "now", "gains"} <= fields


# --- inc2: render-forwarding handlers -----------------------------------------


def test_render_handlers_registered_on_import() -> None:
    from sb.spec.refs import HandlerRef, is_registered

    m.ENSURE_REFS()
    for name in (m.HANDLER_STATUS, m.HANDLER_SHOP, m.HANDLER_PRESTIGE):
        assert is_registered(HandlerRef(name)), name


def test_view_commands_route_to_render_handlers() -> None:
    from sb.spec.refs import HandlerRef

    routes = {c.name: c.route for c in m.MANIFEST.commands if c.group == "idle"}
    assert routes == {
        "status": HandlerRef(m.HANDLER_STATUS),
        "shop": HandlerRef(m.HANDLER_SHOP),
        "prestige": HandlerRef(m.HANDLER_PRESTIGE),
    }


def test_registered_handler_forwards_render_status() -> None:
    # The registered @handler callable IS the pure forwarder — resolving it and
    # calling it returns render_status's dict unchanged (proven fully, without
    # sb, in test_render_forward.py; here we prove the REGISTERED ref resolves
    # to that forwarder).
    from pathlib import Path

    from sb.spec.refs import HandlerRef, resolve

    from idle_engine import GameState, load_theme
    from idle_engine.render import render_status
    from superbot_idle_plugin.render_forward import IdleRenderState

    m.ENSURE_REFS()
    repo_root = Path(__file__).resolve().parents[2]
    theme = load_theme(repo_root / "themes" / "egg-farm.yaml")
    gs = GameState(balances={"primary": 1234}, owned={"tier1": 2}, last_seen=1000)
    handle = IdleRenderState(game_state=gs, theme=theme, now=2000)
    fn = resolve(HandlerRef(m.HANDLER_STATUS))
    assert fn(handle) == render_status(gs, theme, 2000)
