# 2026-07-12 — install auto-merge-enabler workflow (fm ORDER 029)

> **Status:** `in-progress`

- **📊 Model:** fable-5 · high · fleet-manager coordinator hands (ORDER 029 executor) · 2026-07-12T~23:20Z (`date -u`)

## What is about to happen

Install `.github/workflows/auto-merge-enabler.yml` (adapted from
idea-engine@8d0cd53) so agent PRs arm GitHub-native auto-merge at open,
per the owner's live directive (fleet-manager coordinator chat,
2026-07-12T23:00Z) recorded as fm inbox ORDER 029 — uniform PR-landing
workflows fleet-wide. Workflow file + session plumbing only; no engine /
theme / docs changes. With zero required checks currently configured on
main, the enabler's rules-count guard will refuse to arm (safe no-op)
until the owner wires `pytest` + `substrate-gate` as required checks.
