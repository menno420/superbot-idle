# 2026-07-14 — improve: property-suite canonical serialization pins the published save format

> **Status:** `in-progress`

- **📊 Model:** fable-5 · medium · tests-only refactor — determinism suite `_canon` → published `dump_state` · 2026-07-14T02:10Z– (`date -u`)

## What happened

Improvement-wave slice G (owner improvement-wave directive, 2026-07-14) —
replace the hand-rolled canonical serialization in
`tests/test_properties.py` (`_canon`, ~line 221) with the published
`idle_engine.persistence.dump_state` API, so the determinism property
suite pins the REAL save format consumers will store. Requested by
`.sessions/2026-07-11-state-serialization.md` (💡 lines 68-76).
Tests-only — ZERO engine changes.

(in progress — close-out pending)

## 💡 Session idea

(pending)

## ⟲ Previous-session review

previous-session review: (pending)
