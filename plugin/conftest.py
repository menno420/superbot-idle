"""Make the plugin/ dir importable so idle's root `pytest -q` can import
`superbot_idle_plugin` when collecting plugin/tests/.

Mirrors tests/conftest.py's REPO_ROOT insertion, scoped to this subtree: the
package lives beside this file, not at the repo root, so the search path this
conftest adds is plugin/ itself."""

import sys
from pathlib import Path

PLUGIN_ROOT = Path(__file__).resolve().parent
if str(PLUGIN_ROOT) not in sys.path:
    sys.path.insert(0, str(PLUGIN_ROOT))
