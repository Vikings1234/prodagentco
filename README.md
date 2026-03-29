# ProdAgentCo

ProdAgentCo is an autonomous multi-agent product company that discovers, evaluates, and builds software products. It uses a pipeline of specialized AI agents — each with a distinct role (researcher, analyst, PM, engineer, etc.) — orchestrated by CrewAI with LiteLLM for multi-provider model routing and LangSmith for observability.

## Phase 1 — Discovery Agents

| Agent | Role | Model |
|-------|------|-------|
| Web Research Agent | Scans online communities for pain signals | Groq Llama 3.1 8B |
| Market Analyst | ICE-scores and ranks opportunities | Groq Llama 3.1 8B |
| Principal PM | Synthesizes a ranked executive brief | Claude Haiku 3.5 |

## Setup

1. **Clone and enter the project:**
   ```bash
   cd ~/projects/prodagentco
   ```

2. **Create and activate the virtual environment:**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Configure environment variables:**
   ```bash
   cp .env .env.local  # edit .env with your actual API keys
   ```
   Required keys: `ANTHROPIC_API_KEY`, `GROQ_API_KEY`, `LANGCHAIN_API_KEY`

4. **Run the discovery pipeline:**
   ```bash
   python main.py
   ```

## Output Artifacts

After a run, check the `outputs/` directory:

- `signals.json` — Raw opportunity signals from Web Research Agent
- `opportunities.json` — ICE-scored and ranked opportunities from Market Analyst
- `discovery-brief.md` — Executive brief with top 2-3 recommendations from Principal PM

## Tech Stack

- **[CrewAI](https://github.com/joaomdmoura/crewAI)** — Multi-agent orchestration framework
- **[LiteLLM](https://github.com/BerriAI/litellm)** — Unified LLM API (Groq, Anthropic, OpenAI)
- **[LangSmith](https://smith.langchain.com/)** — Tracing and observability
- **python-dotenv** — Environment variable management
- **Pydantic** — Data validation

## Project Structure

```
prodagentco/
├── main.py              # Entry point
├── config/              # Model configs and settings
├── agents/
│   ├── discovery/       # Phase 1: Web Research, Market Analyst, Principal PM
│   ├── executive/       # Phase 2: CEO, CFO (stubs)
│   ├── planning/        # Phase 2: PM, CTO, Marketing, Legal (stubs)
│   └── build/           # Phase 2: Engineer, QA, Security (stubs)
├── tasks/               # Task definitions
├── pipelines/           # Pipeline orchestration
├── outputs/             # Generated artifacts
└── logs/                # Runtime logs
```
