# 2026-07-12 — catalog wave 4: coffee-roastery + arctic-outpost + candy-factory theme packs

> **Status:** `complete`

- **📊 Model:** opus-4.8 · high · feature build · catalog wave 4 (3 data-only theme packs) · 2026-07-12
  — versioned-family name (family + version) only; no build/snapshot/date suffix, no bracketed build id.

## What happened

Wave 4 of the theme catalog (governing decision D-0007: theme packs ship in
waves, data-only, zero schema changes per wave; waves 2 and 3 each added 3
packs). Three new DATA-ONLY packs skin the SAME opaque engine ids as the rest
of the catalog (primary/prestige, tier1/tier2, boost1/boost2) — identical
mechanics, three new worlds:

1. **`themes/coffee-roastery.yaml`** — beans / reserve blends; drip station +
   roasting drum; calibrated burr grinder + convection roast profile;
   *sell the shop and franchise a new roastery*.
2. **`themes/arctic-outpost.yaml`** — snowpack / aurora shards; ice-core drill +
   husky sled team; heated drill bit + seasoned lead musher;
   *pack up and chart a new expedition*.
3. **`themes/candy-factory.yaml`** — candies / sugar crystals; taffy puller +
   gumdrop line; warmed pulling arms + recalibrated sugar duster;
   *sell the recipe and open a new factory*.

Each pack fills EVERY slot the template packs fill (theme identity + embed
frame, primary+prestige currencies, tier1+tier2 generators, boost1+boost2
upgrades, a prestige track, and the FULL 6-slot labels block). Per Q-0264 /
the wave pattern (pirate-cove/ant-colony/idol-agency): NO `balance` block
(every shipped pack stays economy-neutral until the Simulator blesses a
non-neutral tuning) and NO `milestones` block. No smuggled economy numbers
beyond the shared base_rate 1/5. No engine source or schema changes.

Per-wave test flips (the documented wave playbook, data/fixture only):
- Guard pre-flight: every distinctive noun grepped against `idle_engine/` and
  `tools/theme_gate.py` — zero collisions, all guard-safe.
- `tests/test_properties.py` — hard count pin `len(THEME_PATHS) == 12` → `== 15`
  (the only count pin in tests/; `test_theme_catalog.py` uses `>= 12` + a named
  roster, and everything else globs `themes/*.yaml`).
- `tests/vectors/setup-codes.v1.json` — REGENERATED via
  `python3 tools/gen_setup_vectors.py` (its `DOC["themes"]` is derived from the
  catalog stems; valid vectors 60 → 75). Data fixture, not a doc.
- `tests/test_theme_catalog.py` — named roster grown to 15 + a per-pack
  noun-resolve test for each new pack (mirroring the wave-3 coverage).
- `tests/test_core_skin_guard.py` — each pack's distinctive nouns appended to
  `FORBIDDEN_NOUNS` + per-pack catch assertions in
  `test_guard_pattern_actually_catches_nouns`.

`docs/current-state.md` deliberately NOT touched — the pack-count doc bump is a
deferred follow-up owned by open PR #75.

Verify: `python3 tools/theme_gate.py themes` → all 15 pack(s) valid (schema v1);
`python3 -m pytest -q` → 1227 passed (up from the 1131 baseline, 0 failures).

## 💡 Session idea

The setup-code vector count (`valid = packs × feature-combos`) and the property
suite's `len(THEME_PATHS) == N` pin both move on EVERY wave, one by hand and one
by regeneration — a per-wave mechanical tax that a fat-fingered pin can desync
from the actual catalog without any pack being wrong. Guard recipe: replace the
literal `== 15` with an assertion derived from a single source of truth (e.g.
`assert len(THEME_PATHS) == len(list(THEMES_DIR.glob("*.yaml")))` is circular,
so instead pin the count in ONE place — `tools/theme_gate.py` could expose a
`CATALOG_SIZE` or the count could live in a tiny committed `themes/CATALOG`
manifest the gate cross-checks) so the next wave flips one number and every
consumer follows. Until then the two-spot flip is cheap but is real duplicated
state.

## ⟲ Previous-session review

previous-session review: the wave-3 card
(2026-07-11 pirate-cove/ant-colony/idol-agency) established the exact playbook
this slice followed — full-slot packs over opaque ids, count-pin flip, roster +
noun-resolve tests, guard noun extension — and it paid off cleanly: no schema
pinch, no engine touch, the whole flip was mechanical and green first try. The
one thing wave 3 did NOT have to do (regenerate the setup-code vectors) is now
load-bearing because the cross-language parity fixture enumerates the catalog;
this card records that the regenerate-or-red step is a permanent part of the
per-wave tax, so the next wave's builder does not rediscover it as a surprise
red.
