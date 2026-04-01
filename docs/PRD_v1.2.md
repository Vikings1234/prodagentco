# ProdAgentCo — Product Requirements Document v1.2

**Version:** 1.2
**Date:** April 1, 2026
**Status:** Active
**Previous Version:** v1.1 (March 2026)

---

## Changelog (v1.1 -> v1.2)

- Added Brand Manager Agent to Planning Layer (Claude Haiku, output: brand-brief.md)
- Added Designer Agent to Planning Layer (Claude Sonnet, output: ux-brief.md)
- Updated Planning Layer agent count from 5 to 7
- Added Gate 2 HITL section (triggers after Planning phase)
- Updated Telegram webhook to support APPROVE2/REVISE2 commands
- Renamed tech-spec.md to architecture-doc.md throughout

---

## 1. System Overview

ProdAgentCo is an autonomous multi-agent product company that discovers, evaluates, plans, and builds software products. It uses a pipeline of specialized AI agents orchestrated by CrewAI with LiteLLM for multi-provider model routing and LangSmith for observability.

### Architecture Diagram

```
                         ProdAgentCo Pipeline
                         ====================

 PHASE 1: DISCOVERY                PHASE 1: DEBATE
 ==================                ================
 Web Research Agent  ──>           PM Agent (Haiku)
 (Groq Llama 3.1)      |          CTO Agent (Sonnet)
                        |          CFO Agent (Haiku)
 Market Analyst      ──>──> CEO    Marketing Agent (Haiku)
 (Groq Llama 3.1)      |  Debate  Legal Agent (Haiku)
                        |    |
 Principal PM        ──>     |     CEO Agent (Sonnet)
 (Claude Haiku)              |       chairs debate
                             v
                     ┌───────────────┐
                     │   GATE 1      │
                     │  HITL (Tg)    │
                     │ APPROVE/KILL/ │
                     │ DEFER/REVISE  │
                     └───────┬───────┘
                             │ APPROVE
                             v
                 PHASE 2: PLANNING (7 Agents)
                 ============================
                 PM Agent ──────────> prd.md
                 (Haiku)

                 CTO Agent ─────────> architecture-doc.md
                 (Sonnet)

                 CFO Agent ─────────> financial-model.md
                 (Haiku)

                 Marketing Agent ───> gtm-plan.md
                 (Haiku)

                 Brand Manager ─────> brand-brief.md
                 (Haiku)

                 Designer Agent ────> ux-brief.md
                 (Sonnet)

                 Legal Agent ───────> legal-brief.md
                 (Haiku)
                             │
                             v
                     ┌───────────────┐
                     │   GATE 2      │
                     │  HITL (Tg)    │
                     │  APPROVE2 /   │
                     │  REVISE2      │
                     └───────┬───────┘
                             │ APPROVE2
                             v
                 PHASE 3: BUILD (Not Yet Implemented)
                 ====================================
                 Engineer Agent (stub)
                 QA Agent (stub)
                 Security Agent (stub)
```

---

## 2. Phase 1 — Discovery

### 2.1 Discovery Agents

| Agent | Role | Model | Output |
|-------|------|-------|--------|
| Web Research Agent | Scans GitHub, Product Hunt, Reddit, HackerNews for pain signals | Groq Llama 3.1 8B | signals.json |
| Market Analyst | ICE-scores and ranks opportunities (Impact x Confidence x Ease) | Groq Llama 3.1 8B | opportunities.json |
| Principal PM | Synthesizes top 2-3 opportunities into executive brief | Claude Haiku 4.5 | discovery-brief.md |

### 2.2 Debate Agents

| Agent | Role | Model |
|-------|------|-------|
| PM Agent | Argues product-market fit case | Claude Haiku 4.5 |
| CTO Agent | Argues technical feasibility | Claude Sonnet 4.6 |
| CFO Agent | Argues financial viability | Claude Haiku 4.5 |
| Marketing Agent | Argues GTM and positioning | Claude Haiku 4.5 |
| Legal Agent | Argues regulatory risk | Claude Haiku 4.5 |
| CEO Agent (Chair) | Synthesizes, applies consensus rule, issues verdict | Claude Sonnet 4.6 |

**Consensus Rule:** PROCEED if average confidence >= 0.70 AND no agent below 0.40. Otherwise: NEEDS_HUMAN_REVIEW.

**Output:** debate-verdict.md

---

## 3. Gate 1 — Human-in-the-Loop

**Trigger:** CEO verdict is not GO, or average confidence < 0.70.

**Channel:** Telegram via dedicated @prodagentco_gate_bot

**Notification includes:**
- Verdict and emoji indicator
- Average confidence score
- Individual agent scores with color coding (green/yellow/red)
- Lead opportunity summary

**Human options:**
| Command | Action |
|---------|--------|
| `APPROVE` | Proceed to Planning phase |
| `KILL` | Archive the opportunity |
| `DEFER` | Add to backlog |
| `REVISE` | Re-run the debate phase |

---

## 4. Phase 2 — Planning Layer (7 Agents)

After Gate 1 APPROVE, the Planning phase produces 7 deliverables from 7 specialized agents.

### 4.1 Planning Agents

| # | Agent | Role | Model | Output |
|---|-------|------|-------|--------|
| 1 | PM Agent | Writes full PRD with user stories and acceptance criteria | Claude Haiku 4.5 | prd.md |
| 2 | CTO Agent | Technical architecture, stack decisions, effort estimates | Claude Sonnet 4.6 | architecture-doc.md |
| 3 | CFO Agent | Unit economics, pricing model, revenue projections | Claude Haiku 4.5 | financial-model.md |
| 4 | Marketing Agent | GTM plan, ICP definition, positioning, launch strategy | Claude Haiku 4.5 | gtm-plan.md |
| 5 | Brand Manager | Brand naming, identity, tone of voice, visual direction | Claude Haiku 4.5 | brand-brief.md |
| 6 | Designer Agent | UX flows, screen-by-screen wireframes, component inventory | Claude Sonnet 4.6 | ux-brief.md |
| 7 | Legal Agent | Compliance requirements, IP risks, licensing | Claude Haiku 4.5 | legal-brief.md |

