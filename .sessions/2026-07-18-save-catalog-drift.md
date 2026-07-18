# 2026-07-18 — engine: pin save graceful-degradation across catalog drift

> **Status:** `in-progress`

- **📊 Model:** neutral builder-agent · medium · test-only robustness pin · engine-robustness seat (save × catalog drift) · 2026-07-18

## What / why

The CORE/SKIN seam promises a save is **catalog-agnostic opaque data**:
`idle_engine.persistence` serializes `GameState`'s six id-keyed mappings
(`balances`/`owned`/`upgrades`/`lifetime`/`prestige`/`milestones`)
without ever consulting a theme catalog, and the engine reads state
strictly *through the current spec list* — `production_per_second`
iterates the passed `specs` and does `state.owned.get(spec.spec_id, 0)`,
never the other way round; the render layer iterates
`theme.currencies`/`theme.generators`/`theme.upgrades`. So a save
written before a pack edit (a generator/currency/upgrade renamed or
removed) must still load and run: the ids the current catalog no longer
knows are **inert** — they produce nothing, ride through a `tick`
untouched, and never crash a render — while the recognized ids behave
exactly as if the stale ones were absent.

That degradation contract was **untested at the engine level**. The
persistence suite (`tests/test_persistence.py` § 6) only round-trips a
save *within the same theme* (`_play` builds the state from the theme's
own spec ids, so no id is ever stale). Nothing pinned what happens when
a loaded save carries ids **absent from the current catalog** — the
exact "loads cleanly across catalog changes / unknown ids dropped
safely vs crash" question. This slice pins it.

This is a **robustness pin, not a bug fix** — the current behavior is
correct; the gap was coverage. Honest value read: the theme-loader
FORMAT/reference/positivity surface is now well-covered (last two
slices), so this round moved to the save × engine seam. The pins have
teeth: a plausible future "optimization" that iterated `state.owned`
instead of the spec list — or a render layer that read state keys
directly — would silently break graceful degradation, and these tests
go red on it.

## What was added (test-only — zero production change)

New module `tests/test_persistence_catalog_drift.py`:

- `test_catalog_drift_leaves_production_and_render_intact[theme]`
  (parametrized over every `themes/*.yaml`, matching the house style of
  `test_save_load_mid_playthrough_changes_nothing`): build a realistic
  clean state (own N of each generator, accrue an hour of production,
  award milestones), inject a stale id into **every** mapping, then
  assert (a) `production_per_second` is byte-identical clean-vs-stale,
  (b) `tick` leaves every recognized-currency balance identical and
  carries the stale balance/upgrade entries through **untouched**, and
  (c) all three render views (`render_status`/`render_shop`/
  `render_achievements`) return valid embeds without raising
  (`validate_embed` runs inside each).
- `test_stale_owned_ids_produce_nothing` — a **billion** phantom
  generators in `owned` add exactly zero to production (pins that the
  rate reads specs, not state keys).
- `test_stale_save_round_trips_as_opaque_data` — `load(dump(...))`
  preserves ids absent from any catalog, proving the save codec never
  validates ids against a roster.

## Known wrinkle (documented, deliberately NOT pinned — follow-up)

`achievements.milestone_progress` for the `owned` kind is
`sum(state.owned.values())`, so a stale generator id in `owned` **does**
count toward the "total generators owned" milestone even though it
produces nothing and renders nowhere. It is the one place a stale id
leaks past the current-catalog boundary. Whether that is wrong is a
genuine design judgment (a removed generator is arguably still "owned"
in the save), and a clean fix would need `milestone_progress` to know
the current spec set — a signature/architecture change out of scope for
a test-only slice. The drift test therefore asserts render-achievements
does not *crash*, and deliberately does **not** assert its numbers are
unchanged. Flagged here as a follow-up rather than silently pinned as
correct.

## Verification

- `python3 -m pytest -q` — full suite green; count 1568 → NEW (see
  the committed `docs/current-state.md` bump; the pinned-host job is
  the sb-free count + 15).
- `python3 bootstrap.py check --strict` — only the born-red HOLD
  expected (this card, until flipped `complete`).

## Landing (born-red convention)

Card born RED (`in-progress`) in the first commit alongside
`control/claims/claude-save-catalog-drift.md`; then the test +
current-state count-bump commit; card flipped `complete` as the last
commit to clear the HOLD so substrate-gate goes green and the landing
workflow merges on all-green. PR opened DRAFT then READY; the worker
does not merge its own PR.

## 💡 Session idea

The save codec and the engine each guard their own edge of the
catalog-agnostic seam, but nothing had pinned the two together across a
catalog change. The sharpest follow-up is the `owned`-milestone wrinkle
above: decide whether phantom-owned generators should count, and if not,
thread the current spec set into `milestone_progress` so the `owned`
metric matches what production and render already do — read strictly
through the live catalog.

## ⟲ Previous-session review

The last two slices (#164 malformed `embed_color` load-time rejection,
#163 duplicate-id guard) closed the theme-loader's FORMAT/reference gaps
— the "fail loud on a bad pack" contract at the SKIN edge. This slice
turns to the other edge of the same seam: not "is the pack well-formed"
but "does a save survive the pack *changing under it*". Same CORE/SKIN
opaque-id discipline, the load-time-vs-runtime axis swapped for the
save-vs-catalog axis, and — like the embed_color follow-up noted — one
residual asymmetry (the `owned` milestone) surfaced and flagged rather
than force-fixed.
