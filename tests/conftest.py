from __future__ import annotations

from datetime import date

import pytest

from copilot_insights.models import TeamMembership, UsageRecord


@pytest.fixture
def usage() -> list[UsageRecord]:
    return [
        UsageRecord(
            day=date(2026, 11, 1),
            user_id=1,
            user_login="private-login-001",
            user_initiated_interaction_count=4,
            code_generation_activity_count=20,
            code_acceptance_activity_count=10,
            loc_added_sum=40,
            used_agent=True,
            used_chat=True,
        ),
        UsageRecord(
            day=date(2026, 11, 1),
            user_id=2,
            user_login="private-login-002",
            code_generation_activity_count=10,
            code_acceptance_activity_count=1,
        ),
        UsageRecord(day=date(2026, 11, 1), user_id=3, user_login="private-login-003"),
    ]


@pytest.fixture
def memberships() -> list[TeamMembership]:
    return [
        TeamMembership(
            day=date(2026, 11, 1), user_id=1, user_login="private-login-001", team_slug="alpha"
        ),
        TeamMembership(
            day=date(2026, 11, 1), user_id=2, user_login="private-login-002", team_slug="alpha"
        ),
        TeamMembership(
            day=date(2026, 11, 1), user_id=3, user_login="private-login-003", team_slug="beta"
        ),
    ]
