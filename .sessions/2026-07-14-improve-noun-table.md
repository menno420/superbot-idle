# 2026-07-14 — improve: core-skin guard noun table by pack (FORBIDDEN_NOUNS_BY_PACK)

> **Status:** `complete`

- **📊 Model:** fable-5 · medium · tests-only refactor — core/skin guard noun provenance table · 2026-07-14T02:20Z–02:26Z (`date -u`)

## What happened

Improvement-wave slice I (owner improvement-wave directive, 2026-07-14) —
restructure `tests/test_core_skin_guard.py` around a
`FORBIDDEN_NOUNS_BY_PACK` dict, as requested by
`.sessions/2026-07-11-catalog-wave-3.md` (💡 lines 51-59): the guard's
noun regex "is now ~40 lines of hand-ordered alternation and every wave
re-litigates the same distinctive-vs-generic call in a comment"; a
per-pack data shape makes provenance mechanical and lets a test assert
every shipped pack contributes guard nouns. Test-only,
behavior-preserving; PR #123.

1. **`FORBIDDEN_NOUNS_BY_PACK: dict[str, tuple[str, ...]]`** — one entry
   per shipped pack, all 18 `themes/*.yaml` ids, in catalog-growth
   order. Nouns are plain literals (the accented pack noun is listed as
   both `séance` and `seance`, replacing the old `s[eé]ance` character
   class), `re.escape()`d and joined into the same single word-boundary
   `re.IGNORECASE` alternation as before, so boundary semantics are
   unchanged ("when" still does not trip on "hen"). The
   deliberately-EXCLUDED-as-too-generic ledger stays as the pre-existing
   comment block, verbatim — the wave-grouped exclusion comments do not
   record per-pack attribution, so promoting them into a dict would have
   meant inventing provenance (left as a follow-up, below).
2. **Ratchet test** `test_every_shipped_pack_registers_guard_nouns` —
   asserts dict keys == `{p.stem for p in themes/*.yaml}` with a
   both-directions diff in the message; a new pack is red until it
   registers nouns (an explicit empty tuple documents a deliberate
   "none" — today no pack needs one), a removed pack is red until its
   stale entry is dropped.
3. **Everything else untouched**: the three pre-existing tests
   (non-empty engine scan, no-leak scan, catches/boundary self-checks)
   keep their exact assertions.

**Noun-set equality proof** (scratch script executed the old module from
`origin/main:tests/test_core_skin_guard.py`, expanded its alternation
branches incl. `[eé]`, and diffed against the new dict union):

    old effective noun set: 226 nouns
    new effective noun set: 226 nouns
    only in old: []
    only in new: []
    EQUAL: effective noun sets are identical; every noun full-matches both regexes

**Mutation proofs** (local, uncommitted, restored after each):
appended `# polish the fresnel lens before shipping` to
`idle_engine/economy.py` → `test_engine_sources_contain_no_theme_nouns`
red with `AssertionError: theme nouns leaked into engine core:` /
`idle_engine/economy.py:112: 'fresnel'` → `git checkout` → 4 passed.
Deleted the `"ramen-stand"` dict entry →
`test_every_shipped_pack_registers_guard_nouns` red with
`AssertionError: FORBIDDEN_NOUNS_BY_PACK is out of sync with
themes/*.yaml:` / `shipped but unregistered: ['ramen-stand']` /
`registered but not shipped: []` → entry restored, equality proof
re-run → EQUAL again.

Verify: `python3 -m pytest -q` → `1377 passed, 1 skipped in 15.53s`
(baseline 1376 + exactly the one new ratchet test); `python3
bootstrap.py check --strict` → green once this card flips (pre-flip it
held only the designed born-red gate on this card).

## 💡 Session idea

The EXCLUDED-as-too-generic ledger is still a comment block: nothing
executes it, so a noun could be listed both there and in a pack's tuple
without any red. Guard recipe: promote it to an
`EXCLUDED_TOO_GENERIC: tuple[str, ...]` (flat — the wave comments don't
record per-pack attribution, so don't invent it) right above
`FORBIDDEN_NOUNS_BY_PACK` in `tests/test_core_skin_guard.py`, and add a
one-assert test that `set(EXCLUDED_TOO_GENERIC)` is disjoint from the
dict's noun union — anchor it next to
`test_every_shipped_pack_registers_guard_nouns` so the two
table-integrity checks live together. Two-list append then becomes the
whole of wave N+1's guard edit, exactly as the wave-3 card envisioned.

## ⟲ Previous-session review

previous-session review: the improve-catalog-ratchet card
(`.sessions/2026-07-14-improve-catalog-ratchet.md`, slice B of this
wave) supplied the template this slice followed end-to-end: land the
refactor green, then prove each red locally by uncommitted mutation with
the failure quoted verbatim — its "requesting cards under-scope"
observation held again here in data-shape form: the wave-3 card asked
for `dict[str, list[str]]` plus an `EXCLUDED` twin, but the exclusion
comments turned out to carry no per-pack provenance to put in a dict, so
the honest landing was the forbidden-side table plus the catalog-keys
ratchet, with the EXCLUDED twin re-scoped (💡 above) as a flat tuple
with a disjointness check instead of a by-pack mapping.
