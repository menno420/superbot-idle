# 2026-07-13 — close the `1 skipped` CI hole: pytest job against pinned superbot-next

> **Status:** `in-progress`

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
