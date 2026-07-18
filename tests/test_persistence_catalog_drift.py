"""Save × catalog-drift: a save is catalog-agnostic opaque data.

The CORE/SKIN seam promises that a ``GameState`` save carries only opaque
ids and that the engine reads state STRICTLY through the current spec
list — :func:`idle_engine.engine.production_per_second` iterates the
``specs`` it is passed and looks each up in the state
(``state.owned.get(spec.spec_id, 0)``), never the reverse; the render
layer iterates ``theme.currencies``/``theme.generators``/
``theme.upgrades``. So a save written before a pack edit — a generator,
currency or upgrade renamed or removed — must still load and run: the
ids the current catalog no longer knows are INERT (they produce nothing,
ride a ``tick`` through untouched, and never crash a render), while the
recognized ids behave exactly as if the stale ones were absent.

``tests/test_persistence.py`` § 6 only round-trips a save WITHIN the same
theme (``_play`` builds the state from that theme's own spec ids, so no
id is ever stale). These tests pin the untouched case: a loaded save
carrying ids ABSENT from the current catalog. They are robustness pins,
not a bug fix — the behavior is correct today; the gap was coverage. The
pins have teeth: an "optimization" that iterated ``state.owned`` instead
of the spec list, or a render layer that read state keys directly, would
break graceful degradation and turn these red.

Known wrinkle, deliberately NOT pinned here (see the session card): the
``owned``-kind milestone metric is ``sum(state.owned.values())``, so a
stale generator id DOES count toward the "total generators owned"
milestone. That is the one place a stale id leaks past the current
catalog; whether it is wrong is a design judgment call routed as a
follow-up, so the render-view test below asserts only that
``render_achievements`` does not crash, never that its numbers are
unchanged.
"""

from dataclasses import replace
from pathlib import Path

import pytest

from idle_engine import GameState, load_theme
from idle_engine.achievements import award_milestones
from idle_engine.engine import production_per_second, tick
from idle_engine.persistence import dump_state, load_state
from idle_engine.render import render_achievements, render_shop, render_status

REPO_THEMES = Path(__file__).resolve().parent.parent / "themes"

# Ids no current catalog declares — the stale entries a pre-edit save carries.
_GHOST_GEN = "__ghost_gen__"
_GHOST_CURRENCY = "__ghost_currency__"
_GHOST_UPGRADE = "__ghost_upgrade__"
_GHOST_PRESTIGE = "__ghost_prestige__"
_GHOST_MILESTONE = "__ghost_milestone__"


def _specs(theme):
    """The four engine spec lists a theme derives (prestige as a 0/1-list)."""
    prestige = theme.prestige_spec()
    return (
        theme.generator_specs(),
        theme.upgrade_specs(),
        [prestige] if prestige is not None else [],
        theme.milestone_specs(),
    )


def _clean_state(theme) -> GameState:
    """A realistic non-empty save built purely from ``theme``'s own ids."""
    gens, ups, prs, mss = _specs(theme)
    owned = {spec.spec_id: i + 1 for i, spec in enumerate(gens)}
    state = GameState(owned=owned)
    state = tick(state, gens, 3600, ups, prs, mss)  # accrue an hour of income
    return award_milestones(state, mss)  # bank whatever the hour reached


def _with_stale(state: GameState) -> GameState:
    """The same save as it would read after a catalog edit dropped some ids."""
    return replace(
        state,
        owned={**state.owned, _GHOST_GEN: 99},
        balances={**state.balances, _GHOST_CURRENCY: 12_345},
        upgrades={**state.upgrades, _GHOST_UPGRADE: 7},
        lifetime={**state.lifetime, _GHOST_CURRENCY: 88},
        prestige={**state.prestige, _GHOST_PRESTIGE: 3},
        milestones={**state.milestones, _GHOST_MILESTONE: 1},
    )


@pytest.mark.parametrize(
    "path", sorted(REPO_THEMES.glob("*.yaml")), ids=lambda p: p.stem
)
def test_catalog_drift_leaves_production_and_render_intact(path):
    """Stale ids are inert: production/tick unchanged, render never crashes."""
    theme = load_theme(path)
    gens, ups, prs, mss = _specs(theme)
    clean = _clean_state(theme)
    stale = _with_stale(clean)

    # (a) Production reads through the spec list — the stale ids add nothing.
    assert production_per_second(stale, gens, ups, prs, mss) == production_per_second(
        clean, gens, ups, prs, mss
    )

    # (b) A tick credits recognized currencies identically and leaves the
    #     stale entries untouched (no generator produces them, so
    #     with_earnings never names them).
    ticked_clean = tick(clean, gens, 60, ups, prs, mss)
    ticked_stale = tick(stale, gens, 60, ups, prs, mss)
    for currency, amount in ticked_clean.balances.items():
        assert ticked_stale.balances[currency] == amount
    assert ticked_stale.balances[_GHOST_CURRENCY] == 12_345
    assert ticked_stale.lifetime[_GHOST_CURRENCY] == 88
    assert ticked_stale.upgrades[_GHOST_UPGRADE] == 7
    assert ticked_stale.prestige[_GHOST_PRESTIGE] == 3
    assert ticked_stale.milestones[_GHOST_MILESTONE] == 1

    # (c) Every render view survives a stale-carrying state (validate_embed
    #     runs inside each; returning a dict — or None for a pack with no
    #     shop — proves no budget/lookup crash). Numbers are intentionally
    #     not pinned here: render_achievements' owned metric sees the stale
    #     generator (documented wrinkle), so only no-crash is asserted.
    now = clean.last_seen + 100  # a positive offline span for the status view
    status = render_status(stale, theme, now)
    assert isinstance(status, dict) and status["fields"]
    shop = render_shop(stale, theme)
    assert shop is None or isinstance(shop, dict)
    achievements = render_achievements(stale, theme)
    assert isinstance(achievements, dict) and achievements["fields"]


def test_stale_owned_ids_produce_nothing():
    """A billion phantom generators add exactly zero to production.

    Pins the direction of the read: the rate is a sum over the passed
    ``specs``, so an ``owned`` count for an id no spec names contributes
    nothing — no matter how large.
    """
    theme = load_theme(REPO_THEMES / "egg-farm.yaml")
    gens = theme.generator_specs()
    base = GameState(owned={gens[0].spec_id: 1})
    phantom = replace(base, owned={**base.owned, _GHOST_GEN: 1_000_000_000})
    assert production_per_second(phantom, gens) == production_per_second(base, gens)


def test_stale_save_round_trips_as_opaque_data():
    """The save codec never validates ids against a catalog.

    Ids absent from every pack survive ``load(dump(...))`` intact, so a
    save written under one catalog is loadable under another — the codec
    treats every mapping key as opaque data.
    """
    state = GameState(
        balances={_GHOST_CURRENCY: 7},
        owned={_GHOST_GEN: 5},
        upgrades={_GHOST_UPGRADE: 2},
        lifetime={_GHOST_CURRENCY: 7},
        prestige={_GHOST_PRESTIGE: 1},
        milestones={_GHOST_MILESTONE: 1},
    )
    assert load_state(dump_state(state)) == state
