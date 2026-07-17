#!/usr/bin/env python3
"""Deterministic generator for ``tests/vectors/render-embeds.v1.json``.

The committed JSON is the RENDER GOLDEN CORPUS: for every shipped theme
pack, the embed-shaped payload each render view
(``idle_engine.render``) produces at a FIXED, deterministic
``GameState``. It mirrors the repo's blessed regenerate-or-red vector
pattern (``tools/gen_setup_vectors.py`` / ``tools/gen_save_vectors.py``):
the suite (``tests/test_render_vectors.py``) asserts the committed file
is byte-identical to a fresh in-memory regeneration AND replays every
pack through the live render layer — so a silent SKIN/render regression
(a change to ``render.py`` OR to any ``themes/*.yaml`` pack that alters
player-facing embeds) reds a test instead of shipping unnoticed across
all packs at once.

Every embed here is produced BY the real render functions over the real
loaded theme packs; nothing is a hand-written literal. The generator is
pure and deterministic: the fixed ``GameState`` carries no wall clock
and no randomness (``render_status`` takes ``now`` as a fixed constant),
so the same tree always yields the same bytes. The corpus is
catalog-coupled BY DESIGN — its only inputs are the shipped
``themes/*.yaml`` packs and the render layer — so a drift red usually
means a pack or ``render.py`` changed.

Regenerate (after any deliberate render/pack change) with::

    python3 tools/gen_render_vectors.py

The fixed state (see :data:`STATE_RECIPE`) is chosen to exercise each
view's meaningful branches deterministically for every pack:

- generators owned (so ``status`` shows counts, per-second rates, and
  offline gains over the fixed ``now - last_seen`` span), with the LAST
  generator left at 0 so an upgrade targeting it renders the trap-buy
  ``requires`` annotation;
- upgrade levels varied across the roster (so ``shop`` shows a mix of
  levels and afford/lock marks at the fixed currency balance);
- milestones banked at a LOW point then the metrics bumped, so
  ``achievements`` shows all three marks — earned (✅), reached-but-not-
  yet-awarded (⏳), and locked (🔒) — across the owned/lifetime/prestige
  tracks;
- lifetime + prestige balances that leave ``prestige`` mid-progress.
"""

from __future__ import annotations

import json
import sys
from dataclasses import replace
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:  # runnable as a script from anywhere
    sys.path.insert(0, str(REPO_ROOT))

from idle_engine import GameState, load_theme  # noqa: E402
from idle_engine.achievements import award_milestones  # noqa: E402
from idle_engine.render import (  # noqa: E402
    render_achievements,
    render_prestige,
    render_shop,
    render_status,
)
from idle_engine.theme import Theme  # noqa: E402

VECTORS_PATH = REPO_ROOT / "tests" / "vectors" / "render-embeds.v1.json"
THEMES_DIR = REPO_ROOT / "themes"

#: The render views captured per pack, in a fixed order. ``shop`` and
#: ``prestige`` are ``None`` (serialized ``null``) for a pack that
#: declares no upgrades / no prestige block — captured so a pack GAINING
#: or LOSING one of those blocks reds the corpus too.
VIEWS = ("status", "shop", "prestige", "achievements")

#: The fixed, deterministic state recipe (no wall clock, no randomness).
#: Published in the document so a reader can see exactly what state the
#: golden embeds were rendered at.
STATE_RECIPE = {
    "last_seen": 1_000_000,
    "now": 1_003_600,  # last_seen + 3600s: a one-hour offline span
    "currency_balance": 50_000,
    "owned_total_at_award": 15,  # crosses the owned-10 milestone only
    "owned_total_displayed": 150,  # crosses owned-100 (owned-1000 stays locked)
    "lifetime_at_award": 1_500,  # crosses the lifetime-1,000 milestone only
    "lifetime_displayed": 150_000,  # crosses lifetime-100,000 (10,000,000 locked)
    "prestige_at_award": 3,  # crosses the prestige-1 milestone only
    "prestige_displayed": 7,  # crosses prestige-5 (prestige-25 stays locked)
    "upgrade_level_cycle": [0, 1, 2],  # level = index % 3 across the roster
}

#: The regenerate-or-red failure hint, surfaced verbatim by the consumer
#: suite so the red itself names the likely cause and the exact fix.
DRIFT_HINT = (
    "tests/vectors/render-embeds.v1.json drifted from the live render layer "
    "(regenerate-or-red). Did idle_engine/render.py change how a view is "
    "composed, or did a themes/*.yaml pack change its nouns/flavor/emoji "
    "(or was a pack added/removed)? That is the usual cause: the corpus is "
    "catalog-coupled by design — it pins what every pack renders. If the "
    "change is deliberate, regenerate and commit the file with: "
    "python3 tools/gen_render_vectors.py"
)


