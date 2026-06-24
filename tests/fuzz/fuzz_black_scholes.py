"""Fuzz the Black-Scholes pricer and Greeks against arbitrary parameters.

``price`` and the Greeks (``delta``, ``gamma``, ``vega``, ``theta``, ``rho``)
ingest five floats (spot, strike, expiry, rate, volatility). They must never
crash on adversarial inputs — degenerate values (zero/negative spot, zero
volatility or expiry, NaN/inf) should propagate as NaN/inf or raise a clean
error, not blow up with an unexpected exception. This harness exercises that
contract with coverage-guided input.

Run locally:
    pip install atheris numpy scipy
    python tests/fuzz/fuzz_black_scholes.py -atheris_runs=20000

Run in ClusterFuzzLite: this file is built by .clusterfuzzlite/build.sh.
"""

from __future__ import annotations

import contextlib
import sys

import atheris

# Pre-import the native dependencies OUTSIDE the instrumentation block so they
# load uninstrumented; atheris's import hook can miscompile C-accelerated
# libraries. Only the first-party package under test is instrumented.
import numpy as np  # noqa: F401  # pre-imported uninstrumented
import scipy.stats  # noqa: F401  # pre-imported uninstrumented

with atheris.instrument_imports():
    from greeks import OptionType, delta, gamma, price, rho, theta, vega

# Pricing math may legitimately reject some inputs; anything else is a crash.
_ALLOWED = (ValueError, ZeroDivisionError, OverflowError)


def test_one_input(data: bytes) -> None:
    """Price and compute every Greek for fuzzed Black-Scholes parameters."""
    fdp = atheris.FuzzedDataProvider(data)
    s = fdp.ConsumeFloat()
    k = fdp.ConsumeFloat()
    t = fdp.ConsumeFloat()
    r = fdp.ConsumeFloat()
    sigma = fdp.ConsumeFloat()
    option_type = OptionType.CALL if fdp.ConsumeBool() else OptionType.PUT

    # price/delta/theta/rho take an option type; gamma/vega do not.
    for fn in (price, delta, theta, rho):
        with contextlib.suppress(_ALLOWED):
            fn(s, k, t, r, sigma, option_type)
    for fn in (gamma, vega):
        with contextlib.suppress(_ALLOWED):
            fn(s, k, t, r, sigma)


def main() -> None:
    """Run the Atheris fuzz loop."""
    atheris.Setup(sys.argv, test_one_input)
    atheris.Fuzz()


if __name__ == "__main__":
    main()
