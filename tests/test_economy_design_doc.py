"""Doc-honesty guard for docs/design/economy-v1.md (slice (d)).

The economy design doc is a pre-registration contract (README § Integrity
floor): the Simulator (Q-0264 / SIM-001) consumes its section structure, and
its parameter table claims to mirror ``idle_engine/economy.py``. This module
keeps both claims true against drift — same pattern as the md↔json parity
test in ``tests/test_theme_schema.py``.
"""

import re
from pathlib import Path

from idle_engine import economy

REPO_ROOT = Path(__file__).resolve().parent.parent
DOC = REPO_ROOT / "docs" / "design" / "economy-v1.md"

#: The section contract SIM-001 executes against — renaming any of these
#: headers breaks the request the Simulator seat was handed.
REQUIRED_HEADERS = [
    "## Reference world",
    "## Pre-registered pacing targets",
    "## Cost-curve design",
    "## Provisional parameters",
    "## Simulation request — SIM-001 (Q-0264)",
    "### Scenarios",
    "### Inputs",
    "### Outputs",
    "### Acceptance criteria",
]

#: Every pre-registered economy constant must appear in the doc's parameter
#: table with its CURRENT engine value — tune the engine without
#: re-registering and this goes red (the pre-registration contract).
PINNED_PARAMETERS = [
    "UPGRADE_BASE_COST_SECONDS",
    "UPGRADE_COST_GROWTH_NUM",
    "UPGRADE_COST_GROWTH_DEN",
    "UPGRADE_EFFECT_PERCENT",
    "PRESTIGE_THRESHOLD",
    "PRESTIGE_AWARD_DIVISOR",
    "PRESTIGE_BONUS_PERCENT",
]


def doc_text() -> str:
    assert DOC.is_file(), f"{DOC} missing — the pre-registered economy design doc"
    return DOC.read_text(encoding="utf-8")


def test_doc_exists_and_headers_match_sim_contract():
    text = doc_text()
    missing = [h for h in REQUIRED_HEADERS if not re.search(rf"^{re.escape(h)}", text, re.M)]
    assert not missing, f"economy-v1.md lost sim-contract headers: {missing}"


def test_parameter_table_mirrors_engine_values():
    text = doc_text()
    stale = []
    for name in PINNED_PARAMETERS:
        value = getattr(economy, name)
        row = rf"\|\s*`{name}`\s*\|\s*{value}\s*\|"
        if not re.search(row, text):
            stale.append(f"{name}={value}")
    assert not stale, (
        "economy-v1.md parameter table out of sync with idle_engine/economy.py "
        f"(tune + re-register in the SAME PR): {stale}"
    )


def test_targets_and_acceptance_criteria_are_complete():
    text = doc_text()
    targets = set(re.findall(r"^\|\s*(T\d+)\s*\|", text, re.M))
    criteria = set(re.findall(r"^\|\s*(A\d+)\s*\|", text, re.M))
    assert targets == {f"T{i}" for i in range(1, 11)}, f"target rows drifted: {sorted(targets)}"
    assert criteria == {f"A{i}" for i in range(1, 11)}, f"criterion rows drifted: {sorted(criteria)}"
