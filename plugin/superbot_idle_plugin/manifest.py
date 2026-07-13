"""IDLE subsystem manifest — the idle-engine game-plugin adapter (PLUG-001).

One command + one status panel, declared OUT OF TREE and consumed by the
superbot-next host through the ``sb.plugins`` entry point (host side:
``sb/app/plugin_host.py``; binding contract: ``docs/game-plugin-contract.md``
@ ``d3dba9b`` in the host repo — superbot-next). Mirrors the in-tree exemplar
``examples/superbot-plugin-hello/``. Pure declarations + ref registrations —
the same shape as an in-tree ``sb/manifest/<key>.py`` module:

  - importing this module IS reserving (the ``@panel`` registration below
    mirrors the in-tree decorator discipline);
  - the host pins this manifest's canonical hash in its committed
    ``plugins.lock.json`` and refuses drift at boot;
  - the v1 contract facets only: this manifest declares a command, a panel,
    and a capability. Persistence is HOST-OWNED — ``stores`` /
    ``data_invariants`` / ``wizard_sections`` are refused at the gate, so the
    idle engine's ``GameState`` saves ride the host store, not this plugin.
"""

from __future__ import annotations

from sb.spec.commands import CommandKind, CommandSpec
from sb.spec.manifest import SubsystemManifest
from sb.spec.panels import (
    EmbedFrameSpec,
    FooterMode,
    NavigationSpec,
    PanelSpec,
    TextBlock,
)
from sb.spec.refs import PanelRef, is_registered, panel

PANEL_ID = "idle.status"


def idle_status_spec() -> PanelSpec:
    """The one panel — a static text body; the panel engine renders it and
    the engine-injected nav slots carry the never-strand routes."""
    return PanelSpec(
        panel_id=PANEL_ID,
        subsystem="idle",
        title="Idle status",
        frame=EmbedFrameSpec(footer_mode=FooterMode.SUBSYSTEM),
        body=(
            TextBlock(
                "⏳ This panel is declared in the **superbot-idle** engine's "
                "`plugin/` adapter — a thin out-of-tree shell over the pure "
                "idle mechanics — and registered through the `sb.plugins` "
                "entry point. It maps the idle engine onto the game-plugin "
                "contract: entry-point discovery, committed hash pin, joint "
                "compile, live dispatch. Persistence is host-owned."
            ),
        ),
        navigation=NavigationSpec(),
    )


def _ensure_refs() -> None:
    """Idempotent ref registration (the in-tree ``ENSURE_REFS`` discipline:
    decorators run at first import only; the compiler's test seam may clear
    the ref table without evicting module caches)."""
    if not is_registered(PanelRef(PANEL_ID)):
        panel(PANEL_ID)(idle_status_spec)


_ensure_refs()
ENSURE_REFS = _ensure_refs


MANIFEST = SubsystemManifest(
    key="idle",
    version=1,
    commands=(
        CommandSpec(
            name="idle",
            kind=CommandKind.BOTH,
            route=PanelRef(PANEL_ID),
            summary="Open the idle-engine status panel.",
            usage="!idle",
            audience_tier="user",
            capability="idle",
        ),
    ),
    panels=(idle_status_spec(),),
    capabilities=("idle",),
)
