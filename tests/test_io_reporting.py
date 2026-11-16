from pathlib import Path

import pytest

from copilot_insights.analytics import analyze
from copilot_insights.io import InputFormatError, read_memberships, read_usage, write_json
from copilot_insights.reporting import to_html, to_markdown


def test_example_files_parse() -> None:
    assert len(read_usage(Path("examples/usage.ndjson"))) == 8
    assert len(read_memberships(Path("examples/memberships.ndjson"))) == 8


def test_bad_ndjson_reports_line(tmp_path: Path) -> None:
    path = tmp_path / "bad.ndjson"
    path.write_text('{"day":"bad"}\n', encoding="utf-8")
    with pytest.raises(InputFormatError, match=":1:"):
        read_usage(path)


def test_empty_ndjson_rejected(tmp_path: Path) -> None:
    path = tmp_path / "empty.ndjson"
    path.write_text("\n", encoding="utf-8")
    with pytest.raises(InputFormatError, match="no records"):
        read_usage(path)


def test_markdown_has_boundary(usage, memberships) -> None:
    report = to_markdown(analyze(usage, memberships))
    assert "not individual productivity scores" in report
    assert "| alpha |" in report


def test_html_is_escaped(usage, memberships) -> None:
    memberships[0].team_slug = "alpha"  # model validation already constrains slug
    html = to_html(analyze(usage, memberships))
    assert "<!doctype html>" in html
    assert "Agent adoption" in html


def test_json_writer(tmp_path: Path, usage, memberships) -> None:
    output = tmp_path / "nested" / "insights.json"
    write_json(output, analyze(usage, memberships))
    assert output.exists()
    assert '"privacy_note"' in output.read_text(encoding="utf-8")
