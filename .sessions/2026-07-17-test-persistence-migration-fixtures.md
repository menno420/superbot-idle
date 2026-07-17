# 2026-07-17 — persistence migration fixtures: pin the structural next-bump guards on the migration registry

> **Status:** `in-progress`

- **📊 Model:** neutral builder-agent · high · tests · idle-engine seat (persistence migration coverage) · 2026-07-17T23:28Z (`date -u`)

## What / why

Menu **TEST-9** frames the save-migration suite as "only `_migrate_v1_to_v2`
tested" and asks to harden coverage so the next `STATE_VERSION` bump is
test-safe; the owner's overnight order authorizes the slice autonomously.

Reading `idle_engine/persistence.py` and its two suites first
(`tests/test_persistence.py`, `tests/test_save_vectors.py`) shows the module is
already at **100% line coverage**: the real v1→v2 migration, a synthetic
in-test v0→v1→v2 multi-step walk, future/unknown-version rejection, and the
malformed-field taxonomy are all exercised. So this slice does **not** duplicate
that — it pins the three structural invariants of the migration *registry* that
are the actual precondition for a safe next bump and are currently unasserted:

1. **Gapless registry** — `_migrate`'s loop can only reach `STATE_VERSION` from
   the oldest registered version if every intermediate version is registered in
   an unbroken single-step run; a gap silently breaks the previous format. Pin:
   `sorted(_MIGRATIONS)` is a contiguous range ending at `STATE_VERSION - 1`
   (the immediately-previous format is always migratable), with no dead entry
   registered at or above the current version.
2. **No-op identity at the current version** — a current-version document rides
   through `_migrate` unchanged and invokes NO migration (proven with a poison
   step that must never fire), so the loop-not-entered branch is a real, pinned
   behavior.
3. **Malformed-version-from-migration** — a migration that returns a doc whose
   `state_version` is the wrong JSON type is caught by `_read_version` inside
   the chain as a `FieldTypeError`, closing the one misbehaving-migration branch
   the existing `test_misbehaving_migrations_fail_loud` did not reach (it covers
   non-dict / skipped-version / forgot-to-bump, not a bad version type).

Test-only: no product code changes. All assertions read the real module
(`persistence._MIGRATIONS`, `_migrate`, `_read_version`, `STATE_VERSION`) and
match the established seeded/monkeypatch style of the file's migration section.
If a real migration bug had surfaced the order was to STOP and report — none did;
the codec is correct.

## Verification

- `python3 -m pytest -q` — full sb-free suite (recorded in the flip commit).
- Coverage of `idle_engine/persistence.py` stays 100% (structural registry
  guards, not new lines — line coverage was already complete).
- `python3 bootstrap.py check --strict`.

## Landing (born-red convention)

Card born RED (`in-progress`) in the first commit alongside
`control/claims/claude-test-persistence-migration-fixtures.md`; then the added
tests; card flipped `complete` as the last commit to clear the born-red HOLD so
substrate-gate goes green and the landing workflow can merge on all-green. PR
opened READY; the worker does not merge its own PR.

## 💡 Session idea

The gapless-registry guard turns the next `STATE_VERSION` bump into a forcing
function: bump the constant without registering `STATE_VERSION - 1`'s migration
and the structural test reds immediately, before any save ever fails in
production. A cheap follow-up when v3 lands: extend the golden corpus generator
(`tools/gen_save_vectors.py`) with a `golden_v2_migration` block so the v2→v3
step is pinned byte-exactly the same way v1→v2 already is.

## ⟲ Previous-session review

The prior tests slice (theme loader-guards, `tests/test_theme_loader_guards.py`)
closed the last sub-100% engine-core module by pinning `load_theme`'s structural
reject side. This slice applies the same accept/reject-completeness instinct one
layer over — from a module's line coverage to the migration *registry's*
structural invariants — so the guarantee "old saves keep loading after a bump"
is enforced by a test rather than by reviewer vigilance. No product code changed
by either slice.