def catalog_pack_stems() -> list[str]:
    """Shipped pack filename stems (== theme ids, per the theme gate)."""
    stems = sorted(path.stem for path in THEMES_DIR.glob("*.yaml"))
    if not stems:
        raise RuntimeError(f"no theme packs found under {THEMES_DIR}")
    return stems


def _lifetime_currency(theme: Theme) -> str:
    """The currency the pack's lifetime milestone track measures.

    Mirrors ``Theme.milestone_specs``: the prestige track's measured
    currency when a prestige block is declared, else the deterministic
    fallback — the FIRST declared generator's produced currency.
    """
    if theme.prestige is not None:
        return theme.prestige.measures
    return next(iter(theme.generators.values())).produces


def _owned_for_total(theme: Theme, total: int) -> dict[str, int]:
    """Distribute ``total`` owned generators deterministically.

    The LAST generator is left at 0 (when the pack has more than one) so
    an upgrade targeting it renders the display-only ``requires`` trap-buy
    annotation — the un-owned-target branch of ``render_shop``.
    """
    gens = list(theme.generators.values())
    active = gens[:-1] if len(gens) > 1 else gens
    n = len(active)
    base, rem = divmod(total, n)
    return {
        g.generator_id: base + (1 if i < rem else 0) for i, g in enumerate(active)
    }


def build_state(theme: Theme) -> GameState:
    """The fixed, deterministic display state for one pack.

    Built in two moves so ``achievements`` exercises all three milestone
    marks: bank the low-threshold milestones via the REAL
    ``award_milestones`` at a low point, then bump the live metrics so the
    next rung is *reached but unbanked* while the top rung stays locked.
    """
    r = STATE_RECIPE
    lifetime_currency = _lifetime_currency(theme)
    prestige_currency = (
        theme.prestige.currency if theme.prestige is not None else None
    )
    balances = {cid: r["currency_balance"] for cid in theme.currencies}
    upgrades = {
        spec.spec_id: i % 3 for i, spec in enumerate(theme.upgrade_specs())
    }

    at_award = GameState(
        balances=balances,
        owned=_owned_for_total(theme, r["owned_total_at_award"]),
        last_seen=r["last_seen"],
        upgrades=upgrades,
        lifetime={lifetime_currency: r["lifetime_at_award"]},
        prestige=({prestige_currency: r["prestige_at_award"]} if prestige_currency else {}),
    )
    banked = award_milestones(at_award, theme.milestone_specs())
    return replace(
        banked,
        owned=_owned_for_total(theme, r["owned_total_displayed"]),
        lifetime={lifetime_currency: r["lifetime_displayed"]},
        prestige=({prestige_currency: r["prestige_displayed"]} if prestige_currency else {}),
    )


def render_views(theme: Theme) -> dict:
    """Every render view for one pack at the fixed state.

    ``shop`` / ``prestige`` come back ``None`` when the pack declares no
    such block — captured as-is so a pack gaining or losing the block reds.
    """
    state = build_state(theme)
    return {
        "status": render_status(state, theme, STATE_RECIPE["now"]),
        "shop": render_shop(state, theme),
        "prestige": render_prestige(state, theme),
        "achievements": render_achievements(state, theme),
    }


def render_pack(stem: str) -> dict:
    """The committed vector for one pack: its id and every rendered view."""
    theme = load_theme(THEMES_DIR / f"{stem}.yaml")
    return {"pack": stem, "theme_id": theme.theme_id, "views": render_views(theme)}


def build_document() -> dict:
    stems = catalog_pack_stems()
    vectors = [render_pack(stem) for stem in stems]
    embeds = sum(
        1 for v in vectors for view in VIEWS if v["views"][view] is not None
    )
    return {
        "format": "superbot-idle-render-vectors",
        "format_version": 1,
        "generated_by": (
            "tools/gen_render_vectors.py — DO NOT EDIT BY HAND; "
            "regenerate with: python3 tools/gen_render_vectors.py"
        ),
        "contract": "idle_engine/render.py",
        "views": list(VIEWS),
        "state_recipe": STATE_RECIPE,
        "themes": [v["theme_id"] for v in vectors],
        "counts": {"packs": len(vectors), "embeds": embeds},
        "vectors": vectors,
    }


def render() -> str:
    """The vector file's exact byte content (regenerate-or-red target)."""
    return json.dumps(build_document(), indent=2, ensure_ascii=True) + "\n"


def main() -> int:
    VECTORS_PATH.parent.mkdir(parents=True, exist_ok=True)
    content = render()
    VECTORS_PATH.write_text(content, encoding="utf-8")
    doc = build_document()
    print(
        f"wrote {VECTORS_PATH.relative_to(REPO_ROOT)}: "
        + ", ".join(f"{k}={v}" for k, v in doc["counts"].items())
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
