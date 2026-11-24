# ADR 0003: README model table tied to the code by a test

## Status

Accepted.

## Context

The README model count once disagreed with the code (commit `d9dbdcb`, "docs: fix
the model count in README"), and a later commit completed the table, fixed a sign in the
logistic product formula and closed issue #1 (commit `79a7c2c`).

## Decision

`tests/test_readme.py` collects every subclass of `Arithmetic` defined in
`nna.core` and asserts that the README table under the header `| model |` has the
same number of rows, and that the README text says "N konkretnych modeli" with
the same N.

## Consequences

- Adding or removing a core model without updating the README fails the test suite.
- The test checks the row count and the stated number, not the formulas in each row;
  formulas are checked separately in `tests/test_axioms.py`.
- Thermal models in `src/nna/thermal.py` are not counted by this test.

## Evidence

- `tests/test_readme.py`
- Commits `d9dbdcb` and `79a7c2c`.
