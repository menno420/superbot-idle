# superbot-idle — the idle-game ENGINE and its THEME PACKS

> **Status:** `binding` — the lane contract (seeded 2026-07-10 per superbot
> `docs/planning/round3-founding-package-games-idle-2026-07-10.md`, owner directive
> Q-0267; product design: superbot `docs/ideas/games-theme-engine-website-first-2026-07-10.md`).

One mechanical core — generators → currency → upgrades → prestige → collections,
with offline progress — skinned per Discord server by **data-only theme packs**.
The **egg farm is the first theme, not the product**: the product is the engine
plus a growing theme catalog, eventually choosable on the website **before the
bot is invited**.

## The CORE/SKIN split (non-negotiable — this repo's reason to exist)

1. The engine NEVER hard-codes theme content: every player-visible noun (names,
   flavor text, emoji, art refs, embed colors) comes from a theme pack. One found
   in engine code = bug, fix on sight.
2. Theme packs are **DATA ONLY** (`themes/<name>.yaml` against the published
   schema) — never code, never new mechanics. Balance multipliers only within
   schema-declared bounds.
3. **theme-gate**: CI validates every theme against the schema, so shipping a
   theme is merge-on-green. Keep the gate honest — a theme it passes must be safe
   to enable on a live server unreviewed.
4. Two servers on different themes run IDENTICAL mechanics: one codebase to
   balance, fix, and test, forever.

## Integrity floor

Deterministic engine code owns every outcome. Economy numbers are **sim-pinned
and pre-registered**: pacing/prestige/cost-curve parameters get a committed
design rationale in `docs/design/` BEFORE tuning; substantive balance questions
route to the fleet's Simulator via a ⚑ to the manager (Q-0264 pipeline). No
pay-to-win (Q-0039/Q-0190). **Plugin-native**: built against superbot-next's
manifest/plugin contract (read via raw; `superbot-plugin-hello` is its
exemplar); no Discord-API calls inside engine core. No secret values in this
repo, ever.

## Try it (text REPL)

`tools/play.py` is a runnable, text-only way to play the engine — it drives the
real public API and renders through the shipped `render_*` views (no new
mechanics, no economy numbers of its own):

```
python3 tools/play.py                    # default pack (egg-farm)
python3 tools/play.py --pack royal-bakery # a two-generator pack
python3 tools/play.py --list-packs        # show every shipped theme
```

In the loop: `status`, `shop`, `buy <id>`, `prestige [do]`, `offline <secs>`,
`wait <secs>`, `achievements`, `pack <id>`, `help`, `quit`. It seeds a small
starting grant of generators (`--start-count`, default 1) because the engine has
no generator-purchase verb yet — that grant lives only in the entrypoint and
changes no economy constant.

## Where to start

1. `control/inbox.md` (orders) + `control/status.md` (the live heartbeat).
2. `docs/AGENT_ORIENTATION.md` — the read path.
3. `CONVENTIONS.md` — how work ships here.
4. `themes/README.md` — what a theme pack is.
