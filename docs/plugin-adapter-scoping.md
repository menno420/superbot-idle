# Plugin-adapter scoping — mapping this engine onto superbot-next's plugin contract

> **Status:** `plan` — scoping only, written 2026-07-11; **re-probed
> 2026-07-12 and the upstream contract is now VERIFIED** (see § Re-probe
> 2026-07-12 below — it supersedes the 2026-07-11 UNVERIFIED verdict). **No
> adapter code exists yet and none is built here**: this remains a scoping
> doc. With the contract found, the next step is the adapter slice per this
> doc — a separate, non-docs slice. This doc records what our side of the
> seam already guarantees and now maps it onto the verified contract.

## Why this doc exists

The lane contract (README.md § Integrity floor) is explicit: this engine is
**plugin-native** — "built against superbot-next's manifest/plugin contract
(read via raw; `superbot-plugin-hello` is its exemplar); no Discord-API
calls inside engine core." Before writing any adapter we tried to read that
contract at its source. The attempt is logged verbatim below so the next
session doesn't re-derive it.

## Evidence log — contract probe, 2026-07-11 (raw fetch only, per policy)

| Probe (raw URL) | Result |
|---|---|
| `raw.githubusercontent.com/menno420/superbot-next/main/README.md` | **Reachable.** Describes superbot-next as a production Discord bot in ground-up rebuild on substrate-kit, seven port bands, CI procedure. **Zero plugin/manifest contract content**; points to `docs/status/README-first.md`. |
| `…/superbot-next/main/docs/status/README-first.md` | Reachable. Red-status dashboard / parity ledger only — no plugin material. |
| `…/superbot-next/main/docs/architecture.md` | Reachable. Layering/import rules for superbot-next itself — no plugin-loading or manifest content. |
| `…/superbot-next/main/docs/plugins.md` | HTTP 404. |
| `…/superbot-next/main/docs/plugin-contract.md` | HTTP 404. |
| `…/superbot-plugin-hello/main/README.md` | HTTP 404. |
| `…/superbot-plugin-hello/master/README.md` | HTTP 404. |
| `github.com/menno420/superbot-plugin-hello` (HTML page) | Repository **exists, is public, and is EMPTY** — "This repository is empty." No manifest, no files. |

**Verdict (2026-07-11): UNVERIFIED.** The exemplar repo has been created but
not seeded; no reachable superbot-next doc publishes the manifest/plugin
contract yet. Everything below the UNVERIFIED line is therefore a *question
list*, not a design. Building a speculative manifest against a contract that
lands later would be integrity-floor debt, so this slice ships **no**
`plugin/` skeleton.

> **This 2026-07-11 verdict is SUPERSEDED by the re-probe below (2026-07-12).**
> The probe was not wrong — the filenames were hypothesized incorrectly; the
> contract was published all along at a different path, found by listing the
> repo tree.

## Re-probe 2026-07-12 — contract FOUND (supersedes the UNVERIFIED verdict)

Re-ran the probe on 2026-07-12. The two URLs the 2026-07-11 table recorded as
404 are **still 404 today** — so the earlier evidence stands unchanged; the
mistake was only in the guessed filenames, not the probe method:

| Probe (raw URL) | Result 2026-07-12 |
|---|---|
| `raw.githubusercontent.com/menno420/superbot-next/main/docs/plugins.md` | **Still HTTP 404** (unchanged from 2026-07-11). |
| `…/superbot-next/main/docs/plugin-contract.md` | **Still HTTP 404** (unchanged from 2026-07-11). |
| Tree listing of `menno420/superbot-next` @ `d3dba9b` | **Contract FOUND** at `docs/game-plugin-contract.md` (Status: binding; owner decision 2026-07-09, ledger D-0056). |
| `menno420/superbot-plugin-hello` (standalone HTML page) | **Still EMPTY** — zero refs. The working exemplar currently lives IN-TREE at superbot-next `examples/superbot-plugin-hello/`, pending an owner-created standalone repo. |

