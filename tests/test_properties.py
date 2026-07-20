"""Property/invariant tests — randomized but DETERMINISTIC (fixed seeds).

Deepening slice: instead of pinning single examples, these tests sweep
seeded-random rosters, durations, states and corruptions across the
engine's published invariants:

1. **Tick/offline equivalence** — for any roster and any partition of a
   span into ticks, summed tick earnings equal the single closed-form
   ``offline_progress`` credit, exactly (integer math, no drift).
2. **Determinism** — the same seed drives byte-identical GameState
   trajectories across two independent runs, for every shipped pack —
   snapshotted in the PUBLISHED save format (``dump_state``), so the
   suite pins the exact bytes consumers will store.
3. **Monotonicity/conservation** — balances never go negative; spending
   never touches lifetime; prestige awards are monotone in lifetime;
   a prestige reset never increases any run balance.
4. **Render budget fuzz** — extreme states x all shipped packs x every
   view always pass ``validate_embed``; the themed-overflow policy
   still reds on a deliberately broken pack.
5. **Setup-code fuzz** — random valid configs round-trip; seeded
   corruptions of valid codes either raise a documented
   :class:`SetupCodeError` subclass or decode to the ORIGINAL config
   (look-alike/case folding); a crc16 collision decoding to a
   DIFFERENT config is possible in principle — counted, bounded, and
   reported, never any other outcome.

Randomness is stdlib-only (``random.Random(FIXED_SEED)`` instances,
never the global RNG) so CI runs are reproducible byte-for-byte — the
repo deliberately takes no ``hypothesis`` dependency.
"""

import dataclasses
import string
from pathlib import Path
from random import Random

import pytest

from idle_engine import GameState, load_theme
from idle_engine.achievements import MilestoneSpec, award_milestones
from idle_engine.engine import (
    apply_offline_progress,
    offline_progress,
    production_per_second,
    tick,
)
from idle_engine.persistence import dump_state
from idle_engine.prestige import (
    PrestigeSpec,
    apply_prestige,
    prestige_award,
    prestige_eligible,
)
from idle_engine.provisioning import (
    SetupCodeError,
    SetupConfig,
    decode_setup,
    encode_setup,
)
from idle_engine.render import (
    DESCRIPTION_LIMIT,
    FIELD_NAME_LIMIT,
    FIELD_VALUE_LIMIT,
    MAX_FIELDS,
    TITLE_LIMIT,
    RenderBudgetError,
    render_achievements,
    render_prestige,
    render_shop,
    render_status,
)
from idle_engine.state import GeneratorSpec
from idle_engine.theme import ThemeLabels
from idle_engine.upgrades import UpgradeSpec, purchase_upgrade, upgrade_cost

REPO_ROOT = Path(__file__).resolve().parent.parent
THEMES_DIR = REPO_ROOT / "themes"
THEME_PATHS = sorted(THEMES_DIR.glob("*.yaml"))
THEME_IDS = [path.stem for path in THEME_PATHS]

assert len(THEME_PATHS) == 21, "property suite expects the 21-pack catalog"


# --- seeded roster builders ---------------------------------------------------


