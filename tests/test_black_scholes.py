"""Tests for greeks.black_scholes module."""

import pytest

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


class TestPrice:
    """Tests for the Black-Scholes option price."""

    def test_call_price(self):
        """Call price matches the known ATM reference value."""
        # Known value: ~10.4506
        assert abs(price(S, K, T, r, sigma, CALL) - 10.4506) < ABS_TOL

    def test_put_price(self):
        """Put price matches the known ATM reference value."""
        # Known value: ~5.5735
        assert abs(price(S, K, T, r, sigma, PUT) - 5.5735) < ABS_TOL

    def test_put_call_parity(self):
        """Call and put prices satisfy put-call parity."""
        c = price(S, K, T, r, sigma, CALL)
        p = price(S, K, T, r, sigma, PUT)
        # C - P = S - K * exp(-r * T)
        import math

        rhs = S - K * math.exp(-r * T)
        assert abs((c - p) - rhs) < ABS_TOL

    def test_deep_itm_call_approaches_intrinsic(self):
        """A deep in-the-money call approaches its intrinsic value."""
        # Very deep ITM call ≈ S - K * exp(-rT)
        import math

        c = price(200.0, 100.0, T, r, sigma, CALL)
        intrinsic = 200.0 - 100.0 * math.exp(-r * T)
        assert abs(c - intrinsic) < 0.01

    def test_deep_otm_call_near_zero(self):
        """A deep out-of-the-money call is worth almost nothing."""
        c = price(50.0, 200.0, T, r, sigma, CALL)
        assert c < 0.01

    def test_default_option_type_is_call(self):
        """Price defaults to a call when no option type is given."""
        assert price(S, K, T, r, sigma) == price(S, K, T, r, sigma, CALL)


class TestDelta:
    """Tests for delta (sensitivity to spot)."""

    def test_call_delta(self):
        """Call delta matches the known ATM reference value."""
        # Known value: ~0.6368
        assert abs(delta(S, K, T, r, sigma, CALL) - 0.6368) < ABS_TOL

    def test_put_delta(self):
        """Put delta matches the known ATM reference value."""
        # Known value: ~-0.3632
        assert abs(delta(S, K, T, r, sigma, PUT) - (-0.3632)) < ABS_TOL

    def test_call_put_delta_sum(self):
        """Call delta minus put delta equals one."""
        # call_delta - put_delta == 1
        assert abs(delta(S, K, T, r, sigma, CALL) - delta(S, K, T, r, sigma, PUT) - 1.0) < ABS_TOL

    def test_call_delta_bounds(self):
        """Call delta lies strictly between 0 and 1."""
        assert 0.0 < delta(S, K, T, r, sigma, CALL) < 1.0

    def test_put_delta_bounds(self):
        """Put delta lies strictly between -1 and 0."""
        assert -1.0 < delta(S, K, T, r, sigma, PUT) < 0.0

    def test_default_option_type_is_call(self):
        """Delta defaults to a call when no option type is given."""
        assert delta(S, K, T, r, sigma) == delta(S, K, T, r, sigma, CALL)


class TestGamma:
    """Tests for gamma (second derivative with respect to spot)."""

    def test_gamma_value(self):
        """Gamma matches the known ATM reference value."""
        # Known value: ~0.0188
        assert abs(gamma(S, K, T, r, sigma) - 0.0188) < ABS_TOL

    def test_gamma_positive(self):
        """Gamma is strictly positive."""
        assert gamma(S, K, T, r, sigma) > 0

    def test_gamma_matches_second_difference_of_price(self):
        """Gamma equals the numerical 2nd derivative of price — same for calls and puts."""
        h = 0.1

        def second_difference(option_type):
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


class TestVega:
    """Tests for vega (sensitivity to volatility)."""

    def test_vega_value(self):
        """Vega matches the known ATM reference value."""
        # Known value: ~37.524  (per unit vol, not per %)
        assert abs(vega(S, K, T, r, sigma) - 37.524) < 0.01

    def test_vega_positive(self):
        """Vega is strictly positive."""
        assert vega(S, K, T, r, sigma) > 0


class TestTheta:
    """Tests for theta (sensitivity to time)."""

    def test_call_theta_negative(self):
        """Call theta is negative (time decay)."""
        assert theta(S, K, T, r, sigma, CALL) < 0

    def test_put_theta_negative(self):
        """Put theta is negative (time decay)."""
        assert theta(S, K, T, r, sigma, PUT) < 0

    def test_call_theta_value(self):
        """Call theta matches the known ATM reference value."""
        # Known value: ~-0.01757 per calendar day
        assert abs(theta(S, K, T, r, sigma, CALL) - (-0.01757)) < ABS_TOL

    def test_put_theta_value(self):
        """Put theta matches the known ATM reference value."""
        # Known value: ~-0.00454 per calendar day
        assert abs(theta(S, K, T, r, sigma, PUT) - (-0.00454)) < ABS_TOL

    def test_default_option_type_is_call(self):
        """Theta defaults to a call when no option type is given."""
        assert theta(S, K, T, r, sigma) == theta(S, K, T, r, sigma, CALL)


class TestRho:
    """Tests for rho (sensitivity to the risk-free rate)."""

    def test_call_rho_positive(self):
        """Call rho is positive."""
        assert rho(S, K, T, r, sigma, CALL) > 0

    def test_put_rho_negative(self):
        """Put rho is negative."""
        assert rho(S, K, T, r, sigma, PUT) < 0

    def test_call_rho_value(self):
        """Call rho matches the known ATM reference value."""
        # Known value: ~53.23  (per unit rate, not per bp)
        assert abs(rho(S, K, T, r, sigma, CALL) - 53.23) < 0.01

    def test_put_rho_value(self):
        """Put rho matches the known ATM reference value."""
        # Known value: ~-41.89  (per unit rate, not per bp)
        assert abs(rho(S, K, T, r, sigma, PUT) - (-41.89)) < 0.01

    def test_default_option_type_is_call(self):
        """Rho defaults to a call when no option type is given."""
        assert rho(S, K, T, r, sigma) == rho(S, K, T, r, sigma, CALL)


class TestValidation:
    """Every public function rejects degenerate market parameters."""

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
    def test_rejects_invalid_params(self, fn, override):
        """Non-finite or non-positive market parameters raise ValueError."""
        params = {"S": S, "K": K, "T": T, "r": r, "sigma": sigma}
        params.update(override)
        with pytest.raises(ValueError, match="must be"):
            fn(**params)

    @pytest.mark.parametrize("fn", ALL_FUNCS)
    def test_allows_negative_rate(self, fn):
        """A negative (but finite) risk-free rate is a valid input."""
        # Must not raise — negative rates are economically meaningful.
        fn(S=S, K=K, T=T, r=-0.01, sigma=sigma)
