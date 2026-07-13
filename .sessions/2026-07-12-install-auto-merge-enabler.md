# 2026-07-12 — install auto-merge-enabler workflow (fm ORDER 029)

> **Status:** `complete`

- **📊 Model:** fable-5 · high · fleet-manager coordinator hands (ORDER 029 executor) · 2026-07-12T~23:20Z–23:45Z (`date -u`)

## What happened

Installed `.github/workflows/auto-merge-enabler.yml` per the owner's live
directive (fleet-manager coordinator chat, 2026-07-12T23:00Z — uniform
PR-landing workflows fleet-wide + explicit standing permission to merge
all PRs), recorded as fm inbox ORDER 029. PR #77.

- **Source**: adapted from menno420/idea-engine
  `.github/workflows/auto-merge-enabler.yml` @ `8d0cd53e85b5f45d77c7ef2813cc168e9e5e9898`,
  all guards kept: rules-count refuse-to-arm (counts required status-check
  CONTEXTS on the base branch; zero → warn + refuse — arming with no
  required check merges instantly), do-not-automerge fresh-label re-read
  race guard, in-progress session-card skip (matches this repo's born-red
  convention — arms only once the card flips `complete` via a
  `synchronize` re-run), squash with `Head-ref:` provenance body line.
- **Host adaptations**: branch allowlist from the last ~12 PR heads
  (`claude/`, `control/`, `claim/`, `close-out/`; unprefixed heads don't
  arm — safe no-op); required-check messaging names this repo's checks
  (`pytest` + `substrate-gate`); provenance header notes the kit
  regenerate-overwrites-this-filename risk and the re-apply duty.
- **Current state**: main has ZERO required status-check contexts, so the
  enabler correctly refuses to arm (safe no-op) until the owner wires
  `pytest` + `substrate-gate` as required checks and turns "Allow
  auto-merge" ON. That same clickset also gives parked PRs #75/#76 a
  landing path.
- **Collision check**: open PRs #75 (plugin/ + docs) and #76 (themes/ +
  tests) touch no workflow files — no overlap with this install.

Local verify: `python3 -m pytest -q` → 1131 passed; `python3 bootstrap.py
check --strict --session-log <this card>` green at flip; workflow YAML
parses.

## 💡 Session idea

The refuse-to-arm guard's warning (`::warning::the base branch requires
no status-check CONTEXTS`) is only visible inside an Actions run nobody
reads once PRs flow. Guard recipe: teach `control/status.md`'s ⚑
owner-ask block (OA-003 already asks for required checks) to carry the
enabler dependency explicitly — "auto-merge-enabler installed but INERT
until OA-003 lands" — and have the next heartbeat clear it when
`gh api repos/:owner/:repo/rules/branches/main` shows nonzero
required contexts. One-line check, turns a buried CI warning into a
tracked owner-ask with a machine-verifiable done-when.

## ⟲ Previous-session review

The ORDER 003 session (2026-07-12-order-003-pytest-ci) did exactly what
this session needed it to have done: it shipped the `pytest` check-run
this enabler's clickset now points at, and its card explicitly flagged
"NOT wired as a required check — branch protection owner-only" (⚑
OA-003), which is the precise gap the refuse-to-arm guard protects
against tonight. One improvement it could have made: it stopped at
filing OA-003 without pasting the owner a ready-made clickset
(Settings-path + check names); this session's PR body/report does that —
owner-asks land faster when they're paste-ready (the fleet's Q-0263.2
instinct). Workflow improvement carried forward: uniform landing
machinery should ship WITH its repo-settings ask in the same PR body,
not as a separate follow-up.
