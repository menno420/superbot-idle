# 2026-07-14 — EAP final-day closeout (ORDER 008 re-stamp + ORDER 009 walkthrough)

> **Status:** `in-progress`

- **📊 Model:** fable-5 · medium · docs+control — EAP closeout · 2026-07-14T11:29Z–(flip pending)Z (`date -u`)

## What happened

ORDERs 008 (P2, status.md re-stamp — INC-17) + 009 (P1, EAP closeout
walkthrough) from `control/inbox.md`, claimed on main via PR #131 (squash
`914cb1d`, merged 2026-07-14T11:29:06Z) per claim doctrine. This card is the
born-red first commit of the build branch. Deliverables in flight:

1. `control/status.md` top-block overwrite-re-stamp (fresh stamp, ORDER
   006–009 dispositions PR-cited, kit line re-derived v1.15.0, claim
   released).
2. `docs/eap-closeout-walkthrough-2026-07-14.md` — owner-facing walkthrough
   (sections A–E per ORDER 009(b)), linked from repo-root `README.md`.
3. `control/outbox.md` — ≤40-line EAP close-out summary with the OWNER
   ACTIONS checklist.

(To be completed at flip with verify outputs and final PR trail.)

## 💡 Session idea

(placeholder — to be completed at flip)

## ⟲ Previous-session review

previous-session review: `.sessions/2026-07-14-improve-wave-records.md`
(PR #128 — the improvement wave's record-keeping close). Its discipline of
"records true up to source, verified at HEAD before writing" is exactly the
posture ORDER 008 demands here: that card checked every REPL verb against
`tools/play.py` at `c53eba9` before touching README; this session re-derives
the kit line from `bootstrap.py --version` (v1.15.0) instead of trusting the
frozen v1.7.1. Also inherited: its mid-flight-merge recipe (merge
origin/main pre-flip, never rebase published) and its habit of citing PR
numbers per claim rather than summarizing — the dispositions section landing
in status.md follows that beat for beat.

## Verify at flip

(pending — pytest / theme_gate / bootstrap strict outputs recorded at flip)
