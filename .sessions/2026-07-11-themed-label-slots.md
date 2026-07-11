# 2026-07-11 — themed label slots: optional labels block (schema + gate + render + packs)

> **Status:** `complete`

- **📊 Model:** fable-5 · high · idle-engine seat (themed-label-slots builder, coordinator-assigned) · 2026-07-11T01:19Z–01:3xZ (`date -u`)

## What happened

Landed the parked render follow-up (docs/render-layer.md § neutral
scaffolding) in one build PR after a control fast-lane claim (PR #24,
`control/claims/themed-label-slots.md`, merged then removed here).

1. **Schema v1 additive `labels:` block** (schema/theme.schema.json +
   docs/theme-schema.md, parity-tested twin rows): six OPTIONAL slots —
   `offline_return` (flavor template, ≤ 256; MUST carry the one
   substitution token `{gains}` exactly once, no other braces),
   `status_title` / `shop_title` (verbatim titles, ≤ 256 = the cap),
   `shop_description` (verbatim, ≤ 1024), `level` (≤ 32, replaces the
   neutral `Lv`), `prestige_progress` (≤ 64, labels the bare progress
   numbers). Every slot optional; block optional; all budgets carry
   documented composition arithmetic (docs/theme-schema.md § labels) so
   composed output cannot bust embed caps — e.g. the offline line's
   fixed text tops out at 1024 + 2 + 249 = 1275 of the 4096 description
   cap, leaving ≥ 2821 for the substituted gains, which clamp.
2. **Gate** (tools/theme_gate.py): the semantic check the schema cannot
   express — `{gains}` exactly once (zero silently drops the gains
   display, twice is ambiguous), no unknown placeholder or stray brace
   (would leak verbatim into player-visible text). Loader
   (idle_engine/theme.py `ThemeLabels`) enforces the same — engine
   stays ground truth.
3. **Render** (idle_engine/render.py): every slot consumed when
   present via one helper (`_label_slot`), neutral scaffolding
   fallback otherwise — a pre-labels pack renders BYTE-IDENTICALLY
   (pinned). Budget policy unchanged: substituted gains clamp (numeric
   tier); themed template/label text never truncates — theme-overflow
   raises `RenderBudgetError`. Purity kept (no new runtime imports).
4. **All 6 packs filled** with coherent flavor (egg-farm: "While you
   were away, the hens kept laying: {gains}", shop "🧺 The Farm Supply
   Shed", level "Coop size"; equivalents for space-colony,
   potion-brewery, haunted-manor, deep-sea-station, dragon-hoard).
5. **Tests 216 → 240 on my base** (suite 396 on main after the
   concurrent vectors slice merged mid-flight; clean rebase — only the
   anticipated `.substrate/guard-fires.jsonl` union-merge): md↔json
   parity auto-extends; fallback path (labels stripped) and themed path
   (all six slots) both pinned; placeholder abuse red-gated at gate AND
   loader (missing/duplicate/unknown token, stray brace); every slot
   individually optional; boundary-budget pack passes; oversized slots
   red; composition swept at 10^400–10^3000 extremes (template intact,
   gains clamp with `…`; impossible-fit template raises).

Verify: `python3 -m pytest -q` → 396 passed; `python3
tools/theme_gate.py themes` → all 6 packs PASS; `python3 bootstrap.py
check --strict` green with this card flipped.

## 💡 Session idea

`labels.offline_return` is the schema's first TEMPLATE field, and its
safety rests on three coupled literals: `GAINS_PLACEHOLDER` in
idle_engine/theme.py, the mirrored `_GAINS_PLACEHOLDER` in
idle_engine/render.py (kept separate for runtime purity), and the
`"{gains}"` literal in tools/theme_gate.py. If a second template slot
ever lands (e.g. a prestige-award flavor line with `{award}`), extract
a tiny pure `idle_engine/placeholders.py` (stdlib-only, no yaml) that
all three import, and add a test pinning that every template-bearing
schema field names its tokens there. Guard recipe: grep-pin test
asserting `theme.GAINS_PLACEHOLDER == render._GAINS_PLACEHOLDER` +
gate literal, in tests/test_render.py; today the pinned themed-path
tests already break loudly if any copy drifts.

## ⟲ Previous-session review

The render-layer card (2026-07-11-render-layer.md) parked exactly this
slice and its parking note was load-bearing twice over: the slot list
here is literally its "deliberately NOT added" list, and its
composition-headroom reasoning dictated every new budget. Its second
parked item — composing upgrade `description` into the shop field —
was correctly NOT swept in here: the schema still grants that field
the full 1024, so it stays parked pending a themed shop layout with
real headroom (re-documented in docs/render-layer.md). The
catalog-growth card's stem-rule work meant filling six packs needed
zero id churn. One friction note for the next multi-worker window:
`bootstrap.py check` appends to `.substrate/guard-fires.jsonl` on
every run, so ANY two concurrent sessions conflict there — the
coordinator's union-merge instruction was needed exactly once, and it
worked exactly as predicted.
