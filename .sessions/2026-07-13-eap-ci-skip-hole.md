# 2026-07-13 — close the `1 skipped` CI hole: pytest job against pinned superbot-next

> **Status:** `complete`

- **📊 Model:** fable-5 · medium · ci build · close the 1-skipped hole · 2026-07-13

## What this session does

EAP night worklist item 3 (inbox ORDER 007, from fm ORDER 045 relay): idle's CI has
never exercised the adapter contract — `plugin/tests/test_manifest.py` opens with
`pytest.importorskip("sb.spec.manifest")`, so all 15 manifest-contract tests skip in
every CI run (`docs/current-state.md` stability §: "1 skipped … the `sb` host package,
absent in this repo's CI"). Two live-boot bug classes have already slipped through this
hole (capability 3-part fix #85; events-registration + `/idle` collision fixes in the
liveboot-fixes session). The fix: a second job in `.github/workflows/pytest.yml` that
checks out `menno420/superbot-next` at a pinned SHA into a sibling dir, exposes `sb`
via `PYTHONPATH`, and runs the suite so the skip becomes a real run. The existing
sb-free job stays untouched — the suite must remain green without the host.

## What happened

Added the `pytest-with-host` job to `.github/workflows/pytest.yml` (the lane-owned
workflow — deliberately NOT the kit-owned `substrate-gate.yml`, which adopt/upgrade
regenerates in place). The job:

- checks out the idle repo, then `menno420/superbot-next` at **pinned commit
  `9634e81748363184bf13abf1485e80262e19e8cb`** (main HEAD at authoring, resolved and
  verified via `git ls-remote`; the `plugin/pyproject.toml` `[host]` contract SHA
  `d3dba9b` is an ancestor — checked with `git merge-base --is-ancestor`) into
  `superbot-next/` inside the workspace. Bump recipe lives in the workflow comment:
  `git ls-remote https://github.com/menno420/superbot-next main`, update `ref:`,
  confirm green.
- exposes `sb` via `PYTHONPATH="$GITHUB_WORKSPACE/superbot-next"` instead of
  `pip install`: `sb.spec`/`sb.namespace` are pure-stdlib (grepped — zero third-party
  imports), while the host pyproject's dynamic `dependencies = requirements.txt` would
  drag discord.py etc. into a job that doesn't need them.
- runs `python3 -m pytest -q --ignore=superbot-next` — the `--ignore` matters because
  this repo has NO pytest config (bare rootdir collection), so without it the host
  checkout's own test tree would be collected into idle's suite.
- **hard-fails on any skip** (grep guard on the pytest tail): if the pinned host ever
  stops satisfying `importorskip("sb.spec.manifest")`, the job reds instead of
  silently re-opening the hole. The sb-free `pytest` job is byte-identical to before.

Cross-repo pin note (worklist item 4 pointer): the host-side `plugins.lock.json` pin
rides IN superbot-next and points host→idle; this workflow's pin is CI-only and points
idle→host. They are not duplicates; bumps are independent.

Merged `origin/main` (wave 5 packs, #105) into the branch pre-flip; the
`telemetry/model-usage.jsonl` conflict resolved by keeping BOTH appended rows.

## Verification

- `python3 -m pytest -q` (sb-free, CI-faithful) → **1363 passed, 1 skipped** (post-merge
  counts; wave 5 added tests).
- Exact job command locally (host cloned to `superbot-next/` at `9634e81`, same
  `PYTHONPATH` + `--ignore` + skip-grep guard) → **1378 passed**, 0 skipped, guard OK.
- Skip→run proof on the module itself: `python3 -m pytest plugin/tests/test_manifest.py -q`
  → `1 skipped` without the host; `15 passed` with the pinned host on `PYTHONPATH`.
- `python3 -c "import yaml; yaml.safe_load(open('.github/workflows/pytest.yml'))"` → OK.
- `python3 bootstrap.py check --strict` → all checks passed (the born-red hold on this
  card until this flip).

## 💡 Session idea

The pin will rot silently: superbot-next moves, idle's CI stays green on the old SHA,
and a REAL contract break only surfaces when someone bumps. Guard recipe for a later
session: a scheduled (cron) variant of `pytest-with-host` that checks out superbot-next
`main` (unpinned) and runs ONLY `plugin/tests/` — non-blocking, alert-only. Anchors:
`.github/workflows/pytest.yml::pytest-with-host` (copy the job, swap `ref:` for `main`,
add `schedule:` trigger), test target `plugin/tests/test_manifest.py` (the
`importorskip("sb.spec.manifest")` gate), and the liveboot-fixes card's companion idea
of driving `sb.adapters.discord.command_tree.register_app_commands` over `MANIFEST` in
that same lane — one assert per plugin catches the #40-class collisions the manifest
tests can't see.

## ⟲ Previous-session review

Newest prior card: `.sessions/2026-07-13-eap-wave5-packs.md` (worklist item 1, catalog
15 → 18, merged as #105 mid-flight — its telemetry row and this session's row are the
both-kept merge resolution above). Its packs landed with full labels + milestones
blocks and theme-gate green; nothing there touches CI or the plugin adapter, so no
overlap with this slice. One interaction worth noting: wave 5 grew the suite (1264 →
1363 sb-free), which is why this card's verify counts differ from the numbers in the
PR body written pre-merge — same 15-test delta (+skip→run) either way.
