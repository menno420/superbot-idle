"""CORE/SKIN guard: engine source must contain zero theme vocabulary.

The engine is theme-agnostic by contract (README, CONVENTIONS). This
test greps every engine module (and the generic theme-gate tool) for
egg-farm nouns; any hit means theme content leaked into core.
"""

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# Word-boundary match so e.g. "when" does not trip on "hen".
FORBIDDEN_NOUNS = re.compile(
    r"\b(egg|eggs|chicken|chickens|coop|coops|farm|farms|hen|hens)\b",
    re.IGNORECASE,
)

THEME_AGNOSTIC_SOURCES = sorted(REPO_ROOT.glob("idle_engine/**/*.py")) + [
    REPO_ROOT / "tools" / "theme_gate.py",
]


def test_guard_scans_a_nonempty_engine():
    assert len(THEME_AGNOSTIC_SOURCES) >= 4  # package + state + engine + theme + tool


def test_engine_sources_contain_no_theme_nouns():
    violations = []
    for source in THEME_AGNOSTIC_SOURCES:
        for lineno, line in enumerate(source.read_text(encoding="utf-8").splitlines(), 1):
            match = FORBIDDEN_NOUNS.search(line)
            if match:
                violations.append(f"{source.relative_to(REPO_ROOT)}:{lineno}: {match.group(0)!r}")
    assert not violations, "theme nouns leaked into engine core:\n" + "\n".join(violations)


def test_guard_pattern_actually_catches_nouns():
    # Self-check that the guard is not vacuous.
    assert FORBIDDEN_NOUNS.search("a chicken coop")
    assert FORBIDDEN_NOUNS.search("Egg Farm")
    assert not FORBIDDEN_NOUNS.search("when the tick happens")
