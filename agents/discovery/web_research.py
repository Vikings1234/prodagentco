"""Web Research Agent — scans online sources for unmet needs and pain signals."""

import os
import requests
from crewai import Agent
from crewai_tools import SerperDevTool
from config.models import HAIKU_MODEL


def search_github_issues(query: str, domain: str = "") -> str:
    """Search GitHub issues for pain signals and feature requests."""
    token = os.getenv("GITHUB_TOKEN")
    headers = {"Authorization": f"token {token}", "Accept": "application/vnd.github.v3+json"}
    search_query = f"{query} {domain} label:feature-request OR label:enhancement OR label:bug state:open"
    url = f"https://api.github.com/search/issues?q={requests.utils.quote(search_query)}&sort=reactions&order=desc&per_page=10"
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return f"GitHub API error: {response.status_code}"
    data = response.json()
    results = []
    for item in data.get("items", [])[:10]:
        results.append({
            "title": item["title"],
            "url": item["html_url"],
            "reactions": item["reactions"]["total_count"],
            "comments": item["comments"],
            "repo": item["repository_url"].split("/")[-1],
            "body_preview": item["body"][:200] if item["body"] else ""
        })
    return str(results)


def search_product_hunt(query: str) -> str:
    """Search Product Hunt for recent launches and gaps."""
    client_id = os.getenv("PRODUCTHUNT_CLIENT_ID")
    client_secret = os.getenv("PRODUCTHUNT_CLIENT_SECRET")
    # Get access token
    token_response = requests.post("https://api.producthunt.com/v2/oauth/token", json={
        "client_id": client_id,
        "client_secret": client_secret,
        "grant_type": "client_credentials"
    })
    if token_response.status_code != 200:
        return f"Product Hunt auth error: {token_response.status_code}"
    access_token = token_response.json().get("access_token")
    # Search posts
    graphql_query = """
    {
      posts(first: 10, order: VOTES, topic: "%s") {
        edges {
          node {
            name
            tagline
            votesCount
            commentsCount
            url
            topics { edges { node { name } } }
          }
        }
      }
    }
    """ % query
    response = requests.post(
        "https://api.producthunt.com/v2/api/graphql",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"query": graphql_query}
    )
    if response.status_code != 200:
        return f"Product Hunt API error: {response.status_code}"
    return str(response.json())


def create_web_research_agent() -> Agent:
    return Agent(
        role="Web Research Agent",
        goal=(
            "Today is March 2026. Only surface opportunities that are current and relevant "
            "as of 2026. Scan Reddit, HackerNews, Product Hunt, GitHub Issues, and developer "
            "blogs for unmet needs and pain signals. Use the Serper search tool to find "
            "recent discussions. Focus on finding real pain signals with community validation. "
            "Only include opportunities with active discussion from late 2025 or 2026."
        ),
        backstory=(
            "You are an expert market intelligence researcher who specializes in finding "
            "validated pain signals from developer communities and product markets. You use "
            "multiple data sources including GitHub issues, Product Hunt launches, Reddit "
            "discussions, and HackerNews threads to identify real unmet needs. You excel "
            "at distinguishing genuine pain from assumed pain."
        ),
        tools=[SerperDevTool()],
        llm=HAIKU_MODEL,
        verbose=True,
    )
