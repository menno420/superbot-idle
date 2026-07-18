# 2026-07-18 theme-vocabulary & structural-parity audit (THM-17) — superbot-idle

> **Status:** `audit` — a point-in-time snapshot, not a binding doc. Source code
> and the live pack files win over anything below if they disagree. Written under
> the owner's overnight full-autonomy order as the designated final low-risk
> tail item; **analysis-only, no data or code changed by this slice.**

**Audit window:** 2026-07-18 ~02:00Z, local clone hard-synced to `origin/main`
@ `44cc932` (PR #169) before any check was run. Scope: menu item **THM-17**
(`planning/2026-07-16-overnight-menu.md` § "THM-17. Cross-pack vocabulary &
structural-parity audit"), which carries two concrete findings already in hand:
(a) the single-tier `egg-farm` outlier, and (b) prestige/milestone noun overlap.
Corpus: the **20 shipped packs** in `themes/*.yaml`, `docs/theme-schema.md`
(Status `binding`), and its machine twin `schema/theme.schema.json`.

The 20 packs at HEAD: `ant-colony`, `apiary`, `arctic-outpost`, `candy-factory`,
`clockwork-atelier`, `coffee-roastery`, `cyber-city`, `deep-sea-station`,
`dragon-hoard`, `egg-farm`, `forge`, `haunted-manor`, `idol-agency`,
`lighthouse-keep`, `pirate-cove`, `potion-brewery`, `ramen-stand`,
`royal-bakery`, `space-colony`, `wizard-tower`.

---

## Finding (a) — structural-tier parity → RESOLVED: intentional

**Observation (verified).** `egg-farm` is the only pack with a single generator
tier: it declares just `generators[].id: tier1` and `upgrades[].id: boost1`. The
other **19** packs each declare `tier1` **and** `tier2` generators plus `boost1`
**and** `boost2` upgrades. (Count check: `tier2`/`boost2` present in 19 packs,
absent only in `egg-farm`.)

**Ruling: intentional, not a gap.** The published schema
(`docs/theme-schema.md`, machine twin `schema/theme.schema.json`) makes this a
first-class, valid shape:

- `generators` — `required`, **1–20 entries**. One generator is valid.
- `upgrades` — **`optional`**, 1–20 entries when present. Zero or one upgrade is
  valid.

`egg-farm` is the flagship **default** pack (`themes/README.md`: "First theme:
`egg-farm.yaml` (the flagship default)"). Its deliberately minimal one-tier /
one-upgrade shape is the smallest thing the engine can be skinned into and still
be a complete, playable, gate-passing pack — exactly the property that makes it
the reference fixture (its label strings are exact-string-pinned in
`tests/test_render.py` and `tests/test_theme.py`). Nothing in the schema, the
loader, or the theme-gate requires a second tier, so `egg-farm` is not a
half-finished pack — it is the minimal exemplar.

**De-facto convention (recorded for authors).** Every *non-flagship* pack shipped
to date carries the two-tier / two-upgrade shape (`tier1`+`tier2`,
`boost1`+`boost2`). New content packs should follow that two-tier convention for
progression depth; `egg-farm`'s single tier is reserved to its role as the
minimal default and is not a template to copy. This is a documentation
convention, **not** a gate rule — the schema intentionally leaves tier count
free (1–20) so richer packs remain possible.

**No code/data action.** Finding (a) requires no change: the outlier is correct.

---

## Finding (b) — cross-pack vocabulary collisions → ENUMERATED

Method: an exact-string scan across every player-visible naming slot in all 20
packs — prestige currency name, prestige action name, primary currency name,
theme display name, and all **180** milestone names (9 slots × 20 packs).

### Exact cross-pack collisions found (2)

| Vocabulary slot | Colliding string | Packs | Notes |
|---|---|---|---|
| Prestige currency `name` | `royal jelly` | `ant-colony`, `apiary` | Both insect/hive-themed — thematically natural but a genuine cross-pack duplicate. |
| Milestone `owned-1` `name` | `first full counter` | `coffee-roastery`, `ramen-stand` | Both counter-service food packs; identical string in the same milestone slot. |

No other slot collides: prestige **action** names, **primary** currency names,
and theme **display** names are all catalog-unique; the remaining 178 milestone
names are unique.

These two are pack **data** facts, not documentation drift. Because THM-17 is
scoped analysis-only (and this slice is docs-only under the overnight order),
they are **not edited here** — see **Follow-up** below.

### Shared naming *templates* — intentional parity, NOT collisions

Many packs share a structural naming *pattern* that always resolves to a
pack-native noun, so the rendered strings never actually collide. These are the
catalog's deliberate structural-parity convention and should be preserved:

- **Milestone rung templates.** `owned-3`/`lifetime-3` "empire" endings
  (`poultry empire`, `noodle empire`, `confection empire`, `forge empire`, …);
  "X of legend" (`hoard of legend`, `honey of legend`, `iron of legend`, …);
  "keeper of the X" (`keeper of the abyss`, `keeper of the coast`, `keeper of
  the hours`, …); the `lifetime-1` "first thousand X" rung (`first thousand
  eggs`, `first thousand bowls`, `first thousand coins`, …); the `lifetime-3`
  "ten-million-X legend" rung (`ten-million-egg legend`, `ten-million-bean
  legend`, …); the `owned-2` "hundred-X …" rung (`hundred-hen farmstead`,
  `hundred-burner kitchen`, …). Each fills the same engine-derived slot with a
  world-true noun — this uniformity is what makes progression legible across the
  catalog and is a feature, not drift.
- **Shared modifiers with distinct nouns.** "golden X" appears in `egg-farm`
  (`golden eggs` / `golden clutch` / `golden dynasty`) and `ramen-stand`
  (`golden ladles` / `first golden ladle`) — shared *modifier*, distinct pack
  nouns, so no rendered collision. Likewise "starlight"/"starlit" is confined to
  `wizard-tower` (`crystallized starlight`, `first starlight`, `starlit
  reserve`); the earlier menu note about `arctic-outpost` reusing "crystallized
  starlight" was already resolved before ship — `arctic-outpost` uses `aurora
  shards`.

### Naming allowlist for authors (recorded)

For a new or edited pack to stay distinct from the catalog:

1. **Prestige currency `name` must be catalog-unique.** Currently every prestige
   currency is unique *except* `royal jelly` (`ant-colony`/`apiary`). Do not add
   a third `royal jelly`; new packs pick a fresh prestige noun.
2. **Milestone names must be catalog-unique per string.** Currently unique
   *except* `first full counter` (`coffee-roastery`/`ramen-stand`). New packs
   must not reuse an existing milestone name verbatim.
3. **Structural rung *templates* are shared on purpose** — reuse the "X empire",
   "X of legend", "keeper of the X", "first thousand X", "ten-million-X legend",
   "hundred-X …" shapes, but always with a world-native noun so the rendered
   string is unique.
4. **Prestige action names, primary currency names, and theme display names are
   fully unique today — keep them so.**

---

## Follow-up (queued to owner — not actioned in this docs-only slice)

**FUP: dedupe the two exact cross-pack vocabulary collisions.** `royal jelly`
(prestige currency in `ant-colony` + `apiary`) and `first full counter`
(`owned-1` milestone in `coffee-roastery` + `ramen-stand`) are exact duplicates
across packs. Each is a one-line data edit in a `themes/*.yaml` pack, but any
pack-data change is out of scope for this analysis-only slice and must
regenerate the render golden corpus (`tests/vectors/render-embeds.v1.json` via
`tools/gen_render_vectors.py`) as an intentional delta. Recommend a tiny data
slice that renames one side of each pair to a pack-native noun, then regenerates
the corpus. Optionally pair it with the **Session idea** below to make the
property permanent.

**Session idea (enforcement, from the session card).** A catalog-wide uniqueness
test (in `theme-gate` or pytest) asserting that prestige currency names and each
milestone name are unique across all packs would red the moment a new pack reuses
a noun — turning the author allowlist above from doc guidance into an enforced
contract, the same pattern as the render golden corpus. It would red today until
the two collisions above are deduped, so it should land *with or after* the FUP.

---

## Audit result

- **(a)** No action — `egg-farm`'s single-tier shape is intentional and
  schema-valid; the two-tier shape is the recorded convention for non-flagship
  packs.
- **(b)** Two exact cross-pack collisions enumerated (`royal jelly`, `first full
  counter`); shared naming templates ruled intentional parity; an author naming
  allowlist recorded. The two data collisions are queued to the owner as a
  follow-up, not changed here.
- **Docs canonical truth checked:** `docs/current-state.md` header correctly
  reads "Theme catalog: 20 packs"; no pack-count or vocabulary drift found in the
  binding docs (the "18 packs" mentions elsewhere are dated historical changelog
  entries, correct for their dates).
