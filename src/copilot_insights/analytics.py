from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field

from copilot_insights.models import (
    AnalysisMetadata,
    AnalysisResult,
    InsightSeverity,
    Recommendation,
    TeamMembership,
    TeamSummary,
    UsageRecord,
)


@dataclass
class _Accumulator:
    licensed_users: set[int] = field(default_factory=set)
    active_users: set[int] = field(default_factory=set)
    agent_users: set[int] = field(default_factory=set)
    chat_users: set[int] = field(default_factory=set)
    generation_count: int = 0
    acceptance_count: int = 0
    loc_added: int = 0


def _recommend(summary: TeamSummary) -> list[Recommendation]:
    recommendations: list[Recommendation] = []
    if summary.active_user_rate < 0.60:
        recommendations.append(
            Recommendation(
                code="ADOPTION_WORKSHOP",
                severity=InsightSeverity.ATTENTION,
                observation="Fewer than 60% of licensed users were active in the selected period.",
                next_step="Run a role-based workshop, then compare the same metric after two weeks.",
                evidence={"active_user_rate": round(summary.active_user_rate, 4)},
            )
        )
    if summary.acceptance_rate is None:
        recommendations.append(
            Recommendation(
                code="NO_COMPLETION_SIGNAL",
                severity=InsightSeverity.INFO,
                observation="No code-generation activity was present, so acceptance is undefined.",
                next_step="Check client telemetry coverage before interpreting team behavior.",
                evidence={"generation_count": 0},
            )
        )
    elif summary.generation_count >= 10 and summary.acceptance_rate < 0.20:
        recommendations.append(
            Recommendation(
                code="PROMPT_AND_CONTEXT_REVIEW",
                severity=InsightSeverity.OPPORTUNITY,
                observation="Completion acceptance was below 20% across at least ten generations.",
                next_step="Interview users about context quality and test a focused prompting clinic.",
                evidence={
                    "acceptance_rate": round(summary.acceptance_rate, 4),
                    "generation_count": summary.generation_count,
                },
            )
        )
    if summary.active_users >= 3 and summary.agent_adoption_rate < 0.25:
        recommendations.append(
            Recommendation(
                code="AGENT_WORKFLOW_DISCOVERY",
                severity=InsightSeverity.OPPORTUNITY,
                observation="Fewer than 25% of active users tried an agent workflow.",
                next_step="Identify one low-risk engineering workflow and evaluate an agent-assisted trial.",
                evidence={"agent_adoption_rate": round(summary.agent_adoption_rate, 4)},
            )
        )
    if not recommendations:
        recommendations.append(
            Recommendation(
                code="QUALITATIVE_FOLLOW_UP",
                severity=InsightSeverity.INFO,
                observation="No configured threshold was triggered.",
                next_step="Combine these directional metrics with developer feedback before acting.",
                evidence={"active_users": summary.active_users},
            )
        )
    return recommendations


def _to_summary(team_slug: str, acc: _Accumulator) -> TeamSummary:
    licensed = len(acc.licensed_users)
    active = len(acc.active_users)
    summary = TeamSummary(
        team_slug=team_slug,
        licensed_users=licensed,
        active_users=active,
        active_user_rate=(active / licensed) if licensed else 0.0,
        generation_count=acc.generation_count,
        acceptance_count=acc.acceptance_count,
        acceptance_rate=(acc.acceptance_count / acc.generation_count)
        if acc.generation_count
        else None,
        agent_users=len(acc.agent_users),
        agent_adoption_rate=(len(acc.agent_users) / active) if active else 0.0,
        chat_users=len(acc.chat_users),
        loc_added=acc.loc_added,
        recommendations=[],
    )
    summary.recommendations = _recommend(summary)
    return summary


def _add(acc: _Accumulator, record: UsageRecord) -> None:
    acc.licensed_users.add(record.user_id)
    if record.active:
        acc.active_users.add(record.user_id)
    if record.used_agent:
        acc.agent_users.add(record.user_id)
    if record.used_chat:
        acc.chat_users.add(record.user_id)
    acc.generation_count += record.code_generation_activity_count
    acc.acceptance_count += record.code_acceptance_activity_count
    acc.loc_added += record.loc_added_sum


def analyze(usage: list[UsageRecord], memberships: list[TeamMembership]) -> AnalysisResult:
    if not usage:
        raise ValueError("at least one usage record is required")
    if not memberships:
        raise ValueError("at least one membership record is required")

    membership_index = {(item.day, item.user_id): item.team_slug for item in memberships}
    seen: set[tuple[object, int]] = set()
    duplicate_count = 0
    unmatched = 0
    organization = _Accumulator()
    teams: dict[str, _Accumulator] = defaultdict(_Accumulator)

    for record in usage:
        key = (record.day, record.user_id)
        if key in seen:
            duplicate_count += 1
            continue
        seen.add(key)
        _add(organization, record)
        team_slug = membership_index.get(key)
        if team_slug is None:
            unmatched += 1
            continue
        _add(teams[team_slug], record)

    days = [record.day for record in usage]
    return AnalysisResult(
        metadata=AnalysisMetadata(
            period_start=min(days),
            period_end=max(days),
            usage_records=len(usage),
            membership_records=len(memberships),
            unmatched_usage_records=unmatched,
            duplicate_usage_records=duplicate_count,
            privacy_note=(
                "User identifiers are used only for joining and distinct counts; outputs contain "
                "team-level aggregates and no user logins."
            ),
        ),
        organization=_to_summary("organization", organization),
        teams=[_to_summary(slug, teams[slug]) for slug in sorted(teams)],
    )
