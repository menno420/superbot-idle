# 2026-07-13 — born-red hold hardening: enabler card-guard drafted-status + badge-variant tolerance

> **Status:** `complete`

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
- `python3 -m pytest -q` → `1260 passed, 1 skipped in 17.09s` (exit 0).
- `python3 bootstrap.py check --strict` pre-flip → exit 1, red only on
  this slice's own born-red card (designed hold; flip clears it).
- Workflow YAML parses (`yaml.safe_load`); embedded heredoc python
  compiles (`ast.parse`); regex probe: plain/backtick/emoji variants of
  `in-progress`/`drafted`/`complete` all classified correctly.

## Close-out

Shipped as PR #90 (born-red commit `8426af3`, workflow commit
`8922d89`): the repo-owned enabler card guard now refuses to arm on
`drafted` cards and on decorated Status badges, matching
superbot-games @ `d6a9526`. The gate-level born-red HOLD (kit v1.15.0
`--added-card` lane) is NOT hand-ported — the gate is KIT-OWNED; routed
instead as a kit distribution-wave upgrade request (idle kit v1.7.1 →
v1.15.0). Claim `control/claims/idle-born-red-enabler-hardening.md`
released in this flip commit. Flip written 2026-07-13T14:33Z (`date -u`).

## 💡 Session idea

`pytest` runs in CI (pytest.yml, PR #74) but is NOT a required status
context on main — the enabler's own rules read on PR #89 (run
29255821474, step 2) showed `required contexts (2):
["substrate-gate","theme-gate"]`, while the enabler header claims main
requires "the 'pytest' and 'substrate-gate' status checks". So an armed
PR with a RED pytest still auto-merges once the two required contexts go
green — GREEN ≠ TESTED is only half-closed. Guard recipe: owner adds
`pytest` to the main ruleset's required contexts (Settings → Rulesets);
until then, fix the enabler header/warning text so it stops asserting
pytest is required.

## ⟲ Previous-session review

Reviewed `2026-07-13-idle-current-state-groom.md` (PR #89) against live
evidence: its functional diagnosis was right (a born-red card does not
red the gate — the v1.7.1 added-card lane passes the advisory absent
sentinel), but both mechanism claims are contradicted by the record.
The gate does NOT lack `--strict` — all five `bootstrap.py check`
invocations in `substrate-gate.yml` @ `e740810` carry it (unchanged
since `d056609`). And auto-merge did NOT nearly land #89 before its
flip — enabler run 29255821474 (13:56:49Z, head `49753ed`) logged
"refusing to arm" on the in-progress card, and arming happened only in
run 29256299431 (14:03:35Z) after flip `105e3f6`. The guard worked as
designed; the card's near-miss framing would have sent the fix at the
wrong layer ("strict + own-card exemption" in the kit-owned gate)
instead of the kit-upgrade route that already carries it.
