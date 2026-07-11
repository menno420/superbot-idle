# 2026-07-11 — reject leading-zero version prefixes in setup codes (grammar compliance)

> **Status:** `in-progress`

- **📊 Model:** fable-5 · high · idle-engine seat (grammar-compliance fix, coordinator-assigned) · 2026-07-11T01:32Z– (`date -u`)

## What happened

(in progress) Executing the ruling on the ⚑ from
`.sessions/2026-07-11-setup-code-test-vectors.md`: the published grammar
wins — `decode_setup` must reject leading-zero version prefixes
(`IDLE01-`, `IDLE001-`, `IDLE010-`) instead of folding them into a
parsed version. Plan: tighten `provisioning._PREFIX_RE`, pin tests,
add `prefix-leading-zero-version` error vectors (regenerate-or-red),
one-line doc taxonomy clarification.

## 💡 Session idea

(to be written at close-out)

## ⟲ Previous-session review

(to be written at close-out — previous-session review)
