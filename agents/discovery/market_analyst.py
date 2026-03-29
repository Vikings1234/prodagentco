"""Market Analyst Agent — scores and ranks opportunities using ICE scoring."""

from crewai import Agent, Crew, Task, Process
from config.models import GROQ_MODEL


def create_market_analyst_agent() -> Agent:
    return Agent(
        role="Market Analyst",
        goal=(
            "Score and rank market opportunities using ICE scoring "
            "(Impact x Confidence x Ease, max 1000). Estimate TAM, competition "
            "density, moat strength, and effort bucket for each opportunity."
        ),
        backstory=(
            "You are a rigorous market analyst with deep expertise in bottom-up TAM "
            "estimation and opportunity scoring frameworks. You apply ICE scoring with "
            "precision and surface only the most promising opportunities."
        ),
        llm=GROQ_MODEL,
        verbose=True,
    )


def run_market_analysis(signals: str) -> str:
    """Run the market analyst agent standalone."""
    agent = create_market_analyst_agent()
    task = Task(
        description=(
            f"Score the following signals using ICE scoring. Filter to ICE > 200. "
            f"Estimate TAM, competition density, moat strength, and effort bucket.\n\n"
            f"Signals:\n{signals}"
        ),
        expected_output="A JSON list of scored opportunities ranked by ICE score, each with TAM, ICE breakdown, competition, moat, and effort.",
        agent=agent,
    )
    crew = Crew(
        agents=[agent],
        tasks=[task],
        process=Process.sequential,
        verbose=True,
    )
    return str(crew.kickoff())
