# 2026-07-12 — PLUG-001 adapter slice: thin plugin/ shell exporting a SubsystemManifest

> **Status:** `complete`

- **📊 Model:** opus-4.8 · high · feature build · idle-engine seat (PLUG-001 adapter build) · 2026-07-12T21:06Z–21:40Z (`date -u`)
  — versioned-family name (family + version, e.g. `fable-5`) from this session's OWN harness
  self-report (Q-0262 / inbox ORDER 001); no build/snapshot/date suffix, never from the Routines screen.

## What happened

BUILD slice for PLUG-001 — the first adapter code. The upstream superbot-next plugin contract was
VERIFIED last session (docs-only un-park, PR #72); this slice builds the thin `plugin/` shell it
scoped, against the binding contract `superbot-next docs/game-plugin-contract.md` @ `d3dba9b`.

**What the adapter is (v1 facets only):**
- A new top-level `plugin/` subtree — ZERO edits to `idle_engine/`. It mirrors the in-tree exemplar
  `examples/superbot-plugin-hello/` in structure and imports (read via raw @ `d3dba9b` before writing).
- `plugin/superbot_idle_plugin/manifest.py` exports `MANIFEST = SubsystemManifest(key="idle",
  version=1, …)`: one `CommandSpec(name="idle", route=PanelRef("idle.status"), capability="idle")`,
  one `PanelSpec(panel_id="idle.status", subsystem="idle")`, `capabilities=("idle",)`, plus an
  idempotent `ENSURE_REFS` hook guarded by `is_registered`.
- sb.spec imports mirror the exemplar VERBATIM: `from sb.spec.commands import CommandKind,
  CommandSpec` · `from sb.spec.manifest import SubsystemManifest` · `from sb.spec.panels import
  EmbedFrameSpec, FooterMode, NavigationSpec, PanelSpec, TextBlock` · `from sb.spec.refs import
  PanelRef, is_registered, panel`.
- Host-owned facets stay host-owned: `stores` / `data_invariants` / `wizard_sections` are NOT
  declared — persistence rides the host store (contract refuses them at the gate).
- `plugin/pyproject.toml` exports the `sb.plugins` entry point (`idle =
  superbot_idle_plugin.manifest`); the host kernel is an optional `[host]` dep pinned to
  `git+…@d3dba9b`. `plugin/conftest.py` puts `plugin/` on `sys.path` so idle's root `pytest -q`
  imports the package when collecting `plugin/tests/`.

**Keeping idle CI green (sb-free):** `plugin/tests/test_manifest.py`'s first line after imports is
`pytest.importorskip("sb.spec.manifest")` — superbot-next is not installed in idle CI, so the whole
test module skips cleanly and the suite stays green. Under a real host (`pip install -e .[host]`)
the module runs and asserts manifest shape, command→panel routing, empty host-owned facets,
`capabilities == ("idle",)`, and `ENSURE_REFS` ref registration.

**Also (truth-fix, docs only):** `docs/current-state.md` had stale counts — corrected suite
620→1131 (two occurrences) and theme catalog 9→12 packs (appended ant-colony, idol-agency,
pirate-cove, which already ship under `themes/`), and refreshed the groomed date/SHA to 2026-07-12
/ `c753bc8`. Dated historical "Recently shipped" lines left untouched.

**Deferred to a follow-up (NOT in this slice):** settings/events/live-render-handler wiring and the
host-side `plugins.lock.json` pin (`tools/plugin_pin.py`) — those land in the host repo.

Landing (born-red convention): this card born RED (`in-progress`) in the first commit alongside the
telemetry row + `control/claims/plug-001-adapter.md`; then the `plugin/` subtree; then the
current-state truth-fix; card flipped `complete` as the LAST commit. Verify: `python3 -m pytest -q`
→ 1131 passed (5 plugin tests skip via `importorskip` since superbot-next isn't installed);
`python3 bootstrap.py check --strict` → all checks pass; `python3 tools/theme_gate.py themes` → all
12 packs valid. PR opened READY + green; NOT auto-merged (worker does not merge its own PR).

## 💡 Session idea

`plugin/` now imports `sb.spec.*` that only exists under a host checkout, and idle CI proves the
manifest only by *skipping* it — so a real API drift (a renamed `sb.spec` symbol, a changed
`SubsystemManifest` field) would sail through idle green and only bite at the host's joint-compile.
A cheap guard: a host-side CI matrix job (or a nightly) that `pip install -e plugin[host]` and runs
`plugin/tests/` against superbot-next pinned at the contract SHA, so the skip becomes a real
assertion exactly once per pin. Recipe: add a `plugin-host` workflow gated on changes to `plugin/**`
that installs the `[host]` extra and runs the manifest test un-skipped; wire it as advisory first
(the pin can lag the contract), promote to required when `plugins.lock.json` lands.

## ⟲ Previous-session review

previous-session review: the plug-001-unpark-docs slice (PR #72) did the honest thing — it VERIFIED
the contract by listing the repo tree, recorded the exemplar's real path
(`examples/superbot-plugin-hello/`), and shipped ZERO speculative adapter code, explicitly leaving
the build as "a separate, non-docs slice." This slice is that follow-up, and the discipline paid
off twice: because the un-park pinned the contract SHA (`d3dba9b`) and named the exemplar, building
the manifest was a straight mirror of a known-good file rather than an API guess — the imports came
from reading the exemplar verbatim, not from a sketch. And because the un-park kept `idle_engine/`
untouched, this slice could add a wholly new `plugin/` subtree with zero engine risk, exactly the
thin-shell shape the scoping doc demanded.
