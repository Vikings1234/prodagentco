# ProdAgentCo

ProdAgentCo is an autonomous multi-agent product company that discovers, evaluates, plans, and builds software products. It uses a pipeline of specialized AI agents orchestrated by CrewAI with LiteLLM for multi-provider model routing and LangSmith for observability.

## Pipeline

```
Discovery (3 agents) -> Debate (6 agents) -> Gate 1 HITL -> Planning (7 agents) -> Gate 2 HITL -> Build (TBD)
```

## Phase 1 — Discovery & Debate

| Agent | Role | Model |
|-------|------|-------|
| Web Research Agent | Scans GitHub, Product Hunt, Reddit for pain signals | Groq Llama 3.1 8B |
| Market Analyst | ICE-scores and ranks opportunities | Groq Llama 3.1 8B |
| Principal PM | Synthesizes executive brief | Claude Haiku 4.5 |
| PM / CTO / CFO / Marketing / Legal | Debate the opportunity | Haiku + Sonnet |
| CEO (Chair) | Issues GO / NO-GO / NEEDS_HUMAN_REVIEW | Claude Sonnet 4.6 |

## Phase 2 — Planning (7 Agents)

| Agent | Output | Model |
|-------|--------|-------|
| PM Agent | prd.md | Claude Haiku 4.5 |
| CTO Agent | architecture-doc.md | Claude Sonnet 4.6 |
| CFO Agent | financial-model.md | Claude Haiku 4.5 |
| Marketing Agent | gtm-plan.md | Claude Haiku 4.5 |
| Brand Manager | brand-brief.md | Claude Haiku 4.5 |
| Designer Agent | ux-brief.md | Claude Sonnet 4.6 |
| Legal Agent | legal-brief.md | Claude Haiku 4.5 |

## HITL Gates (Telegram)

- **Gate 1** (after Debate): APPROVE / KILL / DEFER / REVISE
- **Gate 2** (after Planning): APPROVE2 / REVISE2

Notifications sent via dedicated @prodagentco_gate_bot. Two-way webhook powered by Flask + ngrok.

## Setup

```bash
cd ~/projects/prodagentco
source venv/bin/activate
pip install -r requirements.txt
```

Required `.env` keys: `ANTHROPIC_API_KEY`, `GROQ_API_KEY`, `LANGCHAIN_API_KEY`, `PRODAGENTCO_BOT_TOKEN`, `PRODAGENTCO_CHAT_ID`

## Run

```bash
# Full pipeline (Discovery + Debate + Gate 1)
python main.py

# Start webhook server (for Telegram replies)
./start_all.sh

# Run planning phase directly
python -c "from pipelines.planning import run_planning_phase; run_planning_phase()"
```

## Output Artifacts

```
outputs/
├── signals.json          # Raw signals from web research
├── opportunities.json    # ICE-scored opportunities
├── discovery-brief.md    # Executive brief
├── debate-verdict.md     # CEO verdict with agent scores
└── planning/             # 7 planning deliverables
    ├── prd.md
    ├── architecture-doc.md
    ├── financial-model.md
    ├── gtm-plan.md
    ├── brand-brief.md
    ├── ux-brief.md
    └── legal-brief.md
```

## Dashboard

Live at **prodagentco-dashboard.vercel.app** — fetches data from GitHub.

## Docs

- [PRD v1.2](docs/PRD_v1.2.md) — Full product requirements document
