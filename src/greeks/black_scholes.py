"""Black-Scholes option pricing and Greeks."""

from enum import StrEnum

import numpy as np
from scipy.stats import norm


class OptionType(StrEnum):
    """Option type: call or put."""

    CALL = "call"
    PUT = "put"


def _d1(S: float, K: float, T: float, r: float, sigma: float) -> float:
    """Compute d1 of the Black-Scholes formula."""
    return (np.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))


def _d2(S: float, K: float, T: float, r: float, sigma: float) -> float:
    """Compute d2 of the Black-Scholes formula (d1 minus sigma*sqrt(T))."""
    return _d1(S, K, T, r, sigma) - sigma * np.sqrt(T)


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

    Examples:
        >>> float(round(price(100, 100, 1.0, 0.05, 0.20, OptionType.CALL), 2))
        10.45
        >>> float(round(price(100, 100, 1.0, 0.05, 0.20, OptionType.PUT), 2))
        5.57
    """
    d1 = _d1(S, K, T, r, sigma)
    d2 = _d2(S, K, T, r, sigma)
    discount = np.exp(-r * T)
    if option_type == OptionType.CALL:
        return S * norm.cdf(d1) - K * discount * norm.cdf(d2)
    else:
        return K * discount * norm.cdf(-d2) - S * norm.cdf(-d1)


def delta(
    S: float,
    K: float,
    T: float,
    r: float,
    sigma: float,
    option_type: OptionType = OptionType.CALL,
) -> float:
    """First derivative of price with respect to spot."""
    d1 = _d1(S, K, T, r, sigma)
    if option_type == OptionType.CALL:
        return norm.cdf(d1)
    else:
        return norm.cdf(d1) - 1


def gamma(S: float, K: float, T: float, r: float, sigma: float) -> float:
    """Second derivative of price with respect to spot (same for calls and puts)."""
    d1 = _d1(S, K, T, r, sigma)
    return norm.pdf(d1) / (S * sigma * np.sqrt(T))


def vega(S: float, K: float, T: float, r: float, sigma: float) -> float:
    """First derivative of price with respect to volatility (same for calls and puts).

    Returns vega per 1-point move in volatility (not per percentage point).
    """
    d1 = _d1(S, K, T, r, sigma)
    return S * norm.pdf(d1) * np.sqrt(T)


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
    """
    d1 = _d1(S, K, T, r, sigma)
    d2 = _d2(S, K, T, r, sigma)
    discount = np.exp(-r * T)
    decay = -(S * norm.pdf(d1) * sigma) / (2 * np.sqrt(T))
    if option_type == OptionType.CALL:
        return (decay - r * K * discount * norm.cdf(d2)) / 365
    else:
        return (decay + r * K * discount * norm.cdf(-d2)) / 365


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
    """
    d2 = _d2(S, K, T, r, sigma)
    discount = np.exp(-r * T)
    if option_type == OptionType.CALL:
        return K * T * discount * norm.cdf(d2)
    else:
        return -K * T * discount * norm.cdf(-d2)
