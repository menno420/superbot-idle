# superbot-idle-plugin — the idle-engine game-plugin adapter (PLUG-001)

A thin, out-of-tree `plugin/` shell that maps the pure idle engine onto
superbot-next's **game-plugin contract**
([`docs/game-plugin-contract.md`](https://github.com/menno420/superbot-next/blob/d3dba9b/docs/game-plugin-contract.md)
@ `d3dba9b`, binding). It exports a `SubsystemManifest` (one `idle` command +
one `idle.status` status panel + the `idle` capability) through the
`sb.plugins` entry-point group; the host discovers it at boot, verifies it
against its committed `plugins.lock.json` pin, joint-compiles it with the
in-tree manifests, and registers it on the live seams.

Mirrors the in-tree exemplar
[`examples/superbot-plugin-hello/`](https://github.com/menno420/superbot-next/tree/d3dba9b/examples/superbot-plugin-hello)
in structure and imports.

## Scope (v1 facets only)

Declares `commands`, `panels`, and `capabilities` — the v1-allowed facets.
**Persistence is host-owned**: `stores` / `data_invariants` /
`wizard_sections` are refused at the gate, so the idle engine's `GameState`
saves ride the host store, not this plugin.

Settings/events/live-render-handler wiring and the host-side
`plugins.lock.json` pin are deferred to a follow-up slice.

## Running the manifest test

The manifest imports the host `sb` package, so its test needs superbot-next
installed. Without it the test module skips cleanly (keeping idle's sb-free CI
green). To run it against the real host:

```
pip install -e .[host]
python3 -m pytest plugin/tests/
```
