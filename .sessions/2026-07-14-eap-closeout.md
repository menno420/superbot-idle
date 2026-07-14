# 2026-07-14 — EAP final-day closeout (ORDER 008 re-stamp + ORDER 009 walkthrough)

> **Status:** `complete`

- **📊 Model:** fable-5 · medium · docs+control — EAP closeout · 2026-07-14T11:29Z–2026-07-14T11:36Z (`date -u`)

## What happened

ORDERs 008 (P2, status.md re-stamp — INC-17) + 009 (P1, EAP closeout
walkthrough) from `control/inbox.md`, claimed on main via PR #131 (squash
`914cb1d`, merged 2026-07-14T11:29:06Z) per claim doctrine; served via PR
#132 (this branch). Docs + control only — zero engine/economy/test changes.

1. **ORDER 008 — `control/status.md` re-stamp**: top block overwritten per
   `control/README.md` — fresh `updated:`, kit line re-derived from the tree
   (`python3 bootstrap.py --version` → substrate-kit 1.15.0; the frozen
   v1.7.1 was the INC-40 class), `orders: acked=000-009 done=000-009` (the
   done-overwrite drops the `claimed-by:` annotation = claim release), new
   `## ORDERS 006–009 — dispositions (2026-07-14)` section citing the merged
   PR trail (006 → #106; 007 → #101–#111; true-up #112–#131), all sections
   below the top block kept unchanged. INC-17 cleared. The ⚑ needs-owner ask
   restructured to the full OWNER-ACTION field format after `check` raised
   its advisory.
2. **ORDER 009(b) — walkthrough**:
   `docs/eap-closeout-walkthrough-2026-07-14.md` (badge `owner-guidance`,
   linked from repo-root `README.md` § Where to start) — A. EAP record
   PR-cited (depth: `docs/audits/2026-07-13-fleet-cleanup-audit.md`) ·
   B. state + exact verify commands · C. OWNER ACTIONS ×5 with deep links,
   **bolded recommendations**, RISK classes, VERIFY steps · D. 5-minute
   tour · E. handoff batons.
3. **ORDER 009 done-when venue**: 24-line EAP CLOSE-OUT summary appended to
   `control/outbox.md` (11:35Z entry) carrying the OWNER ACTIONS checklist.
4. **Parked HONESTLY with citations** (ORDER 009(a)): feltness-floor
   SIM-REQUEST (filed PR #106; fm routing pending) · PRESTIGE_BONUS_PERCENT
   10→25 (behind the SIM-PINNED re-tune process ask, PR #100,
   2026-07-13T18:45Z) · timed-events + generator-purchase (owner Q-blocks
   awaiting fleet Q-numbers) · OA-003 pytest-required (owner-only click).

## Verify at flip

- `python3 -m pytest -q` → `1381 passed, 1 skipped in 18.69s`
- `python3 tools/theme_gate.py themes` → `theme-gate: all 18 pack(s) valid (schema v1)`
- `python3 bootstrap.py check --strict` → pre-flip held ONLY the designed
  born-red card gate (plus the one owner-action advisory, fixed same
  session); exit 0 required and re-verified at this flip commit.

## 💡 Session idea

INC-17 was "done= moved without evidence anyone could check": the heartbeat
said `done=000-005` while merged work sat unrecorded. The kit already parses
the orders line (`ORDERS_LINE_RE` / `ORDERS_DONE_RE`, `bootstrap.py`
~L712–L715, consumed by `check_claims`) and the `updated:` stamp
(`UPDATED_LINE_RE` ~L733, `check_status_current`/`parse_heartbeat`) — but
nothing ties a done id to EVIDENCE. Guard recipe: extend the
`ORDERS_DONE_RE` consumer so that for each id in `done=`, the heartbeat must
contain a `#<PR-number>` citation reachable from that id (the orders-line
parenthetical or a `## ORDER <id>`/dispositions section naming the id and at
least one `#\d+`), advisory-first like the owner-action-fields check;
grammar constants live in the kit's `src/engine/grammar.py` with agreement
pinned by its `tests/test_grammar.py` (the writer/enforcer no-drift pattern
this repo already relies on). That turns the INC-17 class — done-without-
citation — from an fm audit finding into a local `check` warning the same
session it happens.

## ⟲ Previous-session review

previous-session review: `.sessions/2026-07-14-improve-wave-records.md`
(PR #128 — the improvement wave's record-keeping close). Its discipline of
"records true up to source, verified at HEAD before writing" is exactly the
posture ORDER 008 demands here: that card checked every REPL verb against
`tools/play.py` at `c53eba9` before touching README; this session re-derived
the kit line from `bootstrap.py --version` (v1.15.0) instead of trusting the
frozen v1.7.1. Also inherited: its mid-flight-merge recipe (merge
origin/main pre-flip, never rebase published — checked, main had not moved)
and its habit of citing PR numbers per claim rather than summarizing — the
dispositions section landed in status.md follows that beat for beat, and its
line-anchored 💡 style is reused above (`bootstrap.py` anchors).
