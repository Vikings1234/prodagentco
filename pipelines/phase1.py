"""Phase 1 Discovery Pipeline — Web Research -> Market Analysis -> Principal PM Brief."""

import os
import json
import requests
import litellm
from crewai import Crew, Task, Process
from agents.discovery.web_research import create_web_research_agent, search_github_issues, search_product_hunt
from agents.discovery.market_analyst import create_market_analyst_agent
from agents.discovery.principal_pm import create_principal_pm_agent
from config.settings import OUTPUT_DIR
from config.models import HAIKU_MODEL


# ---------------------------------------------------------------------------
# Domain labels — human-readable names for the dashboard domain selector
# ---------------------------------------------------------------------------

DOMAIN_LABELS = {
    "agentic-payments": "Agentic Commerce Payments",
    "sports-analytics": "Sports Analytics",
    "fintech": "Fintech",
    "healthcare": "Healthcare",
}


def get_domain_config(domain: str, custom_query: str = None) -> dict:
    """Use Claude Haiku to dynamically generate a rich search config for any domain."""

    # Resolve the domain description Haiku will reason about
    if domain == "custom" and custom_query:
        domain_description = custom_query
    elif domain in DOMAIN_LABELS:
        domain_description = DOMAIN_LABELS[domain]
    else:
        domain_description = domain

    print(f"🤖 Generating domain config for: {domain_description}")

    prompt = f"""You are a market research expert. Generate a rich discovery configuration for the domain below.

Domain: "{domain_description}"

Return ONLY valid JSON (no markdown fences, no explanation) with these exact keys:
{{
  "label": "Short domain label (2-4 words)",
  "discovery_query": "A detailed 150-200 word search query for finding unmet needs and pain signals in this domain in 2026. Be extremely specific — name real products, protocols, APIs, standards, companies, and technical terms that practitioners actually use. Cover infrastructure gaps, developer friction, compliance pain, and unserved market segments.",
  "github_query": "A GitHub issues search query targeting relevant repos and keywords in this domain, using OR operators, ending with label:feature-request OR label:enhancement state:open",
  "subreddits": ["r/sub1", "r/sub2", ..., "r/sub8"],
  "ph_category": "best matching Product Hunt category slug (one of: artificial-intelligence, developer-tools, saas, fintech, health, marketing, education, productivity, sports, design, e-commerce, crypto, social-media, analytics, hiring, legal, real-estate, food-and-drink, travel)",
  "serper_queries": [
    "targeted google search 1 — specific pain point with 2026",
    "targeted google search 2 — site:reddit.com with domain-specific terms",
    "targeted google search 3 — site:news.ycombinator.com with technology gap",
    "targeted google search 4 — infrastructure or tooling problem",
    "targeted google search 5 — practitioner frustration or workflow friction"
  ],
  "agent_backstory": "A 3-sentence backstory for a web research agent specialized in this domain. Reference specific communities, publications, and data sources this researcher would know. Make them a credible domain expert, not a generalist."
}}

Requirements:
- subreddits: list 8-10 of the most active, relevant subreddits where practitioners in this domain discuss problems
- serper_queries: each query should target a different angle (pain points, gaps, friction, infrastructure, tooling)
- Include real product names, protocols, and community terminology
- All searches should focus on late 2025 or 2026 content"""

    response = litellm.completion(
        model=HAIKU_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
    )
    text = response.choices[0].message.content.strip()
    # Strip markdown fences if present
    if text.startswith("```"):
        text = text.split("\n", 1)[1].rsplit("```", 1)[0]
    config = json.loads(text)

    print(f"✅ Config generated: {config.get('label', 'Unknown')}")
    print(f"   Subreddits: {', '.join(config.get('subreddits', []))}")
    print(f"   Searches: {len(config.get('serper_queries', []))}")
    return config


