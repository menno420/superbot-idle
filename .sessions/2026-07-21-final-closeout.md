# 2026-07-21 — docs: superbot-idle project closeout

> **Status:** `in-progress`

- **📊 Model:** opus-4.8 · high · docs-only

## What / why

Land a plain-language **project closeout** for superbot-idle, written for two
readers who have never seen these autonomous agent sessions: the non-coder owner
and a fresh Claude session picking the repo up cold. The repo is
engine-complete with zero open PRs, so this is a wrap-up, not a build: it names
what shipped (with verified PR citations), states the true live state (suite
1642 passed + 1 skipped at `31a4a3a`, `bootstrap check --strict` green), gives an
honest thin continuation list (idle is the stable baseline — the only open
threads are fleet-sim-blocked or design-deferred), an owner run/verify
walkthrough, and a fresh-session boot route. Cross-links the two sibling
closeouts (superbot-games, superbot-mineverse — the fleet MASTER).

New doc: `docs/PROJECT-CLOSEOUT.md`. Reachability pointers added near the top of
`docs/current-state.md` and in `docs/AGENT_ORIENTATION.md` (lane-layer docs) so
`bootstrap check --strict` does not red the `[reachable]` orphan guard.
True-up: `docs/current-state.md` suite counts corrected 1607→1642 (sb-free) and
1622→1657 (host job) — #175 bumped the suite but left the summary counts stale.
Cleanup: this seat's two terminal claim files deleted (all their PRs merged,
zero open).

## Verification

- `python3 -m pytest -q` — expect `1642 passed, 1 skipped`.
- `python3 bootstrap.py check --strict` — expect all checks passed (the
  born-red HOLD on this card is the only expected gate hold until the flip).
- Every PR citation in the closeout confirmed against `git log`/`git show` at
  `31a4a3a` before writing (no unverified numbers).

## Landing (born-red convention)

Card born RED (`in-progress`) in the first commit — holds the substrate-gate
HOLD. Commit 2: closeout doc + the two reachability pointers + the two claim
deletions. PR opened READY-FOR-REVIEW. After re-verifying the suite and strict
check WITH the new doc present, commit 3 flips this card to `complete` as the
deliberate last step, releasing the enabler so the PR can merge on all-green.
The worker does not merge its own PR.

## 💡 Idea

A `PROJECT-CLOSEOUT.md` is a snapshot that goes stale the moment the suite count
or pack count moves — exactly the drift `test_current_state_counts.py` already
guards for `current-state.md`. A cheap follow-up: extend that doc-honesty guard
to also assert the closeout's headline "N passed" / "21 packs" numbers match the
live catalog and a recorded suite count, so a future pack wave can't silently
leave the closeout lying.

## ⟲ Previous-session review

Predecessor **PR #175** (`2026-07-20-idle-theme-wave6.md`) shipped the 21st
data-only theme pack (vineyard/winery, wave 6) with its catalog-sync guards and
regenerated vector corpora — a clean, self-initiated content slice that took the
suite 1607→1642 and clears the theme-gate 21/21. It holds up: the pack loads,
the guards are green, and the born-red convention was followed correctly. One
gap this closeout fixes: #175 bumped the suite but left the `current-state.md`
*summary* counts at 1607/1622 while updating only the theme count — a small
doc-drift the count-guard did not catch because it keys on pack count, not the
prose suite total. Its 💡 (a milestone-silhouette pairwise-distinctness guard)
remains a sensible unbuilt follow-up.
