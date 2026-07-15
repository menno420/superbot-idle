# EAP closeout walkthrough — superbot-idle (2026-07-14)

> **Status:** `owner-guidance`
>
> ORDER 009 deliverable: the owner's review entry point for this seat at the
> end of the EAP. Section C is the actionable part — every pending click and
> decision, each with a recommendation, risk class, and verify step.

## A. What this seat did during the EAP

One deterministic idle-game ENGINE plus 18 data-only theme packs, built
merge-on-green over ~120 lane PRs (2026-07-10 → 2026-07-14). Compact record:

- **Engine core** — generators → currency → upgrades → prestige →
  achievements, exact-integer offline progress (`tick` ≡ `offline_progress`
  proven), save/load persistence v2 with golden corpora, setup-code format
  with cross-language vectors. Founding waves PRs #1–#68.
- **Governance floor** — economy numbers pre-registered then SIM-graduated:
  VERDICT 038 flipped the table PROVISIONAL → SIM-PINNED (seven values, PR
  #93); A10 re-registered in trend form; re-tune path process ask filed
  (PR #100).
- **CI gates** — theme-gate (schema), substrate-gate (docs/session/heartbeat
  discipline), pytest on PR+push (ORDER 003, PR #74), CI skip-hole closed
  with a pinned-host job (PR #107), advisory host-main drift lane (PR #126).
- **EAP final night (ORDER 007)** — served via PRs #101–#111: catalog wave 5
  → 18 packs (#105/#109), feltness-floor SIM-REQUEST filed (#106), CI
  skip-hole closed (#107), docs groom + night outbox (#111).
- **Improvement wave 2026-07-14** — PRs #113–#128: REPL hardening (#115),
  bulk buy (#116), save/load in the REPL (#119), themed errors (#124), test
  ratchets (#114/#121/#123/#125), doc truth-fixes (#117/#128). Suite 1363 →
  1381.
- **Records true-up** — fleet-cleanup audit found the frozen heartbeat
  (INC-17, PR #112); ORDER 008 re-stamp cleared it (this landing). Depth:
  [fleet cleanup audit](audits/2026-07-13-fleet-cleanup-audit.md).

## B. Current state + how to run/verify

State: engine complete and playable via a text REPL; 18 theme packs; suite
1381 passed + 1 skipped (the skip is by-design sb-free; CI's
`pytest-with-host` job runs it against pinned superbot-next); kit v1.16.0
(v1.15.0 was correct when this walkthrough landed via PR #132; the bump
rode PR #134 `3df5449` later the same day — verify live with
`python3 bootstrap.py --version`).

```bash
pip install jsonschema                 # the one non-stdlib test dep
python3 -m pytest -q                   # expect: 1381 passed, 1 skipped
python3 tools/theme_gate.py themes     # expect: all 18 pack(s) valid (schema v1)
python3 bootstrap.py check --strict    # expect: green (exit 0)
```

Play it (drives the real engine + shipped render views):

```bash
python3 tools/play.py                     # default pack (egg-farm)
python3 tools/play.py --pack royal-bakery # a two-generator pack
python3 tools/play.py --list-packs        # show every shipped theme
```

In the loop: `status`, `shop`, `buy <id> [n|max]` (bulk buy — `max` takes
every affordable level), `prestige [do]`, `offline <secs>`, `wait <secs>`,
`achievements`, `save` / `load <blob>`, `pack <id>`, `help`, `quit`.

## C. OWNER ACTIONS checklist

1. **OA-003 — make `pytest` a required status check on main.**
   WHERE: https://github.com/menno420/superbot-idle/settings/branches →
   edit the `main` protection rule → required status checks → add `pytest`
   (alongside `substrate-gate` + `theme-gate`).
   **Recommendation: do it** — until then GREEN ≠ TESTED (a PR can merge
   with the suite red). RISK: ✅ safe / ↩️ reversible (uncheck to undo).
   VERIFY: the next PR shows `pytest` listed among Required checks.
2. **PRESTIGE_BONUS_PERCENT 10→25 — rule the SIM-PINNED re-tune path.**
   WHERE: the process ask in `control/outbox.md` (2026-07-13T18:45Z entry,
   PR #100), routed via fm. Option A: rule that re-tuning a SIM-PINNED value
   requires a fresh sim verdict (re-verdict path). Option B: allow direct
   re-tune. **Recommendation: A** — it preserves the pre-registration floor
   that kept this economy honest. RISK: ↩️ reversible (a ruling can be
   superseded). VERIFY: the ruling appears in the fm `docs/owner-queue.md`
   thread; this lane then files the first case (10→25).
3. **Timed-events Q-block.** WHERE: awaiting a fleet Q-number from fm;
   the underlying product question (next depth mechanic; scoping already at
   [timed-events scoping](design/timed-events-scoping.md)) can be answered
   directly. **Recommendation: answer the product question directly** if fm
   routing stays slow — safe default (a) timed-events next, numbers stay
   unregistered pending SIM-002. RISK: ✅ safe (docs/design decision only).
   VERIFY: an ORDER or Q-number lands in `control/inbox.md`.
4. **Generator-purchase Q-block.** WHERE: same routing; question + options
   in `control/outbox.md` (2026-07-13 generator-purchase entry). The primary
   idle growth verb is absent — tier2 content is dead until ruled.
   **Recommendation: option (a)** — add `purchase_generator` on a geometric
   curve, SIM-pinned before merge. RISK: ✅ safe to rule (the build itself
   is sim-gated). VERIFY: Q-number lands in `control/inbox.md`.
5. **Feltness-floor SIM-REQUEST routing (fm-side).** WHERE: filed via PR
   #106 (`control/outbox.md` 2026-07-13T22:42Z SIM-REQUEST); needs an fm
   SIM/Q-number + sim-lab routing. **Recommendation: nudge fm** — this
   unblocks the one confirmed player-facing defect (first three purchases
   change nothing visible). RISK: ✅ safe (routing only). VERIFY: SIM number
   assigned; lane then registers the spec section + pins the packet commit.

## D. 5-minute verify-it-yourself tour

1. (60s) Clone + `pip install jsonschema pytest pyyaml`, then
   `python3 -m pytest -q` → `1381 passed, 1 skipped`.
2. (30s) `python3 tools/theme_gate.py themes` → all 18 packs valid.
3. (2m) `python3 tools/play.py --pack dragon-hoard`: `status`, `shop`,
   `buy boost1 max`, `wait 120`, `save`, `load <blob>` (state round-trips),
   `prestige` (preview), `pack ramen-stand` (identical mechanics, different
   skin — the CORE/SKIN split live).
4. (60s) `python3 tools/simulate.py` — the SIM-001 harness that graduated
   the economy table replays the pre-registered scenarios on the real engine.
5. (30s) `python3 bootstrap.py check --strict` → exit 0: docs badged +
   reachable, session cards complete, heartbeat fresh.

## E. Handoff notes (batons)

- **Waiting on rulings, not code**: every backlog item is blocked on §C —
  the verdict-free improvement list was run DRY on 2026-07-14 (outbox
  improvement-wave entry, PR #128).
- **Baton 1**: when the feltness verdict is served, register the spec
  section + harness metrics in `docs/design/economy-v1.md` BEFORE the sim
  runs (recipe in the #106 SIM-REQUEST).
- **Baton 2**: catalog wave 6 is sanctioned standing filler (merge on
  theme-gate green alone); the advisory host-main lane (#126) flags upstream
  superbot-next drift daily — check its Actions tab on wake.
- **Next phase needs**: the generator-purchase verdict (unlocks the core
  growth verb + dead tier2 content), then timed-events (SIM-002) for depth.
- Read path for a resuming agent: `control/inbox.md` →
  `control/status.md` → `docs/AGENT_ORIENTATION.md` → `docs/current-state.md`.
