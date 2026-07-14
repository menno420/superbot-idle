# 2026-07-14 — improve: wave records (README REPL true-up + improvement-wave outbox summary)

> **Status:** `complete`

- **📊 Model:** fable-5 · medium · docs+control — README Try-it true-up vs the grown REPL + improvement-wave outbox record · 2026-07-14T02:41Z–02:47Z (`date -u`)

## What happened

Final improvement-wave slice (owner directive 2026-07-14 ~01:27Z): the wave
grew the product past its player-facing records, so this slice trues the
records up and lands the lane→manager wave summary. PR #128; docs + control
only, zero source/test changes.

1. **README Try-it true-up** — recon found the loop line matched
   `tools/play.py` BEFORE the wave; the wave then added `buy <id> [n|max]`
   (#116), `save` / `load <blob>` (#119), input hardening (#115), and themed
   errors (#124). The loop line now lists the new verbs plus one sentence on
   themed, crash-proof errors — same voice, still a pointer, not a manual.
   Every verb listed was verified against `tools/play.py` at HEAD (`c53eba9`)
   before writing.
2. **`docs/current-state.md` minimal touch-up** — groom header gains an
   improvement-wave touch-up stamp (main `c53eba9`); stability-baseline suite
   claim 1363 → 1381 (kept as prose — the counts guard deliberately UNGUARDS
   the self-referential suite number); one compact "Improvement wave" entry
   (PRs #113–#126, one clause each) atop Recently shipped. The two guarded
   anchors (`**Theme catalog: 18 packs**`, the 224-vector parenthetical) were
   NOT touched; `tests/test_current_state_counts.py` run explicitly:
   `2 passed`.
3. **`control/outbox.md` — IMPROVEMENT WAVE record** (2026-07-14T02:42Z
   entry): the 14 shipped PRs one line each, harvest provenance (17
   candidates ranked; verdict-owned surfaces excluded; C13 shop
   rate-delta/effect preview deliberately PARKED — it enumerates the exact
   surface of the pending feltness SIM-REQUEST and building it pre-verdict
   would prejudge the sim), suite delta 1363 → 1381, and the honest close:
   the verdict-free ranked list is now DRY; the remaining backlog is blocked
   entirely on external unblocks (feltness SIM verdict / PRESTIGE re-tune
   process ask / timed-events + generator-purchase Q-numbers / OA-003 owner
   click).

Verify at flip: `python3 -m pytest -q` → `1381 passed, 1 skipped in 15.36s`;
`python3 -m pytest -q tests/test_current_state_counts.py` → `2 passed`;
`python3 tools/theme_gate.py themes` → `theme-gate: all 18 pack(s) valid
(schema v1)`; `python3 bootstrap.py check --strict` → held only the designed
born-red gate on this card pre-flip, green at flip. `origin/main` moved
mid-flight (#127, stale-claim prune) and was merged into this branch
pre-flip.

## 💡 Session idea

The README loop line is the third doc surface hand-mirroring
`tools/play.py`'s verb set (with the module docstring at
`tools/play.py:24-37` and the in-REPL `_HELP` text at `tools/play.py:218-231`
— those two are already within one file of each other; the README is the one
that silently rotted). Guard recipe: a small doc-parity test
`tests/test_readme_repl_verbs.py` that imports the dispatch surface from
`tools/play.py` (anchor: the `verb ==` chain in `dispatch()` at `tools/play.py:387`, or better,
lift the verb set into a module-level `VERBS` tuple first), extracts the
backticked verb tokens from README.md's "In the loop:" sentence with a
regex anchored to that exact phrase, and asserts set-equality — same
pattern (and same re-anchor-in-the-same-PR rule) as
`tests/test_current_state_counts.py`. That turns "README rotted behind the
REPL" from a recon finding into a CI red.

## ⟲ Previous-session review

previous-session review: `.sessions/2026-07-14-improve-host-main-lane.md`
(slice K, PR #126 — the wave's last build slice; this slice is the wave's
record-keeping close). That card's core move was "guard only what reds for
the right reason": its lane deliberately does NOT gate merges, just as the
counts guard it reviewed deliberately unguards the suite-size claim. This
slice inherited both judgments directly — the 1363 → 1381 suite edit here
stayed prose because that card's review chain explains why an exact pin
would red on every tests-touching PR, and the README edit stayed a
one-sentence true-up rather than a generated manual for the same reason (a
doc that restates source verbatim rots or gates, never both well). Its
mid-flight-merge note also repeated here beat for beat: main moved under
this branch too (#127) and was merged pre-flip per that card's telemetry
union recipe. One transferable nit: that card cites its requesting cards
with line-number anchors (💡 lines 63-73 etc.) — this card's idea now does
the same with `tools/play.py` anchors, which its own reviewer will thank it
for.
