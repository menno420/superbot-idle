# 2026-07-11 — bounded theme multipliers: schema-bounded rate_multiplier_pct mechanism

> **Status:** `complete`

- **📊 Model:** fable-5 · high · idle-engine seat (bounded-multipliers builder, coordinator-assigned) · 2026-07-11T17:58Z–18:1xZ (`date -u`)

## What happened

Exercised the founding contract's last un-exercised clause (README
§ CORE/SKIN split, rule 2): "Balance multipliers only within
schema-declared bounds." MECHANISM only; every shipped pack stays
neutral — non-neutral values are sim-gated (Q-0264). Claim rode the
control fast lane first (PR #58, `control/claims/bounded-multipliers.md`,
merged then removed here); TEST-FIRST — the red suite (+30 tests) was
committed before any implementation.

1. **Schema v1 additive optional `balance` block** (md+json parity):
   entries bind a declared generator id to `rate_multiplier_pct`, an
   integer percent whose HARD BOUNDS 90..110 are literal
   `minimum`/`maximum` keywords in `schema/theme.schema.json` — the
   contract's "schema-declared bounds", taken literally. 100 = neutral;
   absent block/entry = neutral. Gate semantic checks (what JSON Schema
   cannot express): declared-generator reference, at most one entry per
   generator.
2. **Loader = defense in depth**: `idle_engine/theme.py` carries
   `RATE_MULTIPLIER_MIN/NEUTRAL/MAX` (schema parity test-pinned) and
   re-validates type + bounds INDEPENDENTLY of the gate — an
   out-of-bounds pack raises at load even if it never met CI.
   `ThemeGenerator.rate_multiplier_pct` rides into
   `GeneratorSpec.rate_multiplier_pct` (default 100) via
   `generator_specs()`; upgrade pricing deliberately ignores it — the
   multiplier is RATES ONLY.
3. **Engine fold extended with the same single-floor discipline**:
   `base*count*up_pct*pr_pct*ms_pct*theme_pct // 100_000_000`. The
   floor still happens ONCE per generator per second, so the rate is a
   plain integer and tick == closed-form offline stays EXACT by
   construction (rate·dt is linear in dt — partition sums cannot
   drift). Neutral is integer-identical to the previous `// 1_000_000`
   fold: `(x*100) // 10^8 == x // 10^6`, pinned across adversarial
   magnitudes, so every pre-slice output is byte-for-byte unchanged.
4. **Tests red-first** (`tests/test_theme_balance.py` + property-suite
   extension): bounds red/green at gate AND loader (89/111/0/-5 red,
   90/95/100/105/110 green; wrong types incl. bool red at both layers),
   neutral byte-identity pin, hand-computed 90%/110% theme fixtures
   driving `production_per_second`/`tick`/`offline_progress` exactly,
   random rosters now sweep `rate_multiplier_pct ∈ 90..110` through
   every equivalence/monotonicity invariant, determinism suite still
   green across the 12-pack catalog, and the catalog-neutrality pin
   (`test_no_shipped_pack_declares_a_balance_block`).
5. **Values sim-gated on record**: `docs/design/theme-balance-v0.md` —
   bounds rationale (±10% is flavor-level variance, never
   progression-defining; wider = engine-side economy change) and the
   explicit statement that any non-neutral shipped value routes through
   Q-0264 (pre-register → Simulator → value). `sim-harness.md` notes
   the harness models a neutral multiplier (simulate.py logic
   untouched); fold text refreshed in architecture.md, decisions.md
   D-0002, upgrades-prestige-v0.md, achievements-v0.md.

Tests +30 for this slice: 943 → 973 at build time, 1040 on the final
rebased tree after the concurrent buy-max-math slice (PRs #59+#60, +67
tests) merged mid-flight. Verify on that tree: `python3 -m pytest -q` →
1040 passed; `python3 bootstrap.py check --strict` green with this
flip; `python3 tools/theme_gate.py themes` → all 12 packs valid
(neutral). The two slices shared ZERO source files — buy-max's
`idle_engine/upgrades.py` + `tests/test_bulk_purchase.py` vs this
surface — and its bulk-cost math is multiplier-blind exactly as this
slice's design requires (costs price from `base_rate` alone); the only
collisions were `.substrate/guard-fires.jsonl` (usual union merge) and
adjacent-line edits in `docs/design/upgrades-prestige-v0.md` (clean
rebase).

## 💡 Session idea

The `balance` block is capped at 20 entries (one per generator), but
nothing pins the CAP to the generator cap: a future schema change
raising `generators` maxItems past 20 would silently let `balance`
under-cover the roster. Guard recipe: one line in
`tests/test_theme_balance.py` asserting
`schema.properties.balance.maxItems == schema.properties.generators.maxItems`
— pairs the two caps forever. Also worth carrying: when the buy-max
slice lands, its bulk-cost math must NOT fold `rate_multiplier_pct`
(costs are multiplier-blind by design — `build_upgrade_spec` prices
from `base_rate` alone); a one-assert test in its suite would pin that
boundary from the other side.

## ⟲ Previous-session review

The achievements card (2026-07-11-achievements-layer.md) set the exact
template this slice followed: one new fold factor, one shared floor,
neutral integer-identity as the compatibility proof, and awarding kept
at action boundaries so the constant-rate property survives — this
slice's multiplier is even simpler (spec-static, never state-driven,
so no action-boundary question arises at all). Its warning that
`tools/simulate.py` knows nothing of milestones applied here too and
was handled the cheap way while the surface was warm: a one-line
neutral-multiplier assumption note in sim-harness.md rather than a
harness change. Its A10/integer-floor lesson (word Simulator asks as
bands, not strict gates) is baked into theme-balance-v0.md's note that
±10% can flip A-criteria band edges at the extremes — the reason values
stay gated. One friction repeat: `.substrate/guard-fires.jsonl` dirtied
mid-flight again (kit appends on every check), handled with the usual
stash → rebase → pop; the kit-level `merge=union` gitattribute idea
from the ORDER 002 self-review remains the durable fix.
