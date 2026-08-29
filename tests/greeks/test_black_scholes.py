"""Tests for greeks.black_scholes module.

The Rhiza test-layout gate requires a 1:1 test/source mirror: every ``Test<Name>``
class must map to a ``<Name>`` class in the mirrored source module. ``black_scholes``
deliberately exposes module-level *functions* (``price``, ``delta``, ...) rather than
classes, so the per-Greek behaviour is exercised with plain module-level test
functions here. The only class-based test is :class:`TestOptionType`, which mirrors
the source :class:`~greeks.black_scholes.OptionType` enum.

The property-based (Hypothesis) tests that previously lived in ``test_properties.py``
are folded in below; there is no ``properties.py`` source module for them to mirror,
so they belong with the module they actually cover.
"""

import math

import pytest
from hypothesis import given
from hypothesis import strategies as st

from greeks.black_scholes import OptionType, delta, gamma, price, rho, theta, vega

# Reference values computed with well-known BSM inputs:
# S=100, K=100, T=1, r=0.05, sigma=0.2  (ATM, 1-year)
S, K, T, r, sigma = 100.0, 100.0, 1.0, 0.05, 0.20
CALL = OptionType.CALL
PUT = OptionType.PUT
ABS_TOL = 1e-4

# Every public function accepts the five market params positionally, so they can
# be exercised uniformly with keyword arguments in the validation tests.
ALL_FUNCS = [price, delta, gamma, vega, theta, rho]


class TestOptionType:
    """Tests for the OptionType enum."""

    def test_enum_values(self):
        """CALL and PUT compare equal to their string values."""
        assert OptionType.CALL == "call"
        assert OptionType.PUT == "put"

    def test_str_equality(self):
        """Members compare equal to themselves and differ from each other."""
        assert OptionType.CALL == OptionType.CALL
        assert OptionType.CALL != OptionType.PUT


# ---------------------------------------------------------------------------
# price
# ---------------------------------------------------------------------------


def test_call_price():
    """Call price matches the known ATM reference value."""
    # Known value: ~10.4506
    assert abs(price(S, K, T, r, sigma, CALL) - 10.4506) < ABS_TOL


def test_put_price():
    """Put price matches the known ATM reference value."""
    # Known value: ~5.5735
    assert abs(price(S, K, T, r, sigma, PUT) - 5.5735) < ABS_TOL


def test_price_put_call_parity():
    """Call and put prices satisfy put-call parity."""
    c = price(S, K, T, r, sigma, CALL)
    p = price(S, K, T, r, sigma, PUT)
    # C - P = S - K * exp(-r * T)
    rhs = S - K * math.exp(-r * T)
    assert abs((c - p) - rhs) < ABS_TOL


def test_deep_itm_call_approaches_intrinsic():
    """A deep in-the-money call approaches its intrinsic value."""
    # Very deep ITM call ≈ S - K * exp(-rT)
    c = price(200.0, 100.0, T, r, sigma, CALL)
    intrinsic = 200.0 - 100.0 * math.exp(-r * T)
    assert abs(c - intrinsic) < 0.01


def test_deep_otm_call_near_zero():
    """A deep out-of-the-money call is worth almost nothing."""
    c = price(50.0, 200.0, T, r, sigma, CALL)
    assert c < 0.01


def test_price_default_option_type_is_call():
    """Price defaults to a call when no option type is given."""
    assert price(S, K, T, r, sigma) == price(S, K, T, r, sigma, CALL)


# ---------------------------------------------------------------------------
# delta
# ---------------------------------------------------------------------------


def test_call_delta():
    """Call delta matches the known ATM reference value."""
    # Known value: ~0.6368
    assert abs(delta(S, K, T, r, sigma, CALL) - 0.6368) < ABS_TOL


def test_put_delta():
    """Put delta matches the known ATM reference value."""
    # Known value: ~-0.3632
    assert abs(delta(S, K, T, r, sigma, PUT) - (-0.3632)) < ABS_TOL


def test_call_put_delta_sum():
    """Call delta minus put delta equals one."""
    # call_delta - put_delta == 1
    assert abs(delta(S, K, T, r, sigma, CALL) - delta(S, K, T, r, sigma, PUT) - 1.0) < ABS_TOL


def test_call_delta_bounds():
    """Call delta lies strictly between 0 and 1."""
    assert 0.0 < delta(S, K, T, r, sigma, CALL) < 1.0


def test_put_delta_bounds():
    """Put delta lies strictly between -1 and 0."""
    assert -1.0 < delta(S, K, T, r, sigma, PUT) < 0.0


def test_delta_default_option_type_is_call():
    """Delta defaults to a call when no option type is given."""
    assert delta(S, K, T, r, sigma) == delta(S, K, T, r, sigma, CALL)


# ---------------------------------------------------------------------------
# gamma
# ---------------------------------------------------------------------------


def test_gamma_value():
    """Gamma matches the known ATM reference value."""
    # Known value: ~0.0188
    assert abs(gamma(S, K, T, r, sigma) - 0.0188) < ABS_TOL


