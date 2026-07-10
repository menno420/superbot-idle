# superbot-idle · status
updated: 2026-07-10T23:35:00Z
phase: SEEDED born-right (kit v1.7.1 adopt → 9 slots answered with real design values → render --live → mode guided → substrate-gate wired) — awaiting first coordinator boot (founding package: superbot docs/planning/round3-founding-package-games-idle-2026-07-10.md; ORDER 000 walking skeleton defined there)
health: green
kit: v1.7.1 · check: green at seed · engaged: yes
last-shipped: the seed itself (first push to empty main — the one push repository rules allow; everything after ships via READY PR → substrate-gate green → merge)
blockers: none
orders: acked= done=
⚑ needs-owner:

**OA-001 — repo settings: Allow auto-merge + required check `substrate-gate` on `main`**
- WHAT: enable *Allow auto-merge* and make the `substrate-gate` check required on `main`, so this lane lands its own green PRs per CONVENTIONS.md.
- WHERE: github.com/menno420/superbot-idle → Settings → General → Pull Requests → "Allow auto-merge"; and Settings → Rules/Branches → require status checks → `substrate-gate`.
- HOW: two toggles + one check selection; the check name appears after the first PR's CI run.
- WHY-IT-MATTERS: without the required check, auto-merge can fire before CI; without auto-merge, every green PR waits for a human or the REST fallback.
- UNBLOCKS: the seat's whole merge-on-green loop (ORDER 000 onward).
- VERIFIED-NEEDED: next PR shows "Auto-merge enabled" and lists `substrate-gate` as required.

notes: seeded 2026-07-10 by the dispatch copilot at the owner's direct instruction (live dispatch chat), on the fleet seeding recipe (fourth consumer: product-forge, sim-lab precedents). Egg farm = FIRST THEME, not the product — the contract is in README.md. The coordinator overwrites this file (never append) as every session's deliberate last step.
