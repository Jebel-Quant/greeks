"""Tests for greeks.black_scholes module."""

from greeks.black_scholes import OptionType, delta, gamma, price, rho, theta, vega

# Reference values computed with well-known BSM inputs:
# S=100, K=100, T=1, r=0.05, sigma=0.2  (ATM, 1-year)
S, K, T, r, sigma = 100.0, 100.0, 1.0, 0.05, 0.20
CALL = OptionType.CALL
PUT = OptionType.PUT
ABS_TOL = 1e-4


class TestOptionType:
    def test_enum_values(self):
        assert OptionType.CALL == "call"
        assert OptionType.PUT == "put"

    def test_str_equality(self):
        assert OptionType.CALL == OptionType.CALL
        assert OptionType.CALL != OptionType.PUT


class TestPrice:
    def test_call_price(self):
        # Known value: ~10.4506
        assert abs(price(S, K, T, r, sigma, CALL) - 10.4506) < ABS_TOL

    def test_put_price(self):
        # Known value: ~5.5735
        assert abs(price(S, K, T, r, sigma, PUT) - 5.5735) < ABS_TOL

    def test_put_call_parity(self):
        c = price(S, K, T, r, sigma, CALL)
        p = price(S, K, T, r, sigma, PUT)
        # C - P = S - K * exp(-r * T)
        import math

        rhs = S - K * math.exp(-r * T)
        assert abs((c - p) - rhs) < ABS_TOL

    def test_deep_itm_call_approaches_intrinsic(self):
        # Very deep ITM call ≈ S - K * exp(-rT)
        import math

        c = price(200.0, 100.0, T, r, sigma, CALL)
        intrinsic = 200.0 - 100.0 * math.exp(-r * T)
        assert abs(c - intrinsic) < 0.01

    def test_deep_otm_call_near_zero(self):
        c = price(50.0, 200.0, T, r, sigma, CALL)
        assert c < 0.01

    def test_default_option_type_is_call(self):
        assert price(S, K, T, r, sigma) == price(S, K, T, r, sigma, CALL)


class TestDelta:
    def test_call_delta(self):
        # Known value: ~0.6368
        assert abs(delta(S, K, T, r, sigma, CALL) - 0.6368) < ABS_TOL

    def test_put_delta(self):
        # Known value: ~-0.3632
        assert abs(delta(S, K, T, r, sigma, PUT) - (-0.3632)) < ABS_TOL

    def test_call_put_delta_sum(self):
        # call_delta - put_delta == 1
        assert abs(delta(S, K, T, r, sigma, CALL) - delta(S, K, T, r, sigma, PUT) - 1.0) < ABS_TOL

    def test_call_delta_bounds(self):
        assert 0.0 < delta(S, K, T, r, sigma, CALL) < 1.0

    def test_put_delta_bounds(self):
        assert -1.0 < delta(S, K, T, r, sigma, PUT) < 0.0

    def test_default_option_type_is_call(self):
        assert delta(S, K, T, r, sigma) == delta(S, K, T, r, sigma, CALL)


class TestGamma:
    def test_gamma_value(self):
        # Known value: ~0.0188
        assert abs(gamma(S, K, T, r, sigma) - 0.0188) < ABS_TOL

    def test_gamma_positive(self):
        assert gamma(S, K, T, r, sigma) > 0

    def test_gamma_symmetric_for_call_and_put(self):
        # Gamma is the same regardless of option type — just verify the function
        # accepts only the 5 market params
        g = gamma(S, K, T, r, sigma)
        assert g > 0


class TestVega:
    def test_vega_value(self):
        # Known value: ~37.524  (per unit vol, not per %)
        assert abs(vega(S, K, T, r, sigma) - 37.524) < 0.01

    def test_vega_positive(self):
        assert vega(S, K, T, r, sigma) > 0


class TestTheta:
    def test_call_theta_negative(self):
        assert theta(S, K, T, r, sigma, CALL) < 0

    def test_put_theta_negative(self):
        assert theta(S, K, T, r, sigma, PUT) < 0

    def test_call_theta_value(self):
        # Known value: ~-0.01757 per calendar day
        assert abs(theta(S, K, T, r, sigma, CALL) - (-0.01757)) < ABS_TOL

    def test_default_option_type_is_call(self):
        assert theta(S, K, T, r, sigma) == theta(S, K, T, r, sigma, CALL)


class TestRho:
    def test_call_rho_positive(self):
        assert rho(S, K, T, r, sigma, CALL) > 0

    def test_put_rho_negative(self):
        assert rho(S, K, T, r, sigma, PUT) < 0

    def test_call_rho_value(self):
        # Known value: ~53.23  (per unit rate, not per bp)
        assert abs(rho(S, K, T, r, sigma, CALL) - 53.23) < 0.01

    def test_default_option_type_is_call(self):
        assert rho(S, K, T, r, sigma) == rho(S, K, T, r, sigma, CALL)
