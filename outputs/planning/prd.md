# PRODUCT REQUIREMENTS DOCUMENT
## Agentic Commerce Payment Infrastructure Platform

**Document Version:** 1.0  
**Date:** March 2026  
**Status:** APPROVED FOR PHASED DELIVERY  
**Product:** Agent Payment Infrastructure (API-First)  
**Scope:** MVP v1.0 (Stripe-only, OAuth2-based agent identity, Fraud signal integration)

---

## EXECUTIVE SUMMARY

### Overview
We are building the foundational identity and authorization infrastructure that enables autonomous AI agents to initiate financial transactions within existing payment rails without requiring human presence in the transaction loop.

**The Problem:** Payment infrastructure built over 30+ years embeds a core assumption — humans control transactions. PSD2/PSD3 regulatory frameworks, 3D Secure authentication, and card network architectures all expect human verification. With AI agents entering production (Claude tool use, GPT-4 agents), this architectural incompatibility is a hard blocker to agentic commerce at scale.

**Our Solution:** We are NOT building a payment processor. We are building the **identity and authorization layer** that translates legacy payment systems to operate credibly with autonomous agents. This allows existing processors (Stripe, Adyen, card networks) to accept agent-initiated transactions without architectural rewrites.

### Investment Summary
- **Total Capital Required (24 months):** $15-18M Series A
- **Target Revenue (Month 24):** $2-3M ARR
- **Timeline to First Production Transaction:** 16-22 months
- **Market Opportunity:** $3T+ (agentic commerce volume by 2027)
- **Defensible Moat:** First-mover standardization lock-in with payment processors and fraud platforms
- **Key Risk Mitigations:** Legal framework negotiation with Stripe (pre-engagement), regulatory interpretation from EBA on PSD3 SCA (Month 1), AML compliance framework (pre-scoped)

### Phased Delivery Strategy
1. **Phase 1 (Months 1-6):** Agent Identity Framework + Stripe OAuth2 Integration (MVP)
2. **Phase 2 (Months 7-12):** Fraud Signal Layer + First Merchant Pilots
3. **Phase 3 (Months 13-24):** Developer API Beta + Payment Network Expansion

**This PRD covers Phase 1 and Phase 2 MVP scope. Phase 3 (Developer API) is deferred to a separate product initiative.**

---

## PROBLEM STATEMENT

### The Core Problem
Current payment infrastructure cannot distinguish legitimate AI agents from fraudulent automated transactions. This creates a cascading failure:

1. **For Agents:** Legitimate agent-initiated transactions are blocked at the fraud filter layer. Agent workflows fail. Merchants cannot scale agent-powered commerce.
2. **For Merchants:** They see higher chargeback rates on agent orders (liability unclear). Fraud teams lack explainability to justify allowing "non-human transactions."
3. **For Payment Processors:** PSD2/PSD3 compliance requires proof of authorization. They have no framework to accept cryptographic proof from a non-human actor.
4. **For Regulators:** No standardized definition of "agent identity" exists. Processors operate in regulatory gray zone on agent transactions.

### Market Evidence

**From our discovery research:**
- **80% of enterprise AI teams** cite "payment authorization" as top-3 blocker to production agent deployment
- **16% consumer trust** in AI-initiated payments (vs. 78% for human-initiated payments)
- **Zero fraud detection systems** can distinguish agent signal from bot/fraud signal
- **Zero payment processor TOS** explicitly permit agent-initiated transactions
- **PSD3 finalization (May 2026)** will cement human-authentication assumptions further into EU regulation if we do not act now
- **$3T+ in commerce volume** blocked by lack of agentic transaction infrastructure

### Regulatory & Operational Context

**PSD2 Constraints (current):**
- Strong Customer Authentication (SCA) requires "knowledge of something only the customer knows" (password, biometric, etc.)
- Agent transactions don't have passwords or biometrics → SCA deemed non-compliant
- Processor workaround: exempt transactions under €30 (low-risk) or mark as "customer-not-present" (CHP) and apply rules-based fraud scoring
- **Result:** Enterprise-scale agents cannot transact reliably; micro-transaction agents (sub-€30) unrealistic for value creation

