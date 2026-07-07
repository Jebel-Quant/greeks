"""Black-Scholes option pricing and Greeks.

All pricing and Greek functions share the market parameters
``(S, K, T, r, sigma)`` and validate them up front: ``S``, ``K``, ``T`` and
``sigma`` must be finite and strictly positive, and ``r`` must be finite (it may
be negative). Any other value raises :class:`ValueError` rather than silently
returning a NaN/inf result, so a degenerate input always fails loudly at the
call site instead of propagating through downstream calculations.
"""

import math
from enum import StrEnum

import numpy as np
from scipy.stats import norm


class OptionType(StrEnum):
    """Option type: call or put."""

    CALL = "call"
    PUT = "put"


def _validate(S: float, K: float, T: float, r: float, sigma: float) -> None:
    """Validate Black-Scholes market parameters.

    Raises:
        ValueError: If any parameter is non-finite, or if ``S``, ``K``, ``T`` or
            ``sigma`` is not strictly positive.
    """
    for name, value in (("S", S), ("K", K), ("T", T), ("r", r), ("sigma", sigma)):
        if not math.isfinite(value):
            msg = f"{name} must be finite, got {value!r}"
            raise ValueError(msg)
    for name, value in (("S", S), ("K", K), ("T", T), ("sigma", sigma)):
        if value <= 0.0:
            msg = f"{name} must be strictly positive, got {value!r}"
            raise ValueError(msg)


def _d1_d2(S: float, K: float, T: float, r: float, sigma: float) -> tuple[float, float]:
    """Compute d1 and d2 of the Black-Scholes formula in a single pass.

    ``d2`` is derived from ``d1`` (``d2 = d1 - sigma*sqrt(T)``) so ``d1`` is
    evaluated only once even when both are needed.
    """
    vol_sqrt_t = sigma * np.sqrt(T)
    d1 = float((np.log(S / K) + (r + 0.5 * sigma**2) * T) / vol_sqrt_t)
    d2 = float(d1 - vol_sqrt_t)
    return d1, d2


def _d1(S: float, K: float, T: float, r: float, sigma: float) -> float:
    """Compute d1 of the Black-Scholes formula."""
    return _d1_d2(S, K, T, r, sigma)[0]


def _d2(S: float, K: float, T: float, r: float, sigma: float) -> float:
    """Compute d2 of the Black-Scholes formula (d1 minus sigma*sqrt(T))."""
    return _d1_d2(S, K, T, r, sigma)[1]


def price(
    S: float,
    K: float,
    T: float,
    r: float,
    sigma: float,
    option_type: OptionType = OptionType.CALL,
) -> float:
    """Black-Scholes option price.

    Args:
        S: Spot price.
        K: Strike price.
        T: Time to expiry in years.
        r: Risk-free rate (continuously compounded).
        sigma: Volatility (annualised).
        option_type: OptionType.CALL or OptionType.PUT.

    Returns:
        Option price.

    Raises:
        ValueError: If any market parameter is invalid (see the module docstring).

    Examples:
        >>> float(round(price(100, 100, 1.0, 0.05, 0.20, OptionType.CALL), 2))
        10.45
        >>> float(round(price(100, 100, 1.0, 0.05, 0.20, OptionType.PUT), 2))
        5.57
    """
    _validate(S, K, T, r, sigma)
    d1, d2 = _d1_d2(S, K, T, r, sigma)
    discount = np.exp(-r * T)
    if option_type == OptionType.CALL:
        return float(S * norm.cdf(d1) - K * discount * norm.cdf(d2))
    else:
        return float(K * discount * norm.cdf(-d2) - S * norm.cdf(-d1))


def delta(
    S: float,
    K: float,
    T: float,
    r: float,
    sigma: float,
    option_type: OptionType = OptionType.CALL,
) -> float:
    """First derivative of price with respect to spot.

    Raises:
        ValueError: If any market parameter is invalid (see the module docstring).

    Examples:
        >>> float(round(delta(100, 100, 1.0, 0.05, 0.20, OptionType.CALL), 4))
        0.6368
        >>> float(round(delta(100, 100, 1.0, 0.05, 0.20, OptionType.PUT), 4))
        -0.3632
    """
    _validate(S, K, T, r, sigma)
    d1 = _d1(S, K, T, r, sigma)
    if option_type == OptionType.CALL:
        return float(norm.cdf(d1))
    else:
        return float(norm.cdf(d1) - 1)


def gamma(S: float, K: float, T: float, r: float, sigma: float) -> float:
    """Second derivative of price with respect to spot (same for calls and puts).

    Raises:
        ValueError: If any market parameter is invalid (see the module docstring).

    Examples:
        >>> float(round(gamma(100, 100, 1.0, 0.05, 0.20), 4))
        0.0188
    """
    _validate(S, K, T, r, sigma)
    d1 = _d1(S, K, T, r, sigma)
    return float(norm.pdf(d1) / (S * sigma * np.sqrt(T)))


def vega(S: float, K: float, T: float, r: float, sigma: float) -> float:
    """First derivative of price with respect to volatility (same for calls and puts).

    Returns vega per 1-point move in volatility (not per percentage point).

    Raises:
        ValueError: If any market parameter is invalid (see the module docstring).

    Examples:
        >>> float(round(vega(100, 100, 1.0, 0.05, 0.20), 3))
        37.524
    """
    _validate(S, K, T, r, sigma)
    d1 = _d1(S, K, T, r, sigma)
    return float(S * norm.pdf(d1) * np.sqrt(T))


def theta(
    S: float,
    K: float,
    T: float,
    r: float,
    sigma: float,
    option_type: OptionType = OptionType.CALL,
) -> float:
    """First derivative of price with respect to time (per calendar day).

    Returns theta as a negative number representing daily decay.

    Raises:
        ValueError: If any market parameter is invalid (see the module docstring).

    Examples:
        >>> float(round(theta(100, 100, 1.0, 0.05, 0.20, OptionType.CALL), 5))
        -0.01757
        >>> float(round(theta(100, 100, 1.0, 0.05, 0.20, OptionType.PUT), 5))
        -0.00454
    """
    _validate(S, K, T, r, sigma)
    d1, d2 = _d1_d2(S, K, T, r, sigma)
    discount = np.exp(-r * T)
    decay = -(S * norm.pdf(d1) * sigma) / (2 * np.sqrt(T))
    if option_type == OptionType.CALL:
        return float((decay - r * K * discount * norm.cdf(d2)) / 365)
    else:
        return float((decay + r * K * discount * norm.cdf(-d2)) / 365)


def rho(
    S: float,
    K: float,
    T: float,
    r: float,
    sigma: float,
    option_type: OptionType = OptionType.CALL,
) -> float:
    """First derivative of price with respect to the risk-free rate.

    Returns rho per 1-point move in rate (not per basis point).

    Raises:
        ValueError: If any market parameter is invalid (see the module docstring).

    Examples:
        >>> float(round(rho(100, 100, 1.0, 0.05, 0.20, OptionType.CALL), 2))
        53.23
        >>> float(round(rho(100, 100, 1.0, 0.05, 0.20, OptionType.PUT), 2))
        -41.89
    """
    _validate(S, K, T, r, sigma)
    d2 = _d2(S, K, T, r, sigma)
    discount = np.exp(-r * T)
    if option_type == OptionType.CALL:
        return float(K * T * discount * norm.cdf(d2))
    else:
        return float(-K * T * discount * norm.cdf(-d2))
