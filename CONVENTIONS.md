# Conventions — how work ships in superbot-idle

> **Status:** `binding` (seeded 2026-07-10)

- **Every change**: branch → READY PR (never draft) → `substrate-gate` green →
  merge. Arm auto-merge at PR creation; if arming is unavailable/declined both
  ways, REST-merge on green; **one merge attempt** — a platform denial is
  recorded verbatim, the PR parks READY+green with a ⚑, work continues.
- **Direct pushes to `main` are blocked post-seed** (repository rules) — don't
  probe.
- **Session shape**: born-red session card (`.sessions/`) is the first commit;
  flip `complete` last; overwrite `control/status.md` as the deliberate last
  step; kit enders in every card. Continuous work loop per Q-0265 (send_later
  chain = pacemaker, cron = failsafe).
- **Engine changes carry tests in the same PR.** Theme packs merge on
  theme-gate green alone.
- **Verify before push**: `python3 -m pytest -q && python3 bootstrap.py check --strict`.
- Timestamps from `date -u`; family-level model names only; no secret values.
