# 2026-07-14 — preflight-script plant + host card-guard split out of the enabler

> **Status:** `in-progress`
> **Branch:** `claude/preflight-and-enabler-split` · claim PR #136 (merged 2026-07-14T18:05Z, squash `61f9856`)

- **📊 Model:** fable-5 · medium · feature build — plant `scripts/preflight.py` (local-ritual ↔ CI parity) + relocate the host card-guard/provenance customizations out of the kit-owned auto-merge-enabler into a separate host-owned workflow · session opened 2026-07-14T17:54Z (`date -u`)

**Goal:** two v1.16.0 follow-ups, both symptoms visible in `check --strict`
at HEAD `61f9856`:

1. **Plant `scripts/preflight.py`** — v1.16.0 seeds
   `preflight_scripts: ["scripts/preflight.py"]` into
   `substrate.config.json` (kit contract: `_default_preflight_scripts` +
   `_run_preflight_scripts`, `bootstrap.py`), and until the script exists
   every full-lane `check` run — local AND the CI substrate-gate — prints
   `NOTE — preflight script scripts/preflight.py not found — skipped`.
   The script runs this repo's real verify line (`python3 -m pytest -q` +
   `python3 tools/theme_gate.py themes`, the same invocations
   `pytest.yml`/`theme-gate.yml` run in CI) so the local ritual and the CI
   gate converge on one check list. Executes the previous session's 💡
   (`.sessions/2026-07-14-kit-upgrade-v1.16.0.md`).
2. **Make the host enabler customizations regen-proof** — the live
   `.github/workflows/auto-merge-enabler.yml` (sha256 `1a0c5ec3…ade18`) is
   kit-owned (regenerated in place on every adopt/upgrade) but carries three
   host customizations: the in-progress/drafted card-guard step, the
   4-prefix branch allowlist, and the `Head-ref:` squash-body provenance
   stamp. Every kit upgrade banks + clobbers them (v1.16.0 upgrade report
   carve-out section; restored by hand that session). Fix per the kit's own
   doctrine (template header + `_regen_kit_owned_workflow` report text:
   "move them into a separate workflow file"): branch allowlist →
   `substrate.config.json` `automerge.branch_patterns` (regen-preserved,
   quiets the `automerge-branch-drift` advisory); enabler file → regenerated
   byte-identical to the kit v1.16.0 template (future regens = no-op);
   card-guard + Head-ref stamp → new host-owned
   `.github/workflows/automerge-card-guard.yml` that reconciles arming state
   AFTER the enabler runs. Live behavior preserved: never armed (steady
   state) while an in-diff card is `in-progress`/`drafted`; only the four
   agent prefixes arm; squash auto-merge on non-draft PRs otherwise;
   squash bodies keep `Head-ref:`.

## What happened

*(in progress — close-out below at flip)*
