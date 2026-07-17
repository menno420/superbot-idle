# 2026-07-17 — tests: render golden corpus across all theme packs (TEST-2)

> **Status:** `complete`

- **📊 Model:** neutral builder-agent · high · test writing · render golden-corpus seat · 2026-07-17T23:47Z (`date -u`)

## What / why

`idle_engine/render.py` is the pure render layer that turns engine state + a
theme pack into embed-shaped payloads (`status` / `shop` / `prestige` /
`achievements` views). It is the seam superbot-next's plugin renders through, and
the CORE/SKIN contract makes every player-visible noun a pack responsibility. So
a change to `render.py` OR to any theme pack can silently alter what players see
across all packs at once — and today **nothing pins the rendered output**. The
existing vector corpora (`tests/vectors/saves.v2.json`,
`tests/vectors/setup-codes.v1.json`) pin the persistence and setup-code
contracts byte-exactly with a regenerate-or-red generator + consumer test, but
there is **no cross-pack render snapshot**. A new pack (`apiary`) was just added
(19 packs total), which is exactly the kind of change that can shift rendered
output undetected.

This slice (menu **TEST-2**, under the owner's overnight full-autonomy order)
adds a render golden corpus following the repo's BLESSED regenerate-or-red vector
pattern:

- `tools/gen_render_vectors.py` renders every view for every shipped theme pack
  at a FIXED, deterministic `GameState` (fixed resources/levels/time — no
  wall-clock, no randomness) and writes `tests/vectors/render-embeds.v1.json`.
- `tests/test_render_vectors.py` is the consumer: regenerate-or-red (the
  committed file must be byte-identical to a fresh in-memory regeneration) plus
  per-pack replay (re-render each pack's views and assert equality). A drift in
  `render.py` or any pack reds the suite with a hint naming the regenerate
  command.

**TEST + TOOLING only** — no engine or product code changes. `render.py` and the
theme packs are untouched.

## Verification

- `python3 -m pytest -q` — full suite, green (including the new drift test).
- Determinism proof: a second `python3 tools/gen_render_vectors.py` followed by
  `git diff --exit-code tests/vectors/render-embeds.v1.json` yields no diff.
- `python3 bootstrap.py check --strict` (only the born-red HOLD expected).

## Landing (born-red convention)

Card born RED (`in-progress`) in the first commit alongside
`control/claims/claude-test-render-golden-corpus.md`; then the generator, test,
and corpus artifact; card flipped `complete` as the last commit to clear the
born-red HOLD so substrate-gate goes green and the landing workflow can merge on
all-green. PR opened READY (#157); the worker does not merge its own PR.

## Result

`tools/gen_render_vectors.py` renders all four views for all **19** shipped
packs at the fixed state → **76** golden embeds in
`tests/vectors/render-embeds.v1.json`. The fixed state exercises every meaningful
branch across the corpus: earned/reached/locked milestone marks (✅ / ⏳ / 🔒)
on all 19 packs, the trap-buy `requires` annotation on 18, plus offline-gain
lines and afford/lock shop marks. `python3 -m pytest -q` green (1526 passed, 1
skipped); a second regeneration + `git diff --exit-code` proved determinism (no
diff); `bootstrap.py check --strict` showed only the expected born-red HOLD.

## 💡 Session idea

The corpus captures render output at ONE fixed state. A natural follow-up is a
second fixed state — a brand-new save (all-zero, no offline gains, everything
locked) — so the corpus also pins the empty/first-launch embeds every pack shows
a new player, the other end of the render range from this mid-run state.

## ⟲ Previous-session review

The prior overnight render slice (`test-render-offline-dropline`, TEST) closed
the last branch gap in `render.py` from the INSIDE — pinning one budget-boundary
drop to 100% branch coverage. This slice is its cross-pack complement: instead of
one branch it pins the whole rendered SURFACE of all 19 packs from the OUTSIDE,
so a SKIN change (a pack noun/emoji edit) or a render composition change reds a
snapshot even where line coverage already passed. Same born-red session-gate
discipline; same regenerate-or-red vector convention as the saves/setup-code
corpora, now extended to the render layer.
