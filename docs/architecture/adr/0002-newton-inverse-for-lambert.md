# ADR 0002: Newton iteration for the Lambert inverse instead of W(eʸ)

## Status

Accepted.

## Context

The inverse of `f(x) = x + ln x` is `W(eʸ)`. In IEEE 754 double precision,
`eʸ` overflows for `y > 709`, so the closed form fails exactly where the
arithmetic behaves like ordinary addition.

## Decision

`Lambert.f_inv` solves `w + ln w = y` by Newton iteration directly, starting at
`w ≈ y` for `y > 0` and `w ≈ eʸ` otherwise, for at most 100 steps.
`Kepler.f_inv` uses the same pattern for `x + k·sin x = y`.
`HybridCooling.f_inv` reduces its equation to the Lambert one and reuses
`Lambert().f_inv`.

## Consequences

- No overflow for large `y`; the README states correct results up to about `y ≈ 10^{12}`.
- Each call costs several Newton steps; large arrays are slower than closed-form models.
- `scipy` is not a runtime dependency; tests use `scipy.special.lambertw` only as a reference.

## Evidence

- `src/nna/core.py`: `Lambert.f_inv`, `Kepler.f_inv`.
- `src/nna/thermal.py`: `HybridCooling.f_inv`.
- `README.md`: section "Ograniczenia i pułapki numeryczne".
- `pyproject.toml`: `dependencies = ["numpy>=1.24"]`, `scipy` only in `dev`.