def test_gamma_positive():
    """Gamma is strictly positive."""
    assert gamma(S, K, T, r, sigma) > 0


def test_gamma_matches_second_difference_of_price():
    """Gamma equals the numerical 2nd derivative of price — same for calls and puts."""
    h = 0.1

    def second_difference(option_type):
        """Central second difference of price w.r.t. spot."""
        up = price(S + h, K, T, r, sigma, option_type)
        mid = price(S, K, T, r, sigma, option_type)
        down = price(S - h, K, T, r, sigma, option_type)
        return (up - 2 * mid + down) / h**2

    g = gamma(S, K, T, r, sigma)
    # The finite-difference gamma agrees for calls AND puts, confirming gamma
    # is independent of option type.
    assert abs(second_difference(CALL) - g) < 1e-4
    assert abs(second_difference(PUT) - g) < 1e-4
    assert abs(second_difference(CALL) - second_difference(PUT)) < 1e-6


# ---------------------------------------------------------------------------
# vega
# ---------------------------------------------------------------------------


def test_vega_value():
    """Vega matches the known ATM reference value."""
    # Known value: ~37.524  (per unit vol, not per %)
    assert abs(vega(S, K, T, r, sigma) - 37.524) < 0.01


def test_vega_positive():
    """Vega is strictly positive."""
    assert vega(S, K, T, r, sigma) > 0


def test_vega_matches_first_difference_of_price():
    """Vega equals the numerical derivative of price w.r.t. sigma — calls and puts alike."""
    h = 1e-4

    def first_difference(option_type):
        """Central first difference of price w.r.t. volatility."""
        up = price(S, K, T, r, sigma + h, option_type)
        down = price(S, K, T, r, sigma - h, option_type)
        return (up - down) / (2 * h)

    v = vega(S, K, T, r, sigma)
    # Agreeing for calls AND puts confirms vega is independent of option type.
    assert abs(first_difference(CALL) - v) < 1e-4
    assert abs(first_difference(PUT) - v) < 1e-4


# ---------------------------------------------------------------------------
# theta
# ---------------------------------------------------------------------------


def test_call_theta_negative():
    """Call theta is negative (time decay)."""
    assert theta(S, K, T, r, sigma, CALL) < 0


def test_put_theta_negative():
    """Put theta is negative (time decay)."""
    assert theta(S, K, T, r, sigma, PUT) < 0


def test_call_theta_value():
    """Call theta matches the known ATM reference value."""
    # Known value: ~-0.01757 per calendar day
    assert abs(theta(S, K, T, r, sigma, CALL) - (-0.01757)) < ABS_TOL


def test_put_theta_value():
    """Put theta matches the known ATM reference value."""
    # Known value: ~-0.00454 per calendar day
    assert abs(theta(S, K, T, r, sigma, PUT) - (-0.00454)) < ABS_TOL


@pytest.mark.parametrize("option_type", [CALL, PUT])
def test_theta_matches_first_difference_of_price(option_type):
    """Theta is minus the numerical derivative of price w.r.t. time remaining, per day."""
    h = 1e-4
    up = price(S, K, T + h, r, sigma, option_type)
    down = price(S, K, T - h, r, sigma, option_type)
    # Price rises with time *remaining*, so decay per calendar day carries the
    # opposite sign and is scaled by the 365-day convention of the analytic form.
    expected = -(up - down) / (2 * h) / 365.0
    assert abs(theta(S, K, T, r, sigma, option_type) - expected) < 1e-8


def test_theta_default_option_type_is_call():
    """Theta defaults to a call when no option type is given."""
    assert theta(S, K, T, r, sigma) == theta(S, K, T, r, sigma, CALL)


# ---------------------------------------------------------------------------
# rho
# ---------------------------------------------------------------------------


def test_call_rho_positive():
    """Call rho is positive."""
    assert rho(S, K, T, r, sigma, CALL) > 0


def test_put_rho_negative():
    """Put rho is negative."""
    assert rho(S, K, T, r, sigma, PUT) < 0


def test_call_rho_value():
    """Call rho matches the known ATM reference value."""
    # Known value: ~53.23  (per unit rate, not per bp)
    assert abs(rho(S, K, T, r, sigma, CALL) - 53.23) < 0.01


def test_put_rho_value():
    """Put rho matches the known ATM reference value."""
    # Known value: ~-41.89  (per unit rate, not per bp)
    assert abs(rho(S, K, T, r, sigma, PUT) - (-41.89)) < 0.01


@pytest.mark.parametrize("option_type", [CALL, PUT])
def test_rho_matches_first_difference_of_price(option_type):
    """Rho equals the numerical derivative of price w.r.t. the risk-free rate."""
    h = 1e-6
    up = price(S, K, T, r + h, sigma, option_type)
    down = price(S, K, T, r - h, sigma, option_type)
    # Per 1 point of rate, matching the analytic convention (not per basis point).
    expected = (up - down) / (2 * h)
    assert abs(rho(S, K, T, r, sigma, option_type) - expected) < 1e-4


