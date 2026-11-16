# Requirements and verification

| ID | Requirement | Verification |
| --- | --- | --- |
| R1 | Reject malformed dates, identities, counts, team slugs, and impossible acceptance totals. | Model and IO tests |
| R2 | Join usage to membership using day and immutable numeric user id. | Analytics tests |
| R3 | Count duplicate and unmatched usage rows without silently multiplying totals. | Analytics tests |
| R4 | Aggregate active users, generations, acceptances, agent/chat use, and lines added. | Analytics tests |
| R5 | Never expose user logins in analysis outputs. | Privacy regression test |
| R6 | Explain undefined acceptance rather than substituting zero. | Recommendation test |
| R7 | Produce JSON, Markdown, and HTML outputs from one analysis result. | CLI/report tests |
| R8 | Expose health and analysis HTTP endpoints with input limits. | API tests |
| R9 | State the interpretation boundary in human-readable reports. | Report tests |
| R10 | Build and test automatically on pushes and pull requests. | GitHub Actions |

## Acceptance criteria

1. All committed synthetic records pass validation.
2. A duplicate `(day, user_id)` appears once in aggregates and increments the
   duplicate counter.
3. A usage row without a membership increments the unmatched counter.
4. API and CLI return identical aggregate semantics.
5. Generated outputs contain no committed synthetic login values.
6. Lint, formatting, test, coverage, package, and container jobs pass.

