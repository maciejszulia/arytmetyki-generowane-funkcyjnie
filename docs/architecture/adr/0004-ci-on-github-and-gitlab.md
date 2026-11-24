# ADR 0004: The same CI jobs on GitHub Actions and GitLab CI

## Status

Accepted.

## Context

The repository is hosted on GitHub and on GitLab. Each service runs only its own
CI configuration.

## Decision

Both services install the package with `pip install -e ".[dev]"` on Python 3.12,
run `pytest -v`, run `python -m nna.figures`, and keep the PNG figures as a build
artefact.

## Consequences

- Test results are available on both hosts.
- Two files must be changed together when the build steps change.
- Neither pipeline builds the paper PDF.

## Evidence

- `.github/workflows/ci.yml`
- `.gitlab-ci.yml`
