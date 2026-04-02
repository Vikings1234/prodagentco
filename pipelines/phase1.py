"""Phase 1 Discovery Pipeline — Web Research -> Market Analysis -> Principal PM Brief."""

import os
import json
import requests
from crewai import Crew, Task, Process
from agents.discovery.web_research import create_web_research_agent, search_github_issues, search_product_hunt
from agents.discovery.market_analyst import create_market_analyst_agent
from agents.discovery.principal_pm import create_principal_pm_agent
from config.settings import OUTPUT_DIR


# ---------------------------------------------------------------------------
# Domain configs — rich, specific search parameters per vertical
# ---------------------------------------------------------------------------

DOMAIN_CONFIGS = {
    "agentic-payments": {
        "label": "Agentic Commerce Payments",
        "discovery_query": (
            "agentic commerce payment infrastructure gaps 2026: x402 protocol, AP2 agent payments, "
            "Visa TAP-to-Phone agent wallets, MCP payments tool-use billing, autonomous agent billing "
            "infrastructure, agent-to-agent settlement, AI agent checkout friction, machine identity "
            "for payments, PSD3 SCA agent authentication"
        ),
        "github_query": "agent payment x402 OR agent wallet OR MCP payment OR autonomous billing label:feature-request OR label:enhancement state:open",
        "subreddits": ["r/LangChain", "r/MachineLearning", "r/fintech", "r/payments", "r/cryptocurrency"],
        "ph_category": "artificial-intelligence",
        "serper_queries": [
            "x402 agent payment infrastructure problems 2026",
            "autonomous AI agent billing checkout friction site:reddit.com OR site:news.ycombinator.com",
            "MCP payments tool-use commerce gaps 2026",
            "PSD3 SCA machine identity agent transactions",
            "Visa Mastercard agent wallet infrastructure 2025 2026",
        ],
    },
    "sports-analytics": {
        "label": "Sports Analytics",
        "discovery_query": (
            "sports analytics and betting technology gaps 2026: prediction market infrastructure, "
            "fantasy sports pain points, real-time arbitrage detection, sharp money signal tracking, "
            "NFL NBA MLB NHL CFB analytics platform gaps, player prop modeling, in-game betting "
            "latency, odds compilation automation, sports data API limitations"
        ),
        "github_query": "sports analytics OR sports betting OR fantasy sports OR prediction market label:feature-request OR label:enhancement state:open",
        "subreddits": ["r/sportsanalytics", "r/sportsbetting", "r/fantasyfootball", "r/nfl", "r/nba", "r/baseball", "r/CFB"],
        "ph_category": "sports",
        "serper_queries": [
            "sports betting analytics tool pain points 2026 site:reddit.com",
            "fantasy sports platform gaps developer frustration 2025 2026",
            "real-time sports arbitrage detection infrastructure problems",
            "NFL NBA player prop modeling data API limitations 2026",
            "prediction market sports technology gaps site:news.ycombinator.com",
        ],
    },
    "fintech": {
        "label": "Fintech",
        "discovery_query": (
            "fintech infrastructure gaps 2026: embedded payments friction, lending technology automation, "
            "mortgage process automation pain points, revenue cycle management RCM gaps, fraud detection "
            "false positives, open banking API limitations, BNPL infrastructure problems, payment "
            "orchestration complexity, KYC onboarding friction, real-time payments infrastructure"
        ),
        "github_query": "embedded payments OR lending API OR open banking OR BNPL OR fraud detection label:feature-request OR label:enhancement state:open",
        "subreddits": ["r/fintech", "r/personalfinance", "r/smallbusiness", "r/banking", "r/accounting"],
        "ph_category": "fintech",
        "serper_queries": [
            "embedded payments platform pain points 2026 site:reddit.com",
            "open banking API developer frustration 2025 2026",
            "mortgage automation technology gaps lending tech",
            "fraud detection false positive rates fintech infrastructure 2026",
            "BNPL infrastructure problems payment orchestration site:news.ycombinator.com",
        ],
    },
    "healthcare": {
        "label": "Healthcare",
        "discovery_query": (
            "healthcare technology gaps 2026: prior authorization automation pain points, clinical notes "
            "AI documentation burden, dental RCM revenue cycle management gaps, patient engagement "
            "platform friction, care coordination interoperability problems, EHR integration limitations, "
            "telehealth platform gaps, medical billing automation, FHIR API adoption barriers"
        ),
        "github_query": "healthcare OR EHR OR FHIR OR clinical notes OR prior auth OR dental RCM label:feature-request OR label:enhancement state:open",
        "subreddits": ["r/medicine", "r/healthIT", "r/dentistry", "r/telehealth", "r/nursing"],
        "ph_category": "health",
        "serper_queries": [
            "prior authorization automation pain points 2026 healthcare",
            "clinical notes AI documentation burden physician burnout 2025 2026",
            "dental RCM revenue cycle management gaps technology",
            "EHR interoperability FHIR API developer frustration site:reddit.com",
            "patient engagement platform problems telehealth gaps site:news.ycombinator.com",
        ],
    },
}


def _generate_custom_config(custom_query: str) -> dict:
    """Use Claude Haiku to dynamically generate a domain config from a freeform query."""
    import litellm
    from config.models import HAIKU_MODEL

    prompt = f"""You are a market research strategist. Given this product domain or problem description, generate a JSON config for a market research scan.

Domain/problem: "{custom_query}"

Return ONLY valid JSON (no markdown fences) with these exact keys:
{{
  "label": "Short domain label (2-4 words)",
  "discovery_query": "A rich 2-3 sentence research query covering the key pain points, technologies, and gaps in this domain. Be specific with product names, protocols, and technical terms. Include '2026' for recency.",
  "github_query": "A GitHub issues search query with relevant repos/keywords, using OR operators, with label:feature-request OR label:enhancement state:open",
  "subreddits": ["r/relevant1", "r/relevant2", "r/relevant3", "r/relevant4", "r/relevant5"],
  "ph_category": "best matching Product Hunt category slug (e.g. 'artificial-intelligence', 'developer-tools', 'saas', 'fintech', 'health', 'marketing', 'education', 'productivity')",
  "serper_queries": [
    "targeted google search 1 with specific terms and 2026",
    "targeted google search 2 with site:reddit.com",
    "targeted google search 3 with site:news.ycombinator.com",
    "targeted google search 4 with specific pain point",
    "targeted google search 5 with technology gap"
  ]
}}

Be specific and technical. Include real product names, protocols, and community terms that practitioners in this domain would use. The searches should find real pain points from late 2025 or 2026."""

    response = litellm.completion(
        model=HAIKU_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
    )
    text = response.choices[0].message.content.strip()
    # Strip markdown fences if present
    if text.startswith("```"):
        text = text.split("\n", 1)[1].rsplit("```", 1)[0]
    return json.loads(text)


def get_domain_config(domain: str, custom_query: str = None) -> dict:
    """Return a rich domain config for the given domain key or custom query."""
    if domain == "custom" and custom_query:
        print(f"🤖 Generating custom domain config for: {custom_query}")
        config = _generate_custom_config(custom_query)
        print(f"✅ Generated config for: {config.get('label', 'Custom')}")
        return config
    return DOMAIN_CONFIGS.get(domain, DOMAIN_CONFIGS["agentic-payments"])


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

    web_agent = create_web_research_agent()
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
    return str(result)

