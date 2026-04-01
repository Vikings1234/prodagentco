"""Marketing Agent — debate mode (argue GTM) and planning mode (write GTM plan)."""

from crewai import Agent
from config.models import HAIKU_MODEL


def create_marketing_agent() -> Agent:
    """Debate mode — argues positioning and GTM case."""
    return Agent(
        role="Chief Marketing Officer",
        goal=(
            "Evaluate the lead opportunity from a market positioning and GTM perspective. "
            "Argue for or against building based on: brand differentiation, customer "
            "acquisition strategy, messaging clarity, channel viability, competitive "
            "positioning, and launch feasibility. Assign a confidence score 0.0-1.0 "
            "and vote build/kill/defer with a proposed positioning statement and "
            "30-day launch plan outline."
        ),
        backstory=(
            "You are a CMO with experience launching developer tools, fintech products, "
            "and B2B SaaS platforms. You understand both product-led growth and "
            "enterprise sales motions. You are skeptical of products with unclear "
            "positioning and push hard for a crisp ICP definition before approving "
            "any GTM investment."
        ),
        llm=HAIKU_MODEL,
        verbose=True,
    )


def create_marketing_planning_agent() -> Agent:
    """Planning mode — writes full GTM plan."""
    return Agent(
        role="Chief Marketing Officer",
        goal=(
            "Write a complete Go-To-Market plan for the approved opportunity. "
            "Include: Ideal Customer Profile (ICP) with firmographics and psychographics, "
            "positioning statement and messaging framework, competitive positioning map, "
            "channel strategy (content, paid, community, partnerships), "
            "launch timeline with milestones, pre-launch and post-launch playbooks, "
            "key metrics and targets for first 90 days, and budget allocation by channel."
        ),
        backstory=(
            "You are a CMO with experience launching developer tools, fintech products, "
            "and B2B SaaS platforms. You understand both product-led growth and "
            "enterprise sales motions. You write GTM plans with concrete channel "
            "strategies, not vague 'build awareness' platitudes. Every tactic has "
            "a timeline, owner, and measurable outcome."
        ),
        llm=HAIKU_MODEL,
        verbose=True,
    )
