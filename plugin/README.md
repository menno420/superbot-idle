# superbot-idle-plugin — the idle-engine game-plugin adapter (PLUG-001)

A thin, out-of-tree `plugin/` shell that maps the pure idle engine onto
superbot-next's **game-plugin contract**
([`docs/game-plugin-contract.md`](https://github.com/menno420/superbot-next/blob/d3dba9b/docs/game-plugin-contract.md)
@ `d3dba9b`, binding). It exports a `SubsystemManifest` (commands +
one `idle.status` status panel + `settings` + `events` + the
`idle.game.play` capability) through the `sb.plugins` entry-point group;
the host discovers it at boot, verifies it against its committed
`plugins.lock.json` pin,
joint-compiles it with the in-tree manifests, and registers it on the live
seams.

Mirrors the in-tree exemplar
[`examples/superbot-plugin-hello/`](https://github.com/menno420/superbot-next/tree/d3dba9b/examples/superbot-plugin-hello)
in structure and imports.

## Scope (v1 facets only)

Declares `commands`, `panels`, `settings`, `events`, and `capabilities` — the
v1-allowed facets. **Persistence is host-owned**: `stores` / `data_invariants`
/ `wizard_sections` are refused at the gate, so the idle engine's `GameState`
saves ride the host store, not this plugin.

### Increment 2 — settings, events, live render forwarding

- **`settings`** — `SettingSpec`s mirroring the decoded
  `idle_engine.provisioning.SetupConfig` (the engine's real provisioning
  knobs, not economy tuning): `idle.pack` (which theme pack loads, the setup
  code's `theme_id`) + the three v1 feature toggles `idle.offline_progress` /
  `idle.upgrades` / `idle.prestige` (`activation=ON_BY_DEFAULT`, one per
  `FEATURE_BITS` entry). Bindings ride each spec's `settings_key`; **no
  Discord-pointer `BindingSpec`** is declared — the engine is platform-free and
  has no channel/role/thread target to bind.
- **`events`** — `idle.tick` and `idle.offline_return` (`EventSpec`,
  observability-only), payloads shaped from the engine's real outputs.
- **live render forwarding** — `render_forward.py` (sb-free) forwards
  `idle_engine.render.render_status` / `render_shop` / `render_prestige` output
  **verbatim** through an `IdleRenderState` handle; `manifest.py` registers them
  as `@handler` refs (`idle.render.status` / `.shop` / `.prestige`) and routes
  the `idle status` / `idle shop` / `idle prestige` commands at them
  (`CommandSpec.route` accepts a `HandlerRef`).

**Host-validated / deferred:** the exact host state-injection signature for the
render handlers is a `sb/app/plugin_host.py` detail validated against a live
host (the forwarders are typed against `IdleRenderState`); the host-side
`plugins.lock.json` pin (`tools/plugin_pin.py --write`) is a superbot-next PR,
out of idle scope. Any change to the declared surface re-hashes the pin.

## Running the tests

Two test modules, split by dependency:

- `plugin/tests/test_render_forward.py` is **NON-gated** — it exercises the pure
  render forwarding against the real `idle_engine` (no `sb`), so idle's sb-free
  CI runs it and PROVES the forwarding returns the engine's embed dict verbatim.
- `plugin/tests/test_manifest.py` imports the host `sb` package, so it
  `importorskip`s cleanly without superbot-next (keeping idle CI green) and runs
  only against a real host.

```
python3 -m pytest plugin/tests/            # forwarding runs, manifest skips (no sb)
pip install -e .[host] && python3 -m pytest plugin/tests/   # everything runs
```
