"""Phase 1 Discovery Pipeline — Web Research -> Market Analysis -> Principal PM Brief."""

from crewai import Crew, Task, Process
from agents.discovery.web_research import create_web_research_agent
from agents.discovery.market_analyst import create_market_analyst_agent
from agents.discovery.principal_pm import create_principal_pm_agent
from config.settings import OUTPUT_DIR


def run_discovery_phase(query: str = "find unmet software needs and market gaps") -> str:
    """Run the full discovery pipeline: web research -> market analysis -> principal PM brief."""

    web_agent = create_web_research_agent()
    analyst_agent = create_market_analyst_agent()
    pm_agent = create_principal_pm_agent()

    web_task = Task(
        description=f"Research market pain signals for: {query}. Return structured JSON with at least 5 opportunities.",
        expected_output="A JSON list of opportunity signals with source, description, and engagement metrics.",
        agent=web_agent,
        output_file=str(OUTPUT_DIR / "signals.json"),
    )

    analysis_task = Task(
        description="Score all signals from the web research. Apply ICE scoring (Impact x Confidence x Ease). Filter to ICE > 200. Estimate TAM, competition density, moat strength, and effort bucket.",
        expected_output="A JSON list of scored opportunities ranked by ICE score, each with TAM, ICE breakdown, competition, moat, and effort.",
        agent=analyst_agent,
        context=[web_task],
        output_file=str(OUTPUT_DIR / "opportunities.json"),
    )

    pm_task = Task(
        description="Read the scored opportunities. Select the top 2-3 with strategic judgment beyond ICE scores. Write a discovery-brief.md with a why-now/why-us narrative for each, a ranked shortlist, and a lead recommendation with rationale.",
        expected_output="A markdown executive brief with top 2-3 opportunities, narrative framing, lead recommendation, key risks, and suggested debate focus areas.",
        agent=pm_agent,
        context=[analysis_task],
        output_file=str(OUTPUT_DIR / "discovery-brief.md"),
    )

    crew = Crew(
        agents=[web_agent, analyst_agent, pm_agent],
        tasks=[web_task, analysis_task, pm_task],
        process=Process.sequential,
        verbose=True,
    )

    result = crew.kickoff()
    return str(result)
