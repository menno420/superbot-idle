# 2026-07-14 — REPL hardening: negative-time input + post-prestige re-grant

> **Status:** `complete`

- **📊 Model:** fable-5 · medium · bugfix · REPL hardening (negative-time input + post-prestige re-grant) · 2026-07-14 · tools/play.py + its tests only (ZERO engine/economy change)

## What this session is doing

Improvement-wave slice A (owner directive 2026-07-14): fix two REPRODUCED
player-facing bugs in the `tools/play.py` REPL, entrypoint-local only —
no engine, no economy number, no SIM-PINNED constant touched. Claimed first
per `control/claims/README.md`
(`control/claims/claude-improve-repl-hardening.md`; deleted in this card's
flip commit).

1. **Negative-seconds crash.** `wait -5` / `offline -5`: `int("-5")` parses
   fine in `dispatch` (`tools/play.py` ~L289-295), then `advance` /
   `go_offline` raise `ValueError("seconds must be >= 0")` (~L150/L162) —
   uncaught, so the full traceback kills the REPL. `int("abc")` IS already
   handled by the same block. Fix: validate `seconds >= 0` at the dispatch
   layer and return the existing `Usage: <verb> <seconds>` message style
   instead of propagating.
2. **Post-prestige bricked run.** `prestige do` → `apply_prestige` correctly
   wipes `owned` (engine semantics, `idle_engine/prestige.py` ~L92 — NOT
   touched), but `_prestige` (`tools/play.py` ~L236-246) never re-applies the
   entrypoint's starting grant. Result: 0 generators, +0/s, and no purchase
   path back — the run is unrecoverable. Fix REPL-LOCAL: after
   `apply_prestige`, re-seed the starting grant (`start_count`) exactly as
   session startup does. The module docstring (`tools/play.py` L15-18)
   already documents the starting grant as "a RUNTIME entrypoint choice …
   the engine has no generator purchase verb yet" — this fix is that same
   documented runtime choice applied at the one other place a run begins.
   The output says so: "run reset — starting generators re-granted".

Tests land beside the existing graceful-input test
(`tests/test_play_entrypoint.py::test_dispatch_unknown_and_bad_buy_are_graceful`,
~L83): negative `wait`/`offline` stays alive with a usage message;
a post-prestige session has the starting grant and accrues rate again.

## What happened

Both bugs reproduced FIRST at branch base `a537946` with scripted pipe
sessions, then fixed, then the same scripts re-run clean. `tools/play.py`
and `tests/test_play_entrypoint.py` only (PR #115, implementation commit
`bcb7f53`).

- **Repro before (bug 1):** `printf 'wait -5\n' | python3 tools/play.py` →
  `Traceback (most recent call last): … File "tools/play.py", line 151, in
  advance / raise ValueError("seconds must be >= 0") / ValueError: seconds
  must be >= 0` — REPL dead. **After:** `> Usage: wait <seconds> (seconds
  must be >= 0)` (and the same for `offline -5`), next prompt arrives,
  session alive. Fix is two lines in `dispatch`: an `if seconds < 0` branch
  right after the existing `int(arg)` try/except, same message family.
- **Repro before (bug 2):** `wait 150000` → `prestige do` → status shows
  `🥚 eggs: 0 / 🥇 golden eggs: 1 / 🐔 chicken coop: × 0`, and `wait 60`
  still shows `eggs: 0 … × 0` — 0/s forever, no purchase path back.
  **After:** `Prestiged — bonus banked. / run reset — starting generators
  re-granted / … 🐔 chicken coop: × 1 · +1/s`, and `wait 60` accrues
  `eggs: 60`. `_prestige` now takes `start_count` (threaded from
  `dispatch`, which already had it for `pack`) and re-seeds `owned` via
  `dataclasses.replace` exactly as `new_session` does; `start_count 0`
  (the legal empty-save choice) grants nothing and skips the line.
- **Tests:** `test_dispatch_negative_seconds_is_graceful` (both verbs, same
  session object returned, message asserted) and
  `test_prestige_do_regrants_starting_generators` (eligibility crossed via
  `spec.threshold + 1` so no economy number is hardcoded; asserts the
  re-grant line, `owned == {"tier1": 1}`, and that a post-reset `wait 10`
  accrues `primary` again).

Zero engine / theme / SIM-PINNED / A10 touches; `idle_engine/prestige.py`
wipe semantics preserved as-is.

Verify: `python3 -m pytest -q` → `1365 passed, 1 skipped in 15.10s`
(was 1363+2 born here); `python3 -m pytest tests/test_play_entrypoint.py
-q` → `27 passed in 0.26s`; `python3 bootstrap.py check --strict` → the
born-red designed hold on this very card pre-flip ("This red is the
designed hold, not a defect"), green once this flip lands.

## 💡 Session idea

Both bugs share one shape: a code path only a HUMAN at the prompt ever
takes (hostile arg, full prestige loop) that no unit test walked end to
end. Guard recipe: a `repl-fuzz` smoke test that pipes a scripted
adversarial session through the REAL loop —
`subprocess.run([sys.executable, "tools/play.py"], input=...)` with a
script covering every verb in `_HELP` plus hostile args (`wait -5`,
`offline -1e9`, `buy`, `pack nonesuch`, `prestige do` pre- and
post-eligibility) — asserting exit code 0 and `"Traceback" not in output`.
Anchors: sits beside `tests/test_play_entrypoint.py` (which deliberately
never spawns the loop — this would be the one test that does), script
verbs enumerated from `_HELP` in `tools/play.py` so a new verb without
fuzz coverage fails loudly; the `prestige do` leg would have caught bug 2
because the bricked state renders `× 0` where the script expects
production to resume.

## ⟲ Previous-session review

previous-session review: the EAP night-close groom
(`.sessions/2026-07-13-eap-night-groom.md`) is why this slice could start
from a truthful map — its groomed `docs/current-state.md` (suite at 1363
sb-free, SIM-PINNED floor with graduation shipped, in-flight: none) matched
what `git reset --hard origin/main` actually produced, to the digit; the
1363→1365 delta here is exactly this card's two born tests. Its 💡
(`docs-counts` advisory checker) would already be nagging about that same
delta — this session is a live example of the drift it wants to catch, one
night later. Process note it modeled and this card copied: re-verify every
inherited claim at the branch base before writing, and reproduce before
fixing — both bugs were captured verbatim at `a537946` before a line
changed, which made the PR's Before/After trivially honest.
