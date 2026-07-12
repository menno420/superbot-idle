# 2026-07-12 — PLUG-001 un-park: docs-only re-probe + contract verified

> **Status:** `complete`

- **📊 Model:** opus-4.8 · high · idle-engine seat (PLUG-001 docs-only un-park) · 2026-07-12T00:15Z–00:23Z (`date -u`)
  — versioned-family name (family + version, e.g. `fable-5`) from this session's OWN harness
  self-report (Q-0262 / inbox ORDER 001); no build/snapshot/date suffix, never from the Routines screen.

## What happened

DOCS-ONLY slice to un-park PLUG-001. The upstream superbot-next plugin contract, previously
recorded UNVERIFIED (raw-probe 404s on two hypothesized URLs), has now been VERIFIED to EXIST
at a different path found by listing the repo tree.

**Verified facts (contract EXISTS):**
- Canonical path: `superbot-next docs/game-plugin-contract.md` (Status: binding, owner decision
  2026-07-09, ledger D-0056).
- superbot-next HEAD (main): d3dba9b53bf87ededee6ed4942a1e7c87e185add (2026-07-12).
- Host-side implementation exists: `sb/app/plugin_host.py` (loader/enforcer),
  `tools/plugin_pin.py` (pin/hash CLI), `plugins.lock.json` (pin registry), in-tree exemplar
  `examples/superbot-plugin-hello/`.
- Entry point: setuptools entry point group `sb.plugins`; module exports
  `MANIFEST = SubsystemManifest(...)` (or `MANIFESTS` tuple), registers callables via
  `sb.spec.refs` decorators (@handler/@panel/@workflow/@provider), exposes idempotent `ENSURE_REFS`.
- v1 allowed facets: commands, panels, settings(+bindings), events, capabilities.
  Host-owned / refused at gate: stores, data_invariants, wizard_sections.
- Lifecycle: install → `tools/plugin_pin.py --write` (sha256 canonical manifest hash + joint
  compile_manifests) → commit pin diff via host PR → boot-time discovery+pin-verify+register
  (sb/app/main.py step 9b). Hash drift or unpinned ⇒ FAILED_STARTUP(plugin_gate).

**Nuance kept (not a rewrite of history):** the two old probe URLs
(`raw.githubusercontent.com/menno420/superbot-next/main/docs/plugins.md` and
`.../docs/plugin-contract.md`) are STILL 404 today — the old probe was not wrong, the filenames
were hypothesized incorrectly. The standalone repo `menno420/superbot-plugin-hello` is STILL
EMPTY (zero refs) — the exemplar lives in-tree at superbot-next for now.

**Edits (docs only — NO mechanics/engine/theme changes):**
1. `docs/plugin-adapter-scoping.md` — added a dated 2026-07-12 re-probe section that records the
   two URLs still 404, the tree-listing find, a contract summary, and SUPERSEDES the earlier "no
   reachable doc publishes the contract" verdict; next step = adapter slice (docs-only here).
2. `docs/current-state.md` — flipped the "plugin contract does not exist" claim and the roadmap
   BLOCKED marker to UN-PARKED/ready; kept the exemplar-still-empty nuance.
3. `docs/persistence.md` — updated the "blocked upstream" link text to the now-existing contract.
4. `docs/AGENT_ORIENTATION.md` — flipped the contract note from UNVERIFIED to VERIFIED (2026-07-12).

Landing: born-red card first (this file) + telemetry row; doc edits; local checks green; PR #72
opened READY (substrate-gate + theme-gate both green 2026-07-12T00:22Z); heartbeat overwrite of
`control/status.md`; this card flipped complete as the last commit. Verify: `python3 -m pytest -q`
→ 1131 passed; `python3 bootstrap.py check --strict` (born-red advisory path) → all checks
passed; `python3 tools/theme_gate.py themes` → all 12 packs valid. PR NOT auto-merged (worker
does not merge its own PR) — left READY + green.

## 💡 Session idea

`bootstrap.py check --strict` could learn a lightweight "cross-repo pointer" lint: a doc that
cites an upstream file by `<repo> <path>` + a short SHA (like `superbot-next
docs/game-plugin-contract.md @ d3dba9b`) is currently free-text the reachability graph can't
follow. A guard could recognize the `@ <sha>` idiom and at least assert the SHA is well-formed
(7–40 hex) and the same across all docs that cite it in one PR — catching a stale-SHA drift when
the next slice bumps the pin. Guard recipe: extend the backtick-ref scan in `check_links` /
`_outgoing_links` (bootstrap.py) with an `@ <sha>` capture, test target a new
`tests/test_docs_parity.py` case asserting single-SHA-per-PR for cross-repo citations.

## ⟲ Previous-session review

previous-session review: the property-tests-plugin-scoping slice (PRs #30+#31) shipped
`docs/plugin-adapter-scoping.md` as an evidence-GATED scoping doc, and the close-out/archive
retro (PR #70) parked PLUG-001 with an explicit ⚑ ("contract unavailable upstream; ask for a
pointer or seeding ETA"). Both were honest to ground truth at the time — the contract genuinely
was not at the two probed URLs. This slice pays that discipline back: because the earlier doc
recorded the probe verbatim rather than guessing a design, un-parking is a clean ADD of a dated
re-probe section that supersedes one verdict line, with zero speculative adapter code — exactly
the "no integrity-floor debt" the scoping doc demanded.
