# API reference

Every function takes the market parameters `(S, K, T, r, sigma)` and returns a
`float`. `price`, `delta`, `theta` and `rho` also accept an optional
`option_type`, defaulting to `OptionType.CALL`; `gamma` and `vega` are identical
for calls and puts and so take no option type.

See [Parameter conventions](index.md#parameter-conventions) for the units — in
particular that vega is per 1-point move in `sigma`, rho per 1-point move in
`r`, and theta per calendar day.

::: greeks.black_scholes
    options:
      members:
        - OptionType
        - price
        - delta
        - gamma
        - vega
        - theta
        - rho
