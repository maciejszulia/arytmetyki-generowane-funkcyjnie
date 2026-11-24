# ADR 0001: Models define only the generator pair (f, f⁻¹)

## Status

Accepted.

## Context

The repository offers 13 arithmetics. Each needs addition, subtraction, scalar
multiplication, full multiplication, division, negation, neutral elements,
powers, roots, a mean and a distance. Writing these operations per model would
multiply the code and the chance of a wrong simplified formula.

## Decision

The base class `Arithmetic` implements every operation through `f` and `f_inv`.
A model subclass implements only `f`, `f_inv` and descriptive metadata
(`name`, `generator`, `inverse`, `domain`). The simplified closed forms appear
only in the README table and in tests, never in the implementation.

## Consequences

- A new model needs two methods.
- An operation is correct for every model as long as `f_inv` inverts `f`.
- Simplified formulas (for example `ab/(a+b)` for the harmonic model) are not
  faster paths in code; every call pays for `f` and `f_inv`.

## Evidence

- `src/nna/core.py`: module docstring ("Podklasy definiują wyłącznie parę (f, f⁻¹); reszta jest dziedziczona") and class `Arithmetic`.
- `README.md`: paragraph under the model table ("W kodzie nie ma tych uproszczonych wzorów").
