# 2026-07-14 — improve: current-state counts guard (doc counts vs ground truth)

> **Status:** `complete`

- **📊 Model:** fable-5 · medium · tests-only — pin docs/current-state.md count claims to ground truth · 2026-07-14T02:30Z–02:36Z (`date -u`)

## What happened

Improvement-wave slice J (owner improvement-wave directive, 2026-07-14) —
new `tests/test_current_state_counts.py` pins the machine-checkable
count claims in `docs/current-state.md` to ground truth, so the living
ledger's counts cannot rot silently between grooms. Requested twice:
`.sessions/2026-07-13-truthfix-current-state.md` (💡 lines 41-50: "a
drifted doc turns a required check red instead of waiting for a human to
notice") and `.sessions/2026-07-13-eap-night-groom.md` (💡 lines 57-67:
"the stalest lines this groom fixed were COUNTS the repo already
knows"). Tests-only; PR #125.

Scope (the eap-night-groom card's own caveat, honored) — guard ONLY the
clean counts:

1. **Pack count** — the `**Theme catalog: N packs**` bullet vs
   `len(glob("themes/*.yaml"))` (18 == 18 at HEAD, no doc true-up
   needed).
2. **Setup-vector counts** — the `(224 vectors: 90 valid … 109
   tolerance, 25 error)` parenthetical vs the `counts` dict in
   `tests/vectors/setup-codes.v1.json`; the vector file is itself pinned
   to the live codec by regenerate-or-red in `tests/test_setup_vectors.py`,
   so doc → vector file → codec is a closed chain.

The suite-size claim is deliberately UNGUARDED: it is self-referential
(adding this very test changed the collected count 1377→1379, and #124
moved it again mid-slice), so an exact pin would red on every
tests-touching PR for a doc that is groomed, not generated. Pytest
counts stay prose.

Extraction is regex anchored to the stable claim phrases, not full-prose
parsing (brittle parsing is worse than no guard): `\*\*Theme catalog:
(\d+) packs\*\*` and `\((\d+) vectors: (\d+) valid\b[^()]*?\b(\d+)
tolerance,\s+(\d+) error\b` — `[^()]*?` keeps the vector match inside
its (line-wrapped) parenthetical. Each anchor must match EXACTLY ONCE:
zero matches reds with a "re-anchor the regex in the same PR that
rewords the doc" message; 2+ reds as ambiguous. Historical lines ("15 →
18 packs", "setup vectors 75 → 90 valid") do not match. Stale counts red
with a message naming the exact doc line and the fix direction:
"re-groom that docs/current-state.md line to the ground-truth number
(counts only — source wins over the doc, so the doc moves, not the
source)".

**Mutation proofs** (local, uncommitted, restored after each): sed'd the
catalog bullet `18 packs` → `17 packs` →
`test_pack_count_claim_matches_shipped_catalog` red with
`AssertionError: docs/current-state.md claims 'Theme catalog: 17 packs'
but themes/*.yaml ships 18 — re-groom that docs/current-state.md line to
the ground-truth number (…)` / `assert 17 == 18` → `git checkout` →
2 passed. Sed'd `90 valid` → `89 valid` →
`test_setup_vector_count_claims_match_vector_file` red with
`AssertionError: docs/current-state.md setup-vector parenthetical is out
of sync with the counts dict in tests/vectors/setup-codes.v1.json
(claimed != truth: {'valid': (89, 90)}) — re-groom …` → restored →
2 passed.

Verify: `python3 -m pytest -q` → `1379 passed, 1 skipped in 15.27s`
(baseline 1377 + exactly the two new guard tests; #124 merged in
pre-flip adds its own on top in CI); `python3 bootstrap.py check
--strict` → pre-flip it held only the designed born-red gate on this
card ("This red is the designed hold, not a defect"), green once this
flip lands.

## 💡 Session idea

The doc's OTHER machine-checkable claims are still unguarded prose: the
groom header pins a main SHA (`Groomed 2026-07-13 against main
221ade1`) that goes stale every merge by definition, and the "Recently
shipped" bullets cite short merge SHAs + PR numbers that a typo would
silently corrupt. Guard recipe: not a pytest pin (staleness-by-design,
like the suite count) but a `docs-counts` ADVISORY in `bootstrap.py
check` — the eap-night-groom card already named the anchor family
(`claims-stale`-style, never exit-affecting): parse `Groomed .* against
main \`([0-9a-f]{7})\`` and nag when `git merge-base --is-ancestor`
says the SHA is >N merges behind, and verify each `PR #(\d+)
\`([0-9a-f]{7})\`` pair exists in `git log main --oneline`. Anchors:
hang it next to the existing checker family in `bootstrap.py`, reuse
this slice's exactly-once-match discipline for the header regex.

## ⟲ Previous-session review

previous-session review: the improve-noun-table card
(`.sessions/2026-07-14-improve-noun-table.md`, slice I of this wave,
PR #123) set the pattern this slice reused wholesale: a
table-vs-ground-truth ratchet (its dict keys vs `themes/*.yaml`, my doc
numbers vs `themes/*.yaml` + the vector counts dict) proven by
uncommitted mutation with the red quoted verbatim. Its sharpest habit —
asserting the guard's own anchor integrity (its
`test_every_shipped_pack_registers_guard_nouns` both-directions diff) —
translated here into the exactly-once-match rule on each regex, so this
guard fails loudly when the doc phrase it depends on is reworded instead
of silently matching nothing. Where that slice could prove noun-set
equality mechanically, a prose doc offers no such closure; the honest
equivalent was scoping DOWN (pytest counts unguarded, per the requesting
card's own caveat) rather than pinning something that reds on every
tests-touching PR.
