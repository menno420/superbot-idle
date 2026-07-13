# 2026-07-13 — docs/current-state.md groom: record #82–#88, kill the stale "in flight" line

> **Status:** `complete`

- **📊 Model:** Fable-class (Claude 5 family) · docs groom · idle seat (current-state truth pass) · 2026-07-13T13:49Z (`date -u`)

## Scope

Groom `docs/current-state.md` against live GitHub + main HEAD (`05a99f5`):

- Record merged-but-unrecorded work — verified at live GitHub, newest first:
  #88 (`05a99f5`, Q-0264 relay / SIM-001 verdict V038), #87 (`3a4fa5f`,
  merged 2026-07-13T13:31:21Z), #86 (`b03cc96`), #85 (`3e22f69`), #84
  (`d992c56`), #83 (`161bc7d`), #82 (`c735075`) — plus the wider
  "Recently shipped" gap #35–#81, which the list (claiming "newest first")
  silently stopped short of at wave 2 (#33+#34).
- Remove the contradicted "In flight: shop composition" bullet — that slice
  SHIPPED 2026-07-11 as PRs #36 (`9047539`, merged 2026-07-11T02:17:18Z) +
  #38 (`0835adb`, merged 2026-07-11T02:24:53Z); `docs/render-layer.md` no
  longer has a parked seam (replaced by § Shop composition in #38).
- Fix other claims contradicted at HEAD: SIM-001 "still awaiting manager
  relay" (verdict V038 landed via #88 → `control/inbox.md` ORDER 005);
  roadmap item 2 "Not built yet" (adapter built in #75+#78, refined
  #85/#86); roadmap item 5 "Catalog wave 3" (waves 3 AND 4 already
  shipped); adapter capability described as bare `idle` (3-part
  `idle.game.play` since #85).
- Preserve the docs-gate shape: Status badge within the first 12 lines.

Branch `claude/idle-current-state-groom` · claim
`control/claims/idle-current-state-groom.md` · born-red card first commit,
flip complete last.

## Verify

- `python3 -m pytest -q` → `1260 passed, 1 skipped in 17.06s`
- `python3 bootstrap.py check --strict` → `check: all checks passed.` (exit 0)

## Close-out

Groom shipped as PR #89 (head `49753ed`): `docs/current-state.md` re-grounded
against main HEAD `05a99f5` — #35–#88 recorded in "Recently shipped", the
contradicted "In flight: shop composition" line removed, SIM-001/roadmap/adapter
claims fixed, docs-gate badge shape preserved. Claim
`control/claims/idle-current-state-groom.md` released in the flip commit.
Flip written 2026-07-13T14:00Z (`date -u`).

## 💡 Session idea

idle's substrate-gate CI runs bootstrap check WITHOUT `--strict`, so an
in-progress born-red card does not hold the merge red — auto-merge
landed/nearly landed this PR before its card flipped. Fix: make the
substrate-gate workflow run `check --strict` but exempt exactly the card whose
branch matches the PR head, so born-red actually blocks auto-merge as designed.

## ⟲ Previous-session review

Verified `2026-07-13-idle-liveboot-fixes.md` (PR #86) against source: both
claimed fixes are real in `plugin/superbot_idle_plugin/manifest.py` —
`register_event_specs(list(EVENTS))` fires at module import (`:186`) AND inside
`_ensure_refs` (`:204`), and the root `idle` CommandSpec is
`kind=CommandKind.PREFIX` (`:226`) — and all three promised guard tests exist
in `plugin/tests/test_manifest.py` (`:34`, `:133`, `:146`). The card's guard
recipe names exact anchors (function + file + test target), which is precisely
the recipe discipline `.sessions/README.md` asks for — this groom leaned on
those anchors instead of re-deriving them.