def test_rho_default_option_type_is_call():
    """Rho defaults to a call when no option type is given."""
    assert rho(S, K, T, r, sigma) == rho(S, K, T, r, sigma, CALL)


# ---------------------------------------------------------------------------
# validation — every public function rejects degenerate market parameters
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("fn", ALL_FUNCS)
@pytest.mark.parametrize(
    "override",
    [
        {"S": 0.0},
        {"S": -1.0},
        {"K": 0.0},
        {"K": -1.0},
        {"T": 0.0},
        {"T": -1.0},
        {"sigma": 0.0},
        {"sigma": -0.1},
        {"S": float("nan")},
        {"T": float("inf")},
        {"r": float("nan")},
        {"r": float("-inf")},
    ],
)
def test_rejects_invalid_params(fn, override):
    """Non-finite or non-positive market parameters raise ValueError."""
    params = {"S": S, "K": K, "T": T, "r": r, "sigma": sigma}
    params.update(override)
    with pytest.raises(ValueError, match="must be"):
        fn(**params)


@pytest.mark.parametrize("fn", ALL_FUNCS)
def test_allows_negative_rate(fn):
    """A negative (but finite) risk-free rate is a valid input."""
    # Must not raise — negative rates are economically meaningful.
    fn(S=S, K=K, T=T, r=-0.01, sigma=sigma)


# ---------------------------------------------------------------------------
# property-based tests (Hypothesis)
#
# These complement the reference-value tests above by asserting invariants that
# must hold across the whole valid input domain, plus a few degenerate-input
# cases (T->0, sigma->0) the fixed-value tests do not cover. They previously
# lived in ``test_properties.py``, which had no ``properties.py`` source module
# to mirror; they cover ``black_scholes`` and so belong here.
# ---------------------------------------------------------------------------

# Strategies for economically sensible Black-Scholes inputs.
spot = st.floats(min_value=1.0, max_value=1_000.0)
strike = st.floats(min_value=1.0, max_value=1_000.0)
expiry = st.floats(min_value=0.01, max_value=5.0)
rate = st.floats(min_value=0.0, max_value=0.20)
vol = st.floats(min_value=0.01, max_value=2.0)


@pytest.mark.property
@given(s=spot, k=strike, t=expiry, r=rate, sigma=vol)
def test_put_call_parity_property(s, k, t, r, sigma):
    """C - P == S - K * exp(-rT) for every valid input."""
    c = price(s, k, t, r, sigma, OptionType.CALL)
    p = price(s, k, t, r, sigma, OptionType.PUT)
    rhs = s - k * math.exp(-r * t)
    assert math.isclose(c - p, rhs, rel_tol=1e-9, abs_tol=1e-6)


@pytest.mark.property
@given(s=spot, k=strike, t=expiry, r=rate, sigma=vol)
def test_call_delta_in_unit_interval(s, k, t, r, sigma):
    """Call delta lies in (0, 1) and put delta in (-1, 0)."""
    assert 0.0 <= delta(s, k, t, r, sigma, OptionType.CALL) <= 1.0
    assert -1.0 <= delta(s, k, t, r, sigma, OptionType.PUT) <= 0.0


@pytest.mark.property
@given(s=spot, k=strike, t=expiry, r=rate, sigma=vol)
def test_gamma_and_vega_non_negative(s, k, t, r, sigma):
    """Gamma and vega are non-negative everywhere."""
    assert gamma(s, k, t, r, sigma) >= 0.0
    assert vega(s, k, t, r, sigma) >= 0.0


@pytest.mark.property
@given(
    s=spot,
    k=strike,
    t=expiry,
    r=rate,
    sigma1=vol,
    bump=st.floats(min_value=0.01, max_value=1.0),
)
def test_call_price_monotonic_in_volatility(s, k, t, r, sigma1, bump):
    """Higher volatility never decreases a call's price (vega >= 0)."""
    cheaper = price(s, k, t, r, sigma1, OptionType.CALL)
    dearer = price(s, k, t, r, sigma1 + bump, OptionType.CALL)
    assert dearer >= cheaper - 1e-9


def test_call_price_at_near_zero_expiry_is_intrinsic():
    """As T -> 0 a call collapses to its intrinsic value max(S - K, 0)."""
    itm = price(120.0, 100.0, 1e-6, 0.05, 0.20, OptionType.CALL)
    assert math.isclose(itm, 20.0, abs_tol=1e-3)
    otm = price(80.0, 100.0, 1e-6, 0.05, 0.20, OptionType.CALL)
    assert otm < 1e-3


def test_call_price_at_near_zero_vol_is_discounted_intrinsic():
    """As sigma -> 0 a call collapses to max(S - K * exp(-rT), 0)."""
    s, k, t, r = 120.0, 100.0, 1.0, 0.05
    c = price(s, k, t, r, 1e-6, OptionType.CALL)
    expected = s - k * math.exp(-r * t)
    assert math.isclose(c, expected, abs_tol=1e-3)