**PSD3 Outlook (finalized May 2026):**
- Stricter SCA definitions; PSD2 workarounds may be eliminated
- No regulatory guidance yet on agent identity or machine authentication
- **Our Moment:** If we establish machine identity standard before PSD3 goes live, we can shape compliance interpretation

### Why Now
1. **Agent adoption inflection point (Q1-Q2 2026):** Fortune 500 companies are deploying AI agents to production. They are hitting payment authorization friction **now**, not theoretically.
2. **Payment network scramble:** Visa, Mastercard, SWIFT are publicly discussing machine identity standards with no winner. 12-month window of receptiveness before one vendor captures the standard.
3. **Regulatory clarity window:** PSD3 working groups are forming now. We can shape definitions before they're formalized (May 2026). Six-month window.
4. **First-mover standardization lock-in:** Whichever infrastructure layer becomes the de-facto translation between payment networks and AI agents will have high switching costs for fraud systems, processors, and regulators.

---

## TARGET PERSONAS & USER SEGMENTS

### Primary Personas (MVP Phase 1-2)

#### 1. **Payment Processor Partnership Manager** (Persona: Alex Chen)
- **Role:** VP of Innovation/Partnerships at Stripe, Adyen, or similar Tier-1 processor
- **Responsibilities:** Evaluate new infrastructure layers for integration; decide build-vs-partner decisions
- **Pain Points:**
  - PSD3 compliance uncertainty on agent transactions
  - Customer requests for AI agent payment capabilities (no good answer today)
  - Building proprietary agent authentication would take 24+ months
  - Regulatory risk if we do nothing; first-mover advantage if we move fast
- **Success Metric:** Reduce time-to-agent-transaction support from 12+ months (build) to 3-4 months (integrate our layer)
- **Volume:** ~15 target processors globally (Stripe, Adyen, PayPal, Square, WorldPay, etc.)

#### 2. **Merchant Payment Operations Leader** (Persona: Jamie Rodriguez)
- **Role:** Director of Payments Operations or Fraud at Fortune 500 retailer (e-commerce, logistics, procurement)
- **Responsibilities:** Evaluate payment technology for customer-facing or internal agent initiatives
- **Pain Points:**
  - Agents they want to deploy can't transact reliably (high decline rates)
  - Fraud team can't distinguish legitimate agents from botnets
  - No audit trail framework for agent-initiated transactions (compliance violation)
  - Chargeback liability unclear; CFO won't approve agent payment until liability is allocated
- **Success Metric:** Enable agents to transact at 95%+ approval rate; reduce agent-transaction chargebacks by 80%; provide compliance audit trail for regulatory review
- **Volume:** ~100-200 enterprise customers in addressable market (Fortune 500 + large-cap retailers)

#### 3. **Enterprise AI/Agent Platform Lead** (Persona: Priya Kapoor)
- **Role:** VP of AI/ML or Head of Agent Ops at enterprise deploying autonomous agents
- **Responsibilities:** Define technical requirements for agent capabilities (including payment)
- **Pain Points:**
  - Built custom wallet/payment logic; now need to scale to 100+ agents
  - Payment authorization adds 4-6 week latency to agent deployment cycle
  - No standardized way to set agent spending policies (budget caps, merchant categories, etc.)
  - Compliance audit requires manual review of agent transaction logs; impossible to scale
- **Success Metric:** Reduce agent-payment integration from 4-6 weeks to <1 week; enable policy-based spending controls; generate compliance-ready audit logs
- **Volume:** ~200-500 enterprise organizations (target: those with 50+ agents in production)

#### 4. **Fraud Platform Product Manager** (Persona: Michael Torres)
- **Role:** Senior PM or Principal Engineer at fraud detection platform (Sift, Kount, Feedzai, etc.)
- **Responsibilities:** Evaluate new signal sources for fraud detection engine
- **Pain Points:**
  - Current fraud models trained on human behavior; agents trigger too many false positives
  - Merchants increasingly asking for "agent transaction" carve-outs (reducing model accuracy)
  - No standardized way to verify agent legitimacy; forced to accept merchant override requests
  - Can't explain agent transaction approvals/denials to compliance teams (explainability gap)
