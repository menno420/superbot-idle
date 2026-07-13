"""Authoring-time checks for the idle manifest (needs the host `sb` package —
`pip install -e .[host]` or run inside a host checkout).

The whole module SKIPS cleanly when superbot-next is not installed, so idle's
sb-free CI stays green — the manifest imports `sb.spec.manifest`, so gating on
it is the exact availability signal."""

import pytest

pytest.importorskip("sb.spec.manifest")

from superbot_idle_plugin import manifest as m  # noqa: E402


def test_manifest_shape() -> None:
    assert m.MANIFEST.key == "idle"
    assert [c.name for c in m.MANIFEST.commands] == ["idle"]
    assert [p.panel_id for p in m.MANIFEST.panels] == [m.PANEL_ID]
    assert m.PANEL_ID == "idle.status"


def test_command_routes_to_the_panel() -> None:
    (cmd,) = m.MANIFEST.commands
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
