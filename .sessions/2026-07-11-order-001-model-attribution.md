# 2026-07-11 — ORDER 001: model-attribution ground truth (template + fired-card compliance)

> **Status:** `complete`

- **📊 Model:** fable-5 · idle-engine seat (ORDER 001 executor) · 2026-07-11T04:16Z–04:2xZ (`date -u`)
  — family-level name taken from this session's OWN harness/environment self-report (harness
  system context states the exact model id `claude-fable-5` → family `fable-5`); NOT copied
  from the Routines screen, per Q-0262 / inbox ORDER 001.

## 💡 Session idea

Execute inbox ORDER 001 (P3, fleet standing rule Q-0262 — model-attribution ground truth):
(1) confirm the session-card template carries a `📊 Model:` line — it does (`.sessions/README.md`
lists it among the required byte-form markers) — and strengthen it with the attribution
instructions the order specifies (family-level, harness-self-reported, never the Routines
screen); (2) this fired session's committed card (this file) carries the line, filled honestly
from its own harness self-report; (3) keep the standing rule.

## Previous-session review

previous-session review: last shipped work was catalog wave 3 (PRs #43+#44, 12 packs, 827
tests green) followed by the steady-state-hold heartbeat (PR #45); lane was deliberately
holding for new inbox ORDERs — ORDER 001 arrived via manager relay (main 6f94109, fm PR #63
provenance) and is exactly the kind of wake the hold anticipated. No unfinished work or guard
recipes pending from prior cards that touch this slice.

## What happened

1. **Claim FIRST** (control fast-lane PR #47, auto-merge armed at creation, merged on green
   2026-07-11T04:17:07Z → main 58b86ae): `control/status.md` orders line →
   `acked=000-001 done=000 claimed-by: 001 idle-engine seat 2026-07-11T04:16Z`. Bus re-read
   at HEAD after merge: no competing claim.
2. **Template confirmed + strengthened** (`.sessions/README.md`): the `📊 Model:` marker was
   already among the required byte-form markers (order item 1: confirmed present, not
   missing). Added the standing-rule instruction block: family-level name as reported by the
   fired session's OWN harness/environment (e.g. fable-5, opus-4.8, sonnet-5); never copied
   from the Routines screen (cross-surface disagreement evidenced in fm
   `docs/findings/model-matrix-2026-07.md`).
3. **This fired card carries the line** (order item 2 / done-when): `📊 Model: fable-5`,
   determined from this session's own harness system context, which states the exact model id
   `claude-fable-5` — family-level `fable-5`. Not inferred from the order text, not read off
   the Routines screen.
4. **Legacy-card audit (no history rewrites):** all 18 pre-existing `.sessions/*.md` cards
   already carry a `📊 Model:` line (all report `fable-5`) — zero cards lack it; nothing to
   flag, nothing rewritten.
5. **Verify:** `python3 -m pytest -q` → 827 passed; `python3 bootstrap.py check --strict` →
   green once this card flipped complete (the only red during the session was this card's own
   born-red badge, by design).

Standing rule kept (order item 3): every future fired session fills the line from its own
harness/environment self-report.