**Verdict (2026-07-12): VERIFIED.** The plugin contract EXISTS and is binding.

- **Canonical doc:** superbot-next `docs/game-plugin-contract.md` (binding; owner
  decision 2026-07-09, ledger D-0056), at superbot-next HEAD `main` @
  `d3dba9b53bf87ededee6ed4942a1e7c87e185add` (commit dated 2026-07-12).
- **Host-side implementation is real, not just a spec:** `sb/app/plugin_host.py`
  (loader/enforcer), `tools/plugin_pin.py` (pin/hash CLI), `plugins.lock.json`
  (pin registry root), and a working in-tree exemplar at
  `examples/superbot-plugin-hello/`.

### Contract summary (from `docs/game-plugin-contract.md` @ `d3dba9b`)

- **Entry point / discovery:** setuptools entry point group `sb.plugins`. A
  plugin module exports `MANIFEST = SubsystemManifest(...)` (or a `MANIFESTS`
  tuple), registers callables via `sb.spec.refs` decorators
  (`@handler` / `@panel` / `@workflow` / `@provider`), and exposes an
  idempotent `ENSURE_REFS`.
- **v1 allowed facets** (what a plugin MAY declare): `commands`, `panels`,
  `settings` (+ `bindings`), `events`, `capabilities`.
- **Host-owned / refused at the gate** (a plugin may NOT declare these):
  `stores`, `data_invariants`, `wizard_sections`.
- **Pin / hash lifecycle:** install → `tools/plugin_pin.py --write` (sha256 of
  the canonical manifest hash + a joint `compile_manifests`) → commit the pin
  diff via a host PR → boot-time discovery + pin-verify + register
  (`sb/app/main.py` step 9b). Hash drift or an unpinned plugin ⇒
  `FAILED_STARTUP(plugin_gate)`.

### How our side maps on (already-verified, in-repo)

The four seams in the next section are unchanged and still ground truth. Against
the verified contract they land as facets rather than open questions:

- **Commands / panels** ← our `render_*` payloads (§ 4): the adapter registers
  `@handler`/`@panel` refs that forward `idle_engine/render.py`'s
  embed-shaped dicts verbatim.
- **Settings (+bindings)** ← the decoded `SetupConfig` (§ 1): `decode_setup`
  runs at the plugin trust boundary; the setup code / config enters through
  the host's `settings` facet.
- **Persistence** is **host-owned** (`stores` is refused at the gate), which
  resolves the old open question (§ 4 / persistence.md): `GameState` saves
  (`dump_state`/`load_state`) ride the host's store — the plugin never ships
  its own storage backend.
- **Events / capabilities** cover tick/offline triggers and any declared
  permissions.

**Next actionable step (NOT done here — this slice is docs-only):** scope and
build the adapter slice per this doc — a thin `plugin/` shell exporting a
`SubsystemManifest` over the four verified seams, pinned via
`tools/plugin_pin.py`. That is a separate, non-docs slice; no adapter code is
written in this docs-only un-park.

## Our side of the seam — VERIFIED (in-repo, source is ground truth)

Whatever shape the contract takes, the adapter is a thin shell around four
seams this repo already ships and tests. All four are pure, stdlib-first,
and free of chat-platform imports (enforced by `tests/test_core_skin_guard.py`).

### 1. Setup-code decode — the provisioning entry point

`idle_engine/provisioning.py` (contract doc: [`provisioning.md`](provisioning.md)):

- `decode_setup(code) -> SetupConfig` — pure, I/O-free; run it at the
  plugin's trust boundary. Distinct error taxonomy (`MalformedCodeError`,
  `UnknownVersionError`, `ChecksumError`, `UnknownFeatureError`, all
  subclassing `SetupCodeError`) so the plugin can map failures to user
  messages without string-matching.
