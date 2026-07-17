# 2026-07-17 — record OA-003 done: `pytest` is now a required status check on `main`

> **Status:** `in-progress`

- **📊 Model:** neutral builder-agent · high · docs · control seat (owner-action ledger) · 2026-07-17T16:47Z (`date -u`)

## What / why

OA-003 was the last-standing owner-only branch-protection click: add `pytest`
as a REQUIRED status check on `main`, alongside the existing `substrate-gate` +
`theme-gate` contexts. Until then a PR could merge GREEN-but-not-TESTED — the
`pytest` job (`.github/workflows/pytest.yml`) ran on every PR but nothing forced
it to pass before merge, so "merge-on-green" was not the same as "merge-on-
tested". The ask stood open since PR #74 (the slice that added the `pytest`
job); it is recorded in the frozen `control/status.md` archive as a
`⚑ needs-owner` item and echoed as outstanding in `docs/current-state.md`.

The owner (menno420) reported live on 2026-07-17 that the click is done —
"I also added pytest to idle" — i.e. `pytest` is now a required status check on
`main` branch protection. This slice records that completion in the LIVE record
(`docs/current-state.md`), so the roadmap/state stops reading it as outstanding.

**Verification status:** owner-reported, NOT agent-verifiable this session.
Branch-protection settings are owner/admin-only and this seat holds no repo
admin scope; the live check could not be read from this container —
`gh` CLI is absent (`gh: command not found`) and the available GitHub MCP
toolset exposes no branch-protection / ruleset reader. So the completion is
recorded on the owner's report, with that limitation stated plainly rather than
guessed either way.

**Landing interaction (checked, no change needed):** the `pytest` workflow
produces a check-run named exactly `pytest`, so a required `pytest` context is
satisfiable. The kit-owned auto-merge enabler
(`.github/workflows/auto-merge-enabler.yml`) counts required status-check
CONTEXTS generically (it refuses to arm on zero, does not hardcode a name), so
adding a required `pytest` only strengthens the gate — it does not break the
enabler. No workflow file touched.

Docs-only: no product code changes.

## Verification

- `python3 -m pytest -q` — full sb-free suite (recorded in the record-update commit).
- `python3 bootstrap.py check --strict` (expect only the born-red HOLD).

## Landing (born-red convention)

Card born RED (`in-progress`) in the first commit alongside
`control/claims/claude-oa-003-pytest-required-recorded.md`; then the
`docs/current-state.md` record update; card flipped `complete` as the last
commit to clear the born-red HOLD so substrate-gate goes green and the landing
workflow can merge on all-green. PR opened READY; the worker does not merge its
own PR. `control/status.md` is the FROZEN archive and is NOT edited — the live
completion note lands only in `docs/current-state.md`.

## 💡 Session idea

Owner-only branch-protection clicks (the OA-00x class) are recorded on report
because agent sessions hold no admin scope and this container ships no
branch-protection reader. A cheap standing follow-up: expose a read-only
required-checks probe (a tiny `gh api .../rules/branches/main` wrapper the
enabler already uses, or a documented MCP path) so future OA-00x completions can
be live-verified instead of owner-reported — closing the "verified-needed" gap
these items carry by construction.
