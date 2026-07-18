# 2026-07-18 — theme loader: reject malformed embed_color at load

> **Status:** `in-progress`

- **📊 Model:** neutral builder-agent · medium · runtime bugfix · engine-robustness seat (theme-loader embed_color guard) · 2026-07-18

## What / why

`idle_engine.load_theme` validates every schema-declared constraint it
can at load time — reference resolution (`produces`/`target`/prestige
currencies), positive `base_rate`, the `offline_return` template's
substitution token, and the `balance` block's `rate_multiplier_pct`
bounds (the last re-checked at load as explicit *defense in depth*,
theme.py comment: "the SAME schema-declared bounds the gate enforces,
re-checked at load time — an out-of-bounds pack raises here even if it
never met the gate"). `embed_color` is the ONE schema-declared *format*
constraint left out: the loader only requires a non-empty string via
`_require_str`, never the `#RRGGBB` shape the schema
(`schema/theme.schema.json`, pattern `^#[0-9A-Fa-f]{6}$`) and the render
layer (`idle_engine/render.py:embed_color_int`, regex
`#[0-9A-Fa-f]{6}\Z`) both demand.

The wrong behavior is provable: a pack with `embed_color: "red"` (or
`"#FFF"`, or `"123456"`) loads clean and returns a `Theme`, then
crashes deep at first render — `embed_color_int` raises
`ValueError: embed color must be #RRGGBB hex` from inside every view
(status/shop/prestige/achievement embeds). The loader's "fail loud on a
bad pack, with a clear where-anchored message" contract stops one field
short of the render boundary, so a malformed color surfaces as a late
render-time crash instead of a load-time rejection like every sibling
constraint.

Fix is minimal and mirrors the balance defense-in-depth pattern exactly:
a module-level `_HEX_COLOR` regex (its own copy — the loader must not
import the render module, same discipline render already follows by
keeping its own copy of `GAINS_PLACEHOLDER`) and a single check right
after `embed_color` is required, raising
`"{where}: 'embed_color' (...) must be #RRGGBB hex"`. No mechanics,
render output, schema, catalog, or pack-color change — every shipped
pack already uses `#RRGGBB`, so valid themes load and render
byte-identically; only invalid input is newly rejected earlier.

## Verification

- New regression test in `tests/test_theme.py`
  (`test_loader_rejects_malformed_embed_color`, parametrized over
  `red` / `#FFF` / `123456` / `#GGGGGG`) — RED on pre-fix main (loader
  accepts the bad color; the crash only fires later in
  `embed_color_int`), GREEN after the guard.
- `python3 -m pytest -q` — full suite green; count 1563 → 1564.
- `python3 bootstrap.py check --strict` — only the born-red HOLD
  expected (this card, until flipped `complete`).

## Landing (born-red convention)

Card born RED (`in-progress`) in the first commit with
`control/claims/claude-theme-embed-color-guard.md`; then the fix + test
commit; card flipped `complete` as the last commit to clear the HOLD so
substrate-gate goes green and the landing workflow merges on all-green.
PR opened DRAFT then READY; the worker does not merge its own PR.

## 💡 Session idea

`embed_color` is now the last of the theme block's schema-declared
constraints to gain a load-time defense-in-depth re-check. A follow-up
worth noting (not taken here to keep the fix minimal): the loader and
render each keep their own `#RRGGBB` regex and their own
`GAINS_PLACEHOLDER` literal by design — a tiny parity test pinning the
two hex patterns equal (as the placeholder copies could also use) would
catch a future drift between the loader's rejection and the render
layer's, the same way the balance bounds ↔ schema parity is test-pinned.

## ⟲ Previous-session review

The two prior slices (#163 duplicate currency/generator id guard, and
the suite-count reconcile before it) established that the loader's
"fail loud on bad packs" contract had asymmetric gaps — the dup-id fix
closed the collection-level ones. This slice closes the matching gap on
the field level: `embed_color` was the only schema-declared *format*
rule the loader trusted CI to enforce instead of re-checking itself,
even though the render layer already proves the format matters at
runtime. Same seam, same contract, one field short — now closed end to
end.