def _random_roster(rng: Random):
    """A random but valid mechanical roster + a state that owns some of it."""
    n_currencies = rng.randint(1, 3)
    currencies = [f"cur{i}" for i in range(n_currencies)]
    n_generators = rng.randint(1, 4)
    gen_specs = [
        GeneratorSpec(
            spec_id=f"gen{i}",
            produces=rng.choice(currencies),
            base_rate=rng.randint(1, 1_000),
            # the theme lane's full schema-declared bound range (90..110,
            # bounded-multipliers slice) sweeps through every invariant
            rate_multiplier_pct=rng.randint(90, 110),
        )
        for i in range(n_generators)
    ]
    upgrade_specs = []
    for i in range(rng.randint(0, 3)):
        target = rng.choice(gen_specs)
        upgrade_specs.append(
            UpgradeSpec(
                spec_id=f"up{i}",
                cost_currency=target.produces,
                base_cost=rng.randint(1, 10_000),
                cost_growth_num=rng.randint(100, 130),
                cost_growth_den=100,
                target=target.spec_id,
                effect_percent=rng.randint(1, 100),
            )
        )
    prestige_specs = []
    if n_currencies >= 2 and rng.random() < 0.8:
        threshold = rng.randint(1_000, 1_000_000)
        prestige_specs.append(
            PrestigeSpec(
                awards=currencies[-1],
                measures=currencies[0],
                threshold=threshold,
                award_divisor=rng.randint(1, threshold),
                bonus_percent=rng.randint(0, 25),
            )
        )
    milestone_specs = []
    for i in range(rng.randint(0, 4)):
        kind = rng.choice(("owned", "lifetime", "prestige"))
        milestone_specs.append(
            MilestoneSpec(
                spec_id=f"ms{i}",
                kind=kind,
                subject="" if kind == "owned" else rng.choice(currencies),
                threshold=rng.randint(1, 1_000_000),
                bonus_percent=rng.randint(0, 25),
            )
        )
    state = GameState(
        balances={c: rng.randint(0, 10**9) for c in currencies},
        owned={g.spec_id: rng.randint(0, 50) for g in gen_specs},
        last_seen=rng.randint(0, 10**9),
        upgrades={u.spec_id: rng.randint(0, 20) for u in upgrade_specs},
        lifetime={c: rng.randint(0, 10**12) for c in currencies},
        prestige={p.awards: rng.randint(0, 30) for p in prestige_specs},
        milestones={
            m.spec_id: 1 for m in milestone_specs if rng.random() < 0.5
        },
    )
    return state, gen_specs, upgrade_specs, prestige_specs, milestone_specs


def _random_partition(rng: Random, total: int, parts: int) -> list[int]:
    """Split ``total`` seconds into ``parts`` non-negative integer chunks."""
    cuts = sorted(rng.randint(0, total) for _ in range(parts - 1))
    bounds = [0, *cuts, total]
    return [b - a for a, b in zip(bounds, bounds[1:])]


# --- 1. tick/offline equivalence ---------------------------------------------


@pytest.mark.parametrize("seed", range(30))
def test_partitioned_ticks_equal_closed_form_offline(seed):
    """Sum of ANY random tick partition == one closed-form offline credit."""
    rng = Random(1_000 + seed)
    state, gens, ups, prs, mss = _random_roster(rng)
    total = rng.randint(0, 1_000_000)
    parts = rng.randint(1, 12)
    partition = _random_partition(rng, total, parts)
    assert sum(partition) == total

    closed = offline_progress(
        state, gens, state.last_seen, state.last_seen + total, ups, prs, mss
    )

    walked = state
    for dt in partition:
        walked = tick(walked, gens, dt, ups, prs, mss)

    assert walked.last_seen == state.last_seen + total
    for currency in set(state.balances) | set(closed):
        expected = state.balances.get(currency, 0) + closed.get(currency, 0)
        assert walked.balances.get(currency, 0) == expected
        expected_life = state.lifetime.get(currency, 0) + closed.get(currency, 0)
        assert walked.lifetime.get(currency, 0) == expected_life


@pytest.mark.parametrize("seed", range(10))
def test_one_second_loop_equals_closed_form(seed):
    """The doc's strongest claim: 1s-at-a-time looping == the closed form."""
    rng = Random(2_000 + seed)
    state, gens, ups, prs, mss = _random_roster(rng)
    total = rng.randint(0, 200)
    closed = offline_progress(
        state, gens, state.last_seen, state.last_seen + total, ups, prs, mss
    )
    walked = state
    for _ in range(total):
        walked = tick(walked, gens, 1, ups, prs, mss)
    for currency, earned in closed.items():
        assert walked.balances.get(currency, 0) == state.balances.get(currency, 0) + earned


@pytest.mark.parametrize("seed", range(10))
def test_apply_offline_progress_equals_tick_of_elapsed(seed):
    """apply_offline_progress(now) == tick(now - last_seen), state for state."""
    rng = Random(3_000 + seed)
    state, gens, ups, prs, mss = _random_roster(rng)
    elapsed = rng.randint(0, 10**6)
    via_offline = apply_offline_progress(
        state, gens, state.last_seen + elapsed, ups, prs, mss
    )
    via_tick = tick(state, gens, elapsed, ups, prs, mss)
    assert via_offline == via_tick


