# 2026-07-11 — docs grooming: current-state + architecture + decisions to shipped reality

> **Status:** `complete`

- **📊 Model:** fable-5 · high · idle-engine seat (docs-grooming worker, coordinator-assigned) · 2026-07-11T02:15Z–02:2xZ (`date -u`)

## What happened

Groomed the orientation/state docs to everything shipped since seed
(28fac02..b6e6b68, PRs #1–#34) in one docs-only build PR after a control
fast-lane claim (PR #35, `control/claims/docs-grooming.md`, auto-merge
armed at creation, merged 02:14:25Z; claim removed here). No
engine/schema/theme/tool/test files touched — the shop-composition
worker owns those.

1. **`docs/current-state.md`** — rewritten from the empty seed skeleton
   to reality: stability baseline (all 8 `idle_engine/` modules, 9-pack
   catalog, schema v1 + `labels`, theme-gate check list, setup-code v1 +
   125-vector file, 620-test suite shape); an explicit **what does NOT
   exist** section (no bot runtime, no persistence, no plugin adapter —
   PLUG-001; economy numbers provisional — SIM-001; no generator
   purchase path; no website encoder here); a shipped ledger newest-first
   with PR numbers; and the **groomed roadmap** — ordered, blockers
   marked (shop composition IN FLIGHT; plugin adapter BLOCKED PLUG-001;
   economy tuning BLOCKED SIM-001; memoized rate table needs a bot
   runtime; catalog wave 3 optional volume; setup-code v2 version-bound
   ruling deferred to the v2-defining PR).
2. **`docs/architecture.md`** — layer table filled with real import
   rules (`idle_engine/` incl. the render + provisioning seams;
   PyYAML-in-`theme.py`-only), invariants written as testable statements
   naming their enforcing tests, per-seam contracts pointed at their
   authoritative docs instead of duplicated, stale verify parenthetical
   ("once ORDER 000 lands it in CI") replaced — theme-gate has been a
   required check since OA-002.
3. **`docs/decisions.md`** — appended [D-0002..D-0007], each dated with
   PR provenance: integer-only single-floor math (#7+#8), schema v1
   additive-only policy (#4+#5), labels neutral-fallback (#24+#27),
   grammar-wins setup-code ruling (#26+#28), evidence-gated plugin work
   (#30+#31, PLUG-001), volume-first catalog (#10/#11, #19/#21, #33/#34).
4. **`docs/repo-navigation-map.md`** — placement table filled, one row
   per top-level area including `tests/vectors/`, `control/claims/`,
   `.sessions/`, and the root governance files.
5. **`docs/AGENT_ORIENTATION.md`** — same stale verify claim fixed;
   `theme-schema.md` and the two `design/` docs added to the router
   (the "first file arrives with the economy design slice" line was
   stale — both files shipped).
6. `review-queue.md` audited, NOT stale (genuinely empty — no external
   reviews requested since seed), left untouched.

Verify: `python3 -m pytest -q` → 620 passed; `python3 bootstrap.py
check --strict` green after this flip.

## 💡 Session idea

`control/status.md` § SHIPPED RECORD and `docs/current-state.md` §
Recently shipped now say the same thing in two voices, and both grow
per slice. Consider making current-state's ledger the single narrative
home and having status.md's SHIPPED RECORD hold only one line per slice
(PR numbers + pointer) — the heartbeat stays scannable and the two can
never disagree about details.

## ⟲ Previous-session review

The catalog-wave-2 card (2026-07-11-catalog-wave-2.md) made this
grooming almost mechanical: its "zero pinches" audit line and 533 → 620
count pin were exactly the evidence needed for D-0003/D-0007 and the
current-state baseline, no re-derivation. One gap it inherited rather
than caused: no card in the run ever owned updating the seed-skeleton
docs (current-state.md sat empty through 14 shipped slices), which is
why this slice had to exist — the kit's "keep it current as the project
moves" instruction needs an owner per slice, not a catch-up pass.
