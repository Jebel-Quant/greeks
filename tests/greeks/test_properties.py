"""Property-based tests for greeks.black_scholes using Hypothesis.

These complement the reference-value tests in ``test_black_scholes.py`` by
asserting invariants that must hold across the whole valid input domain, plus a
few degenerate-input cases (T->0, sigma->0) the fixed-value tests do not cover.
"""

import math

import pytest
from hypothesis import given
from hypothesis import strategies as st

from greeks.black_scholes import OptionType, delta, gamma, price, vega

# Strategies for economically sensible Black-Scholes inputs.
spot = st.floats(min_value=1.0, max_value=1_000.0)
strike = st.floats(min_value=1.0, max_value=1_000.0)
expiry = st.floats(min_value=0.01, max_value=5.0)
rate = st.floats(min_value=0.0, max_value=0.20)
vol = st.floats(min_value=0.01, max_value=2.0)


@pytest.mark.property
@given(s=spot, k=strike, t=expiry, r=rate, sigma=vol)
def test_put_call_parity(s, k, t, r, sigma):
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