# --- 2. determinism across independent runs -----------------------------------


def _canon(state: GameState) -> bytes:
    """Canonical bytes of a GameState — the PUBLISHED save format itself.

    Delegating to :func:`idle_engine.persistence.dump_state` (rather than
    re-implementing the field list/sort_keys/separators here) means the
    byte-identical-trajectory tests pin the REAL format consumers will
    store: the determinism driver and the save format can never drift
    apart. ``dump_state`` is ASCII by contract (``ensure_ascii``), so the
    strict encode below is a free extra check.
    """
    return dump_state(state).encode("ascii")


def _drive_trajectory(theme, seed: int) -> list[bytes]:
    """One seeded play-through against a real pack; returns canon snapshots."""
    rng = Random(seed)
    gens = theme.generator_specs()
    ups = theme.upgrade_specs()
    pr = theme.prestige_spec()
    prs = [pr] if pr is not None else []
    mss = theme.milestone_specs()
    state = GameState(last_seen=rng.randint(0, 10**6))
    snapshots = [_canon(state)]
    for _ in range(60):
        op = rng.choice(("tick", "offline", "own", "buy", "prestige", "award"))
        if op == "tick":
            state = tick(state, gens, rng.randint(0, 100_000), ups, prs, mss)
        elif op == "offline":
            # Occasionally a PAST now: clock skew must accrue nothing.
            now = state.last_seen + rng.randint(-1_000, 100_000)
            state = apply_offline_progress(state, gens, now, ups, prs, mss)
        elif op == "own":
            spec = rng.choice(gens)
            owned = dict(state.owned)
            owned[spec.spec_id] = owned.get(spec.spec_id, 0) + rng.randint(1, 5)
            state = dataclasses.replace(state, owned=owned)
        elif op == "buy" and ups:
            spec = rng.choice(ups)
            cost = upgrade_cost(spec, state.upgrades.get(spec.spec_id, 0))
            if state.balances.get(spec.cost_currency, 0) >= cost:
                state = purchase_upgrade(state, spec)
        elif op == "prestige" and prs and prestige_eligible(state, prs[0]):
            state = apply_prestige(state, prs[0])
        elif op == "award":
            state = award_milestones(state, mss)
        snapshots.append(_canon(state))
    return snapshots


@pytest.mark.parametrize("path", THEME_PATHS, ids=THEME_IDS)
def test_identical_seed_gives_byte_identical_trajectory(path):
    theme = load_theme(path)
    for seed in (7, 42, 20260711):
        first = _drive_trajectory(theme, seed)
        second = _drive_trajectory(theme, seed)
        assert first == second  # byte-identical, snapshot for snapshot


def test_different_seeds_actually_diverge():
    """Sanity guard: the trajectory driver is not vacuously constant."""
    theme = load_theme(THEMES_DIR / "egg-farm.yaml")
    assert _drive_trajectory(theme, 7) != _drive_trajectory(theme, 8)


# --- 3. monotonicity / conservation -------------------------------------------


