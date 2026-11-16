# Executed verification

This file is updated only with commands actually run against the published
commit. The service uses synthetic data and no live GitHub Enterprise report.

## Local verification - 16 November 2026

- Ruff lint: passed.
- Ruff format check: passed.
- Pytest: **28 passed**, 0 failed, 0 skipped.
- Coverage: **99% total** with branch measurement (234 statements, 42 branches).
- Wheel build: passed with `pip wheel --no-build-isolation --no-deps`.
- CLI end-to-end run: passed; produced JSON, Markdown, and HTML from the
  committed synthetic fixtures.

The host drive had insufficient free space for a fresh isolated build
environment, so the wheel was built against the already installed and declared
`setuptools` backend. GitHub Actions repeats installation, lint, formatting,
tests with a 90% coverage gate, package build, CLI generation, and container
build in clean hosted environments.

## Hosted verification

GitHub Actions run
[43915174464](https://github.com/pthanureddy/copilot-adoption-insights-service/actions/runs/43915174464)
completed successfully against commit
`26d1b74899bdf572f16e24b15696297f71a257dc` on 16 November 2026.

- Test job: dependency install, Ruff lint/format, 28 tests with branch coverage
  above the 90% gate, package build, CLI report generation, and artifact upload
  all passed.
- Container job: Docker Buildx image build passed.

