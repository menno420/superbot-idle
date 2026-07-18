# 2026-07-18 — docs: cross-pack vocabulary & structural-parity audit (THM-17)

> **Status:** `in-progress`

- **📊 Model:** Opus · medium · docs · theme-vocab-parity audit seat · 2026-07-18T02:07Z (`date -u`)

## What / why

Menu item **THM-17** (`planning/2026-07-16-overnight-menu.md`) is a two-part,
analysis-only audit of the theme catalog carrying two concrete findings already
in hand:

- **(a) structural-tier parity** — "`egg-farm` is the only single-tier pack —
  all others carry `tier2`+`boost2`; decide intentional vs gap."
- **(b) vocabulary collisions** — "prestige/milestone nouns overlap; enumerate
  collisions so new packs stay distinct" and produce "a naming allowlist for
  authors."

This slice executes THM-17 as a **DOCS-ONLY** audit against the 20 shipped
packs + `docs/theme-schema.md` + `schema/theme.schema.json`, and records the
result as a point-in-time audit under `docs/audits/`, matching the existing
`docs/audits/2026-07-13-fleet-cleanup-audit.md` precedent.

No engine, render, mechanic, schema, pack, or vector change — the deliverable is
one new audit record. The audit ruled finding (a) INTENTIONAL (schema permits
1–20 generators and makes `upgrades` optional; `egg-farm` is the deliberately
minimal flagship default) and enumerated finding (b), surfacing two genuine
exact cross-pack collisions in pack DATA. Per the docs-only scope those data
collisions are recorded as an owner follow-up, NOT edited here.

## Verification

- `python3 -m pytest -q` — unchanged full green (docs-only; no test added or
  removed).
- `python3 bootstrap.py check --strict` — only the born-red HOLD expected
  pre-flip; cleared on the `complete` flip.
- Confirmed diff touches only `docs/audits/`, `control/claims/`, and
  `.sessions/` — no code/test/schema/pack/vector file.

## Landing (born-red convention)

Card born RED (`in-progress`) in the first commit alongside
`control/claims/claude-theme-vocab-parity.md`; then the audit-doc commit; card
flipped `complete` as the last commit to clear the born-red HOLD so the
substrate-gate goes green and the landing workflow can merge on all-green. PR
opened DRAFT then marked ready; the worker does not merge its own PR.

## Result

The audit (`docs/audits/2026-07-18-theme-vocab-parity-THM-17.md`) recorded:

- **Finding (a) — RESOLVED: intentional.** `egg-farm` carries only `tier1` +
  `boost1`; the other 19 packs carry `tier1`+`tier2` and `boost1`+`boost2`. The
  schema (`generators` 1–20, `upgrades` optional) makes a single-tier pack fully
  valid, and `egg-farm` is the flagship minimal default. No gap — recorded as an
  intentional structural choice, with the two-tier shape noted as the de-facto
  convention for non-flagship packs.
- **Finding (b) — ENUMERATED.** An exact-string scan across every vocabulary
  slot (prestige currency, prestige action, primary currency, theme display
  name, all 180 milestone names) found exactly two cross-pack exact collisions:
  `royal jelly` (prestige currency, `ant-colony` + `apiary`) and `first full
  counter` (`owned-1` milestone, `coffee-roastery` + `ramen-stand`). Shared
  structural naming *templates* ("X empire", "X of legend", "keeper of the X",
  "first thousand X", "ten-million-X legend") are intentional parity, not
  collisions. A naming allowlist for authors was recorded.

The two exact data collisions are pack-data facts, outside a docs-only slice —
queued to the owner as a follow-up (see the audit's "Follow-up" section).

## 💡 Session idea

The two exact collisions surfaced here are the kind of drift a cheap catalog
test could pin permanently: a `theme-gate`/pytest check asserting that prestige
currency names and each milestone-slot name are unique across the whole pack
catalog (the same "enforce the eyeball property" pattern as the render golden
corpus and the proposed flavor-density floor) would red the moment a new pack
reuses a noun, turning the author naming allowlist from a doc into a contract.

## ⟲ Previous-session review

The immediately prior theme-lane slices — `theme-parity-guard` (#169, a
loader↔schema meta parity-guard) and `theme-flavor-depth` (THM-19, #159) —
progressively converted "eyeball" catalog properties into enforced contracts
(schema-constraint coverage; flavor density was flagged as the next candidate).
This slice is the analysis half of the same arc for *vocabulary* parity: it
inventories the cross-pack noun space and its two live collisions so the
unique-noun contract sketched in Session idea has a verified baseline to lock,
rather than adding enforcement blind.