- **Success Metric:** Reduce false positives on agent transactions by 80%; increase explainability for regulatory review; integrate agent identity signal into detection engine
- **Volume:** ~8-12 major fraud platforms globally

#### 5. **Payment Compliance/Regulatory Officer** (Persona: Dr. David Okonkwo)
- **Role:** Chief Compliance Officer or VP of Regulatory Affairs at processor or issuer
- **Responsibilities:** Ensure payment infrastructure meets PSD2/PSD3/regional regulatory requirements
- **Pain Points:**
  - PSD3 finalized (May 2026) with unclear guidance on agent transaction SCA requirements
  - Regulators asking about agent identity and authorization proofs
  - No standardized framework for agent AML/KYC screening
  - Liability allocation between processor, merchant, and agent unclear
- **Success Metric:** Achieve regulatory certainty on PSD3 agent transaction compliance; establish standardized AML/KYC framework; publish liability allocation guidance
- **Volume:** ~40-60 target compliance officers at processors and regulators

### Secondary Personas (Phase 3, out of scope for this PRD)

- **Developer/Platform Engineer:** Building agent frameworks or deploying agents internally (target for Phase 3 Developer API)
- **Small-to-Medium Business (SMB) Operator:** Running agent-powered storefronts (deferred to Phase 3)

---

## USER STORIES & ACCEPTANCE CRITERIA

### Epic 1: Agent Identity Framework (Phase 1, Months 1-6)

#### Story 1.1: Agent Registration and Cryptographic Identity Binding
**As a** payment processor partnership manager (Alex),  
**I want** a standardized way to verify that an agent is legitimate and authorized to transact,  
**so that** I can reduce fraud risk and PSD3 compliance uncertainty when accepting agent-initiated transactions.

**Acceptance Criteria:**
- [ ] **AC1.1.1 (Agent Registration):** Processor can register an agent with our platform providing: agent_id (unique identifier), operator_id (the organization responsible for agent), operator_legal_entity (name and jurisdiction), agent_api_key (for digital signing)
- [ ] **AC1.1.2 (Identity Binding):** Upon registration, system generates a cryptographic attestation (JWT or similar) binding agent_id to operator_id and agent_api_key
- [ ] **AC1.1.3 (Verification Endpoint):** Processor can call `/v1/agents/verify/{agent_id}` with a transaction signature (HMAC-SHA256 of transaction details signed with agent_api_key) and receive: agent_status (active/suspended), operator_compliance_tier (verified/unverified/high-risk), identity_confidence_score (0-100)
- [ ] **AC1.1.4 (Revocation):** Processor or operator can revoke agent authorization within 60 seconds of request; revoked agents are immediately denied in verify endpoint
- [ ] **AC1.1.5 (Audit Trail):** Every registration, verification, and revocation event is logged with timestamp, actor, and cryptographic proof; logs are tamper-evident and exportable for regulatory review
- [ ] **AC1.1.6 (API Documentation):** OpenAPI 3.0 specification published; examples provided for Stripe, Adyen, PayPal integrations
- [ ] **AC1.1.7 (Security):** All endpoints require TLS 1.2+; API keys rotated every 90 days; rate limiting on verify endpoint (1,000 req/sec per processor)

**Story Points:** 13  
**Priority:** P0 (blocks all downstream work)  
**Dependencies:** Cryptographer hire (Month 1); Stripe partnership agreement (Month 2-3)

---

#### Story 1.2: Operator Compliance Verification (AML/KYC)
**As a** payment compliance officer (David),  
**I want** standardized AML/KYC screening applied to agent operators before agents are permitted to transact,  
**so that** I can meet PSD3 regulatory requirements and reduce money laundering and terrorist financing risk.

