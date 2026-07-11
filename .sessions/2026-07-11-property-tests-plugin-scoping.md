# 2026-07-11 — property/invariant test suite + plugin-adapter scoping

> **Status:** `in-progress`

- **📊 Model:** fable-5 · high · idle-engine seat (deepening builder, coordinator-assigned) · 2026-07-11T01:50Z– (`date -u`)

## What happened

(born-red — build in flight)

Claimed via `control/claims/property-tests-plugin-scoping.md` (PR #30,
control fast lane, merged 2026-07-11T01:49Z). Plan:

1. `tests/test_properties.py` — seeded stdlib-random property tests:
   tick/offline equivalence over random partitions, cross-run
   determinism for all 6 packs, monotonicity/conservation invariants,
   render-budget fuzz (extreme states × 6 packs × 3 views + a
   deliberate themed-overflow red case), setup-code corruption fuzz
   with an observed crc16 collision-rate report.
2. `docs/plugin-adapter-scoping.md` — evidence-gated: raw probes of
   superbot-next / superbot-plugin-hello for the real manifest
   contract; UNVERIFIED path if unreachable (it is — see close-out).

## 💡 Session idea

(to be written at close-out)

## ⟲ Previous-session review

(to be written at close-out)
