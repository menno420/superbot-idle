# 2026-07-16 — idle engine test coverage: defensive-guard edge cases

> **Status:** `complete`
> **Branch:** `claude/idle-test-coverage` · claim `control/claims/claude-idle-test-coverage.md`

- **📊 Model:** opus-4.8 · high · test writing — autonomous overnight project work: add sb-free unit coverage for `idle_engine/` defensive guards (negative counts/levels/balances, non-int spec fields) that had zero test coverage · session opened 2026-07-16T21:50Z (`date -u`)

**Goal:** the `idle_engine/` suite sits at 98% line coverage, but the
last 2% is exactly the defensive-guard branches that keep a corrupt
state (negative owned counts, negative upgrade levels, negative prestige
balances, non-int spec fields) from propagating silently through the
economy math. Those guards raise on purpose and are load-bearing — a
save-file round-trip that smuggles a negative should fail loud, not
compute a negative rate. Add a focused, sb-free test module that
exercises every currently-uncovered guard branch so a regression that
drops a guard turns CI red.

**Baseline at HEAD `25d34f1` (before edits):**
`python3 -m pytest -q` → `1381 passed, 1 skipped`;
`python3 -m pytest --cov=idle_engine --cov-report=term-missing` →
`TOTAL 910 stmts, 21 miss, 98%`, with the misses concentrated in
`prestige.py` (28, 30, 64, 107), `engine.py` (62), `state.py` (34),
and `upgrades.py` (245) — all raise-on-bad-input guards.
`python3 bootstrap.py check --strict` → exit 0 (pre-existing advisory
`model-line-class` warnings on older cards only, never exit-affecting).

## What happened

Read every guard in `idle_engine/` and cross-checked the existing
suites (`test_engine.py`, `test_upgrades_prestige.py`,
`test_bulk_purchase.py`, `test_achievements.py`, `test_properties.py`)
to confirm the uncovered branches were genuinely untested — not just
uncounted. The seven cold branches, all defensive guards that raise:

1. `state.GeneratorSpec.__post_init__` — `base_rate` a non-int (`bool`
   / `float`) → `TypeError` (line 34). The `< 0` twin was already
   pinned; the type twin was not.
2. `engine.production_per_second` — a negative `owned` count →
   `ValueError` before any rate is computed (line 62).
3. `prestige._require_int` — a non-int `PrestigeSpec` field →
   `TypeError` (28); a below-minimum value (`threshold=0`,
   `award_divisor=0`, `bonus_percent=-1`) → `ValueError` (30).
4. `prestige.prestige_award` — a negative measured lifetime →
   `ValueError` (64).
5. `prestige.prestige_percent` — a negative held prestige balance →
   `ValueError` (107).
6. `upgrades.upgrade_percent` — a negative stored upgrade level →
   `ValueError` (245).

Added `tests/test_engine_guards.py` — one focused module, opaque ids
only (no theme nouns, no `sb` host import), each guard asserted with
its own `pytest.raises`. Also pinned the two positive invariants that
sit next to the guards and were thin: `prestige_percent` additivity
across MULTIPLE prestige specs (the loop body with >1 spec), and that a
non-negative boundary (`0`) passes every guard rather than tripping it,
so the tests document the exact accept/reject line.

## Verify at flip

- `python3 -m pytest -q` → fully green (baseline + new tests)
- `python3 -m pytest --cov=idle_engine` → guard branches now covered
- `python3 bootstrap.py check --strict` → exit 0 (pre-flip red ONLY on
  this card's designed born-red hold; the older-card `model-line-class`
  advisories are pre-existing, untouched scope)

## 💡 Session idea

The persistence loader (`persistence.py`, 100% line) rejects negative
values on load, and these engine guards reject them at compute time —
two independent walls around the same invariant (no negative quantity
in a live `GameState`). Guard recipe: a single property test
(`tests/test_no_negative_invariant.py`) that fuzzes a `GameState` with
one injected negative field and asserts SOME layer raises before a rate
or award is produced — anchoring the "corrupt state fails loud"
contract in one place so a future refactor that moves a guard can't
quietly open a gap between the two walls.

## ⟲ Previous-session review

previous-session review: `.sessions/2026-07-15-truth-refresh.md`
(PR #141) — its baseline (`1381 passed, 1 skipped`) reproduced exactly
this session at HEAD `25d34f1`, confirming the suite count was stable
across the intervening merges (#141–#144). That card's 💡 proposed a
doc-kit-version guard (a check that turns red when a value drifts from
its source of truth); this session applies the same "guard the
invariant, don't exhort it" instinct one layer down — to the engine's
own runtime guards, which had the branches but not the tests.
