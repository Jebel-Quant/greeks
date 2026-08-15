# [greeks](https://jebel-quant.github.io/greeks)

Option pricing and Greeks under the Black-Scholes model.

## Features

- **Pricing** — closed-form call and put prices
- **Delta** — first-order sensitivity to spot
- **Gamma** — second-order sensitivity to spot
- **Vega** — sensitivity to implied volatility
- **Theta** — time decay (per calendar day)
- **Rho** — sensitivity to the risk-free rate

## Installation

This package is not published to PyPI — install it from the repository:

```bash
pip install git+https://github.com/Jebel-Quant/greeks.git
```

Or, to pin a release:

```bash
pip install git+https://github.com/Jebel-Quant/greeks.git@v0.1.1
```

Requires Python 3.11+.

## Usage

```python
from greeks import OptionType, price, delta, gamma, vega, theta, rho

S, K, T, r, sigma = 100.0, 100.0, 1.0, 0.05, 0.20

# Price
print(f"call  {price(S, K, T, r, sigma, OptionType.CALL):8.4f}")
print(f"put   {price(S, K, T, r, sigma, OptionType.PUT):8.4f}")

# Greeks
print(f"delta {delta(S, K, T, r, sigma, OptionType.CALL):8.4f}")
print(f"gamma {gamma(S, K, T, r, sigma):8.4f}")
print(f"vega  {vega(S, K, T, r, sigma):8.4f}")
print(f"theta {theta(S, K, T, r, sigma, OptionType.CALL):8.4f}")  # per day
print(f"rho   {rho(S, K, T, r, sigma, OptionType.CALL):8.4f}")
```

```result
call   10.4506
put     5.5735
delta   0.6368
gamma   0.0188
vega   37.5240
theta  -0.0176
rho    53.2325
```

Those numbers are executed and diffed against this block on every CI run, so they
cannot go stale silently.

### API reference

Every function takes the market parameters `(S, K, T, r, sigma)`; `price`, `delta`, `theta`, and `rho` also take an optional `option_type` (defaults to `OptionType.CALL`). All return a `float`.

| Function | Signature | Returns |
|----------|-----------|---------|
| `price` | `price(S, K, T, r, sigma, option_type=CALL)` | Option price |
| `delta` | `delta(S, K, T, r, sigma, option_type=CALL)` | ∂Price/∂S — sensitivity to spot |
| `gamma` | `gamma(S, K, T, r, sigma)` | ∂²Price/∂S² — same for calls and puts |
| `vega` | `vega(S, K, T, r, sigma)` | ∂Price/∂sigma — same for calls and puts |
| `theta` | `theta(S, K, T, r, sigma, option_type=CALL)` | ∂Price/∂t — per calendar day |
| `rho` | `rho(S, K, T, r, sigma, option_type=CALL)` | ∂Price/∂r — sensitivity to the rate |

`OptionType` is a `StrEnum` with members `OptionType.CALL` (`"call"`) and `OptionType.PUT` (`"put"`).

### Parameter conventions

| Symbol | Description |
|--------|-------------|
| `S` | Spot price |
| `K` | Strike price |
| `T` | Time to expiry in years |
| `r` | Continuously compounded risk-free rate (e.g. `0.05` for 5%) |
| `sigma` | Annualised volatility (e.g. `0.20` for 20%) |

- **Vega** is per 1-point move in `sigma` (i.e. per 100 vol-points), not per percentage point.
- **Rho** is per 1-point move in `r`, not per basis point.
- **Theta** is per calendar day.

### Input validation

`S`, `K`, `T`, and `sigma` must be finite and strictly positive; `r` must be
finite (it may be negative). Any other value raises `ValueError` rather than
returning a NaN/inf result, so degenerate inputs fail loudly at the call site.

## Stability

This project follows [semantic versioning](https://semver.org). While the
version is `0.x`, the public API (the functions and `OptionType` exported from
`greeks`) may change in a backwards-incompatible way in any minor release;
breaking changes will be called out in the release notes. From `1.0.0` onward,
breaking changes to the public API will only ship in a major release.

## Development

```bash
make install   # create virtualenv and install dependencies
make test      # run test suite
make fmt       # lint and format
make all       # full quality gate
```
