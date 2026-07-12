# 2026-07-12 — ORDER 003: pytest CI on PR + push (GREEN ≠ TESTED)

> **Status:** `in-progress`

- **📊 Model:** opus-4.8 · high · idle-engine seat (ORDER 003 executor, coordinator-assigned) · 2026-07-12T~09:00Z (`date -u`)

## What happened

*(born-red — filled at close-out)*

Executing ORDER 003 (`control/inbox.md`, 2026-07-12T08:30Z, P1): the CI
gap is real — `.github/workflows/` holds only `substrate-gate.yml` +
`theme-gate.yml`, and neither runs the pytest suite, so a green PR was
never actually test-run (GREEN ≠ TESTED). Adding
`.github/workflows/pytest.yml` that runs `python3 -m pytest -q` on
`pull_request` + `push`, mirroring the `theme-gate.yml` style
(ubuntu-latest, `actions/checkout@v4`, `actions/setup-python@v5`,
`python-version: "3.x"`, `pip install --quiet pyyaml jsonschema`).

## 💡 Session idea

*(born-red — filled at close-out)*

## ⟲ Previous-session review

*(born-red — filled at close-out)*
