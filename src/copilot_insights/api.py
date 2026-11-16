from __future__ import annotations

from fastapi import FastAPI

from copilot_insights.analytics import analyze
from copilot_insights.models import AnalysisResult, AnalyzeRequest


def create_app() -> FastAPI:
    app = FastAPI(
        title="Copilot Adoption Insights Service",
        version="0.1.0",
        description="Team-level analytics for validated GitHub Copilot usage reports.",
    )

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.post("/v1/insights", response_model=AnalysisResult)
    def insights(request: AnalyzeRequest) -> AnalysisResult:
        return analyze(request.usage, request.memberships)

    return app


app = create_app()
