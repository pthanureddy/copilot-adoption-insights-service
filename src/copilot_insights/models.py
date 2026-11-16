from __future__ import annotations

from datetime import date
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, model_validator


class FeatureMetric(BaseModel):
    model_config = ConfigDict(extra="ignore")

    feature: str = Field(min_length=1)
    code_acceptance_activity_count: int = Field(default=0, ge=0)
    code_generation_activity_count: int = Field(default=0, ge=0)
    loc_added_sum: int = Field(default=0, ge=0)
    user_initiated_interaction_count: int = Field(default=0, ge=0)


class UsageRecord(BaseModel):
    """Validated subset of GitHub's per-user Copilot usage report schema."""

    model_config = ConfigDict(extra="ignore")

    day: date
    user_id: int = Field(ge=1)
    user_login: str = Field(min_length=1)
    user_initiated_interaction_count: int = Field(default=0, ge=0)
    code_acceptance_activity_count: int = Field(default=0, ge=0)
    code_generation_activity_count: int = Field(default=0, ge=0)
    loc_added_sum: int = Field(default=0, ge=0)
    used_agent: bool = False
    used_chat: bool = False
    totals_by_feature: list[FeatureMetric] = Field(default_factory=list)

    @model_validator(mode="after")
    def acceptance_cannot_exceed_generation(self) -> UsageRecord:
        if self.code_acceptance_activity_count > self.code_generation_activity_count:
            raise ValueError("accepted generations cannot exceed generated suggestions")
        return self

    @property
    def active(self) -> bool:
        return bool(
            self.user_initiated_interaction_count
            or self.code_generation_activity_count
            or self.loc_added_sum
        )


class TeamMembership(BaseModel):
    model_config = ConfigDict(extra="ignore")

    day: date
    user_id: int = Field(ge=1)
    user_login: str = Field(min_length=1)
    team_slug: str = Field(min_length=1, pattern=r"^[a-z0-9][a-z0-9-]*$")


class InsightSeverity(StrEnum):
    INFO = "info"
    OPPORTUNITY = "opportunity"
    ATTENTION = "attention"


class Recommendation(BaseModel):
    code: str
    severity: InsightSeverity
    observation: str
    next_step: str
    evidence: dict[str, float | int | str]


class TeamSummary(BaseModel):
    team_slug: str
    licensed_users: int
    active_users: int
    active_user_rate: float = Field(ge=0, le=1)
    generation_count: int
    acceptance_count: int
    acceptance_rate: float | None = Field(default=None, ge=0, le=1)
    agent_users: int
    agent_adoption_rate: float = Field(ge=0, le=1)
    chat_users: int
    loc_added: int
    recommendations: list[Recommendation]


class AnalysisMetadata(BaseModel):
    period_start: date
    period_end: date
    usage_records: int
    membership_records: int
    unmatched_usage_records: int
    duplicate_usage_records: int
    privacy_note: str


class AnalysisResult(BaseModel):
    metadata: AnalysisMetadata
    organization: TeamSummary
    teams: list[TeamSummary]


class AnalyzeRequest(BaseModel):
    usage: list[UsageRecord] = Field(min_length=1, max_length=100_000)
    memberships: list[TeamMembership] = Field(min_length=1, max_length=100_000)
