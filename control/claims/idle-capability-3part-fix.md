# Claim — `idle-capability-3part-fix`

- `idle-capability-3part-fix` · **plugin capability facet fix** — change the idle manifest's `capabilities` facet from the bare `("idle",)` to the host-required 3-part `("idle.game.play",)` so the plugin compiles against superbot-next's namespace validator (`_CAPABILITY_PARTS=3`); idle's sb-free CI never ran the host compiler so it never caught it · `plugin/superbot_idle_plugin/manifest.py` + `plugin/tests/test_manifest.py` · 2026-07-13
