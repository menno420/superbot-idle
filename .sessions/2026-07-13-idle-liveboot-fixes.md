# 2026-07-13 — idle LIVE-boot fixes: events registration + `/idle` command-shape collision

> **Status:** `complete`

- **📊 Model:** neutral builder-agent · high · bugfix · idle-engine seat (two LIVE-boot source fixes) · 2026-07-13T10:19Z (`date -u`)

## What happened

Two idle-source bugs that only bite on the host's LIVE boot path (idle's own CI is
sb-free, `plugin/tests/test_manifest.py` opens with
`pytest.importorskip("sb.spec.manifest")`, so neither surfaced in idle CI). Both fixed
in `plugin/superbot_idle_plugin/manifest.py`.

**FIX 1 — events declared but never registered (P2).** The manifest declared
`EVENTS = (idle.tick, idle.offline_return)` but nothing called
`register_event_specs`, so the two EventSpecs never entered the runtime
`KNOWN_EVENTS` registry (`sb/spec/events.py`). The in-tree discipline is explicit:
`sb/manifest/xp.py` calls `register_event_specs(list(_EVENTS))` at module import
(`:165`) AND inside its `_ensure_refs`/`ENSURE_REFS` hook (`:180`) — the compiler's
test seam may clear `KNOWN_EVENTS` without evicting module caches, so re-registration
must be idempotent. Mirrored exactly here: imported `register_event_specs` from
`sb.spec.events` and called `register_event_specs(list(EVENTS))` both at module import
(after the `EVENTS` tuple) and inside `_ensure_refs`. `register_event_specs` is a no-op
on an identical re-registration (raises `EventRedefined` only on a *different* spec for
the same name), so the double-call is idempotent.

**FIX 3 — `/idle` was BOTH a root command AND a group parent (P1, live startup fails
before the gateway).** The manifest had a root `CommandSpec(name="idle",
kind=BOTH, group="")` routing the status panel AND three `group="idle"` subcommands
(`status`/`shop`/`prestige`). The host's `register_app_commands`
(`sb/adapters/discord/command_tree.py`) adds the standalone `idle` slash Command to the
tree (the root, kind BOTH) and — via `_group_for` — also builds an `idle` slash Group
for the three subcommands. Two tree entries named `idle` ⇒ discord.py
`CommandAlreadyRegistered: Command 'idle' already registered` at startup, before the
gateway connects.

**The fix — root `idle` → `kind=CommandKind.PREFIX`.** Chosen as the minimal,
least-player-visible shape (one field change). It preserves ALL prefix behavior
(`!idle`, `!idle status|shop|prestige`) and the status panel — the panel is still
routed by the prefix `idle` command and still registered via the `@panel` ref,
independent of the slash surface — while leaving the slash tree to the group. Result:
the slash surface is exactly `/idle status`, `/idle shop`, `/idle prestige` (the three
live render-forwarding views); the redundant standalone `/idle` slash (a static panel)
is dropped, since it is the entry that collided with the group and is fully reachable
via `!idle`. **⚑ This is a player-visible command-shape choice and is open to owner
redirect** (the alternative — keep the standalone `/idle` slash and make the three
subcommands prefix-only — is a larger 3-line diff that sacrifices the real game-view
slashes for a static-panel slash, strictly more disruptive).

Facets untouched by both fixes: SETTINGS, capabilities (`idle.game.play`), the panel
spec, the render-forwarding handlers, prefix routing, and all economy/balance.

## Verification

- `python3 -m pytest -q` (sb-free, CI-faithful) → **1260 passed, 1 skipped**.
- `python3 -m pytest -q` (with superbot-next importable) → **1275 passed**
  (`plugin/tests/test_manifest.py` runs; +4 new tests:
  `test_root_idle_is_prefix_only_no_slash_collision`,
  `test_events_registered_in_known_events_on_import`,
  `test_event_registration_is_idempotent`, plus the updated shape assertions).
- `python3 bootstrap.py check --strict` → all checks passed.
- `python3 tools/theme_gate.py themes` → all 15 packs valid (schema v1).
- **Host-side validation** (superbot-next importable; idle CI never does this):
  - `sb.app.plugin_host.load_plugins` over the fixed idle manifest + live host corpus
    → **`violations == ()`**, `idle` admitted, `loaded == ('superbot-idle-plugin==0.1.0 [idle]',)`.
    `manifest_stable_hash = sha256:48bf953dc6a91962e4d5841f85435b20eafa7f614f6916be2320be2c8646fe1c`
    (the surface changed vs the prior `963f2c…befb9265`, so the host pin must be re-pinned —
    done in the superbot-next re-vendor PR).
  - `sb.adapters.discord.command_tree.register_app_commands(_bot(), [MANIFEST])` over a
    real discord.py `commands.Bot` → returns 3 leaves, `/idle` is a single Group with
    subcommands `{status, shop, prestige}`, **no exception**. The pre-fix control
    (root reset to `kind=BOTH`) raises `CommandAlreadyRegistered: Command 'idle'
    already registered` — proving the fix removes the collision.
  - Events: `idle.tick` and `idle.offline_return` present in `KNOWN_EVENTS` after import.

## Landing (born-red convention)

Card born RED (`in-progress`) in the first commit alongside the telemetry row +
`control/claims/idle-liveboot-fixes.md`; then the two-fix manifest edit + the test
update; card flipped `complete` as the last commit. PR opened READY; NOT auto-merged
(worker does not merge its own PR). `@codex` question left in the PR body.

## 💡 Session idea

FIX 1 and FIX 3 are both LIVE-path-only bugs invisible to idle's sb-free CI — the same
class as the `capabilities` 3-part fix. The optional scheduled host-compile lane already
proposed there (`pip install 'superbot-next @ git+…' && pytest plugin/tests -q`, non-blocking)
would catch the events-registration miss AND a command-shape collision if it also drove
`register_app_commands` over the manifest against a real discord.py tree. Worth folding a
`register_app_commands` smoke into that same follow-up lane — a one-call assert per plugin.

## ⟲ Previous-session review

The capability-3part-fix (PR #85) closed the namespace-validator gap but only exercised
`load_plugins`; it did not drive the live command-tree registration or the event
registry, so FIX 1 and FIX 3 (both live-boot-only) survived it. This session drives both
live seams host-side. The forwarding/settings/capability facets it and inc2 built are
untouched; only the event-registration calls and the root command `kind` changed.

## Guard recipe

- **Events must register:** `register_event_specs(list(EVENTS))` at module import AND in
  `_ensure_refs` — guard `plugin/tests/test_manifest.py::test_events_registered_in_known_events_on_import`
  (anchor: `sb.spec.events.KNOWN_EVENTS`; mirror `sb/manifest/xp.py:165,180`).
- **No `/idle` root+group collision:** the root `idle` CommandSpec stays PREFIX-only —
  guard `plugin/tests/test_manifest.py::test_root_idle_is_prefix_only_no_slash_collision`
  (anchor: host `sb/adapters/discord/command_tree.py::register_app_commands`/`_group_for`).