- `validate_against_catalog(config, themes_dir) -> Theme` — the separate
  load-time step (`UnknownThemeError`, `FeatureUnavailableError`).
- v1 is FROZEN; unknown flag bits and versions fail loud, so a v2 engine
  never silently misreads v1 codes and vice versa.

### 2. Theme loader — the catalog the adapter ships

`idle_engine/theme.py` — `load_theme(path) -> Theme`; packs are data-only
YAML under `themes/*.yaml`, validated by `schema/theme.schema.json` +
`tools/theme_gate.py` (gate-green = safe to enable unreviewed, README § 3).
The adapter bundles the catalog directory and never edits packs.

### 3. Engine API — pure state-in/state-out mechanics

`idle_engine/engine.py`, `upgrades.py`, `prestige.py`, `economy.py`:
`tick` / `offline_progress` / `apply_offline_progress`,
`purchase_upgrade` / `upgrade_cost`, `prestige_eligible` / `prestige_award`
/ `apply_prestige`. All integer-exact and deterministic
(`tests/test_properties.py` pins partition-equivalence, determinism, and
conservation as properties). `GameState` is an immutable dataclass of
plain dicts/ints — trivially serializable; **persistence is the plugin's
job**, the engine takes state in and hands state back.

### 4. Render payloads — what the plugin sends to Discord

`idle_engine/render.py` (contract doc: [`render-layer.md`](render-layer.md)):
`render_status` / `render_shop` / `render_prestige` return plain
embed-shaped dicts (`title`, `description`, `color` int, `fields`) already
validated against the platform caps (PLATFORM-LIMITS.md). The plugin
forwards them verbatim to its embed constructor — zero formatting logic on
the adapter side.

## ~~UNVERIFIED~~ ANSWERED — what we needed from the exemplar (historical)

> **Superseded 2026-07-12.** The contract at superbot-next
> `docs/game-plugin-contract.md` @ `d3dba9b` answers this question list — see
> § Re-probe 2026-07-12 above for the resolutions. Kept here as the record of
> what was open before verification; no longer a blocker.

Exactly these were open, in priority order; each is now resolved by the
verified contract (§ Re-probe 2026-07-12):

1. **Manifest**: file name, format (TOML/YAML/JSON?), required fields
   (id, version, entry point, permissions?), and where it lives in the
   plugin repo layout.
2. **Entry point / lifecycle**: how superbot-next discovers and loads a
   plugin (Python entry point? module path in the manifest?), and which
   lifecycle hooks exist (load/unload/ready).
3. **Command registration**: how a plugin declares slash commands /
   interactions, and what the handler signature receives — this decides
   how thin the shell around `render_*` can be.
4. **Persistence contract**: what storage the host offers a plugin (KV?
   per-guild scoping?) — this decides where `GameState` lives and how
   `last_seen` survives restarts.
5. **Configuration ingestion**: where a setup code (or its decoded
   `SetupConfig`) enters — an install-time argument, a command, or host
   config — i.e. where `decode_setup` runs.
6. **Dependency policy**: whether a plugin may vendor PyYAML (the theme
   loader's one non-stdlib import) or must pre-resolve packs to JSON.

**~~Recommended ⚑ to the manager~~ RESOLVED 2026-07-12**: the pointer the ⚑
asked for now exists — superbot-next `docs/game-plugin-contract.md` @
`d3dba9b`. The probe was re-run (§ Re-probe 2026-07-12) and the real mapping is
recorded there. PLUG-001 is UN-PARKED; the remaining work is the adapter slice
(a separate, non-docs slice), not a contract hunt.

## Cross-links

Reachable from [`AGENT_ORIENTATION.md`](AGENT_ORIENTATION.md) § Lane-layer
docs. Related: [`provisioning.md`](provisioning.md),
[`render-layer.md`](render-layer.md), [`theme-schema.md`](theme-schema.md),
[`../README.md`](../README.md) (integrity floor).