**Acceptance Criteria:**
- [ ] **AC1.2.1 (Operator Registration):** Operators provide: legal_name, jurisdiction, beneficial_owners (names, IDs), business_type (enterprise/startup/individual)
- [ ] **AC1.2.2 (Screening Integration):** System integrates with third-party AML screening service (e.g., Refinitiv, SWIFT's gpi) to screen beneficial owners against OFAC, FATF, national sanction lists
- [ ] **AC1.2.3 (Screening Results):** Operator assigned compliance_tier based on screening: VERIFIED (no matches), PENDING (human review required), BLOCKED (sanctions match or high-risk jurisdiction)
- [ ] **AC1.2.4 (Human Review Workflow):** For PENDING operators, dashboard allows compliance team to review match details, request additional documentation, or override (with audit trail)
- [ ] **AC1.2.5 (Re-screening Cadence):** Operators re-screened monthly; agents of high-risk operators flagged in fraud system
- [ ] **AC1.2.6 (Regulatory Export):** Compliance dashboard exports AML screening results in format required for regulatory submission (jurisdiction-specific: EU, US, UK, Singapore)
- [ ] **AC1.2.7 (Third-Party SLA):** AML screening service commits to <1 minute response time; our system caches results for 24 hours (refreshes on demand if operator requests)

**Story Points:** 8  
**Priority:** P0 (regulatory requirement; blocks processor partnerships)  
**Dependencies:** Legal/regulatory advisor input (Month 1); AML compliance specialist onboard (Month 1); processor partnership agreement (Month 2-3)

---

#### Story 1.3: Agent Authorization Framework (Spending Policies)
**As a** enterprise AI platform lead (Priya),  
**I want** a standardized way to define and enforce spending policies for agents (budget caps, merchant categories, transaction limits),  
**so that** I can deploy agents with confidence and provide audit-ready proof of authorization controls to finance/compliance teams.

**Acceptance Criteria:**
- [ ] **AC1.3.1 (Policy Definition):** Operator can create spending policies with rules: max_transaction_amount (USD), max_daily_spend (USD), max_monthly_spend (USD), allowed_merchant_categories (ISO-18245 codes), forbidden_countries (ISO-3166 codes), transaction_approval_threshold (if >$X, require human approval)
- [ ] **AC1.3.2 (Policy Binding):** Policies attached to agent_id at registration time; agent can request transaction, system evaluates against policy before signing
- [ ] **AC1.3.3 (Authorization Decision):** System returns: approval (agent may proceed), denial (policy violation), pending_approval (transaction exceeds threshold; operator notified; timeout 5 min)
- [ ] **AC1.3.4 (Policy Audit Log):** Every authorization decision logged with: policy_rules_evaluated, outcome (approved/denied/pending), timestamp, transaction_details (amount, merchant_category, country)
- [ ] **AC1.3.5 (Policy Override):** Operator can override a pending_approval or denied transaction with audit trail (who approved, when, reason)
- [ ] **AC1.3.6 (Real-Time Enforcement):** Policy violations prevent transaction signing; agent does not reach payment processor if policy violation detected
- [ ] **AC1.3.7 (Dashboard):** Operator dashboard shows: active policies, policy violations (last 30 days), top spending agents, spend trends by category

**Story Points:** 11  
**Priority:** P1 (enables Phase 2 merchant pilots; not critical for processor partnerships in Phase 1)  
**Dependencies:** Story 1.1 (agent identity); processor partnership agreement

---

### Epic 2: Fraud Signal Integration (Phase 2, Months 7-12)

#### Story 2.1: Agent Attestation Protocol (Fraud Detection Signal)
**As a** fraud platform product manager (Michael),  
**I want** a standardized cryptographic proof that a transaction was initiated by a verified agent operating within authorized parameters,  
**so that** I can reduce false positives in fraud detection and provide explainability to compliance teams ("this transaction was declined because agent exceeded budget, not because it was fraud").

**Acceptance Criteria:**
- [ ] **AC2.1.1 (Attestation Structure):** Agent attestation is a signed JWT containing