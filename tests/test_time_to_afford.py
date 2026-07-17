"""``time_to_afford`` — seconds-until-affordable, integer-exact.

The affordability dual of ``max_affordable_levels``: given a ``cost``, a
current ``balance`` and a per-second income ``rate``, how many WHOLE
seconds until the balance covers the cost? The contract has three arms,
all pinned here:

- already affordable (``balance >= cost``) -> ``0``;
- unreachable (``rate == 0`` and not yet affordable) -> ``None``, the
  "never" sentinel;
- otherwise the exact ceil of the shortfall over the rate — and the ceil
  must round UP (a partial second still needs a whole second to elapse),
  computed in integer arithmetic with no float leakage.

Sb-free by construction: bare integers, no spec, no theme noun, no host
import — ``python3 -m pytest -q`` passes standalone.
"""

import pytest

from idle_engine import time_to_afford


def test_already_affordable_is_zero():
    # balance exactly covers cost, and comfortably over it -> 0 seconds.
    assert time_to_afford(cost=100, balance=100, rate=7) == 0
    assert time_to_afford(cost=100, balance=250, rate=7) == 0
    # zero cost is affordable from an empty balance.
    assert time_to_afford(cost=0, balance=0, rate=0) == 0


def test_exact_boundary_divides_evenly():
    # shortfall 100 at 10/s closes in exactly 10 seconds — no rounding.
    assert time_to_afford(cost=100, balance=0, rate=10) == 10
    # shortfall 90 at 10/s from a non-zero balance -> 9 seconds exactly.
    assert time_to_afford(cost=100, balance=10, rate=10) == 9


def test_ceil_rounds_up_on_partial_second():
    # shortfall 100 at 3/s: 33.33.. -> 34 whole seconds (33s leaves 99 < 100).
    assert time_to_afford(cost=100, balance=0, rate=3) == 34
    # a one-unit shortfall still needs a whole second.
    assert time_to_afford(cost=100, balance=99, rate=10) == 1
    # one over an exact multiple rounds to the next second.
    assert time_to_afford(cost=101, balance=0, rate=10) == 11


def test_zero_rate_not_affordable_is_never():
    # no production and short of the cost -> unreachable sentinel.
    assert time_to_afford(cost=100, balance=0, rate=0) is None
    assert time_to_afford(cost=100, balance=99, rate=0) is None


def test_integer_exact_no_float_leakage():
    # A shortfall/rate that a float would round wrong at scale: the exact
    # ceil is an int, never a float, and matches the pure ceil-division.
    cost = 10**30 + 1
    balance = 0
    rate = 10**15
    result = time_to_afford(cost=cost, balance=balance, rate=rate)
    assert result == -(-(cost - balance) // rate)  # exact ceil, big-int
    assert isinstance(result, int) and not isinstance(result, bool)
    # ..and the return is a plain int in the affordable/never arms too.
    assert isinstance(time_to_afford(cost=5, balance=5, rate=1), int)
    assert time_to_afford(cost=5, balance=0, rate=0) is None


def test_rejects_corrupt_inputs():
    # Negative quantities are corrupt state — fail loud, like the module's
    # other guards, rather than compute a nonsense ETA.
    with pytest.raises(ValueError):
        time_to_afford(cost=-1, balance=0, rate=1)
    with pytest.raises(ValueError):
        time_to_afford(cost=100, balance=-1, rate=1)
    with pytest.raises(ValueError):
        time_to_afford(cost=100, balance=0, rate=-1)
    # bools are not ints here (they slip through ``isinstance(x, int)``).
    with pytest.raises(TypeError):
        time_to_afford(cost=True, balance=0, rate=1)
