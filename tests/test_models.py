from datetime import date

import pytest
from pydantic import ValidationError

from copilot_insights.models import TeamMembership, UsageRecord

TEST_DAY = date(2026, 11, 1)


def test_usage_active_from_interaction() -> None:
    record = UsageRecord(
        day=TEST_DAY, user_id=1, user_login="a", user_initiated_interaction_count=1
    )
    assert record.active


def test_usage_inactive_without_signal() -> None:
    record = UsageRecord(day=TEST_DAY, user_id=1, user_login="a")
    assert not record.active


def test_acceptance_cannot_exceed_generation() -> None:
    with pytest.raises(ValidationError, match="cannot exceed"):
        UsageRecord(
            day=TEST_DAY,
            user_id=1,
            user_login="a",
            code_generation_activity_count=1,
            code_acceptance_activity_count=2,
        )


def test_negative_counts_rejected() -> None:
    with pytest.raises(ValidationError):
        UsageRecord(day=TEST_DAY, user_id=1, user_login="a", loc_added_sum=-1)


def test_team_slug_is_constrained() -> None:
    with pytest.raises(ValidationError):
        TeamMembership(day=TEST_DAY, user_id=1, user_login="a", team_slug="Bad Team")


def test_unknown_github_fields_are_ignored() -> None:
    record = UsageRecord.model_validate(
        {"day": "2026-11-01", "user_id": 1, "user_login": "a", "future_field": "ok"}
    )
    assert record.user_login == "a"