def run_discovery_phase(domain: str = "agentic-payments", custom_query: str = None) -> str:

    config = get_domain_config(domain, custom_query)
    query = config["discovery_query"]
    github_query = config.get("github_query", query)
    ph_category = config.get("ph_category", "artificial-intelligence")
    serper_queries = config.get("serper_queries", [])
    subreddits = config.get("subreddits", [])

    print(f"🔎 Domain: {config.get('label', domain)}")

    # Pre-fetch GitHub and Product Hunt signals
    print("🔍 Fetching GitHub issues...")
    github_signals = search_github_issues(github_query)

    print("🚀 Fetching Product Hunt signals...")
    ph_signals = search_product_hunt(ph_category)

    # Build serper search instructions for the agent
    serper_instructions = ""
    if serper_queries:
        serper_instructions = "\n\n## Targeted Google Searches (use your Serper tool for each):\n"
        for i, sq in enumerate(serper_queries, 1):
            serper_instructions += f"{i}. {sq}\n"

    subreddit_instructions = ""
    if subreddits:
        subreddit_instructions = f"\n\n## Subreddits to scan: {', '.join(subreddits)}\n"

    # Combine into enriched context
    enriched_context = f"""
## GitHub Issue Signals (Real developer pain points):
{github_signals}

## Product Hunt Signals (Recent launches and gaps):
{ph_signals}
{serper_instructions}
{subreddit_instructions}
## Query Focus: {query}
"""

    web_agent = create_web_research_agent(
        backstory=config.get("agent_backstory"),
        subreddits=subreddits,
    )
    analyst_agent = create_market_analyst_agent()
    pm_agent = create_principal_pm_agent()

    web_task = Task(
        description=(
            f"Today is April 2026. Research market pain signals for: {query}. "
            f"Only include signals from late 2025 or 2026. "
            f"You have been pre-loaded with the following real signals from GitHub and Product Hunt — "
            f"use these as primary sources, then supplement with your Serper web search tool.\n\n"
            f"{enriched_context}\n\n"
            f"Run EACH of the targeted Google searches listed above using your Serper tool. "
            f"Also search the listed subreddits for recent pain discussions. "
            f"Find at least 5 current pain points. Return structured JSON with source URLs and engagement metrics."
        ),
        expected_output="A JSON list of current opportunity signals (2025-2026 only) with source, description, and engagement metrics.",
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
    result_text = str(result)

    # Generate a business-friendly opportunity name from the technical title
    result_text = _add_friendly_title(result_text)

    return result_text


def _add_friendly_title(brief_text: str) -> str:
    """Use Haiku to generate a business-friendly opportunity name and prepend it to the brief."""
    import re as _re

    # Extract the technical title from LEAD RECOMMENDATION
    lines = brief_text.split('\n')
    tech_title = ''
    tam = ''
    for i, line in enumerate(lines):
        if 'LEAD RECOMMENDATION' in line:
            for j in range(i + 1, min(i + 4, len(lines))):
                if lines[j].strip().startswith('#'):
                    tech_title = lines[j].replace('#', '').strip()
                    break
        tam_match = _re.search(r'TAM:\s*([^|]+)', line)
        if tam_match and not tam:
            tam = tam_match.group(1).strip()

    if not tech_title:
        return brief_text

    print(f"🏷️  Generating friendly title for: {tech_title}")

    response = litellm.completion(
        model=HAIKU_MODEL,
        messages=[{"role": "user", "content": (
            f"Rewrite this technical opportunity title into a short, compelling business headline "
            f"that a non-technical executive or recruiter would immediately understand. "
            f"Max 12 words. Include the market size if available.\n\n"
            f"Technical title: \"{tech_title}\"\n"
            f"Market size: {tam or 'unknown'}\n\n"
            f"Return ONLY the headline, nothing else."
        )}],
        temperature=0.5,
    )
    friendly = response.choices[0].message.content.strip().strip('"')
    print(f"✅ Friendly title: {friendly}")

    # Prepend friendly title metadata to the brief
    metadata = f"<!-- friendly_title: {friendly} -->\n"
    return metadata + brief_text

