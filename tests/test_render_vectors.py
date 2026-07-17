"""Render golden corpus — regenerate-or-red + per-pack replay.

``tests/vectors/render-embeds.v1.json`` pins the embed-shaped payload
every render view (``idle_engine.render``) produces for every shipped
theme pack at a FIXED, deterministic ``GameState``;
``tools/gen_render_vectors.py`` generates it FROM the live render layer
over the real packs. Two duties here, mirroring
``tests/test_setup_vectors.py`` / ``tests/test_save_vectors.py``:

1. **Regenerate-or-red** (the repo's md-parity pattern applied to JSON):
   the committed file must be byte-identical to a fresh in-memory
   regeneration — change ``render.py``, a ``themes/*.yaml`` pack, or the
   file alone and this reds until ``python3 tools/gen_render_vectors.py``
   is re-run and committed. A silent SKIN/render regression therefore
   CANNOT land across all packs unnoticed.
2. **Consumer replay**: every committed pack vector is re-rendered
   through the live render layer (at the same fixed state) and asserted
   equal, and every captured embed is re-validated against the render
   layer's own budget gate — so the corpus is proven reproducible, not
   just self-consistent.
"""

import json
from pathlib import Path

import pytest

from idle_engine.render import validate_embed
from tools.gen_render_vectors import (
    DRIFT_HINT,
    STATE_RECIPE,
    VECTORS_PATH,
    VIEWS,
    render,
    render_pack,
)

REPO_ROOT = Path(__file__).resolve().parent.parent
THEMES_DIR = REPO_ROOT / "themes"

DOC = json.loads(VECTORS_PATH.read_text(encoding="utf-8"))
VECTORS = DOC["vectors"]

_ids = lambda vectors: [v["pack"] for v in vectors]  # noqa: E731


# --- regenerate-or-red ---------------------------------------------------------


def _assert_byte_identical_to_regeneration(committed: str) -> None:
    assert committed == render(), DRIFT_HINT


def test_committed_vector_file_is_byte_identical_to_regeneration():
    _assert_byte_identical_to_regeneration(VECTORS_PATH.read_text(encoding="utf-8"))


def test_drift_red_names_the_likely_cause_and_the_regen_command():
    # The hint is the developer-facing contract of a drift red: it must
    # name the likely cause (render.py or a pack changed) and the fix.
    with pytest.raises(AssertionError) as excinfo:
        _assert_byte_identical_to_regeneration(render() + "# drifted\n")
    message = str(excinfo.value)
    assert "idle_engine/render.py" in message
    assert "themes/*.yaml" in message
    assert "python3 tools/gen_render_vectors.py" in message


# --- file shape: what the corpus pins ------------------------------------------


def test_document_pins_the_corpus_constants():
    assert DOC["format"] == "superbot-idle-render-vectors"
    assert DOC["format_version"] == 1
    assert DOC["contract"] == "idle_engine/render.py"
    assert DOC["views"] == list(VIEWS)
    assert DOC["state_recipe"] == STATE_RECIPE


def test_counts_match_the_vectors():
    embeds = sum(
        1 for v in VECTORS for view in VIEWS if v["views"][view] is not None
    )
    assert DOC["counts"] == {"packs": len(VECTORS), "embeds": embeds}
    assert len(VECTORS) and embeds


def test_every_shipped_pack_has_a_vector():
    # This is the red a pack add/remove hits first — carry the same hint.
    shipped = sorted(path.stem for path in THEMES_DIR.glob("*.yaml"))
    assert [v["pack"] for v in VECTORS] == shipped, DRIFT_HINT
    assert DOC["themes"] == [v["theme_id"] for v in VECTORS]


def test_every_vector_captures_every_view():
    for vector in VECTORS:
        assert set(vector["views"]) == set(VIEWS)
        # status and achievements are mechanics — always rendered, never null.
        assert vector["views"]["status"] is not None
        assert vector["views"]["achievements"] is not None


# --- consumer replay: re-render each pack and compare ---------------------------


@pytest.mark.parametrize("vector", VECTORS, ids=_ids(VECTORS))
def test_pack_re_renders_to_its_committed_views(vector):
    # Replay through the live render layer at the same fixed state: the
    # committed embeds must reproduce exactly, view for view.
    assert render_pack(vector["pack"]) == vector


@pytest.mark.parametrize("vector", VECTORS, ids=_ids(VECTORS))
def test_every_committed_embed_satisfies_the_budget_gate(vector):
    # Independent re-validation through the render layer's own gate — a
    # captured embed that busts a cap would be a corpus we must never bless.
    for view in VIEWS:
        embed = vector["views"][view]
        if embed is not None:
            assert validate_embed(embed) == embed
