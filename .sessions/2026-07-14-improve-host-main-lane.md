# 2026-07-14 — improve: scheduled advisory host-main CI lane (drift check vs superbot-next main)

> **Status:** `complete`

- **📊 Model:** fable-5 · medium · CI-config — scheduled advisory host-main lane · 2026-07-14T02:31Z–02:38Z (`date -u`)

## What happened

Improvement-wave slice K (owner improvement-wave directive, 2026-07-14) —
new workflow `.github/workflows/host-main-advisory.yml`: a cron lane that
runs the `pytest-with-host` job's steps against UNPINNED superbot-next
`main`, advisory-only, so pin drift is detected daily instead of only when
someone bumps the pin. Requested by three cards:
`.sessions/2026-07-13-eap-ci-skip-hole.md` (💡 lines 63-73: "a scheduled
(cron) variant of `pytest-with-host` … checks out superbot-next `main`
(unpinned) … non-blocking, alert-only"),
`.sessions/2026-07-13-idle-capability-3part-fix.md` (💡 lines 58-65:
optional scheduled lane "not blocking, not on the sb-free critical path"),
`.sessions/2026-07-13-idle-liveboot-fixes.md` (💡 lines 83-90: same lane
for live-path host-contract drift). PR #126; ONE new file under
`.github/workflows/` — `pytest.yml` and all existing workflows untouched.

Design, mirroring `pytest.yml::pytest-with-host` verbatim except the ref:

1. **Steps identical to the pinned job** — self checkout, host checkout to
   `path: superbot-next`, setup-python `3.x`, same deps, same run block
   (`PYTHONPATH="$GITHUB_WORKSPACE/superbot-next" python3 -m pytest -q
   --ignore=superbot-next` + `PIPESTATUS` check + grep skip-guard) — with
   `ref: main` replacing the pinned SHA. Checkout stays unauthenticated
   (superbot-next is public; no token, no secrets).
2. **Triggers: `schedule` + `workflow_dispatch` ONLY** — cron
   `17 5 * * *` (daily 05:17 UTC: after the owner's overnight, before the
   working day, off the :00 boundary where GitHub delays/drops queued
   crons). NO `pull_request`/`push`, so the lane never appears on a PR
   and never gates a merge.
3. **Advisory semantics in the header comment** — the workflow may fail
   loudly (that is its job): a red means superbot-next main moved
   incompatibly, the adapter contract broke, or the skip-guard tripped
   (host main stopped satisfying `importorskip("sb.spec.manifest")` —
   the `1 skipped` hole re-opening even against main, hence the guard is
   kept). Fix path: bump the PIN in `pytest.yml` per its "PIN:" comment,
   or fix the adapter in `plugin/`.
4. **Activation caveat** (in header + PR body): scheduled workflows only
   run from the default branch, so the lane activates on merge —
   validated here by local simulation, not by a pre-merge run.

**Local simulation** (exact job semantics: superbot-next cloned at `main`
= `a05f6899ac2538c3140f96e06651a55460ea7418` into a sibling dir, same
PYTHONPATH + pytest command + `PIPESTATUS` + skip-grep; final OK line is
the simulation harness's echo, not a workflow step) — tail verbatim:

    ........................................................................ [ 98%]
    ..........................                                               [100%]
    1394 passed in 15.31s
    SKIP-GUARD OK (0 skipped)

So today host `main` is drift-free vs the adapter (1394 = 1379 sb-free
passes + the 15 formerly-skipped manifest tests, 0 skipped — matching
the pinned job's shape),
and the born-green state of the lane is proven, not assumed.

Verify: `python3 -c "import yaml; yaml.safe_load(...)"` → `YAML OK`;
`python3 -m pytest -q` (sb-free baseline) → `1379 passed, 1 skipped in
15.62s` pre-merge, `1381 passed, 1 skipped in 15.30s` after merging
origin/main (slice J's counts-guard tests landed mid-flight; merged into
this branch pre-flip, telemetry rows both-kept); `python3 bootstrap.py
check --strict` → pre-flip it held only the designed born-red gate on
this card, `all checks passed` at this flip.

## 💡 Session idea

The lane un-skips the 15 manifest tests but still does not drive the two
LIVE-boot seams the liveboot card flagged (its 💡 explicitly asked to fold
this in): command-tree registration and the event registry. Guard recipe:
add one step to `.github/workflows/host-main-advisory.yml::pytest-with-host-main`
after the pytest step — `pip install discord.py`, then a one-call smoke
that imports the plugin `MANIFEST` (anchor:
`plugin/tests/test_manifest.py`'s `importorskip("sb.spec.manifest")`
module) and drives `sb.adapters.discord.command_tree.register_app_commands`
over it, one assert per plugin — catching #40-class command-shape
collisions the manifest tests cannot see. Second, smaller gap: an
advisory red is only visible in the Actions tab; nothing routes it to a
human. A `if: failure()` step that opens/refreshes a single pinned issue
(`gh issue` with the built-in `GITHUB_TOKEN`) would make "alert-only"
actually alert.

## ⟲ Previous-session review

previous-session review: `.sessions/2026-07-14-improve-counts-guard.md`
(slice J, PR #125 — landed on main mid-flight and merged into this
branch pre-flip, which is why this card's final sb-free tail reads 1381
where the pre-merge run read 1379). It and this slice are the same move
against the same failure mode in two mediums: counts in
`docs/current-state.md` rotted because "the repo already knows" the
truth but nothing compared them — the pin in `pytest.yml` rots because
host `main` already knows the truth and nothing compared against it
until this lane. Its scoping judgment transfers directly to this lane's
future: it deliberately UNGUARDED the self-referential suite-size claim
(an exact pin would red on every tests-touching PR); the analogue here
is that this lane deliberately does NOT gate merges — an unpinned-host
red on PRs would block idle for breaks idle didn't cause. Advisory
placement is that same "guard only what reds for the right reason" call.
No file overlap (tests/ + docs vs one new workflow); telemetry union
resolved both-kept at the pre-flip merge.
