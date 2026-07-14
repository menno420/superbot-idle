# 2026-07-14 — improve: setup-vector drift hint (did the catalog change? + regen command)

> **Status:** `complete`

- **📊 Model:** fable-5 · medium · tooling/tests message text — setup-vector regenerate-or-red failure hint · 2026-07-14T02:04Z–02:08Z (`date -u`)

## What happened

Improvement-wave slice F (owner improvement-wave directive, 2026-07-14) —
improve the failure text in the setup-code vector machinery so a red run
tells the developer to check whether the catalog changed and how to
regenerate. Requested by `.sessions/2026-07-11-catalog-wave-2.md` (💡
lines 48-56): the old red "points at the codec ('regenerate with…') not
at the catalog". Message/tooling text only — ZERO engine or
vector-content changes; PR #120.

1. **`DRIFT_HINT` constant** in `tools/gen_setup_vectors.py` (just below
   `VECTORS_PATH`) — the generator owns the developer-facing drift text:
   names the usual cause ("Did the catalog change — a themes/*.yaml pack
   added, removed, or renamed? … the vector file is catalog-coupled by
   design") and the exact fix ("regenerate and commit the file with:
   python3 tools/gen_setup_vectors.py").
2. **Both regenerate-or-red surfaces carry it**
   (`tests/test_setup_vectors.py`): the byte-identical check (assert
   moved into `_assert_byte_identical_to_regeneration`, message =
   `DRIFT_HINT`) and `test_every_shipped_pack_has_valid_vectors` — the
   red a pack add/remove hits first, previously bare — now both
   assertions there cite `DRIFT_HINT`.
3. **Hint pinned by test** —
   `test_drift_red_names_the_catalog_question_and_the_regen_command`
   drives the helper with drifted content under
   `pytest.raises(AssertionError)` and asserts the message contains the
   catalog question, `themes/*.yaml`, and the regen command.

Verify: `python3 -m pytest -q` → `1371 passed, 1 skipped in 15.13s`
(baseline 1370 + exactly the one new test); `python3
tools/gen_setup_vectors.py` idempotent → `wrote
tests/vectors/setup-codes.v1.json: valid=90, tolerance=109, errors=25`
with `git status --porcelain` showing ONLY the two edited source files —
zero diff to the JSON; `python3 bootstrap.py check --strict` green once
this card flips (pre-flip it held the designed born-red gate).
**Mutation proof** (local, uncommitted, restored after): perturbed the
first `crc16_hex` in the committed vector file (`805e` → `8050`) →
`test_committed_vector_file_is_byte_identical_to_regeneration` went red
with `AssertionError: tests/vectors/setup-codes.v1.json drifted from the
live codec/catalog (regenerate-or-red). Did the catalog change — a
themes/*.yaml pack added, removed, or renamed? That is the usual cause:
the vector file is catalog-coupled by design. If the change is
deliberate, regenerate and commit the file with: python3
tools/gen_setup_vectors.py` (plus pytest's byte diff pointing at the
perturbed hex); `git checkout -- tests/vectors/setup-codes.v1.json` →
suite green again.

## 💡 Session idea

The generator's own red-path asserts (`_tolerance_vector`'s "does not
decode", `_error_vector`'s "decoded successfully"/wrong-class messages in
`tools/gen_setup_vectors.py`) still fail bare when run after a codec
change — the same "what probably happened?" gap this slice closed for
the test surfaces. Guard recipe: thread `DRIFT_HINT` (or a codec-facing
sibling constant) into those three `assert`/`raise AssertionError` sites
in `tools/gen_setup_vectors.py` (`_tolerance_vector`, `_error_vector`),
and pin one of them with a `pytest.raises` message-match test alongside
`test_drift_red_names_the_catalog_question_and_the_regen_command` in
`tests/test_setup_vectors.py`.

## ⟲ Previous-session review

previous-session review: the improve-catalog-ratchet card
(`.sessions/2026-07-14-improve-catalog-ratchet.md`, slice B of this same
wave) modeled the pattern this slice reused wholesale: recon the exact
red surface before editing, land the change green, then prove the red by
local uncommitted mutation with the failure quoted verbatim — its
ramen-stand milestone mutation is the direct template for this slice's
crc16 perturbation. Its anchors were again exact
(`test_pack_fills_every_egg_farm_slot` at `tests/test_theme_catalog.py`),
and its observation that requesting cards under-scope (both its
requesters asked only for milestones; labels had the identical exposure)
repeated here in miniature: the wave-2 card asked for the hint on the
byte-identical red, but `test_every_shipped_pack_has_valid_vectors` — the
red the card itself says a pack add/remove hits — was just as bare, so
this slice put the shared hint on both surfaces.
