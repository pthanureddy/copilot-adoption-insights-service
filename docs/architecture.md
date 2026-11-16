# Architecture and decisions

## Data path

The service separates four concerns:

1. `models.py` validates a deliberately small, additive-compatible subset of
   the GitHub report contract.
2. `io.py` records file and line numbers for invalid NDJSON.
3. `analytics.py` performs deterministic joins, aggregation, and transparent
   recommendation rules.
4. `api.py`, `cli.py`, and `reporting.py` expose the same result through HTTP,
   JSON, Markdown, and HTML.

## Privacy boundary

`user_id` and `user_login` exist only in validated input models. The numeric id
is used for daily joins and distinct counts; neither field exists in output
models. This structural boundary is reinforced by a test that serializes the
complete output and checks fixture logins are absent.

Production use should enforce a minimum team size before returning any team
slice. It should also define retention, access, audit, deletion, and data-
residency rules with privacy, security, and employee-representative input.

## Metric choices

- Active user: any interaction, generation, or lines-added signal in the period.
- Acceptance rate: accepted generation activities divided by generation
  activities; undefined when the denominator is zero.
- Agent adoption: distinct agent users divided by distinct active users.
- Lines added: reported directional total, shown without productivity claims.

The project does not create a composite productivity score. GitHub's own
guidance recommends interpreting patterns across signals and combining them
with qualitative feedback.

## Recommendation rules

Thresholds are configuration candidates, kept explicit for review:

- active-user rate below 60% -> role-based workshop and follow-up measurement;
- at least ten generations with acceptance below 20% -> context/prompt review;
- at least three active users with agent adoption below 25% -> discover one
  low-risk agent workflow;
- no generation activity -> check telemetry before interpreting behavior.

These are not industry benchmarks. They are safe, reversible actions derived
from observable signals.

## Trade-offs

- NDJSON matches large report workflows and streams cleanly, but this version
  reads each file into memory before analysis.
- Unknown fields are ignored for additive compatibility; CI should add schema
  fixtures when GitHub changes a field used by the service.
- One team per user/day simplifies attribution. Multi-team attribution needs an
  explicit allocation rule to avoid double-counting.

