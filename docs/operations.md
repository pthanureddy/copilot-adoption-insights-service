# Operations and workshop guide

## Proposed scheduled workflow

1. Use a GitHub App or fine-grained token with the minimum organization Copilot
   metrics read permission.
2. Request the 28-day organization usage report and daily user-team report using
   GitHub's current versioned API.
3. Download signed report URLs immediately; never log them.
4. Validate checksums, dates, schema, row counts, and membership match rate.
5. Run this analyzer in a private job and publish only approved aggregates.
6. Expire raw reports and tokens under organization policy.
7. Record job status, schema errors, unmatched rate, and output publication in
   operational telemetry.

## Troubleshooting

| Symptom | Check | Action |
| --- | --- | --- |
| 403 from GitHub | API policy, role, token scope | Request minimum documented permission; do not broaden blindly |
| 204 or empty report | Processing delay, date, telemetry policy | Retry later and record missing period |
| High unmatched count | Team snapshot day and user id | Fetch matching daily team report; do not guess membership |
| Acceptance suddenly undefined | Generation telemetry and client versions | Validate coverage before communicating a trend |
| Metric jump | Schema version, population, date range | Reconcile with GitHub dashboard and release notes |

## Facilitated review

Use the dashboard as a conversation aid:

1. State that usage telemetry is not a performance-management instrument.
2. Review data quality and population before interpreting a change.
3. Ask developers what creates friction, where suggestions lack context, and
   which low-risk workflows deserve experimentation.
4. Choose one action with an owner, safety boundary, and follow-up date.
5. Pair quantitative trends with a short anonymous developer-feedback pulse.

## Production readiness gaps

Add enterprise authentication/authorization, signed-link download handling,
encrypted object storage, retention automation, audit logs, rate-limit/backoff,
observability, minimum aggregation thresholds, accessibility review, and threat
modeling before organizational use.

