# 2026-07-11 — reject leading-zero version prefixes in setup codes (grammar compliance)

> **Status:** `complete`

- **📊 Model:** fable-5 · high · idle-engine seat (grammar-compliance fix, coordinator-assigned) · 2026-07-11T01:32Z–01:4xZ (`date -u`)

## What happened

Executed the ruling on the ⚑ from
`.sessions/2026-07-11-setup-code-test-vectors.md`: the PUBLISHED GRAMMAR
WINS. `decode_setup` accepted leading-zero version prefixes —
`IDLE01-<valid v1 body>` decoded as v1, and `IDLE010-` zero-stripped
into "version 10" — while docs/provisioning.md § Grammar says
"version = decimal integer, no leading zeros". One build PR after a
control fast-lane claim (PR #26, `control/claims/fix-leading-zero-version.md`,
merged then removed here).

1. **`idle_engine/provisioning.py`** — `_PREFIX_RE` tightened from
   `IDLE([0-9]+)-` to `IDLE(0|[1-9][0-9]*)-`, so the grammar lives in
   the regex itself. Error-class ruling (taxonomy read): a zero-led
   version string is not a well-formed prefix AT ALL →
   `MalformedCodeError` ("not shaped like a setup code"), never
   `UnknownVersionError`, whose documented meaning is "valid shape,
   but a version this decoder does not speak". The single digit `0`
   carries no leading zero — it IS the integer zero — so `IDLE0-`
   stays `UnknownVersionError`, exactly as the doc field table ("any
   other value") and the published `unknown-version-0` vector already
   pinned. No behavior change for any grammar-valid code.
2. **`tests/test_provisioning.py`** (+7 tests, suite 372 → 381) —
   leading-zero prefixes (`IDLE01-`/`IDLE001-`/`IDLE00-`/`IDLE010-`/
   `IDLE042-`) around a REAL v1 body raise `MalformedCodeError` (all
   red pre-fix), `IDLE0-` pinned as `UnknownVersionError`, plus the
   `_PREFIX_RE` regex pin from the prior card's guard recipe.
3. **`tools/gen_setup_vectors.py` + regenerated
   `tests/vectors/setup-codes.v1.json`** — two new error vectors
   (`prefix-leading-zero-version`, `prefix-leading-zero-version-multi-digit`),
   errors 23 → 25; valid and tolerance vectors byte-identical
   (regenerate-or-red stays green).
4. **`docs/provisioning.md`** — one clarifying sentence under Grammar
   (zero-led string → `MalformedCodeError`; lone `0` →
   `UnknownVersionError`) and the taxonomy's `MalformedCodeError` row
   now names the leading-zero case. All pinned literals untouched.

Verify: `python3 -m pytest -q` → 381 passed; `python3 bootstrap.py
check --strict` green after this flip.

## 💡 Session idea

The prefix is now grammar-tight, but `UnknownVersionError` still fires
for arbitrarily large well-formed versions (`IDLE99999999999999-…`
parses `int()` fine). If v2 ever ships, consider a doc line bounding
the version integer (e.g. fits in a u16) so foreign decoders don't need
bignum parsing to match the reference — add it to the grammar and a
`prefix-version-overflow` vector in the same PR that defines v2.

## ⟲ Previous-session review

The test-vectors card (2026-07-11-setup-code-test-vectors.md) did this
slice's discovery work perfectly: its ⚑ named the exact seam
(`_PREFIX_RE` + `int()`), correctly left it OUT of the vector file so
neither behavior got enshrined, and its 💡 guard recipe (error vector in
`_build_errors` + pinned regex test) is precisely the shape landed here
— the grammar sentence, the regex, and the vector file now red
together, as it predicted. Its wider parked idea (version-integer
bounds) is restated above rather than silently dropped.
