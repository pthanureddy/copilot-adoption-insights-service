from pathlib import Path

from fastapi.testclient import TestClient

from copilot_insights.api import create_app
from copilot_insights.cli import run


def test_health() -> None:
    response = TestClient(create_app()).get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_insights_endpoint(usage, memberships) -> None:
    response = TestClient(create_app()).post(
        "/v1/insights",
        json={
            "usage": [item.model_dump(mode="json") for item in usage],
            "memberships": [item.model_dump(mode="json") for item in memberships],
        },
    )
    assert response.status_code == 200
    assert response.json()["organization"]["active_users"] == 2


def test_insights_rejects_empty_payload() -> None:
    response = TestClient(create_app()).post("/v1/insights", json={"usage": [], "memberships": []})
    assert response.status_code == 422


def test_cli_writes_three_outputs(tmp_path: Path) -> None:
    exit_code = run(
        [
            "--usage",
            "examples/usage.ndjson",
            "--memberships",
            "examples/memberships.ndjson",
            "--output-dir",
            str(tmp_path),
        ]
    )
    assert exit_code == 0
    assert {path.name for path in tmp_path.iterdir()} == {
        "insights.json",
        "insights.md",
        "dashboard.html",
    }
