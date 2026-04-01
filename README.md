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

```bash
pip install greeks
```

Requires Python 3.11+.

## Usage

```python
from greeks.black_scholes import OptionType, price, delta, gamma, vega, theta, rho

S, K, T, r, sigma = 100.0, 100.0, 1.0, 0.05, 0.20

# Price
call_price = price(S, K, T, r, sigma, OptionType.CALL)   # ~10.45
put_price  = price(S, K, T, r, sigma, OptionType.PUT)    # ~5.57

# Greeks
d = delta(S, K, T, r, sigma, OptionType.CALL)   # ~0.637
g = gamma(S, K, T, r, sigma)                    # ~0.019
v = vega(S, K, T, r, sigma)                     # ~37.52
t = theta(S, K, T, r, sigma, OptionType.CALL)   # ~-0.018  (per day)
p = rho(S, K, T, r, sigma, OptionType.CALL)     # ~53.23
```

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

## Development

```bash
make install   # create virtualenv and install dependencies
make test      # run test suite
make fmt       # lint and format
make all       # full quality gate
```
