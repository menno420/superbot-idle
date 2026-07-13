# 2026-07-13 — PLUG-001 adapter increment 2: settings + lifecycle events + live render forwarding

> **Status:** `in-progress`

- **📊 Model:** opus-4.8 · high · feature build · idle-engine seat (PLUG-001 adapter inc2) · 2026-07-13
  — versioned-family name (family + version, e.g. `fable-5`) from this session's OWN harness
  self-report (Q-0262 / inbox ORDER 001); no build/snapshot/date suffix, never from the Routines screen.

## What happened

FOLLOW-UP build for PLUG-001 — increment 2, stacked on the adapter slice (PR #75, head `712e162`;
NOT branched from main). The slice exported a command + status panel + `idle` capability shell; the
four seams' settings/events and the live render forwarding were explicitly deferred there. This
increment lands them, still against the binding contract `superbot-next docs/game-plugin-contract.md`
@ `d3dba9b`, mirroring the exemplar `examples/superbot-plugin-hello/` for the sb.spec symbols.

**What the increment adds (v1 facets only, extending the slice):**
- **SETTINGS** — `plugin/superbot_idle_plugin/manifest.py` now declares a `settings=(...)` facet of
  `SettingSpec`s that mirror the decoded `SetupConfig` (the engine's real provisioning knobs, NOT
  economy tuning numbers): `idle.pack` (str — which theme pack this instance loads, the setup code's
  `theme_id`) plus the three v1 feature toggles `idle.offline_progress` / `idle.upgrades` /
  `idle.prestige` (bool, `activation=ON_BY_DEFAULT` per §4.4 — each maps 1:1 to a `FEATURE_BITS`
  entry / a `SetupConfig` field the engine ships today). Bindings ride each spec's `settings_key`
  (the canonical persisted key) — NO Discord-pointer `BindingSpec` is fabricated, because the engine
  is platform-free and has no channel/role/thread target to bind (would be inventing a target the
  engine doesn't have). Host-owned facets (`stores` / `data_invariants` / `wizard_sections`) stay
  empty.
- **EVENTS** — an `events=(...)` facet declaring the idle lifecycle the contract supports:
  `idle.tick` (a production tick) and `idle.offline_return` (offline progress credited on return),
  each an `EventSpec` with a `FieldSpec` payload schema grounded in the engine's real outputs
  (`elapsed_s`, `now`, `last_seen`, credited `gains`), `owner_subsystem="idle"`,
  `observability_only=True`, default `BEST_EFFORT` delivery.
- **LIVE RENDER FORWARDING** — a new sb-free module `plugin/superbot_idle_plugin/render_forward.py`
  with pure forwarders `forward_status` / `forward_shop` / `forward_prestige` that return
  `idle_engine.render.render_status` / `render_shop` / `render_prestige` output VERBATIM (zero
  formatting on the adapter side), taking a clearly-typed `IdleRenderState` handle (`game_state`,
  `theme`, `now`). `manifest.py` registers these as `@handler` refs
  (`idle.render.status` / `.shop` / `.prestige`) and routes three grouped commands
  (`idle status` / `idle shop` / `idle prestige`) at them (`CommandSpec.route` accepts a
  `HandlerRef` — the command-only class in the frozen §2.2 grammar). The static `idle.status` panel
  + `idle` command from the slice stay untouched.

**sb.spec symbols used (mirrored VERBATIM from the source @ `d3dba9b`, not guessed):**
`from sb.spec.settings import Activation, SettingSpec` · `from sb.spec.events import EventSpec,
FieldSpec` · `from sb.spec.refs import HandlerRef, handler, is_registered` (alongside the slice's
`PanelRef`, `panel`). Settings/bindings/resources all ride the ONE `settings` facet tuple
(`validate_settings_facets` filters by `isinstance`).

**Keeping idle CI green (sb-free):** the sb-coupled manifest checks stay under one
`pytest.importorskip("sb.spec.manifest")`-gated module (`plugin/tests/test_manifest.py`) so idle's
sb-free CI skips them. A SEPARATE NON-gated module `plugin/tests/test_render_forward.py` exercises
the pure forwarding path against the REAL `idle_engine` (no sb) — asserting each forwarder returns
the render dict byte-identically for a sample `GameState` + the egg-farm pack — so CI actually PROVES
the forwarding works, not merely that it imports. `plugin/conftest.py` now adds the repo root to
`sys.path` alongside `plugin/` so plugin tests import both `superbot_idle_plugin` AND `idle_engine`.

**Deferred / host-validated (NOT in this increment):** the exact host state-injection signature for
the render handlers (the host adapter provides the idle instance's state handle at dispatch — the
forwarders are typed against `IdleRenderState`; live wiring is validated host-side against
`sb/app/plugin_host.py`, out of idle-CI scope), and the host-side `plugins.lock.json` pin
(`tools/plugin_pin.py --write` — a superbot-next PR, out of idle scope). Any change to the declared
manifest surface changes the pin hash: re-pin deliberately host-side.

Landing (born-red convention): this card born RED (`in-progress`) in the first commit alongside the
telemetry row + `control/claims/plug-001-adapter-inc2.md`; then the increment code
(manifest + `render_forward.py` + conftest); then the tests + README/docstring; card flipped
`complete` as the LAST commit. Verify: `python3 -m pytest -q` → >1131 passed (the non-gated
forwarding tests ADD passing tests; sb-coupled manifest checks stay under the one module skip);
`python3 bootstrap.py check --strict` → green; `python3 tools/theme_gate.py themes` → all 12 packs
valid (this base is #75's head — wave-4 packs are on #76). PR opened READY + green, base=main with
the #75 stack noted; NOT auto-merged (worker does not merge its own PR).

## 💡 Session idea

The render forwarders return WHOLE embeds (`title`/`description`/`color`/`fields`), but the contract's
declarative panel grammar builds embeds from `PanelSpec` blocks — the closest dynamic seam,
`FieldsBlock(provider=ProviderRef)`, emits FIELDS (rows), not a whole embed. So "a handler returns a
complete embed verbatim → a panel" is a shape the declarative grammar can't fully express; it needs
host-side wiring, which is exactly why the exact injection is host-validated here. A cheap follow-up
that would let idle-CI prove MORE: publish a tiny `RenderEnvelope` contract type in the shared
`sb.spec` (or a documented dict shape) that a `@handler`-backed panel body is allowed to return
verbatim — then the forwarders could be typed against it and a host-side matrix job (the slice's
proposed `plugin-host` workflow) could assert the whole-embed round-trip once per pin, closing the
gap between "forwarding returns the right dict" (proven here, non-gated) and "the host renders it"
(still host-only).

## ⟲ Previous-session review

previous-session review: the plug-001-adapter slice (PR #75) did the disciplined thing — it mirrored
the exemplar's sb.spec imports VERBATIM rather than guessing, kept `idle_engine/` untouched, and
gated the sb-coupled test behind `importorskip` so idle CI stayed green by skipping. That discipline
set this increment up cleanly: because the slice pinned the contract SHA and the exemplar path, the
new settings/events/handler symbols came straight from reading the source (`sb/spec/settings.py`,
`events.py`, `refs.py`, `commands.py`) at `d3dba9b`, not from a sketch. The one place this increment
goes BEYOND the slice's caution is its own session idea from #75: the slice worried that a real
`sb.spec` API drift would sail through idle-green because the only manifest proof is a skip — this
increment narrows that blind spot for the render seam specifically by adding a NON-gated test that
runs the forwarding against real `idle_engine`, so at least the forwarding contract (the load-bearing
new behavior) is asserted in idle CI, not merely imported-then-skipped.
