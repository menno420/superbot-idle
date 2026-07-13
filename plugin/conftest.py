"""Make BOTH the plugin package AND the idle engine importable so idle's root
`pytest -q` can collect plugin/tests/.

Two search paths are inserted:

- `plugin/` (this file's dir) — the `superbot_idle_plugin` package lives beside
  this file, not at the repo root; this mirrors tests/conftest.py's REPO_ROOT
  insertion, scoped to this subtree.
- the repo root — the render-forwarding handler (and its NON-gated forwarding
  test) import `idle_engine.render`, which lives at the repo root.
"""

import sys
from pathlib import Path

PLUGIN_ROOT = Path(__file__).resolve().parent
REPO_ROOT = PLUGIN_ROOT.parent

for _path in (PLUGIN_ROOT, REPO_ROOT):
    if str(_path) not in sys.path:
        sys.path.insert(0, str(_path))