@pytest.mark.parametrize("path", THEME_PATHS, ids=THEME_IDS)
def test_balances_and_lifetime_never_negative_along_trajectories(path):
    theme = load_theme(path)
    gens = theme.generator_specs()
    ups = theme.upgrade_specs()
    pr = theme.prestige_spec()
    prs = [pr] if pr is not None else []
    mss = theme.milestone_specs()
    rng = Random(4_000)
    state = GameState()
    prev_lifetime: dict[str, int] = {}
    prev_milestones: set[str] = set()
    for _ in range(80):
        op = rng.choice(("tick", "own", "buy", "prestige", "award"))
        if op == "tick":
            state = tick(state, gens, rng.randint(0, 50_000), ups, prs, mss)
        elif op == "own":
            spec = rng.choice(gens)
            owned = dict(state.owned)
            owned[spec.spec_id] = owned.get(spec.spec_id, 0) + 1
            state = dataclasses.replace(state, owned=owned)
        elif op == "buy" and ups:
            spec = rng.choice(ups)
            cost = upgrade_cost(spec, state.upgrades.get(spec.spec_id, 0))
            if state.balances.get(spec.cost_currency, 0) >= cost:
                state = purchase_upgrade(state, spec)
            else:
                with pytest.raises(ValueError):
                    purchase_upgrade(state, spec)
        elif op == "prestige" and prs:
            if prestige_eligible(state, prs[0]):
                state = apply_prestige(state, prs[0])
                prev_lifetime = {}
            else:
                with pytest.raises(ValueError):
                    apply_prestige(state, prs[0])
        elif op == "award":
            state = award_milestones(state, mss)
        for mapping in (state.balances, state.owned, state.upgrades, state.lifetime, state.prestige, state.milestones):
            assert all(v >= 0 for v in mapping.values())
        # Lifetime is monotone non-decreasing WITHIN a run (reset wipes it).
        for currency, value in prev_lifetime.items():
            assert state.lifetime.get(currency, 0) >= value
        prev_lifetime = dict(state.lifetime)
        # The earned milestone set only ever GROWS — prestige never wipes it.
        earned_now = {m for m, v in state.milestones.items() if v >= 1}
        assert prev_milestones <= earned_now
        prev_milestones = earned_now


@pytest.mark.parametrize("seed", range(15))
def test_purchase_conserves_lifetime_and_spends_exactly_cost(seed):
    rng = Random(5_000 + seed)
    state, gens, ups, prs, mss = _random_roster(rng)
    while not ups:  # deterministic redraw: same rng stream, so still seeded
        state, gens, ups, prs, mss = _random_roster(rng)
    spec = rng.choice(ups)
    level = state.upgrades.get(spec.spec_id, 0)
    cost = upgrade_cost(spec, level)
    funded = dataclasses.replace(
        state, balances={**state.balances, spec.cost_currency: cost + rng.randint(0, 10**6)}
    )
    after = purchase_upgrade(funded, spec)
    # Spending conserves lifetime earnings — there is no refund path either.
    assert after.lifetime == funded.lifetime
    assert (
        funded.balances[spec.cost_currency] - after.balances[spec.cost_currency] == cost
    )
    assert after.upgrades[spec.spec_id] == level + 1
    # Every other balance is untouched.
    for currency, value in funded.balances.items():
        if currency != spec.cost_currency:
            assert after.balances[currency] == value


@pytest.mark.parametrize("seed", range(10))
def test_prestige_award_monotone_in_lifetime(seed):
    rng = Random(6_000 + seed)
    threshold = rng.randint(1_000, 10**6)
    spec = PrestigeSpec(
        awards="meta",
        measures="cur0",
        threshold=threshold,
        award_divisor=rng.randint(1, threshold),
        bonus_percent=rng.randint(0, 25),
    )
    lifetime = 0
    last_award = 0
    for _ in range(200):
        lifetime += rng.randint(0, 10**7)
        award = prestige_award(GameState(lifetime={"cur0": lifetime}), spec)
        assert award >= last_award
        last_award = award


@pytest.mark.parametrize("seed", range(10))
def test_apply_prestige_never_increases_run_balances(seed):
    rng = Random(7_000 + seed)
    state, gens, ups, prs, mss = _random_roster(rng)
    while not prs:  # deterministic redraw: same rng stream, so still seeded
        state, gens, ups, prs, mss = _random_roster(rng)
    spec = prs[0]
    eligible = dataclasses.replace(
        state, lifetime={**state.lifetime, spec.measures: spec.threshold + rng.randint(0, 10**9)}
    )
    award = prestige_award(eligible, spec)
    after = apply_prestige(eligible, spec)
    # The run is wiped: no balance rises, everything run-scoped is zeroed.
    assert after.balances == {}
    assert after.owned == {}
    assert after.upgrades == {}
    assert after.lifetime == {}
    for currency, value in eligible.balances.items():
        assert after.balances.get(currency, 0) <= value or value < 0
    # The award banks exactly once, and last_seen (persistent) survives.
    assert after.prestige[spec.awards] == eligible.prestige.get(spec.awards, 0) + award
    assert award >= 1  # threshold >= divisor guarantees an eligible reset pays
    assert after.last_seen == eligible.last_seen


