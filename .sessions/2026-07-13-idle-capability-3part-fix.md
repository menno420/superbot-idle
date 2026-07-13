# 2026-07-13 — idle capability facet fix: bare `idle` → 3-part `idle.game.play`

> **Status:** `complete`

- **📊 Model:** neutral builder-agent · high · bugfix · idle-engine seat (plugin capability 3-part fix) · 2026-07-13T09:3xZ (`date -u`)

## What happened

The idle plugin manifest declared `capabilities=("idle",)`. superbot-next's host
namespace validator requires every CAPABILITY facet to be a 3-part `a.b.c` string
(`sb/namespace/validate.py` `_CAPABILITY_PARTS=3`; `sb/spec/authority.py:160-161`
`capability_not_3_part`). The bare single-token `idle` fails that format check, so
the idle plugin did **not** compile against superbot-next's real host — the joint
`load_plugins` compile emitted:

```
joint compile FORMAT_ERROR (namespace) capability:idle: capability_not_3_part
```

idle's own CI is sb-free (`plugin/tests/test_manifest.py` opens with
`pytest.importorskip("sb.spec.manifest")`), so the host compiler never ran here and
the blocker went unnoticed until superbot-next's host-side coexistence proof exercised it.

**The fix** (`plugin/superbot_idle_plugin/manifest.py`): `capabilities=("idle",)` →
`capabilities=("idle.game.play",)`. Everything else (the four CommandSpecs, the
status panel, SETTINGS, EVENTS, ENSURE_REFS) is unchanged.

**Capability string choice — `idle.game.play`.** Chosen to MATCH superbot-next's
established convention. Its governance registry (`sb/domain/governance/registry.py`)
declares every game subsystem's capability as `<subsystem>.game.<action>`:
`blackjack.game.play`, `casino.game.play`, `counting.game.play`, `chain.game.play`,
`deathmatch.game.challenge`, `rps_tournament.game.join`. idle is an idle **game**, its
subsystem key is `idle`, and `play` is the primary user action — so `idle.game.play`
is the exact convention-faithful slot. **This is a namespace choice and is open to
owner redirect** (e.g. `idle.game.tick`, `idle.play.core`); the mechanical requirement
is only that it be a valid non-reserved 3-part string.

## Verification

- `python3 -m pytest -q` → **1260 passed, 1 skipped** (the sb-gated
  `plugin/tests/test_manifest.py` module skips because superbot-next isn't installed
  in idle CI; `test_capabilities` updated to assert `("idle.game.play",)`).
- `python3 bootstrap.py check --strict --status-only` → control-status check passed.
- `python3 tools/theme_gate.py themes` → all 15 packs valid.
- **Best-effort host-compile validation** (idle's CI never does this): with
  superbot-next importable, ran its real `sb.app.plugin_host.load_plugins` over the
  fixed idle manifest + the live host corpus → **`violations == ()`**, `idle` admitted,
  `idle.status` panel resolves after `register_manifest_panels`.
  `manifest_stable_hash = sha256:963f2c3b5db77d23513747862e883ac6ca724b24814d8501c8de61e3befb9265`.

## Landing (born-red convention)

Card born RED (`in-progress`) in the first commit alongside the telemetry row +
`control/claims/idle-capability-3part-fix.md`; then the one-line manifest fix + the
test update; card flipped `complete` as the last commit. PR opened READY; NOT
auto-merged (worker does not merge its own PR).

## 💡 Session idea

idle's plugin CI is deliberately sb-free (`importorskip`), which is why a
host-invalid capability string shipped unnoticed. A tiny OPTIONAL CI lane —
`pip install 'superbot-next @ git+…' && pytest plugin/tests -q` on a schedule
(not blocking, not on the sb-free critical path) — would surface exactly this
class of host-contract drift at authoring time instead of at the host's
coexistence proof. Belongs as a follow-up order, not this fix.

## ⟲ Previous-session review

PLUG-001 inc2 (PR #78) declared `capabilities=("idle",)` and proved the plugin
against the host contract doc, but never ran the host's actual namespace
validator — the sb-free-CI gap this session closes. The forwarding/settings/events
seams it built are untouched here; only the capability facet string changed.
