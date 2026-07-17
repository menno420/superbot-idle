# Overnight Planning Menu — 2026-07-16

> **Status:** `plan`
>
> **UNGROOMED overnight autonomous brainstorm — for owner triage, not a build queue.**
> Nothing here is approved, prioritized, or scheduled. The owner vetoes, promotes,
> or re-scopes each item. Quantity is deliberate: this preserves the full option
> space in one place. Substrate kit version at synthesis: v1.16.0 (plain-text note,
> measured via `bootstrap.py --version`).

## What this is

Five READ-ONLY domain idea-generators ran overnight against `menno420/superbot-idle`
(engine/gameplay, theme packs/content, tooling/DX/CI, testing/quality/sim, and
plugin/records/process). Each produced grounded, concrete proposals with file/line
citations. This document consolidates them into one menu for owner triage.

- **96 raw proposals** generated (18 engine · 20 theme · 20 tooling · 16 testing · 22 plugin).
- **Consolidated to 91 distinct** by merging genuine cross-domain overlaps — nine source
  proposals folded into four consolidated items (coverage instrumentation, the
  determinism/golden-corpus guard, claims-lifecycle hygiene, telemetry outcome-backfill),
  each noted inline where it lands.
- **Un-prioritized for build.** The only ordering is the honest shortlist at the end.
- Each proposal keeps **Title · Pitch · Effort (S/M/L) · Risk & reversibility · Unblocks**,
  and the generators' grounded citations where present.
- Blocked items are flagged inline and collected in the **Blockers** section: owner-only,
  host-only (need the `sb`/superbot-next runtime), verdict-blocked economy numbers, and a
  policy decision. `[TUNE-BLOCKED]` = mechanism is buildable but the numbers need a fleet/owner
  economy verdict; `[HOST-BLOCKED]` = needs a live bot runtime to be meaningful.

Where a proposal was independently raised in two domains, it appears once (merged) with a
cross-reference, so the count is honest.

---

## 1. Engine & gameplay mechanics (18)

Grounded in `idle_engine/` (state, engine, upgrades, prestige, achievements, economy, render)
and `docs/design/`. Shaping facts: production is `base_rate * count * upgrade_pct * prestige_pct
* milestone_pct * theme_pct // 100_000_000`, additive within a layer, multiplicative across
layers, single floor per generator per second (`engine.py:65`); **no generator-purchase path
exists** (`state.owned` is read-only — grown nowhere, wiped by prestige; T10 pre-registered);
offline progress is **uncapped** (`engine.py:123`); prestige is single-layer, single-currency,
`isqrt` award, currency never spent (`prestige.py:96`); milestones are three fixed 3-rung ladders
granting a flat +5% global each (`economy.py:42`). Economy numbers are **SIM-PINNED** — re-tuning
needs a fresh fleet verdict (`current-state.md`).

### ENG-1. Build the generator-purchase economy path
The single largest hole: `state.owned` is read by `production_per_second`, render, and the `owned`
milestone track, but *nothing writes it* except prestige-wipe. Add `purchase_generator(s)` mirroring
the upgrade shop's geometric-cost + atomic-bulk pattern, wiring T10 (`docs/design/economy-v1.md:56`)
into a live mechanic — the "grow your fleet" core loop the game currently lacks.
· **Effort:** L · **Risk:** additive module + state writer, purely additive API, but the cost curve is `[TUNE-BLOCKED]` — land plumbing + tests now, pin numbers later. · **Unblocks:** T10, `owned` milestone rungs 2–3 (currently unreachable per `achievements-v0.md:114`), ENG-3/ENG-14/ENG-17.

### ENG-2. Cap offline progress with a pre-registered horizon
`offline_progress` (`engine.py:103`) credits `rate * elapsed` with no upper bound — a year-old save
pays a year of production. Add an integer `offline_cap_seconds` that clamps `elapsed` before crediting,
preserving closed-form/tick exactness.
· **Effort:** S (mechanism) · **Risk:** trivially reversible (one `min()`); the cap *value* is `[TUNE-BLOCKED]`; parameter can land defaulting to "uncapped" (no behavior change). · **Unblocks:** offline-efficiency tuning (ENG-11), re-engagement pacing, difficulty presets (ENG-13).

### ENG-3. Add a generator sell / refund path
Once generators are purchasable (ENG-1), players need an exit for misclicks/re-specs. Add
`sell_generator` returning a pre-registered refund fraction of the last purchase cost, integer-exact,
atomic.
· **Effort:** S · **Risk:** additive, fully reversible; refund fraction `[TUNE-BLOCKED]`; depends on ENG-1. · **Unblocks:** re-spec loops, "sell to fund prestige" strategies.

### ENG-4. Add a second prestige layer (meta-ascension)
Prestige today is one flat track (`isqrt(lifetime // divisor)` → passive `+bonus_percent`,
`prestige.py`). A second layer measuring accumulated prestige currency and awarding a rarer
meta-currency gives the genre's signature long-arc progression; the additive-percent model composes
cleanly as another `*_pct` factor.
· **Effort:** L · **Risk:** new spec type + multiplier lane + save-format bump (precedent: milestones added save v2); touches hot path + persistence; curve `[TUNE-BLOCKED]`. · **Unblocks:** endgame retention, prestige sinks (ENG-5), deeper milestone tracks.

### ENG-5. Make prestige currency spendable (prestige shop / sinks)
Prestige currency is accumulate-only — held units grant `+bonus_percent`, never spent. A prestige
shop (permanent global upgrades surviving resets like `state.milestones`) turns a passive number into
a "what do I buy this run" decision surface.
· **Effort:** M–L · **Risk:** additive persistent-state map + spec + render view, reversible; contends with the parked PRESTIGE 10→25 ask; numbers `[TUNE-BLOCKED]`. · **Unblocks:** meaningful prestige choices, offline/cost perks (ENG-12), layer-2 economy.

### ENG-6. Expand the achievement engine (per-generator & new metric tracks)
Milestones watch only three metrics × three rungs; the `owned` track deliberately has no
per-generator ladder (`achievements-v0.md:29`, citing the 25-field embed budget). Add per-generator
and per-upgrade-level tracks (render-paginated to respect the budget) plus new metrics
(prestige-count, total-spent).
· **Effort:** M · **Risk:** additive specs, reversible; render budget is the real constraint (needs pagination); thresholds `[TUNE-BLOCKED]`. · **Unblocks:** long-tail goals, milestone-reward diversity (ENG-12).

### ENG-7. Implement the timed-event system
`docs/design/timed-events-scoping.md` is a full design (piecewise-exact offline recommendation,
engine-owned numbers, theme-owned nouns) with zero code. Build the piecewise-exact event window: a
bounded production multiplier over `[start, end]`, integrated exactly through offline spans so
tick == closed-form across an event boundary.
· **Effort:** L · **Risk:** new module + delicate offline-integration (must preserve exactness across window edges); magnitudes `[TUNE-BLOCKED]`; a live scheduler is `[HOST-BLOCKED]` but the pure math is testable now. · **Unblocks:** seasonal content, re-engagement hooks, the deferred "feltness" lever.

### ENG-8. Add `time_to_afford` ETA helpers
Render shows a cost and a `+/s` rate but never "when can I afford this." A pure
`time_to_afford(state, spec, rates)` returning integer seconds (ceil-division, `None`/`inf` at rate 0)
is a few deterministic lines usable by shop/status render and tests.
· **Effort:** S · **Risk:** pure additive function, zero risk. · **Unblocks:** richer shop view, "buy next" hints, sim assertions on pacing targets T1–T2.