# --- 4. render budget fuzz -----------------------------------------------------


def _assert_budgets(embed):
    assert 1 <= len(embed["title"]) <= TITLE_LIMIT
    assert len(embed["description"]) <= DESCRIPTION_LIMIT
    assert len(embed["fields"]) <= MAX_FIELDS
    for field in embed["fields"]:
        assert 1 <= len(field["name"]) <= FIELD_NAME_LIMIT
        assert 1 <= len(field["value"]) <= FIELD_VALUE_LIMIT
    assert 0 <= embed["color"] <= 0xFFFFFF


def _extreme_state(rng: Random, theme) -> GameState:
    """A hostile but VALID save: astronomically large integers everywhere."""
    def huge() -> int:
        return rng.choice((0, 1, rng.randint(0, 10**6), 10 ** rng.randint(10, 3_000)))

    currencies = list(theme.currencies)
    generators = list(theme.generators)
    upgrades = list(theme.upgrades)
    return GameState(
        balances={c: huge() for c in currencies},
        owned={g: huge() for g in generators},
        last_seen=rng.choice((0, rng.randint(0, 2**63))),
        upgrades={u: rng.choice((0, rng.randint(0, 10_000))) for u in upgrades},
        lifetime={c: huge() for c in currencies},
        prestige={c: rng.choice((0, rng.randint(0, 10_000))) for c in currencies},
        milestones={
            m.spec_id: 1
            for m in theme.milestone_specs()
            if rng.random() < 0.5
        },
    )


@pytest.mark.parametrize("path", THEME_PATHS, ids=THEME_IDS)
def test_render_fuzz_engine_content_never_busts_budgets(path):
    """Extreme states x every view: validate_embed never raises."""
    theme = load_theme(path)
    rng = Random(8_000)
    for _ in range(25):
        state = _extreme_state(rng, theme)
        # ``now`` sweeps the far future AND the past (clock skew).
        now = state.last_seen + rng.choice((-10**9, 0, 1, rng.randint(0, 2**40)))
        _assert_budgets(render_status(state, theme, now))
        shop = render_shop(state, theme)
        if shop is not None:
            _assert_budgets(shop)
        prestige = render_prestige(state, theme)
        if prestige is not None:
            _assert_budgets(prestige)
        _assert_budgets(render_achievements(state, theme))


def test_render_fuzz_themed_overflow_still_reds():
    """The deliberate red case: themed text over budget must RAISE, not clamp.

    A status_title label longer than the title cap is theme-sourced text —
    the two-tier policy forbids silent truncation there even under fuzz.
    """
    theme = load_theme(THEMES_DIR / "egg-farm.yaml")
    broken = dataclasses.replace(
        theme, labels=ThemeLabels(status_title="X" * (TITLE_LIMIT + 1))
    )
    state = _extreme_state(Random(8_100), theme)
    with pytest.raises(RenderBudgetError):
        render_status(state, broken, state.last_seen + 60)


def test_render_fuzz_oversized_theme_description_reds():
    """Second tier check: a too-long pack description raises at the gate."""
    theme = load_theme(THEMES_DIR / "egg-farm.yaml")
    broken = dataclasses.replace(theme, description="d" * (DESCRIPTION_LIMIT + 1))
    with pytest.raises(RenderBudgetError):
        render_status(GameState(), broken, 60)


# --- 5. setup-code fuzz ---------------------------------------------------------


def _random_slug(rng: Random) -> str:
    """A random schema-v1 slug: lowercase a-z0-9 words joined by hyphens."""
    words = []
    remaining = rng.randint(1, 32)
    while remaining > 0 and len(words) < 5:
        size = rng.randint(1, min(8, remaining))
        words.append(
            "".join(rng.choice(string.ascii_lowercase + string.digits) for _ in range(size))
        )
        remaining -= size + 1
    return "-".join(words)


def _random_config(rng: Random) -> SetupConfig:
    return SetupConfig(
        theme_id=_random_slug(rng),
        offline_progress=rng.random() < 0.5,
        upgrades=rng.random() < 0.5,
        prestige=rng.random() < 0.5,
    )


