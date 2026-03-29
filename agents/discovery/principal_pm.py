"""Principal PM Agent — synthesizes opportunities into an executive brief."""

from crewai import Agent, Crew, Task, Process
from config.models import HAIKU_MODEL


def create_principal_pm_agent() -> Agent:
    return Agent(
        role="Principal PM",
        goal=(
            "Synthesize scored opportunities into a crisp executive brief. Select the "
            "top 2-3 opportunities with a why-now, why-us narrative. Produce a ranked "
            "shortlist with a lead recommendation."
        ),
        backstory=(
            "You are a senior product strategist who turns raw market data into focused "
            "executive recommendations. You apply judgment beyond the numbers — considering "
            "timing, market windows, and builder capabilities."
        ),
        llm=HAIKU_MODEL,
        verbose=True,
    )


def run_principal_pm(opportunities: str) -> str:
    """Run the principal PM agent standalone."""
    agent = create_principal_pm_agent()
    task = Task(
        description=(
            f"Read the scored opportunities below. Select the top 2-3 with strategic "
            f"judgment beyond ICE scores. Write a discovery brief with a why-now/why-us "
            f"narrative, ranked shortlist, and lead recommendation.\n\n"
            f"Opportunities:\n{opportunities}"
        ),
        expected_output="A markdown executive brief with top 2-3 opportunities, narrative framing, lead recommendation, key risks, and suggested debate focus areas.",
        agent=agent,
    )
    crew = Crew(
        agents=[agent],
        tasks=[task],
        process=Process.sequential,
        verbose=True,
    )
    return str(crew.kickoff())
