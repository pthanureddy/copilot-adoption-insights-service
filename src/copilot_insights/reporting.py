from __future__ import annotations

from html import escape

from copilot_insights.models import AnalysisResult, TeamSummary


def _percent(value: float | None) -> str:
    return "n/a" if value is None else f"{value:.1%}"


def to_markdown(result: AnalysisResult) -> str:
    lines = [
        "# GitHub Copilot adoption insights",
        "",
        f"Period: {result.metadata.period_start} to {result.metadata.period_end}",
        "",
        "| Team | Active / licensed | Acceptance | Agent adoption | Lines added |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for team in [result.organization, *result.teams]:
        lines.append(
            f"| {team.team_slug} | {team.active_users} / {team.licensed_users} "
            f"({_percent(team.active_user_rate)}) | {_percent(team.acceptance_rate)} | "
            f"{_percent(team.agent_adoption_rate)} | {team.loc_added} |"
        )
    lines.extend(["", "## Recommended next steps", ""])
    for team in [result.organization, *result.teams]:
        lines.append(f"### {team.team_slug}")
        for item in team.recommendations:
            lines.append(f"- **{item.code}:** {item.observation} {item.next_step}")
        lines.append("")
    lines.extend(
        [
            "## Interpretation boundary",
            "",
            (
                "These metrics are directional usage signals, not individual productivity scores. "
                "Combine them with developer feedback and delivery-quality measures."
            ),
            "",
            result.metadata.privacy_note,
            "",
        ]
    )
    return "\n".join(lines)


def _team_card(team: TeamSummary) -> str:
    recs = "".join(
        f"<li><strong>{escape(item.code)}</strong>: {escape(item.next_step)}</li>"
        for item in team.recommendations
    )
    return f"""
    <section class="card">
      <h2>{escape(team.team_slug)}</h2>
      <div class="metrics">
        <div><span>Active</span><b>{team.active_users}/{team.licensed_users}</b></div>
        <div><span>Acceptance</span><b>{_percent(team.acceptance_rate)}</b></div>
        <div><span>Agent adoption</span><b>{_percent(team.agent_adoption_rate)}</b></div>
        <div><span>Lines added</span><b>{team.loc_added}</b></div>
      </div>
      <ul>{recs}</ul>
    </section>"""


def to_html(result: AnalysisResult) -> str:
    cards = "\n".join(_team_card(team) for team in [result.organization, *result.teams])
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width">
<title>Copilot adoption insights</title><style>
body{{font-family:system-ui,sans-serif;background:#f5f7fb;color:#172033;margin:0;padding:2rem}}
main{{max-width:1000px;margin:auto}} .card{{background:white;border:1px solid #d9e0ec;border-radius:12px;
padding:1.2rem;margin:1rem 0;box-shadow:0 4px 14px #20304a12}} .metrics{{display:grid;
grid-template-columns:repeat(auto-fit,minmax(140px,1fr));gap:.8rem}} .metrics div{{background:#eef4ff;
padding:.8rem;border-radius:8px}} span{{display:block;color:#5b6780;font-size:.82rem}} b{{font-size:1.3rem}}
.boundary{{border-left:4px solid #4776d0;padding-left:1rem;color:#46546c}} li{{margin:.45rem 0}}
</style></head><body><main><h1>GitHub Copilot adoption insights</h1>
<p>{result.metadata.period_start} to {result.metadata.period_end}</p>{cards}
<p class="boundary">Directional usage signals only - not individual productivity scores. 
Combine with developer feedback and delivery-quality measures.</p></main></body></html>"""