@pytest.mark.parametrize("seed", range(20))
def test_random_valid_configs_round_trip(seed):
    rng = Random(9_000 + seed)
    for _ in range(50):
        config = _random_config(rng)
        code = encode_setup(config)
        assert decode_setup(code) == config
        assert encode_setup(config) == code  # deterministic, byte for byte


# Characters a fat-fingered paste can realistically introduce.
_CORRUPTION_CHARSET = (
    string.ascii_uppercase + string.ascii_lowercase + string.digits + "-_ .!*"
)

# One knob for the fuzz volume; keep CI fast but the sample meaningful.
_CORRUPTION_TRIALS = 4_000


def _corrupt(rng: Random, body: str) -> str:
    """One seeded corruption of the code body: substitute, delete, or insert."""
    kind = rng.random()
    pos = rng.randrange(len(body))
    if kind < 0.70:  # substitution (the classic typo)
        replacement = rng.choice(_CORRUPTION_CHARSET)
        while replacement == body[pos]:
            replacement = rng.choice(_CORRUPTION_CHARSET)
        return body[:pos] + replacement + body[pos + 1 :]
    if kind < 0.85:  # deletion
        return body[:pos] + body[pos + 1 :]
    return body[:pos] + rng.choice(_CORRUPTION_CHARSET) + body[pos:]  # insertion


def test_corrupted_codes_fail_loud_or_fold_to_original():
    """Seeded corruption sweep: every outcome is documented, nothing else.

    Allowed outcomes per trial:
      - a documented :class:`SetupCodeError` subclass (typo caught), or
      - the ORIGINAL config (the grammar's deliberate tolerance: case,
        hyphens, O/I/L look-alike folding — not a real corruption), or
      - a crc16 COLLISION: a successful decode to a DIFFERENT config.
        The checksum is 16 bits, so this is possible by design; it is
        counted and must stay rare (<= 0.1% of trials, ~26x the 2^-16
        a priori rate). Observed rate is reported in the assert message.

    Any other outcome — a non-SetupCodeError exception, a non-config
    return — fails the test immediately.
    """
    rng = Random(0xC0DE)
    outcomes = {"error": 0, "folded_to_original": 0, "crc_collision": 0}
    error_classes = set()
    for _ in range(_CORRUPTION_TRIALS):
        config = _random_config(rng)
        code = encode_setup(config)
        prefix, body = code.split("-", 1)
        corrupted = prefix + "-" + _corrupt(rng, body)
        if corrupted == code:
            continue
        try:
            decoded = decode_setup(corrupted)
        except SetupCodeError as exc:
            outcomes["error"] += 1
            error_classes.add(type(exc).__name__)
        else:
            assert isinstance(decoded, SetupConfig)
            if decoded == config:
                outcomes["folded_to_original"] += 1
            else:
                outcomes["crc_collision"] += 1
    total = sum(outcomes.values())
    assert total > 0
    collision_rate = outcomes["crc_collision"] / total
    assert collision_rate <= 0.001, (
        f"crc16 collision rate {collision_rate:.5%} exceeds the 0.1% budget "
        f"(outcomes: {outcomes})"
    )
    # The sweep must actually exercise the loud path, not just tolerance.
    assert outcomes["error"] > total * 0.5, outcomes
    # And every error observed is a documented taxonomy class.
    documented = {
        "MalformedCodeError",
        "UnknownVersionError",
        "ChecksumError",
        "UnknownFeatureError",
    }
    assert error_classes <= documented, error_classes


def test_prefix_corruptions_raise_documented_errors():
    """Corrupting the version/prefix half also stays inside the taxonomy."""
    rng = Random(0xBEEF)
    config = SetupConfig(theme_id="egg-farm")
    code = encode_setup(config)
    for _ in range(500):
        corrupted = _corrupt(rng, code)  # anywhere in the string this time
        if corrupted == code:
            continue
        try:
            decoded = decode_setup(corrupted)
        except SetupCodeError:
            continue
        assert isinstance(decoded, SetupConfig)
