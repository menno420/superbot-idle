# 2026-07-20 — docs+control(readiness): refresh current-state truth-stamp + prune terminal stale claims

> **Status:** `complete`

- **📊 Model:** Opus 4.8 · medium · docs-only — docs-readiness sweep · 2026-07-20
- **Previous-session review:** predecessors idle #169 (loader↔schema parity-guard capstone) / #170 (THM-17 cross-pack vocab audit) / #171 (merge-doctrine de-wall — agents merge own green PRs) / #172 (retired merge-decision convention in status.md) / #173 (ORDER 011 record). This sweep grooms `docs/current-state.md` to their HEAD and prunes the claim files their merges left orphaned.

## What / why

Readiness sweep to make the recreated project boot-clean at HEAD `d2b6d38`. Two truths were stale:

1. **`docs/current-state.md` truth-stamp** was groomed only through 2026-07-18 `97e4c71` (post-#161), and its **In flight** note (dated 2026-07-17) claimed `control/claims/` held only its README — contradicted on disk by 23 orphaned claim files, 10 flagged `claims-stale` (>72h). Refreshed the stamp to HEAD `d2b6d38` (2026-07-20), corrected the In-flight note (verified **zero open PRs** on live GitHub), and recorded ORDER 011 (owner 2026-07-18 live resume direction, #173) plus the merge-doctrine de-walling (#171/#172 — agents merge their own green PRs). The EAP Projects read-only date (2026-07-21) stays a platform fact to re-verify on the day.

2. **Orphaned claim files.** Every non-README claim was an orphan of an already-merged PR (#150–#173). Pruned all 23 after confirming on live GitHub that each branch is gone / its PR is merged; kept `README.md`.

`docs/NEXT-TASKS.md` (referenced by CLAUDE.md) **does not exist** in this repo. Not created — a readiness sweep should not invent a new tracked doc, and the Roadmap section in current-state does not clearly ask for extraction.

Regenerated `docs/seat-digest.md` (`python3 bootstrap.py seat-digest`) to clear the `seat-digest-stale` advisory (clean deterministic render). Left the historical `model-line-class` advisory on `.sessions/2026-07-18-theme-flavor-depth.md` untouched — rewriting a shipped card would edit history.

## 💡 Idea

`claims-stale` only nags; nothing auto-reconciles a claim against its merged PR. A `bootstrap claim --sweep-merged` verb that deletes any claim whose branch is gone / PR is merged on live GitHub would keep `control/claims/` boot-clean without a manual readiness pass each time.

## Verification

- `python3 -m pytest -q` — full green (no code/test touched: 1607 passed / 1 skipped).
- `python3 bootstrap.py check --strict` — passes; the 10 `claims-stale` advisories drop with the pruned files.

## Landing (born-red convention)

Born red: held `in-progress` through the sweep; flipped `complete` in the final commit (PR #174), clearing the HOLD so the landing workflow can merge on all-green.