### ENG-9. Add prestige preview / `next_prestige_at` helpers
Players can't see the reset payoff without eyeballing lifetime totals. Add
`seconds_to_prestige_eligible(state, spec, rates)` and an award-delta preview ("reset now = +N,
wait for +1 more"). Pure, deterministic, cheap.
· **Effort:** S · **Risk:** pure additive, zero risk. · **Unblocks:** better prestige UX, sim/telemetry on reset cadence.

### ENG-10. Introduce multiplicative / synergy upgrades
Every upgrade is additive within a target (`100 + sum(effect_percent*level)`, `upgrades.py:232`).
A second upgrade *kind* that multiplies (or cross-boosts: "each owned A adds X% to B") introduces
build variety and a compounding curve additive-only stacking can't produce. Slots into the existing
per-generator `pct` fold.
· **Effort:** M · **Risk:** new `effect_kind` on `UpgradeSpec` (additive default preserves current output byte-for-byte), reversible; magnitudes `[TUNE-BLOCKED]`. · **Unblocks:** non-linear builds, synergy achievements, richer sim scenarios.

### ENG-11. Add an offline-efficiency multiplier
Offline pays 100% of online rate. A pre-registered `offline_efficiency_pct` (e.g. 50% while away) is
the genre-standard nudge toward active play; folds into `offline_progress` as one integer factor,
preserving determinism. Pairs with ENG-2.
· **Effort:** S–M · **Risk:** one factor in the closed-form path, reversible (defaults to 100 = no change); percentage `[TUNE-BLOCKED]`. · **Unblocks:** active-vs-idle balance, difficulty presets (ENG-13), feltness work.

### ENG-12. Diversify milestone/achievement rewards beyond flat +5% global
Every milestone grants the same flat `+5%` to all production (`MILESTONE_BONUS_PERCENT`,
`economy.py:55`). Add reward *kinds* — cost reduction, offline-efficiency boost, per-generator boost,
one-time currency grant — so achievements feel distinct. Reuses the existing earned-set award boundary.
· **Effort:** M · **Risk:** new reward-kind field (flat-global stays default), reversible; numbers `[TUNE-BLOCKED]`; best after ENG-6. · **Unblocks:** meaningful achievement pursuit, interaction with cost/offline systems.

### ENG-13. Add selectable difficulty-curve presets
The economy is one fixed curve (×1.15 growth, 60-s base, isqrt prestige). Parameterize `economy.py`
into named presets (casual/standard/hardcore) selectable per-save, each a pre-registered table —
variety without re-tuning the canon, and multiple curves for the sim harness.
· **Effort:** M · **Risk:** refactor builders to take a preset, reversible (standard = today's numbers); preset tables `[TUNE-BLOCKED]`. · **Unblocks:** replayability, sim coverage, seasonal/mode content.

### ENG-14. Add generator-unlock gating (progression ladder)
With purchasable generators (ENG-1), gate higher tiers behind a condition (own N of the previous tier,
or a lifetime threshold) so the fleet reveals progressively. The `owned`/`lifetime` predicates already
exist in milestone code and can be reused as unlock gates.
· **Effort:** M · **Risk:** additive gate check + render "locked" annotation (mirrors the trap-buy guard at `render.py:308`), reversible; depends on ENG-1; thresholds `[TUNE-BLOCKED]`. · **Unblocks:** paced reveal, tutorialization, T-target pacing.

### ENG-15. Add a prestige-carryover ("keep N") mechanic
`apply_prestige` wipes `balances/owned/upgrades/lifetime` unconditionally (`prestige.py:92`).
A carryover rule — keep a chosen upgrade level, or a fraction of owned generators, bought via the
prestige shop (ENG-5) — softens the reset and adds a "what do I protect" layer.
· **Effort:** M · **Risk:** changes the reset writer + save format; care around the milestone-preservation invariant; reversible as opt-in; numbers `[TUNE-BLOCKED]`. · **Unblocks:** deeper prestige strategy, synergy with ENG-4/ENG-5.

### ENG-16. Memoize the per-second rate table
`production_per_second` recomputes `upgrade_percent` per generator (inner loop over all upgrade specs)
on every call — once per tick and again per-generator inside render (`render.py:263`). A memoized
rate table cached on state-change boundaries removes redundant recomputation. Already on the roadmap.
· **Effort:** M · **Risk:** reversible (cache is transparent), but `[HOST-BLOCKED]` — `current-state.md:141` defers this until a live host exists (perf work without a caller is speculative). Worth staging the design now. · **Unblocks:** live-tick performance headroom once a runtime lands.

### ENG-17. Add buy-max / bulk purchase for generators
Upgrades already have `max_affordable_levels` + atomic `purchase_upgrades` with exact big-int bulk
cost (`upgrades.py:123`). Once generators are purchasable (ENG-1), port the same exponential-search +
bisection buy-max — the hard math is already written and tested.
· **Effort:** S (given ENG-1) · **Risk:** additive, reuses a proven algorithm, reversible; depends on ENG-1. · **Unblocks:** late-game QoL, parity between the two spend surfaces.

### ENG-18. Add a soft-cap / diminishing-returns lane on stacked multipliers
All bonuses are additive-then-multiplicative with no ceiling — prestige `+10%/unit` and milestone
`+5%` each stack linearly forever, so late-game rates run away. A pre-registered soft-cap (logarithmic
compression above a threshold, integer-exact) bounds the curve. Anti-inflation insurance as ENG-4/5/10
multiply.
· **Effort:** M · **Risk:** touches the core multiplier fold (must preserve tick/offline exactness) — higher blast radius; reversible (default = no cap); curve shape `[TUNE-BLOCKED]`, likely needs a sim first. · **Unblocks:** long-run balance, safe stacking of new multiplier layers.

---

## 2. Theme packs & content (20)

Grounded in `themes/*.yaml` (18 packs, all `schema_version: 1`, data-only), `schema/theme.schema.json`,
and `tools/theme_gate.py`. A pack skins opaque engine ids (currencies `primary`/`prestige`, generators
`tier1`/`tier2`, upgrades `boost1`/`boost2`, a `prestige` block, a `labels` block with the `{gains}`
offline template, and a 9-slot `milestones` block). All mechanics/numbers are engine-side;
`additionalProperties: false` everywhere; every string field is budgeted; `embed_color` is `#RRGGBB`.
A gate-passing pack is safe to enable live unreviewed (README Q-0266). Observed gaps: no localization;
single `embed_color` per pack (no palette/icons/audio); no gallery/preview generator; `egg-farm` is the
only single-tier pack; several `embed_color` values cluster close.

### New named theme packs (each its own proposal; all pure data, gate-reversible by deleting one file)

### THM-1. Mushroom Grotto (`mushroom-grotto`)
Damp underground grove; `primary` = spores, `prestige` = fruiting crowns; *mycelium mat* → *fungal
bloom*; prestige "let the flush go to spore." Fills an earthy/organic niche none of the fungal-adjacent
packs occupy. · **Effort:** S · **Risk:** none (data). · **Unblocks:** +1 toward Q-0266 catalog growth.

### THM-2. Apiary / Beehive (`apiary`)
Sun-warm bee yard; `primary` = honey, `prestige` = royal jelly; *worker hive* → *super frame*;
milestones on comb built and colonies swarmed; prestige "split the hive and move the queen." Needs a
gold hue distinct from egg-farm's `#F5C542`. · **Effort:** S · **Risk:** none (data). · **Unblocks:** catalog growth; a color-distinctness case for THM-16.

### THM-3. Vineyard & Winery (`vineyard`)
Terraced vines and a cool cellar; `primary` = grapes/bottles, `prestige` = vintage reserve; *trellis
row* → *press house*; prestige "lay down a legendary vintage and replant." Aging maps onto the
lifetime-earnings ladder. · **Effort:** S · **Risk:** none (data). · **Unblocks:** catalog growth.

### THM-4. Blacksmith Forge (`forge`)
Ringing smithy; `primary` = ingots, `prestige` = masterwork seals; *coal forge* → *trip-hammer*;
prestige "open a legendary forge elsewhere." Fire/metal tone diversifies the food-heavy roster.
· **Effort:** S · **Risk:** none (data). · **Unblocks:** catalog growth.

### THM-5. Steam Railway (`rail-baron`)
Growing rail network; `primary` = freight, `prestige` = golden spikes; *branch line* → *mainline
junction*; milestones on cars hauled and lines laid; prestige "survey new territory." Movement/expansion
is structurally fresh. · **Effort:** S · **Risk:** none (data). · **Unblocks:** catalog growth.

### THM-6. Coral Reef (`coral-reef`)
A living reef; `primary` = polyps, `prestige` = pearls; *coral head* → *reef shelf*; prestige "seed a
new lagoon." Organic/ecological contrast to the industrial `deep-sea-station`. · **Effort:** S ·
**Risk:** low — blue `embed_color` must dodge the existing `#4FA8D8`/`#0E7490`/`#00C2D1` cluster. ·
**Unblocks:** catalog growth; contrast/audit data.

### THM-7. Observatory (`observatory`)
Hilltop dome charting the sky; `primary` = starlight readings, `prestige` = named constellations;
*reflector scope* → *radio array*; prestige "point the dome at a new sky." `wizard-tower` already uses
"crystallized starlight" — pick non-overlapping vocabulary (feeds THM-17). · **Effort:** S · **Risk:**
low — vocab overlap to avoid. · **Unblocks:** catalog growth.

### THM-8. Tea House (`tea-house`)
Quiet mountainside tea house; `primary` = cups poured, `prestige` = ceremony scrolls; *kettle hearth* →
*terrace garden*; prestige "pass the house to a student." Calm tone adjacent to coffee-roastery but its
own. · **Effort:** S · **Risk:** none (data). · **Unblocks:** catalog growth.

### THM-9. Toy Workshop (`toy-workshop`)
Cluttered workshop of gears and clockwork toys; `primary` = toys, `prestige` = heirloom masterpieces;
*workbench* → *assembly line*; prestige "gift the workshop and start anew." Playful/whimsical vs
`clockwork-atelier`'s precision. · **Effort:** S · **Risk:** low — proximity to clockwork-atelier;
needs distinct nouns. · **Unblocks:** catalog growth.

> **Note on THM-1..9:** individually S-effort, but their shared ceiling is milestone/flavor *quality*,
> not schema mechanics. Nine authored well is a full overnight batch; a coordinator may fan them to
> parallel workers (and THM-14 turns each from S into XS).

### Schema-v2 additions (each needs a design + gate + loader twin; all share a `schema_version: 2` bump that should land once, first)

### THM-10. Multi-color palette (`palette` block)
Today one `embed_color` is reused across status/shop/prestige/achievement embeds. Add an optional
`palette` object with per-view accents, each defaulting to `embed_color` when absent — strictly
additive; every current pack renders identically. Mirrors the `labels` "absent → neutral default"
discipline. · **Effort:** M · **Risk:** medium — touches schema (v2 bump), render, `theme_gate.py`,
loader twin; reversible but multi-file. · **Unblocks:** richer per-view identity; a real reason for v2.

### THM-11. Art/icon asset refs (`art` block)
Beyond emoji, add optional validated image refs (embed thumbnail / author-icon / footer-icon). Needs a
URL-safety gate rule (allowed hosts, https-only) consistent with "safe to enable unreviewed."
· **Effort:** L · **Risk:** med-high — introduces an external-asset trust surface; must not break the
unreviewed-safe property. · **Unblocks:** visual richness. · **Blocker:** requires an asset-hosting +
URL-safety decision before authoring.

### THM-12. Sound cues (`audio` block)
Optional audio refs for events (milestone-reached, prestige). · **Effort:** M (schema) / L (delivery) ·
**Risk:** high feasibility risk. · **Unblocks:** nothing until platform confirms. · **Blocker — likely
infeasible:** Discord chat embeds cannot autoplay audio; consult `PLATFORM-LIMITS.md`; recommend
discuss-first / probable-reject. Listed for completeness.

### THM-13. Tiered / stateful flavor (`flavor_tiers`)
Milestone/prestige flavor is single-string. Add optional near/at/far variants so render can pick by
progress state; absent → today's single string. Pairs with the achievements render path.
· **Effort:** M · **Risk:** medium — schema + render-layer state plumbing, reversible. · **Unblocks:**
makes the milestone-depth pass (THM-19) much higher-impact.

### Tooling, audits & scaffolding for themes

### THM-14. Theme-authoring scaffolder (CLI/skill)
A `tools/new_theme.py` taking a slug + a few nouns, emitting a gate-passing skeleton (all required
fields, correct ids, `{gains}` token, filename-stem match) so authors fill flavor, not structure.
· **Effort:** M · **Risk:** low — new file, doesn't touch existing packs, reversible. · **Unblocks:**
turns THM-1..9 from S into XS; de-risks parallel authoring.

### THM-15. Quality linter (beyond the gate)
The gate proves validity; nothing proves quality. A `tools/theme_lint.py` (advisory) flags duplicate
emoji, milestone descriptions under a richness floor, `offline_return` missing sensory flavor, budget
headroom, and tone/vocab reuse across the catalog. · **Effort:** M · **Risk:** low — advisory, no
enforcement. · **Unblocks:** consistent quality across a fast-growing catalog; feeds THM-16/THM-17.

### THM-16. Cross-pack color-distinctness audit
Concrete finding: `embed_color` values cluster — two near-identical purples (`#6A3FB5`/`#7B3FA0`), two
pinks (`#EC5C9C`/`#E75480`), a dense brown run (`#8B5A2B`/`#6F4E37`/`#B08D57`/`#D98E32`/`#B8860B`).
Produce a ΔE/hue-separation report + recolor recommendation. · **Effort:** S · **Risk:** none —
analysis only; any recolor is a one-line data edit. · **Unblocks:** a legible picker/gallery (THM-18);
input to palette-v2 (THM-10).

### THM-17. Cross-pack vocabulary & structural-parity audit
Two concrete findings: (a) `egg-farm` is the only single-tier pack — all 17 others carry
`tier2`+`boost2`; decide intentional vs gap. (b) Prestige/milestone nouns overlap ("golden X",
"starlight") — enumerate collisions so new packs stay distinct. · **Effort:** S · **Risk:** none —
analysis only. · **Unblocks:** a structural-consistency decision; a naming allowlist for authors.

### THM-18. Theme gallery / preview doc generator
No tool renders the catalog for humans. Build `tools/gen_theme_gallery.py` emitting a `docs/` gallery
(per theme: color swatch, emoji, currencies, generators, prestige action, milestone ladder) — a
browsable menu; could also drive a shareable Artifact preview. · **Effort:** M · **Risk:** low —
generated doc, no engine impact. · **Unblocks:** whole-catalog owner review; author onboarding; QA
surface for THM-16/THM-17.

### THM-19. Milestone-flavor depth pass (retrofit)
Systematic enrichment of thinner milestone/label flavor across older packs to match the strongest
exemplars (wizard-tower, ramen-stand). Pure flavor edits within existing budgets; gate stays green.
Best after THM-15 defines the floor and with THM-13 if it lands. · **Effort:** M (per batch) ·
**Risk:** low — data-only, revertible. · **Unblocks:** uniform catalog quality; showcases in THM-18.

### THM-20. Localization scaffolding
Zero i18n today. Design a locale-overlay approach (sibling `themes/<id>.<locale>.yaml` overlays or a
`locales` block) translating only player-visible strings while ids/mechanics stay canonical; needs a
gate extension validating overlays against the base slot set and budgets. · **Effort:** L · **Risk:**
medium — new schema surface + gate + render selection. · **Unblocks:** non-English servers. ·
**Blocker:** route discuss-first — pick overlay-files vs in-pack `locales` block before building.

---

## 3. Tooling, DX & CI/CD infra (16)

Grounded in 5 workflows (substrate-gate kit-owned; pytest / theme-gate / host-main-advisory /
automerge-card-guard host-owned), `scripts/preflight.py` (the single shared check list for local ritual
+ CI gate), `tools/{play,simulate,theme_gate,gen_setup_vectors,gen_save_vectors}.py`, and
`telemetry/model-usage.jsonl` (append-only, `merge=union`). No `requirements*.txt` / `pyproject.toml` /
`Makefile` / `.pre-commit-config.yaml`; no CI caching; `python-version: "3.x"` everywhere; no coverage;
the `superbot-next` pin `9634e81` in `pytest.yml` is bumped by hand. Making any check *required* is an
owner-UI action (only `substrate-gate` is required today) — see OA-003 in Blockers.

### TOOL-1. Coverage instrumentation (line + branch) + ratchet floor  · *[merged: tooling coverage-measure + coverage-gate + testing branch-coverage]*
Add `pytest-cov` to preflight's dep trio and run `pytest --cov=idle_engine --cov=tools --cov=plugin
--cov-branch --cov-report=term --cov-report=xml`; upload `coverage.xml` as an artifact and print the
total in the job summary. **Phase 1:** no threshold — make the number visible. **Phase 2:** once a
baseline exists, add `--cov-fail-under=<baseline>` in `preflight.py` so both local `check` and
substrate-gate enforce it with zero workflow edits, ratcheting up only (the repo's catalog-ratchet
pattern, `2026-07-14-improve-catalog-ratchet.md`). Branch coverage matters because `theme.py`'s
hand-written `load_theme` has ~30 `raise ValueError` branches and `provisioning.validate_against_catalog`
has error paths no report confirms are hit. · **Effort:** S (measure) / M (gate) · **Risk:** low
additive; a floor set too high reds unrelated PRs — seed at baseline−2%; revert = drop the flag. ·
**Unblocks:** makes every "under-tested branch X" claim measurable (TEST-2, TEST-4); quantitative
"GREEN = TESTED". · **Note:** to *require* the floor is an owner click (OA-###).

### TOOL-2. pip caching across all workflows
Every job re-installs `pytest pyyaml jsonschema` cold. Add `cache: pip` to the setup-python steps (or
`actions/cache` keyed on the TOOL-5 lockfile). · **Effort:** S · **Risk:** low, transparent; leave
substrate-gate's control fast-lane (no setup-python) untouched. · **Unblocks:** faster feedback; narrows
the green-behind stall window.

### TOOL-3. Python version matrix + one real pin
`python-version: "3.x"` floats — a runner upgrade could break `pytest.yml` invisibly. Add a matrix
(`3.11`/`3.12`/`3.13`) on the sb-free `pytest` job and pin the substrate-gate/preflight interpreter to
match `substrate.config.json`. · **Effort:** M · **Risk:** low–medium; matrix multiplies minutes,
reversible by trimming. · **Unblocks:** catches version-specific breakage; documents the supported range.

### TOOL-4. Flaky-test detection lane
The engine is deterministic by charter, so any flake is a real bug. A scheduled (non-gating) job runs
`pytest -p no:randomly` twice and `pytest --count=3` (`pytest-repeat`), logging the fuzz-test RNG seeds;
a divergence fails loud. · **Effort:** M · **Risk:** low — advisory, no PR trigger. · **Unblocks:**
protects the determinism floor; surfaces seed-dependent fuzz failures a single run hides.

### TOOL-5. Automated `superbot-next` pin-bump bot
The `pytest-with-host` pin `9634e81` is bumped by hand. A scheduled workflow that, when
`host-main-advisory` is green on `main`, opens a PR rewriting only the `ref:` line + `PIN:` date —
branch→PR→gate, never pushing to main. · **Effort:** M · **Risk:** medium — the bot PR must itself pass
the gate; scope the sed to one line, gate on advisory-green; revert = disable schedule. · **Unblocks:**
stops silent pin-rot; turns a manual chore into a reviewable PR.

### TOOL-6. Centralized dependency manifest (`requirements-dev.txt`)
`pytest pyyaml jsonschema` is duplicated across `pytest.yml` (×2), `theme-gate.yml`,
`host-main-advisory.yml`, and `preflight.py`. Create `requirements-dev.txt` (already honored by
`scripts/env-setup.sh`) and point every venue at it. · **Effort:** S · **Risk:** low, drop-in,
reversible. · **Unblocks:** single source of truth for TOOL-1/TOOL-2/coverage; a hashable lockfile
target for cache keys.

### TOOL-7. Required-check parity guard (surfaces OA-003)
A checker in `preflight.py` (or a scheduled job) reads the branch ruleset via `gh api
repos/.../rules/branches/main` and warns loudly if `pytest`/`theme-gate` are not in required-contexts
— i.e. if green can merge while tests are red. It cannot *set* the requirement (owner-only) but makes
the gap visible and dated. · **Effort:** S · **Risk:** low — advisory warning. · **Unblocks:** converts
the invisible OA-003 blocker into a self-reporting reminder. · **Blocker:** the actual fix is owner-UI.

### TOOL-8. `ruff` lint + format config
No linter/formatter exists. Add `ruff` with a conservative `ruff.toml` and wire `ruff check` +
`ruff format --check` into `preflight.py` (gates both venues). Start with a curated rule set to avoid a
500-finding first run. · **Effort:** M · **Risk:** medium — first adoption may need a bulk autoformat
commit; land format-only separately from rule enforcement. · **Unblocks:** consistent style; catches
dead imports/undefined names the CORE/SKIN grep guard doesn't cover.

### TOOL-9. CORE/SKIN guard promoted to a standalone linter
The "no theme noun in engine code" rule is one pytest (`test_core_skin_guard.py`). Extract the
word-boundary grep into `tools/coreskin_lint.py` runnable outside pytest (fast pre-commit hook,
diff-scoped output) while keeping the test as the gate. The charter calls this "fix on sight."
· **Effort:** S · **Risk:** low — reuses existing logic, test stays authoritative. · **Unblocks:**
sub-second local feedback on the repo's most important invariant; feeds TOOL-12.

### TOOL-10. `actionlint` + action SHA-pinning pass
Five workflows with intricate bash (the substrate-gate card logic, the card-guard heredoc) and
unpinned `actions/*`. Add an `actionlint` job and pin third-party actions to SHAs. The kit-owned
`substrate-gate.yml` is regenerated on upgrade — lint it, don't hand-pin it. · **Effort:** S · **Risk:**
low — actionlint advisory, SHA-pinning mechanical. · **Unblocks:** prevents a shell typo in the delicate
card-gate logic; supply-chain hardening on the `contents: write` auto-merge workflows.

### TOOL-11. `Makefile` (or `justfile`) task runner
The canonical verify line plus theme-gate/play/simulate/vector-regen are bare memorized commands. A
`Makefile` with `make test|check|gate|play|sim|vectors` gives one discoverable entry surface without
touching kit or workflows. · **Effort:** S · **Risk:** low — convenience wrapper. · **Unblocks:** lower
onboarding friction; stable target names for TOOL-12.

### TOOL-12. `.pre-commit-config.yaml`
Wire the fast local checks — `ruff` (TOOL-8), CORE/SKIN linter (TOOL-9), theme-gate on changed
`themes/*.yaml`, trailing-whitespace/EOF, a "no secret-shaped literal" guard — into pre-commit.
Explicitly exclude `bootstrap.py` (vendored kit) and the append-only JSONL ledgers. · **Effort:** M ·
**Risk:** low — opt-in per developer. · **Unblocks:** shifts the whole suite left of CI; fewer red-PR
round-trips against the shared rate limit.

### TOOL-13. Session-card scaffolding helper
Every session's first commit is a born-red `.sessions/<date>-<slug>.md` card whose grammar the
substrate-gate grades hard (Status badge, `📊 Model:` line, `💡`, kit enders). A `tools/new_session_card.py`
stamping a compliant born-red card (date from `date -u`, slug arg) removes the #1 source of grammar-red
failures. · **Effort:** S · **Risk:** low — generates a file, changes no gate. · **Unblocks:** fewer
badge-less/malformed-card reds; faster session bring-up. Must mirror `.sessions/README.md` grammar exactly.

### TOOL-14. Docs link-checker
`docs/` has ~40 files with dense cross-references (reading-path, repo-navigation-map, workflow header
citations to session cards). A scheduled advisory Markdown link-checker over `docs/`, `README.md`,
`CONVENTIONS.md`, `control/` flags dead relative links and moved/renamed card references. · **Effort:**
S · **Risk:** low — advisory, allowlist external URLs. · **Unblocks:** keeps navigation docs honest as
files move.

### TOOL-15. Release / version helper (403-wall-aware)
Tag pushes, release creation, and branch deletion hit the 403 wall (queue for owner, never retry). A
`tools/prepare_release.py` computes the next version, assembles a changelog from merged session cards /
squash provenance, writes a release-notes artifact, and emits a ready-to-paste owner instruction —
everything *up to* the privileged step, then stops. · **Effort:** M · **Risk:** low — produces
artifacts + an owner queue item, attempts nothing privileged. · **Unblocks:** release-cutting becomes
one owner click. · **Blocker:** the tag push / release publish itself is owner-manual (403).

### TOOL-16. CI concurrency cancellation on superseded pushes
`pytest`, `theme-gate`, and `host-main-advisory` have no `concurrency` group, so a rapid re-push (the
rebase-to-retrigger pattern) leaves stale runs burning minutes. Add `concurrency: { group:
<wf>-${{ github.ref }}, cancel-in-progress: true }` to the PR-triggered lanes; deliberately skip the
auto-merge enabler/card-guard (they use `cancel-in-progress: false` on purpose). · **Effort:** S ·
**Risk:** low — one block per workflow; don't cancel substrate-gate mid-run if a cancel could leave the
required context pending — test the interaction. · **Unblocks:** less minute/rate-limit pressure; faster
latest-push feedback.

---

## 4. Testing, quality, correctness & simulation (15)

Grounded in 1381 collected tests (428 `def test_` bodies, heavy `parametrize`), a property/invariant
layer that is deliberately stdlib-`Random(FIXED_SEED)` with **no `hypothesis`** (an explicit repo
policy stated in three module docstrings), golden regenerate-or-red corpora
(`tests/vectors/setup-codes.v1.json` 224 vectors, `saves.v2.json`), the `tools/simulate.py` harness
(scenarios S1–S3, `--quick` 2-day vs full 14-day, criteria A1–A10, A10 v2 TREND gate), and CI that runs
the sb-free suite plus a `pytest-with-host` job pinning `superbot-next@9634e81`. No coverage, mutation,
benchmark, or full-horizon-sim job anywhere. Engine math is integer/big-int, closed-form-offline ==
looped-tick by construction.

> Coverage instrumentation (independently raised here as branch-coverage) is merged into **TOOL-1**.

### TEST-1. Exercise every `load_theme` validation branch directly
The schema tests prove the 18 valid packs load and reject bad ones, but the imperative loader
(`theme.py` ~219–430) re-validates by hand with its own `raise ValueError` ladder (duplicate balance
entry, `produces` not a declared currency, unknown label slot, non-mapping prestige). Those bespoke
messages are the runtime's real gate and only incidentally covered. Add one focused red-path test per
branch. · **Effort:** M · **Risk:** low — pure new tests. · **Unblocks:** lets schema and loader diverge
safely; catches loader-message regressions the schema can't see.

### TEST-2. Golden snapshot corpus for render output (18 packs × 4 views)
`render.py` (459 lines) is tested with inline byte-pins for `egg-farm` and budget-fuzz for all packs,
but there's no snapshot of the actual embed payloads across the catalog. Add `tools/gen_render_vectors.py`
+ `render-embeds.v1.json` following the proven regenerate-or-red pattern: dump
`render_status/shop/prestige/achievements` per pack at a fixed `GameState`, red on drift. · **Effort:**
M · **Risk:** low — mirrors a blessed pattern. · **Unblocks:** any theme-label/composition change becomes
a reviewable diff; catches silent SKIN regressions across all 18 packs at once.

### TEST-3. Mutation testing on the integer-math core
Correctness lives in tiny surfaces — `engine.production_per_second` (the `// 100_000_000` fold),
`prestige.prestige_award` (`isqrt(lifetime // divisor)`), `upgrades.upgrade_cost` (geometric big-int),
`achievements.milestone_percent`. Run `mutmut`/`cosmic-ray` scoped to those modules and drive surviving
mutants to zero. · **Effort:** M (initial) / L (killing all survivors) · **Risk:** low — offline tool,
no production change. · **Unblocks:** turns "1381 tests" into a measured assertion-quality number;
likely exposes untested boundaries (`count < 0` guard, `>=` vs `>`).

### TEST-4. Coverage-guided fuzzing of `decode_setup`
`test_properties.py` already does seeded corruption fuzzing of setup codes and asserts the taxonomy
invariant. Promote to a real fuzz harness (`atheris` or a stdlib time-boxed loop) over `_crockford_decode`
+ `decode_setup`, asserting "never crashes with an undocumented exception" and "non-canonical padding
always `MalformedCodeError`". The Crockford padding-bits check (line 174) and look-alike folding are
prime targets. · **Effort:** M · **Risk:** low — standalone harness, opt-in nightly. · **Unblocks:**
hardens the plugin's attacker-supplied trust boundary beyond the fixed 25 error vectors.

### TEST-5. Sim-batch expansion — all 18 packs, not just the reference world (ORDER 006)
`simulate.py` runs S1–S3 against a single synthetic reference world; the 18 shipped packs never flow
through the harness. Add a pack-sweep mode running each scenario against every pack's real
`base_rate`/`rate_multiplier_pct`, reporting A1–A10 per pack. · **Effort:** L · **Risk:** medium —
larger runtime + bigger committed artifact, but purely additive behind a flag. · **Unblocks:** catches a
pack whose bounded multiplier pushes it outside the pacing band; feeds real balance decisions. Directly
serves ORDER 006.

### TEST-6. Run the full 14-day simulation in CI (determinism + acceptance)
`test_simulate.py` builds one `run_report(quick=True)` (2-day smoke, "NOT meaningful" per its docstring).
The full `FULL_HORIZON_S = 14*86_400` run — the one whose A1–A10 verdict matters — never runs in CI. Add
a slow/nightly job that runs the full report, asserts byte-identical determinism across two runs, and
pins the A1–A10 PASS set. · **Effort:** M · **Risk:** low — new slow job. · **Unblocks:** guards the
SIM-PINNED economy verdict; makes the A10 TREND gate a live check. Serves ORDER 006.

### TEST-7. Hypothesis property suite for tick/offline equivalence & monotonicity
The most load-bearing invariant — summed one-second ticks == closed-form `offline_progress`, exactly —
is checked only over fixed seeds. Hypothesis with shrinking would search rosters/spans/multiplier stacks
adversarially and produce minimal counterexamples. · **Effort:** M · **Risk:** medium — adds a dependency
the repo deliberately refused; reversible but a policy change (see Blockers: no-hypothesis policy). Could
live behind an optional extra. · **Unblocks:** deeper search for drift and multiplier-fold edges than
fixed seeds reach.

### TEST-8. Hypothesis (or extended seeded) properties for the prestige/award curve
`prestige_award = isqrt(lifetime // divisor)` claims monotonicity and strong diminishing returns;
`apply_prestige` claims "a reset never increases any run balance" and preserves other prestige balances.
Property-test award monotonicity, the `threshold >= award_divisor` invariant, and reset-wipe completeness.
Same policy caveat as TEST-7 if hypothesis-based; otherwise extend the seeded sweep. · **Effort:** S
(seeded) / M (hypothesis) · **Risk:** low / medium. · **Unblocks:** locks the prestige headline math,
not just spot examples.

### TEST-9. Persistence migration regression fixtures (forward chain + downgrade rejection)
`persistence._migrate` walks a version chain but only `_migrate_v1_to_v2` exists; tests use a synthetic
v0→v1 to exercise walking, and downgrade must raise `UnknownVersionError`. Add a frozen fixture corpus:
real v1 → exact v2, v0-synthetic chained migration, a future-version doc rejected, and the `FieldSetError`
path. · **Effort:** S · **Risk:** low — new fixtures only. · **Unblocks:** makes the next `STATE_VERSION`
bump safe; the "migration in the same PR" policy becomes test-enforced.

### TEST-10. De-gate the 15 manifest-contract tests with a stub `sb` (host-blocked today)
`plugin/tests/test_manifest.py` opens with `pytest.importorskip("sb.spec.manifest")`, so locally it
skips — two live-boot bug classes already slipped through. Options: (a) commit a minimal in-repo
`sb.spec.*` stub so shape assertions run sb-free, or (b) contract tests asserting the manifest against a
committed golden JSON snapshot needing no host. · **Effort:** M · **Risk:** medium — a stub can drift
from the real host contract; golden-snapshot is safer. · **Unblocks:** manifest regressions caught in the
fast job. · **Blocker:** full validation needs a live host; the stub/snapshot route is the sb-free unblock.

### TEST-11. `play.py` REPL / `main()` end-to-end coverage
`tools/play.py` (527 lines) has strong `dispatch()` unit coverage, but `main()` (the argparse surface +
the `input()` REPL loop ~506 + `QuitGame` handling + `_build_session`) is essentially untested. Drive
`main(argv=...)` with a monkeypatched `input` feeding a scripted session (buy, offline, save, load, quit)
and assert the transcript + exit code. · **Effort:** M · **Risk:** low — new tests. · **Unblocks:**
protects the CONVENTIONS-blessed local verify entrypoint from arg-parsing and loop regressions.

### TEST-12. Performance / benchmark guards on the big-int hot paths
No timing guard exists. `upgrade_cost` computes `growth_num**level` in exact big-int — superlinear at
high levels. Add `pytest-benchmark` (or a wall-clock budget assert) for `upgrade_cost` at level 10k,
`offline_progress` over a 10-year span (closed-form must stay O(1) vs the span), and full-catalog
`render_status`. · **Effort:** M · **Risk:** low — opt-in / soft-gated to avoid CI flakiness. ·
**Unblocks:** locks the "closed-form offline is span-independent" performance claim, not just its numeric
equality.

### TEST-13. Byte-determinism guard — regenerate-and-diff + pinned trajectory golden  · *[merged: tooling reproducibility-CI + testing cross-run-determinism-golden]*
Two complementary guards for the integer-exact, no-float-drift guarantee. (a) A CI job that regenerates
`tests/vectors/{saves.v2,setup-codes.v1}.json` (and `docs/design/sim-results-*.json` vs a fresh
`simulate.py --quick`) in-CI and `git diff --exit-code`s them — drift means a generator or the engine
changed output without the committed corpus updating. (b) A new corpus running a fixed scripted
playthrough per pack and pinning a SHA-256 of the concatenated `dump_state` outputs — the strongest
statement of determinism. · **Effort:** M · **Risk:** low — read-only diff checks + one golden file, no
writes to main. · **Unblocks:** any accidental float introduction or dict-ordering change reds instantly;
guards goldens at the artifact level.

### TEST-14. Differential test: independent second decoder for the setup-code grammar
`test_setup_vectors.py` already recomputes CRC intermediates independently (a partial differential check).
Extend to a full independent reference decoder (~40 lines, no `provisioning` imports) and assert it agrees
with `decode_setup` across all 90 valid + 109 tolerance vectors plus fuzzed inputs — the parity a foreign
implementation (the websites-lane encoder) must achieve. · **Effort:** M · **Risk:** low — test-only. ·
**Unblocks:** proves the published grammar is self-sufficient (a foreign impl can be written from the doc
alone).

### TEST-15. Adversarial render-budget fuzz across all packs + `labels`-overflow matrix
`test_render.py` proves themed-text overflow raises for hand-crafted broken packs and budget-fuzzes
extreme states, but only per-slot in isolation. Add a matrix that, per pack, pushes every optional
`labels` slot to its exact budget boundary simultaneously and asserts clean render or `RenderBudgetError`
— never silent truncation. The `SHOP_FLAVOR_LIMIT = 768` composition (768 + 139 + 116 = 1024) is a
specific boundary. · **Effort:** M · **Risk:** low — test-only. · **Unblocks:** locks the two-tier budget
policy against every pack's real label set at once.

---

## 5. Plugin, records, docs & process (20)

Scope: `plugin/`, `docs/`, `control/`, `telemetry/`, `.sessions/`. Docs/records/plugin-shell only — no
engine-math (verdict-owned, out of domain). Key facts: `control/status.md` line 5 reads `kit: v1.15.0`
while the tree is v1.16.0 (live drift — see Blockers); `docs/ideas/` has an elaborate lifecycle +
frontmatter contract but zero idea files; `docs/` has no index/README; `telemetry/model-usage.jsonl` has
37 rows with every `outcome.*`/`tokens_out` field `null`; 60+ session cards with no rollup since the
2026-07-11 retro snapshots; the plugin adapter is a thin `SubsystemManifest` shell whose binding host
contract lives out-of-repo (superbot-next `docs/game-plugin-contract.md @ d3dba9b`).

### Plugin / host-integration

### PLG-A1. In-repo host-contract mirror doc (`plugin/HOST-CONTRACT.md`)
The binding contract is a superbot-next file pinned `@ d3dba9b`, referenced by URL only. A dated,
quote-pinned local mirror of the four consumed seams (entry-point group `sb.plugins`; `@handler/@panel`
+ `ENSURE_REFS`; v1 facets; pin/hash lifecycle) makes it readable without leaving the repo and gives
drift a local anchor. · **Effort:** M · **Risk:** low — docs-only, additive; risk the mirror itself
drifts (mitigate with a "verified-against `d3dba9b`" stamp, as `plugin-adapter-scoping.md` does). ·
**Unblocks:** drift checks (PLG-A3), onboarding, any host-wiring session.

### PLG-A2. Runnable integration example (`plugin/examples/host_wiring_demo.py`)
`render_forward.py` is sb-free and typed against `IdleRenderState`, but nothing demonstrates the full
"host loads GameState → builds IdleRenderState → calls forwarder → gets embed dict" path. A small
stdlib-only script (mirroring `test_render_forward.py`) would be executable documentation. · **Effort:**
S · **Risk:** low — sb-free, non-gated; exercises the real forwarders so it can't silently rot. ·
**Unblocks:** faster host-side wiring; a template for future facet demos.

### PLG-A3. Manifest-surface freshness assertion (host-side test enrichment)
`test_manifest.py` pins the current surface (4 commands, 1 panel, 4 settings, 2 events, 1 capability).
Any surface change re-hashes the host's `plugins.lock.json` pin — documented in prose but not asserted.
A test snapshotting the full declared facet set into one comparable "surface fingerprint" makes "you
changed the pinned surface" a loud, deliberate failure. · **Effort:** S · **Risk:** low — test-only. ·
**Unblocks:** safe manifest evolution. · **Blocker:** host-only — asserts against `sb`, runs only in the
`pytest-with-host` job.

### PLG-A4. Documented manifest-surface roadmap (which v1 facets are deliberately unused)
The manifest declares commands/panels/settings/events/capabilities and refuses host-owned
stores/data_invariants/wizard_sections, but no doc states which in-facet surface is intentionally left on
the table. A short "declared vs deliberately-deferred surface" ledger prevents a future session
speculatively "enriching" the manifest (a D-0006 evidence-gating violation). · **Effort:** S · **Risk:**
low — docs-only. · **Unblocks:** keeps manifest growth evidence-gated; gives the host a menu of
ready-to-pin extensions.

### PLG-A5. Milestone/achievements lifecycle `EventSpec` (manifest enrichment)
The engine fires observable milestone/achievement transitions (save v2) but the manifest declares only
`idle.tick` + `idle.offline_return`. An `idle.milestone_earned` observability-only `EventSpec` (payload
shaped from real engine output) is a grounded, non-fabricated surface addition. · **Effort:** M ·
**Risk:** medium — a real surface change re-hashes the host pin; must land with a coordinated superbot-next
re-pin PR; do NOT ship half (manifest changed, pin not bumped) — fails host boot at the gate. ·
**Unblocks:** host-side milestone notifications. · **Blocker:** host-only coordination (the pin bump is a
superbot-next PR out of idle scope).

### Docs freshness / truth-drift

### PLG-B1. Truth-drift checker: kit-version single-source assertion
`status.md` says v1.15.0 while the tree is v1.16.0 — the recurring self-report lag `control/README.md`
documents. A `scripts/preflight.py` check cross-checking the `kit:` heartbeat line against
`substrate.config.json.kit_version` turns invisible drift into a nagged finding. (Same idea as the
2026-07-15 truth-refresh card's 💡: a `tests/test_doc_kit_version.py` anchoring current-state kit phrases.)
· **Effort:** M · **Risk:** medium — preflight is on the exit-affecting substrate-gate lane; ship as an
advisory print, not a non-zero exit, since heartbeats lag by doctrine. · **Unblocks:** GREEN == truthful
heartbeat for the one field wrong today; template for PLG-B2.

### PLG-B2. Counts-guard generalization
PR #125 pins pack-count + setup-vector-count in `current-state.md` to ground truth in CI
(`test_current_state_counts.py`). The same pattern is un-applied to other drift-prone numbers (test-suite
count 1381, theme-pack list membership, `📊 Model:` marker presence). Extend the guard to stable,
high-value counts. · **Effort:** M · **Risk:** low–medium — test-only, established green pattern;
over-pinning volatile numbers creates churn. · **Unblocks:** fewer truth-fix sessions (there have been ~5:
#81/#117/#125/#128/#139).

### PLG-B3. Doc-freshness stamp audit
Docs carry dated groom stamps but nothing flags a `living` doc whose newest stamp is older than the
`staleness_days: 14` cadence. A read-only audit listing living docs by stamp age surfaces which need a
groom. · **Effort:** M · **Risk:** low — advisory report. · **Unblocks:** systematic grooming instead of
reactive truth-fixes; feeds onboarding.

### Idea backlog & design/ADR index

### PLG-C1. Idea-backlog seeding pass (fill the empty conveyor)
`docs/ideas/` has a full lifecycle + YAML-frontmatter outcome contract and not one idea file. The outbox
+ status carry real parked ideas (feltness floor, generator-purchase economy, timed-events,
content-depth/endgame, PRESTIGE 10→25, shop rate-delta preview). Seed each as a properly-framed
`<slug>-YYYY-MM-DD.md` with `state`/`origin`/`outcome` frontmatter. **(This is also where triaged
survivors of THIS menu should land.)** · **Effort:** M (6–10 files) · **Risk:** low — additive docs, each
linked from the ideas README; mark verdict-owned items `state: routed`/blocked explicitly. · **Unblocks:**
the GROOM step can finally run; nothing on the belt = a dead process.

### PLG-C2. Idea-frontmatter validator
Once PLG-C1 seeds files, a checker enforcing the README contract (`shipped`/`survived`/`reverted` need all
three ship fields; `open`/`rejected` keep them null; `<slug>-YYYY-MM-DD.md` naming; every file linked)
keeps the machine-readable outcome record actually valid. · **Effort:** S · **Risk:** low — advisory,
pairs with PLG-C1 (sequence C1→C2). · **Unblocks:** a scoreable backlog sweep.

### PLG-C3. Design-doc / ADR index (`docs/design/README.md` or `docs/INDEX.md`)
`docs/decisions.md` is a clean ADR ledger (D-0001…D-0007) and `docs/design/` holds economy-v1,
achievements-v0, sim-harness, theme-balance-v0, timed-events-scoping, upgrades-prestige-v0 — but nothing
ties design docs to their decisions, PROVISIONAL/SIM-PINNED status, and governing D-numbers. A one-page
index (doc → status → owning decision → sim state). · **Effort:** M · **Risk:** low — additive index,
must be kept current (a PLG-B3 stamp-check candidate). · **Unblocks:** onboarding; finding SIM-PINNED vs
PROVISIONAL without reading every doc.

### PLG-C4. Cross-link ADRs ↔ design docs ↔ session cards
Provenance is rich but one-directional: `decisions.md` cites PRs/cards, but design docs don't back-link
their governing D-number and cards aren't indexed by the decision they enacted. A light back-linking pass
(each design doc names its D-NNNN; each D-entry's provenance verified live). · **Effort:** S · **Risk:**
low — docs-only header edits. · **Unblocks:** faster "why is this the way it is"; supports PLG-C3.

### Records / heartbeat / onboarding

### PLG-D1. Heartbeat re-stamp + status.md truth refresh (the live drift)  · *[blocked tonight — read-only archive]*
`control/status.md` is frozen at `2026-07-14T11:32:05Z`, `kit: v1.15.0`, phase text describing "EAP
final-day closeout" — but ORDER 010 (EAP extended to 07-21) has landed + been acked, and the kit is
v1.16.0. An overwrite re-stamp per `control/README.md` clears it. · **Effort:** S · **Risk:** low —
single-writer overwrite is the sanctioned ritual. · **Unblocks:** the manager's roster regen stops showing
a heartbeat-vs-commits divergence; makes PLG-B1's checker green. · **Blocker (tonight):** this synthesis
session treats `status.md` as a **read-only ARCHIVE** and did NOT change it — surfaced here + in Blockers
for the owner / next heartbeat-owning session. This is the one item that fixes a *currently-wrong* record.

### PLG-D2. Fresh-seat onboarding doc (`docs/ONBOARDING.md`)
A rebooted seat assembles its picture from `README → status.md → retro snapshots → CAPABILITIES →
PLATFORM-LIMITS → control/README` with no single "start here for a resuming session" page. A concise
onboarding doc (venue-posture rule, claim-first ritual, where truth lives, the verify line, known walls,
parked-items map). · **Effort:** M · **Risk:** low — additive; must be a digest+pointer (the
`seat-digest.md` "no third copy" doctrine), not a duplicate. · **Unblocks:** faster seat reboots (more
incoming per the EAP extension).

### PLG-D3. Records-consolidation map (one page: which file is authoritative for what)
The repo has a subtle records topology — `status.md` (frozen archive + overwrite heartbeat), `outbox.md`
(append-only lane→manager), `inbox.md` (manager-only), `claims/`, `decisions.md`, `current-state.md`
(living), `seat-digest.md` (derived). New sessions repeatedly mis-target these (e.g. the inbox-grammar
rejection on PR #104). A single "record → sole writer → when to write → defers-to" table. · **Effort:** S
· **Risk:** low — docs-only. · **Unblocks:** fewer gate rejections from writing to the wrong file;
complements PLG-D2.

### PLG-D4. Claims-directory lifecycle hygiene + convention note  · *[merged: tooling claims-linter/reaper + plugin claims-hygiene-sweep]*
`control/claims/` holds files whose backing work appears merged (e.g. `claude-eap-ack`,
`claude-reconcile-race-fix`, `claude-truth-refresh` → PRs #141/#142/#143); the README says
delete-at-session-close and ~72h stale = prune-on-sight. Two facets: (a) a `tools/claims_lint.py`
validating claim-file shape and flagging claims with no matching open PR / merged-but-not-cleared, plus an
advisory scheduled job listing claims older than `staleness_days: 14` (read-only reporting — never
auto-deletes); (b) a one-time read-only staleness assessment + a "prune on sight" convention reminder.
· **Effort:** S (assessment) / M (linter) · **Risk:** low as reporting-only; a reaper that *deletes* would
be medium — keep it advisory; verify each claim's PR is truly merged before recommending prune. ·
**Unblocks:** a clean claims dir = accurate in-flight signal for parallel sessions. *(A separate draft PR
#145 already proposes sweeping these three specific stale claims.)*

### Telemetry

### PLG-E1. Telemetry schema doc + validator (`telemetry/README.md` + checker)
`telemetry/model-usage.jsonl` has a consistent implicit schema
(`date/effort/model/outcome{4}/session/task_class/tokens_out`) enforced by nothing, and every
`outcome.*`/`tokens_out` is `null` across 37 rows. A documented schema + a JSONL validator (well-formed
lines, known keys, `📊 Model:` family-name format matching the session-card rule). · **Effort:** M ·
**Risk:** low–medium — `.gitattributes` already sets `merge=union`; validator is advisory. · **Unblocks:**
the model-attribution analysis (ORDER 001 / Q-0262) the file exists to feed; catches malformed appends.

### PLG-E2. Telemetry-vs-session-card reconciliation report
Each card carries a `📊 Model:` line and the jsonl carries a `model` field, but nothing checks they agree,
and cards exist that telemetry rows may not. A read-only reconciliation listing cards without a telemetry
row (and any model mismatches). · **Effort:** M · **Risk:** low — read-only report. · **Unblocks:**
trustworthy per-session attribution (the point of ORDER 001); a candidate future preflight check.

### PLG-E3. Backfill the null outcome fields (evidence-gated)  · *[merged: tooling telemetry-backfill + plugin backfill-null-outcomes]*
The `outcome{checker_findings, ci_green_first_push, merged_pr, reverted_within_window}` fields are null
for every row, but much is knowable post-hoc from `gh`/git (each session's merged PR is cited in
`current-state.md`'s Recently-shipped). A `tools/telemetry_backfill.py` derives these for a session/PR and
**appends** a corrected row (respecting append-only + `merge=union`, never rewriting); leave genuinely-
ambiguous rows null. · **Effort:** M (tool) / L (all 37 rows) · **Risk:** medium — writing derived data
risks fabrication if a session doesn't map cleanly to one PR; append-only by construction. · **Unblocks:**
retroactive model×effort→outcome analysis; only worth it after PLG-E1 pins the schema.

### Session cards & review-queue

### PLG-F1. Session-card retrospective digest (rolling)
60+ cards; the only rollups are two `docs/retro/` snapshots frozen at 2026-07-11. Everything since (waves
4/5, the improvement wave, EAP closeout, kit upgrade, reboot) has no digest. A dated retrospective
(what shipped, recurring friction classes, guard recipes carried forward) covering 07-11→now. · **Effort:**
L (~50 cards) / M if scoped to the improvement-wave + EAP window. · **Risk:** low — additive docs. ·
**Unblocks:** the mandated review rhythm; surfaces repeated friction (inbox-grammar rejections, heartbeat
freezes) worth guarding.

### PLG-F2. Session-card marker validator as a preflight check
`substrate.config.json.session_markers` lists the four required byte-forms (`**Status:**`, `💡`,
`previous-session review`, `📊 Model:`) and `.sessions/README.md` describes the born-red→complete
lifecycle, but enforcement is kit-internal. A repo-local check (or documented invocation of the kit's)
that a *completed* card carries all four markers catches a half-flipped card. · **Effort:** S · **Risk:**
low — advisory; the kit may already cover this (verify before duplicating). · **Unblocks:** reliable card
completeness.

### PLG-F3. Review-queue lifecycle automation / documentation
`review-queue.md` is a `living` stub, hand-drained, seeded empty 2026-07-10, never used. Either document a
"when does a row get added, by whom, how drained" convention (it has none) or honestly mark it dormant.
· **Effort:** S · **Risk:** low — docs-only. · **Unblocks:** clarity on an unused process file; the
"conveyor not graveyard" ethic applied to review-queue.

---

## Blockers

These are surfaced, not scheduled. Nothing below is buildable-to-green tonight without an external action.

- **Owner-only — OA-003:** make `pytest` a required status check on `main` (Settings → branch ruleset).
  Today only `substrate-gate` is a required context, so `pytest`/`theme-gate` and every proposed gate stay
  **advisory** — a PR can merge green while the suite is red (GREEN ≠ TESTED). Standing since PR #74. Every
  "gating" proposal (TOOL-1 phase 2, TOOL-7) is a two-part: land the workflow (agent) + one owner click.
- **Host-only (need the `sb`/superbot-next runtime; these run only in the `pytest-with-host` CI job, or
  require a superbot-next PR out of idle scope):** PLG-A3 and PLG-A5 (any manifest surface change re-hashes
  the host `plugins.lock.json` pin — a coordinated superbot-next re-pin PR); TEST-10's full validation (the
  `sb` package that gates `test_manifest.py`; the sb-free stub/golden-snapshot is the unblock); live
  host-state-injection wiring; ENG-16 (memoized rate table — `[HOST-BLOCKED]`, deferred until a live host
  exists); the pure math of ENG-7's timed-event scheduler is testable now but a live scheduler is host-blocked.
- **Verdict-blocked economy items (engine-math/sim-owned; the numbers need a fleet/owner economy verdict —
  belong in the PLG-C1 backlog as `routed`/blocked, never built here):** the **feltness floor**
  (min-visible-delta, ASK1 confirmed-inert, needs its own sim); **PRESTIGE_BONUS_PERCENT 10→25** (ASK2
  candidate row, awaiting the SIM-PINNED re-tune ruling); **generator-purchase economy tuning** (the ENG-1
  cost curve — mechanism buildable, numbers `[TUNE-BLOCKED]`); **timed-events magnitudes** (ENG-7 —
  unregistered pending SIM-002/Q-0264). All the `[TUNE-BLOCKED]` engine items share this gate.
- **Policy decision required (not just effort) — no-hypothesis policy:** TEST-7 and (if hypothesis-based)
  TEST-8 directly contradict the repo's explicit, thrice-documented *no-`hypothesis`-dependency* stance. The
  owner must decide whether property-based testing with a third-party dep is wanted, or whether to keep
  deepening the existing stdlib-`Random` approach. Not an agent call.
- **Live record drift, flagged NOT fixed (PLG-D1):** `control/status.md` line 5 still reads `kit: v1.15.0`
  while the measured tree is **v1.16.0** (`bootstrap.py --version`; `substrate.config.json.kit_version`;
  corrected in `current-state.md` via PR #139). The status heartbeat is a **read-only ARCHIVE** with a
  single-writer overwrite ritual, so this synthesis session did **not** touch it. It is owed to the owner /
  the next heartbeat-owning session (per the truth-refresh card's Lane-owed note). Surfaced here so it is
  not lost.

---

## Highest-leverage, lowest-risk to start (honest read)

Not a mandate — a starting read for triage. Biased toward small, additive, high-signal, verdict-free items.

1. **TOOL-6 (`requirements-dev.txt`)** → unblocks TOOL-2 caching and cleans four workflows; **TOOL-11
   (Makefile)** + **TOOL-13 (session-card scaffolder)** for immediate DX; **TOOL-1 phase 1 (coverage
   visibility)** before any gating debate. All S, all reversible, none verdict-blocked.
2. **TEST-2, TEST-9, TEST-13** — small, follow the blessed regenerate-or-red pattern, pure additions that
   lock the determinism/render/migration contracts. **TEST-13** and **TOOL-4 (flaky lane)** are the biggest
   latent-bug catchers, both guarding the stated integrity floor.
3. **Engine ergonomics helpers ENG-8 / ENG-9** (`time_to_afford`, prestige preview) — pure, deterministic,
   zero-risk, immediately useful in render/sim, and verdict-free (unlike the tuned mechanics).
4. **Theme audits THM-16 / THM-17** (analysis-only, concrete findings already in hand) and **THM-14
   (scaffolder)** — the scaffolder turns the nine new-pack pitches (THM-1..9) from S into XS; packs merge on
   theme-gate green alone.
5. **PLG-C1 (seed the empty idea conveyor)** — highest process leverage: it turns this very menu into the
   backlog the lifecycle was built for, and is where the owner's triaged survivors should land.
6. **The one thing only the owner can move:** OA-003 (make `pytest` required). Until then every gate above
   is advisory. **The one currently-wrong record:** the `status.md` kit-version drift (PLG-D1) — owner /
   next-heartbeat session, not this one.
