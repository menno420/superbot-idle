# 2026-07-14 — improve: core-skin guard noun table by pack (FORBIDDEN_NOUNS_BY_PACK)

> **Status:** `in-progress`

- **📊 Model:** fable-5 · medium · tests-only refactor — core/skin guard noun provenance table · 2026-07-14T02:20Z– (`date -u`)

## What happened

Improvement-wave slice I (owner improvement-wave directive, 2026-07-14) —
restructure `tests/test_core_skin_guard.py` around a
`FORBIDDEN_NOUNS_BY_PACK` dict, as requested by
`.sessions/2026-07-11-catalog-wave-3.md` (💡 lines 51-59): the guard's
noun regex "is now ~40 lines of hand-ordered alternation and every wave
re-litigates the same distinctive-vs-generic call in a comment"; a
per-pack data shape makes provenance mechanical and lets a test assert
every shipped pack contributes guard nouns. Test-only,
behavior-preserving: the effective forbidden-noun set must be identical
before and after (equality proof below when complete).

(in progress — refactor, equality proof, mutation proofs, and verify to
follow)
