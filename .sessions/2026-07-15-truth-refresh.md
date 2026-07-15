# 2026-07-15 — truth refresh: kit version claims in docs

> **Status:** `in-progress`
> **Branch:** `claude/truth-refresh` · claim `control/claims/claude-truth-refresh.md`

- **📊 Model:** fable-5 · medium · docs-only — truth refresh: correct stale kit-version claims (v1.15.0 → measured v1.16.0) in docs/ + current-state truth-stamp re-groom · session opened 2026-07-15T04:18Z (`date -u`)

**Goal:** the tree runs substrate-kit v1.16.0 (measured this session:
`python3 bootstrap.py --version` → `substrate-kit 1.16.0`, matching
`substrate.config.json` → `kit_version: "1.16.0"`; the bump landed via
PR #134 `3df5449`), but two docs still claim v1.15.0. Correct those
claims, re-stamp `docs/current-state.md` against HEAD `8a7275d`, and
re-verify the rest of the current-state ledger at HEAD (correct what
moved, keep what's still true). The OA-003 owner ask (mark `pytest`
required) stays untouched — it is still open.

**Baseline at HEAD `8a7275d` (before edits):**
`python3 bootstrap.py check --strict` → exit 0, all checks passed
(6 pre-existing advisory `model-line-class` warnings on older cards,
never exit-affecting); `python3 -m pytest -q` →
`1381 passed, 1 skipped in 12.47s`.

## What happened

Measured ground truth first: `python3 bootstrap.py --version` →
`substrate-kit 1.16.0`; `substrate.config.json` → `"kit_version":
"1.16.0"`; `.substrate/state.json` agrees. The docs-vs-tree mismatch was
real: the bump landed 2026-07-14 via PR #134 `3df5449` and two docs
still claimed v1.15.0. Full-repo grep for `1.15.0` / `v1.15` found doc
claims ONLY in:

1. `docs/eap-closeout-walkthrough-2026-07-14.md` §B — "kit v1.15.0" as a
   CURRENT-state claim → corrected to v1.16.0 with the #134 citation and
   a verify-live pointer (`bootstrap.py --version`). True when written
   (#132 predates #134 by hours); stale since.
2. `docs/current-state.md` shipped-record line "kit v1.15.0 (#90, #91)"
   — a TRUE historical record, so annotated ("kit since bumped to
   v1.16.0, PR #134 `3df5449`") rather than falsified.

Remaining v1.15 hits are history (session cards, `.substrate/backup/`,
upgrade report) or control-bus files this slice must not touch
(`control/status.md` line 5 `kit: v1.15.0` — the heartbeat re-stamp
stays owed to the seat's next status overwrite, per one-writer rules and
the #137 card's Lane-owed note).

Current-state re-groom at HEAD `8a7275d`: truth-stamp advanced
(2026-07-15, post-PR #139); In-flight snapshot refreshed (0 open PRs
verified via API; EAP EXTENDED through 2026-07-21 per inbox ORDER 010,
dormancy superseded pending owner reboot go); post-#126 merges added to
the shipped record (kit v1.16.0 + preflight/enabler split #134+#137;
EAP closeout #132 with #128/#112). Verified-still-true and kept: 18
packs (`ls themes`), 224/90/109/25 vector counts (counts-guard green),
pytest-with-host pin `9634e81` (`pytest.yml`), OA-003 owner ask
(UNTOUCHED — still open). Both touched docs keep their Status badge in
the first 12 lines.

## Verify at flip

- `python3 -m pytest -q` → `1381 passed, 1 skipped` (pre- and
  post-edit; CI has no local-suite substitute for this — pytest is not
  a required check yet, see OA-003)
- `python3 tools/theme_gate.py themes` → all 18 packs valid
- `python3 bootstrap.py check --strict` → pre-flip red ONLY on this
  card's designed born-red hold; the 6 `model-line-class` advisories on
  older cards are pre-existing, untouched scope

## 💡 Session idea

Kit-version doc claims have now gone stale twice (status.md INC-17
class, and this session's two doc hits) and only hand grooms catch
them. Extend the #125 counts-guard pattern to kit-version claims: a
`tests/test_doc_kit_version.py` that anchors the CURRENT-state kit
phrases (the walkthrough §B "kit vX.Y.Z" clause, the current-state
truth-stamp's "kit vX.Y.Z") and asserts they equal
`substrate.config.json["kit_version"]` — historical lines stay
unanchored, exactly like the counts guard skips "15 -> 18 packs".
Guard recipe: copy `tests/test_current_state_counts.py`'s
`_single_match` anchor discipline; truth source
`json.load(substrate.config.json)["kit_version"]` (the same value
`bootstrap.py --version` prints); test target: a kit upgrade that
forgets the docs turns CI red in the upgrade PR itself.

## ⟲ Previous-session review

previous-session review: `.sessions/2026-07-14-preflight-and-enabler-split.md`
(PR #137) — its verify block reproduced exactly this session (baseline
`1381 passed, 1 skipped`; enabler regen a no-op — no carve-out bank
appeared in the #134→HEAD range), and its Lane-owed note was the honest
flag this slice leaned on: it named the status.md `kit:` v1.15.0 debt
precisely instead of quietly re-stamping outside an order, and that
debt is confirmed STILL outstanding at `8a7275d` (line 5). One gap: it
did not mention the two docs/ v1.15.0 claims its own kit-upgrade
predecessor left behind — this session existed to close that hole; the
💡 above is the guard so no third session has to.
