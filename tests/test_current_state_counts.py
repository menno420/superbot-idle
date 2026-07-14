"""Counts guard for docs/current-state.md — doc claims vs ground truth.

The current-state doc is a hand-groomed living ledger whose count claims
drift every merge: both requesting cards
(.sessions/2026-07-13-truthfix-current-state.md,
.sessions/2026-07-13-eap-night-groom.md) watched the pack total and the
setup-vector tallies go stale (15->18 packs, 75->90 valid vectors) with
no gate noticing. This module pins the machine-checkable counts so a
drifted doc turns CI red instead of waiting for the next groom — same
doc-honesty pattern as ``tests/test_economy_design_doc.py``.

Guarded (the clean, non-self-referential counts only):

1. **Pack count** — the ``**Theme catalog: N packs**`` bullet vs
   ``len(themes/*.yaml)``.
2. **Setup-vector counts** — the ``(N vectors: N valid ... N tolerance,
   N error)`` parenthetical vs the ``counts`` dict in
   ``tests/vectors/setup-codes.v1.json`` (itself pinned to the live
   codec by the regenerate-or-red test in ``tests/test_setup_vectors.py``,
   so doc -> vector file -> codec is a closed chain).

Deliberately UNGUARDED: the suite-size claim ("1363 passing", "1378 in
CI"). It is self-referential — adding a test (including this one)
changes the collected count — so an exact pin would red on every
tests-touching PR for a doc that is groomed, not generated. Pytest
counts stay prose.

Extraction is regex anchored to the stable claim phrases, NOT full-prose
parsing (a brittle parser is worse than no guard). Each anchor must
match EXACTLY ONCE: zero matches means the phrase itself was reworded
(re-anchor the regex here in the same PR that rewords the doc); two+
matches means the anchor went ambiguous. Historical lines like "15 -> 18
packs" or "setup vectors 75 -> 90 valid" do not match the anchors.
"""

import json
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DOC = REPO_ROOT / "docs" / "current-state.md"
THEMES_DIR = REPO_ROOT / "themes"
VECTORS_PATH = REPO_ROOT / "tests" / "vectors" / "setup-codes.v1.json"

#: The catalog bullet: ``- **Theme catalog: 18 packs**, ...``.
PACK_CLAIM_RE = re.compile(r"\*\*Theme catalog: (\d+) packs\*\*")

#: The vector parenthetical, which wraps across lines:
#: ``(224 vectors: 90 valid with layer-by-layer intermediates,
#: 109 tolerance, 25 error; ...)``. ``[^()]*?`` keeps the match inside
#: the parenthetical (and tolerant of the prose between the numbers)
#: while spanning the line wrap.
VECTOR_CLAIM_RE = re.compile(
    r"\((\d+) vectors: (\d+) valid\b[^()]*?\b(\d+) tolerance,\s+(\d+) error\b"
)

REGROOM_HINT = (
    "re-groom that docs/current-state.md line to the ground-truth number "
    "(counts only — source wins over the doc, so the doc moves, not the source)"
)


def doc_text() -> str:
    assert DOC.is_file(), f"{DOC} missing — the living status ledger"
    return DOC.read_text(encoding="utf-8")


def _single_match(pattern: re.Pattern, text: str, claim: str) -> re.Match:
    matches = list(pattern.finditer(text))
    assert matches, (
        f"docs/current-state.md no longer contains the {claim} claim phrase "
        f"(anchor: {pattern.pattern!r}) — if the doc was reworded, re-anchor "
        "the regex in tests/test_current_state_counts.py in the same PR"
    )
    assert len(matches) == 1, (
        f"the {claim} anchor matched {len(matches)} times in "
        f"docs/current-state.md — anchor went ambiguous, tighten it in "
        "tests/test_current_state_counts.py"
    )
    return matches[0]


def test_pack_count_claim_matches_shipped_catalog():
    shipped = len(sorted(THEMES_DIR.glob("*.yaml")))
    claimed = int(_single_match(PACK_CLAIM_RE, doc_text(), "pack-count").group(1))
    assert claimed == shipped, (
        f"docs/current-state.md claims 'Theme catalog: {claimed} packs' but "
        f"themes/*.yaml ships {shipped} — {REGROOM_HINT}"
    )


def test_setup_vector_count_claims_match_vector_file():
    counts = json.loads(VECTORS_PATH.read_text(encoding="utf-8"))["counts"]
    truth = {
        "total": counts["valid"] + counts["tolerance"] + counts["errors"],
        "valid": counts["valid"],
        "tolerance": counts["tolerance"],
        "error": counts["errors"],
    }
    match = _single_match(VECTOR_CLAIM_RE, doc_text(), "setup-vector-count")
    claimed = {
        "total": int(match.group(1)),
        "valid": int(match.group(2)),
        "tolerance": int(match.group(3)),
        "error": int(match.group(4)),
    }
    stale = {k: (claimed[k], truth[k]) for k in truth if claimed[k] != truth[k]}
    assert not stale, (
        "docs/current-state.md setup-vector parenthetical is out of sync with "
        "the counts dict in tests/vectors/setup-codes.v1.json "
        f"(claimed != truth: {stale}) — {REGROOM_HINT}"
    )
