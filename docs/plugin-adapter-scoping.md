# Plugin-adapter scoping — mapping this engine onto superbot-next's plugin contract

> **Status:** `plan` — scoping only, written 2026-07-11. **No adapter code
> exists and none should be built from this doc alone**: the upstream
> contract is UNVERIFIED (evidence below). This doc records what our side
> of the seam already guarantees, and exactly what we still need from the
> exemplar before an adapter can be scoped for real.

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

**Verdict: UNVERIFIED.** The exemplar repo has been created but not seeded;
no reachable superbot-next doc publishes the manifest/plugin contract yet.
Everything below the UNVERIFIED line is therefore a *question list*, not a
design. Building a speculative manifest against a contract that lands later
would be integrity-floor debt, so this slice ships **no** `plugin/` skeleton.

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

## UNVERIFIED — what we need from the exemplar before scoping the adapter

Exactly these, in priority order; none can be assumed:

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

**Recommended ⚑ to the manager**: ask for the superbot-next plugin/manifest
contract pointer (or a seeding ETA for `superbot-plugin-hello`). The moment
the exemplar has content, re-run the probe table above and replace this
section with the real mapping plus the minimal manifest skeleton — verified
parts only.

## Cross-links

Reachable from [`AGENT_ORIENTATION.md`](AGENT_ORIENTATION.md) § Lane-layer
docs. Related: [`provisioning.md`](provisioning.md),
[`render-layer.md`](render-layer.md), [`theme-schema.md`](theme-schema.md),
[`../README.md`](../README.md) (integrity floor).
