from __future__ import annotations

import argparse
from pathlib import Path

from copilot_insights.analytics import analyze
from copilot_insights.io import read_memberships, read_usage, write_json
from copilot_insights.reporting import to_html, to_markdown


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Analyze GitHub Copilot usage reports")
    parser.add_argument("--usage", type=Path, required=True, help="Per-user usage NDJSON")
    parser.add_argument("--memberships", type=Path, required=True, help="User-team NDJSON")
    parser.add_argument("--output-dir", type=Path, default=Path("out"))
    return parser


def run(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    result = analyze(read_usage(args.usage), read_memberships(args.memberships))
    args.output_dir.mkdir(parents=True, exist_ok=True)
    write_json(args.output_dir / "insights.json", result)
    (args.output_dir / "insights.md").write_text(to_markdown(result), encoding="utf-8")
    (args.output_dir / "dashboard.html").write_text(to_html(result), encoding="utf-8")
    print(f"Wrote aggregate insights to {args.output_dir.resolve()}")
    return 0


def main() -> None:
    raise SystemExit(run())


if __name__ == "__main__":
    main()