### 4.2 Task Dependencies

Tasks run sequentially with context passing:
1. **PM** runs first (PRD is the foundation)
2. **CTO** reads PM output (sizes architecture to PRD scope)
3. **CFO** reads PM + CTO output (costs informed by tech spec)
4. **Marketing** reads PM + CFO output (GTM constrained by budget)
5. **Brand Manager** reads PM + Marketing output (brand aligned to positioning)
6. **Designer** reads PM + Brand output (UX informed by PRD stories and brand)
7. **Legal** reads PM + CTO + CFO output (compliance covers full scope)

### 4.3 Output Location

All planning deliverables are saved to `outputs/planning/`:
- prd.md
- architecture-doc.md
- financial-model.md
- gtm-plan.md
- brand-brief.md
- ux-brief.md
- legal-brief.md
- planning-summary.md (index with links)

---

## 5. Gate 2 — Human-in-the-Loop (Planning Review)

**Trigger:** All 7 planning agents complete successfully.

**Channel:** Telegram via @prodagentco_gate_bot

**Notification includes:**
- Product name (from brand-brief.md)
- PRD headline
- Tech stack summary (from architecture-doc.md)
- Revenue projection (from financial-model.md)
- Count of deliverables ready

**Human options:**
| Command | Action |
|---------|--------|
| `APPROVE2` | Proceed to Build phase |
| `REVISE2` | Re-run the Planning phase |

---

## 6. Phase 3 — Build (Not Yet Implemented)

Stub agents exist at `agents/build/`:
- Engineer Agent
- QA Agent
- Security Agent

These will be wired after Gate 2 APPROVE2.

---

## 7. Two-Way Telegram Webhook

### Architecture

A Flask server (`gates/telegram_webhook.py`) listens for incoming Telegram messages via ngrok tunnel.

**Startup:** `./start_all.sh` launches ngrok + Flask on port 5001, auto-registers webhook with Telegram.

### Supported Commands

| Command | Gate | Action |
|---------|------|--------|
| `APPROVE` | Gate 1 | Triggers `run_planning_phase()` |
| `KILL` | Gate 1 | Archives opportunity to `outputs/archived.json` |
| `DEFER` | Gate 1 | Adds to `outputs/backlog.json` |
| `REVISE` | Gate 1 | Re-runs `run_debate_phase()` |
| `APPROVE2` | Gate 2 | Triggers `run_build_phase()` (not yet implemented) |
| `REVISE2` | Gate 2 | Re-runs `run_planning_phase()` |

### Security
- Only accepts messages from configured `PRODAGENTCO_CHAT_ID`
- Dedicated bot token (`PRODAGENTCO_BOT_TOKEN`) separate from other bots
- All decisions logged to `logs/gate1_decisions.json`

---

## 8. Dashboard

**URL:** prodagentco-dashboard.vercel.app

**Tabs:**
- **Overview** — KPIs, CEO verdict, agent scores, lead opportunity
- **Discovery** — Product proposal, signal sources, all opportunities scored
- **Debate** — Expandable agent argument cards, CEO synthesis, winning arguments, key risks
- **Gate 1** — HITL decision buttons, prescribed next actions
- **Planning** — 7 deliverable cards (PRD, Architecture, Brand, UX, Financial, GTM, Legal)
- **History** — Past run history with expandable details
- **Log** — Pipeline execution log

**Data source:** Fetches live from GitHub raw URLs (Vikings1234/prodagentco/main/outputs/).

---

## 9. Tech Stack

| Component | Technology |
|-----------|------------|
| Agent orchestration | CrewAI |
| Model routing | LiteLLM |
| Models | Claude Sonnet 4.6, Claude Haiku 4.5, Groq Llama 3.1 8B |
| Observability | LangSmith |
| HITL notifications | Telegram Bot API |
| Webhook server | Flask + ngrok |
| Dashboard | Next.js + Tailwind CSS (Vercel) |
| Environment | python-dotenv, Pydantic |

---

## 10. Project Structure

```
prodagentco/
├── main.py                  # Entry point — Phase 1 Discovery + Debate + Gate 1
├── config/
│   ├── settings.py          # Thresholds, paths, budget limits
│   └── models.py            # LLM model definitions
├── agents/
│   ├── discovery/           # Web Research, Market Analyst, Principal PM
│   ├── executive/           # CEO, CFO (debate)
│   ├── planning/            # PM, CTO, CFO, Marketing, Brand Manager, Designer, Legal
│   └── build/               # Engineer, QA, Security (stubs)
├── pipelines/
│   ├── phase1.py            # Discovery pipeline
│   ├── debate.py            # CEO debate pipeline
│   └── planning.py          # Planning pipeline (7 agents)
├── gates/
│   ├── hitl_gates.py        # Gate 1 + Gate 2 Telegram notifications
│   └── telegram_webhook.py  # Flask webhook server
├── outputs/
│   ├── signals.json
│   ├── opportunities.json
│   ├── discovery-brief.md
│   ├── debate-verdict.md
│   └── planning/            # 7 planning deliverables
├── logs/                    # Decision logs
├── docs/
│   └── PRD_v1.2.md          # This document
├── start_webhook.py         # Flask server entry point
└── start_all.sh             # Starts ngrok + Flask together
```
