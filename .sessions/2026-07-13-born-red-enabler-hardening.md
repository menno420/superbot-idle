# 2026-07-13 — born-red hold hardening: enabler card-guard drafted-status + badge-variant tolerance

> **Status:** `in-progress`

- **📊 Model:** Fable-class (Claude 5 family) · fleet worker · born-red hold audit + enabler hardening · 2026-07-13T14:21Z (`date -u`)

## Scope

Make the born-red HOLD robust in this repo, least-divergent path after
investigation:

- The kit-owned `substrate-gate.yml` (v1.7.1 generation) gates a card
  ADDED by a PR via the advisory absent sentinel — an in-progress
  born-red card does NOT hold the required `substrate-gate` context red.
  The gate file is KIT-OWNED (header: "adopt/upgrade regenerates this
  file in place... hand edits are OVERWRITTEN"), so it is NOT edited
  here; the upstream fix already exists (kit v1.15.0 `--added-card`
  lane, live in superbot-games' gate @ `d6a9526`) and lands via a kit
  distribution-wave upgrade (v1.7.1 → v1.15.0), routed separately.
- What IS repo-owned is `auto-merge-enabler.yml` (HAND-INSTALLED,
  2026-07-12, PR #77 `457407c`), whose card-status guard is today the
  only live born-red hold (proven on PR #89: run 16 refused to arm on
  the in-progress head; run 17 armed only after the flip). This slice
  hardens that guard to superbot-games' current semantics
  (`.github/workflows/auto-merge-enabler.yml` @ `d6a9526`):
  1. `drafted` (the kit auto-draft state, also not-final) refuses to
     arm, same as `in-progress`;
  2. Status-badge parsing tolerates emoji/backtick prefixes
     ("✅ `complete`", "🚧 in-progress") — the old regex read a
     decorated badge as `<no Status badge>` and would have ARMED an
     in-progress-card PR.

Branch `claude/idle-born-red-enabler-hardening` · claim
`control/claims/idle-born-red-enabler-hardening.md` · born-red card
first commit, flip complete last.

## Verify

- Local gate-behavior measurement at main `e740810`: `python3
  bootstrap.py check` and `check --strict` both exit 0; with a dummy
  in-progress card, non-strict exits 0 (finding advisory) and strict
  exits 1; flipped complete, strict exits 0.
- `python3 -m pytest -q` and workflow-YAML parse checks recorded at
  close-out.
