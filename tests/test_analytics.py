from datetime import date

import pytest

from copilot_insights.analytics import analyze
from copilot_insights.models import TeamMembership, UsageRecord

TEST_DAY = date(2026, 11, 1)


def test_team_aggregation(usage, memberships) -> None:
    result = analyze(usage, memberships)
    alpha = result.teams[0]
    assert alpha.team_slug == "alpha"
    assert alpha.licensed_users == 2
    assert alpha.active_users == 2
    assert alpha.acceptance_rate == pytest.approx(11 / 30)
    assert alpha.agent_users == 1


def test_organization_distinct_users(usage, memberships) -> None:
    result = analyze(usage, memberships)
    assert result.organization.licensed_users == 3
    assert result.organization.active_users == 2


def test_unmatched_records_are_counted(usage, memberships) -> None:
    result = analyze(usage, memberships[:-1])
    assert result.metadata.unmatched_usage_records == 1


def test_duplicates_are_ignored(usage, memberships) -> None:
    result = analyze([*usage, usage[0]], memberships)
    assert result.metadata.duplicate_usage_records == 1
    assert result.organization.generation_count == 30


def test_output_does_not_include_user_logins(usage, memberships) -> None:
    output = analyze(usage, memberships).model_dump_json()
    assert "private-login-001" not in output
    assert "private-login-002" not in output


def test_no_usage_rejected(memberships) -> None:
    with pytest.raises(ValueError, match="usage record"):
        analyze([], memberships)


def test_no_memberships_rejected(usage) -> None:
    with pytest.raises(ValueError, match="membership"):
        analyze(usage, [])


def test_low_adoption_triggers_workshop(usage, memberships) -> None:
    result = analyze(usage, memberships)
    beta = next(item for item in result.teams if item.team_slug == "beta")
    assert "ADOPTION_WORKSHOP" in {item.code for item in beta.recommendations}


def test_no_generations_explains_undefined_acceptance(usage, memberships) -> None:
    result = analyze(usage, memberships)
    beta = next(item for item in result.teams if item.team_slug == "beta")
    assert beta.acceptance_rate is None
    assert "NO_COMPLETION_SIGNAL" in {item.code for item in beta.recommendations}


def test_low_acceptance_triggers_review() -> None:
    usage = [
        UsageRecord(
            day=TEST_DAY,
            user_id=1,
            user_login="x",
            code_generation_activity_count=10,
            code_acceptance_activity_count=1,
        )
    ]
    memberships = [TeamMembership(day=TEST_DAY, user_id=1, user_login="x", team_slug="alpha")]
    result = analyze(usage, memberships)
    assert "PROMPT_AND_CONTEXT_REVIEW" in {
        item.code for item in result.organization.recommendations
    }


def test_agent_discovery_trigger_for_active_team() -> None:
    usage = [
        UsageRecord(day=TEST_DAY, user_id=i, user_login=f"u{i}", loc_added_sum=1)
        for i in range(1, 5)
    ]
    memberships = [
        TeamMembership(day=TEST_DAY, user_id=i, user_login=f"u{i}", team_slug="alpha")
        for i in range(1, 5)
    ]
    result = analyze(usage, memberships)
    assert "AGENT_WORKFLOW_DISCOVERY" in {item.code for item in result.organization.recommendations}


def test_team_order_is_stable(usage, memberships) -> None:
    result = analyze(usage, list(reversed(memberships)))
    assert [item.team_slug for item in result.teams] == ["alpha", "beta"]
