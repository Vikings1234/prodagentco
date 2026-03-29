"""Web Research Agent — scans online communities for unmet needs and pain signals."""

from crewai import Agent, Crew, Task, Process
from config.models import GROQ_MODEL


def create_web_research_agent() -> Agent:
    return Agent(
        role="Web Research Agent",
        goal=(
            "Scan Reddit, HackerNews, Product Hunt, GitHub Issues, and AppSumo "
            "for unmet needs and pain signals. Return a JSON list of raw opportunity "
            "signals with source URLs and engagement metrics."
        ),
        backstory=(
            "You are an expert market intelligence researcher specializing in finding "
            "validated pain signals from online communities. You excel at identifying "
            "threads where users express strong frustration with missing tools."
        ),
        llm=GROQ_MODEL,
        verbose=True,
    )


def run_web_research(query: str = "find unmet software needs") -> str:
    """Run the web research agent standalone."""
    agent = create_web_research_agent()
    task = Task(
        description=f"Research market pain signals for: {query}. Return structured JSON with at least 5 opportunities.",
        expected_output="A JSON list of opportunity signals with source, description, and engagement metrics.",
        agent=agent,
    )
    crew = Crew(
        agents=[agent],
        tasks=[task],
        process=Process.sequential,
        verbose=True,
    )
    return str(crew.kickoff())
