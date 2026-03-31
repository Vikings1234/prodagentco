"""Phase 1 Debate Pipeline — CEO chairs debate between worker agents."""

from crewai import Crew, Task, Process
from agents.executive.ceo import create_ceo_agent
from agents.executive.cfo import create_cfo_agent
from agents.planning.pm import create_pm_agent
from agents.planning.cto import create_cto_agent
from agents.planning.marketing import create_marketing_agent
from agents.planning.legal import create_legal_agent
from config.settings import OUTPUT_DIR


def run_debate_phase(discovery_brief: str = None) -> str:

    if discovery_brief is None:
        brief_path = OUTPUT_DIR / "discovery-brief.md"
        with open(brief_path, "r") as f:
            discovery_brief = f.read()

    ceo = create_ceo_agent()
    pm = create_pm_agent()
    cto = create_cto_agent()
    cfo = create_cfo_agent()
    marketing = create_marketing_agent()
    legal = create_legal_agent()

    pm_task = Task(
        description=f"Read the discovery brief and argue the product-market fit case for the LEAD opportunity. Assign confidence 0.0-1.0 and vote build/kill/defer.\n\nDiscovery Brief:\n{discovery_brief}",
        expected_output="Position (for/against/neutral), confidence score, vote, top 3 reasons, key risks.",
        agent=pm,
    )

    cto_task = Task(
        description=f"Read the discovery brief and argue the technical feasibility case for the LEAD opportunity. Assign confidence 0.0-1.0 and vote build/kill/defer.\n\nDiscovery Brief:\n{discovery_brief}",
        expected_output="Position, confidence score, vote, effort estimate, top 3 technical risks, build time estimate.",
        agent=cto,
    )

    cfo_task = Task(
        description=f"Read the discovery brief and argue the financial viability case for the LEAD opportunity. Assign confidence 0.0-1.0 and vote build/kill/defer.\n\nDiscovery Brief:\n{discovery_brief}",
        expected_output="Position, confidence score, vote, revenue projections, payback period, top 3 financial risks.",
        agent=cfo,
    )

    marketing_task = Task(
        description=f"Read the discovery brief and argue the GTM and positioning case for the LEAD opportunity. Assign confidence 0.0-1.0 and vote build/kill/defer.\n\nDiscovery Brief:\n{discovery_brief}",
        expected_output="Position, confidence score, vote, positioning statement, ICP definition, 30-day launch outline.",
        agent=marketing,
    )

    legal_task = Task(
        description=f"Read the discovery brief and argue the legal and regulatory risk case for the LEAD opportunity. Assign confidence 0.0-1.0 and vote build/kill/defer.\n\nDiscovery Brief:\n{discovery_brief}",
        expected_output="Position, confidence score, vote, top 3 legal risks, compliance requirements, mitigations.",
        agent=legal,
    )

    ceo_task = Task(
        description="You are chairing the product debate. Read all agent arguments and synthesize into a final CEO decision. Apply consensus rule: PROCEED if average confidence >= 0.70 AND no agent below 0.40. Issue final verdict: GO / NO-GO / NEEDS_HUMAN_REVIEW.",
        expected_output="Final verdict (GO/NO-GO/NEEDS_HUMAN_REVIEW), average confidence score, individual agent scores, key winning arguments, key risks, rationale.",
        agent=ceo,
        context=[pm_task, cto_task, cfo_task, marketing_task, legal_task],
        output_file=str(OUTPUT_DIR / "debate-verdict.md"),
    )

    crew = Crew(
        agents=[pm, cto, cfo, marketing, legal, ceo],
        tasks=[pm_task, cto_task, cfo_task, marketing_task, legal_task, ceo_task],
        process=Process.sequential,
        verbose=True,
    )

    return str(crew.kickoff())
