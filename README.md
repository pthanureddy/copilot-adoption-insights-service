# Copilot Adoption Insights Service

A privacy-aware Python service that converts GitHub Copilot per-user usage and
user-team reports into team-level adoption insights, a static dashboard, and
specific follow-up actions for developer-experience teams.

This is an independent portfolio implementation built with synthetic data. It
has not processed SEB or other employer data, and it has not been connected to
a live GitHub Enterprise account.

## Why it exists

AI-tool adoption data is easy to misuse. A single acceptance or line-of-code
number is not a productivity score. This project validates report inputs, joins
daily usage to team membership, aggregates only the signals needed for action,
and removes user identifiers from every output. Recommendations are transparent
threshold rules intended to start a workshop or investigation, not to evaluate
individual developers.

## Implemented capabilities

- Parses a validated subset of GitHub's current per-user Copilot usage report
  schema (`day`, user identity, interaction, generation, acceptance, lines,
  chat/agent usage, and feature totals).
- Joins daily user-team membership by `(day, user_id)` and explicitly reports
  unmatched and duplicate records.
- Calculates active-user rate, completion acceptance, agent adoption, chat
  adoption, and directional lines-added totals at organization and team level.
- Produces JSON, Markdown, and a responsive HTML dashboard with no user logins.
- Generates evidence-linked next steps for low adoption, low acceptance,
  missing telemetry, or low agent exploration.
- Exposes a FastAPI endpoint for integrations and a CLI for scheduled automation.
- Includes synthetic fixtures, 28 automated tests, linting, coverage, packaging,
  Docker, and GitHub Actions CI.

GitHub recommends interpreting multiple signals together and combining metrics
with developer feedback. The implementation follows that boundary and does not
rank people or claim that generated lines equal delivered value.

## Architecture

```text
GitHub usage report ----\
                         -> validation -> day/user join -> team aggregates
GitHub user-team report -/                                 |
                                                           +-> JSON API
                                                           +-> Markdown brief
                                                           +-> HTML dashboard
                                                           +-> action rules
```

The repository accepts local NDJSON so tests remain reproducible without a
GitHub Enterprise account. In production, an approved scheduled job would call
GitHub's organization usage-report endpoints, download the short-lived report
links, store raw files under the organization's retention policy, then invoke
this service. That authenticated collector is deliberately outside this
portfolio scope.

## Quick start

Requires Python 3.11 or newer.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
copilot-insights --usage examples/usage.ndjson `
  --memberships examples/memberships.ndjson --output-dir out
```

Open `out/dashboard.html`, or inspect `out/insights.json` and
`out/insights.md`.

Run the API:

```powershell
uvicorn copilot_insights.api:app --host 127.0.0.1 --port 8000
```

- Health: `GET /health`
- Analysis: `POST /v1/insights`
- OpenAPI: `GET /docs`

## Verification

```powershell
python -m ruff check .
python -m ruff format --check .
python -m pytest --cov=copilot_insights --cov-branch --cov-report=term-missing
python -m build
docker build -t copilot-adoption-insights-service .
```

See [executed verification](docs/verification.md) for measured results and the
hosted CI run. See [requirements](docs/requirements.md),
[architecture and decisions](docs/architecture.md), and
[operations and workshop guide](docs/operations.md).

## Data contract

The committed files in `examples/` contain fictional users. Unknown fields are
ignored to tolerate additive GitHub schema changes; required fields, non-negative
counts, and `accepted <= generated` are enforced. Team slugs use lowercase
letters, digits, and hyphens.

Current GitHub reference material:

- [Copilot usage metrics](https://docs.github.com/en/copilot/concepts/billing-and-usage/copilot-usage-metrics/copilot-metrics)
- [Usage-metrics REST endpoints](https://docs.github.com/en/rest/copilot/copilot-usage-metrics?apiVersion=2026-03-10)
- [Example report schema](https://docs.github.com/en/copilot/reference/copilot-usage-metrics/example-schema)
- [Reconciling metrics](https://docs.github.com/en/copilot/reference/copilot-usage-metrics/reconciling-usage-metrics)

## Limitations

- No live GitHub Enterprise ingestion or organizational deployment is claimed.
- "Licensed users" means distinct users appearing in the joined report period;
  it is not a billing-seat inventory.
- A user can belong to only one team per day in this simplified model.
- Thresholds are documented hypotheses, not universal benchmarks.
- Lines-added and acceptance are directional usage signals, not quality,
  productivity, or business-value measures.
- Before production use, add enterprise identity, encrypted storage, retention,
  data residency review, schema monitoring, rate-limit handling, and an approved
  minimum aggregation threshold.

## License

MIT

