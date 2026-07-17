# 2026-07-17 — tests: cover tools/play.py main() REPL loop (TEST-11)

> **Status:** `in-progress`

- **📊 Model:** neutral builder-agent · high · test coverage · play-entrypoint seat (REPL loop) · 2026-07-17T23:10Z (`date -u`)

## What / why

`tools/play.py` is the project's blessed manual-verify entrypoint — the small
text REPL that drives the real engine so a human (or agent) can actually *play*
a pack end to end. Its pure helpers (`new_session`, `advance`, `dispatch`,
`_buy`, `_load`, ...) are thoroughly covered by
`tests/test_play_entrypoint.py`, but the interactive `main()` loop itself
(argparse, the `--list-packs` short-circuit, the bad-pack/bad-code startup
guard, and the read-eval-print `while True` body with its between-command clock
advance and EOF/quit unwind) is only reached when a human runs the tool by
hand. End-to-end review measured it at **72%** — the biggest coverage hole in
game-facing code (`tools/play.py` lines ~470-523).

This slice (menu **TEST-11**, under the owner's overnight full-autonomy order)
closes that hole with a **test-only** scripted-session harness. Because the loop
reads stdin via `input()` and prints to stdout, it is driven by monkeypatching
`builtins.input` to feed a scripted command sequence and capturing the printed
transcript with `capsys`; the wall-clock (`time.monotonic`) is monkeypatched so
the between-command advance is deterministic. The harness asserts on stable
transcript substrings (never brittle full-string economy numbers) and on
`main()`'s integer return code (0 for a clean quit / EOF, 2 for a bad-pack
startup failure).

**No product code changes** — `tools/play.py` behavior is untouched; this slice
only *drives* the existing `main()` through paths that were previously exercised
only by hand.

## Verification

- `python3 -m pytest -q` — full suite, green.
- New `tests/test_play_repl.py` drives `main()` through: `--list-packs` (exit
  0), a scripted play session (status → offline → buy → save → load → help →
  invalid command → quit, exit 0), the EOF/empty-stdin unwind (exit 0), the
  between-command clock advance, and a bad-pack startup failure (exit 2).
- Coverage of `tools/play.py` rises from 72%.
- `python3 bootstrap.py check --strict` (only the born-red HOLD expected).

## Landing (born-red convention)

Card born RED (`in-progress`) in the first commit alongside
`control/claims/claude-test-play-main-repl.md`; then the test; card flipped
`complete` as the last commit to clear the born-red HOLD so substrate-gate goes
green and the landing workflow can merge on all-green. PR opened READY; the
worker does not merge its own PR.

## 💡 Session idea

The REPL harness now exercises the loop's structural paths. A natural follow-up
is a golden-transcript smoke test that pins one full scripted session's rendered
output for a fixed pack + seed, giving `main()` a regression tripwire on the
*shape* of what a player sees — kept behind a small vector the same way the
render views are pinned.
