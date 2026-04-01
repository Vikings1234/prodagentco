# Technical Specification: Agentic Commerce Payment Infrastructure Platform

**Document Version:** 1.0  
**Date:** March 2026  
**Classification:** Internal — Engineering & Investment Committee  
**Author:** CTO  
**Status:** APPROVED FOR ENGINEERING EXECUTION (Phase 1 & 2 Scope)  
**Companion Documents:** PRD v1.0, Executive Brief (March 2026), CEO Debate Verdict

---

## TABLE OF CONTENTS

1. Architecture Overview
2. Technology Stack
3. API Design
4. Data Model
5. Infrastructure Plan
6. Security Architecture
7. Effort Estimates
8. Risk Register

---

## 1. ARCHITECTURE OVERVIEW

### 1.1 System Context

We are building a **translation and authorization layer** — not a payment processor. Our system sits between AI agent operators and existing payment rails (initially Stripe). We add agent identity verification, spending policy enforcement, fraud signal generation, and regulatory audit capability without requiring processors to rewrite their infrastructure.

The following text diagram represents our system architecture at Phase 1-2 scope:

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           EXTERNAL ACTORS                                       │
│                                                                                 │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │  AI Agent    │    │  Operator    │    │  Fraud       │    │  Regulatory  │  │
│  │  (Autonomous │    │  Dashboard   │    │  Platform    │    │  Authority   │  │
│  │   Process)   │    │  (Web App)   │    │  (Sift,      │    │  (EBA, FinCEN│  │
│  │              │    │              │    │   Kount)     │    │  FCA)        │  │
│  └──────┬───────┘    └──────┬───────┘    └──────┬───────┘    └──────┬───────┘  │
│         │                  │                   │                   │           │
└─────────┼──────────────────┼───────────────────┼───────────────────┼───────────┘
          │                  │                   │                   │
          ▼                  ▼                   ▼                   ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                        API GATEWAY LAYER                                        │
│                    (Kong Gateway + AWS API Gateway)                             │
│                                                                                 │
│   TLS 1.3 Termination │ Rate Limiting │ Auth (API Key + mTLS) │ Request Logging│
└───────────────────────────────────┬─────────────────────────────────────────────┘
                                    │
          ┌─────────────────────────┼──────────────────────────┐
          ▼                         ▼                           ▼
┌─────────────────┐      ┌─────────────────────┐    ┌─────────────────────┐
│  AGENT IDENTITY │      │  AUTHORIZATION &     │    │  FRAUD SIGNAL       │
│  SERVICE        │      │  POLICY ENGINE       │    │  SERVICE            │
│                 │      │                      │    │                     │
│  - Registration │      │  - Spending policy   │    │  - Attestation JWT  │
│  - Signing      │      │    evaluation        │    │    generation       │
│  - Verification │      │  - Real-time         │    │  - Signal export    │
│  - Revocation   │      │    enforcement       │    │    API              │
│  - Key rotation │      │  - Approval workflows│    │  - Behavioral       │
│                 │      │  - Limit tracking    │    │    baseline feed    │
└────────┬────────┘      └──────────┬───────────┘    └──────────┬──────────┘
         │                          │                            │
         └──────────────────────────┼────────────────────────────┘
                                    │
                    ┌───────────────┼────────────────┐
                    ▼               ▼                 ▼
          ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐
          │  AML/KYC     │  │  AUDIT LOG   │  │  OPERATOR        │
          │  COMPLIANCE  │  │  SERVICE     │  │  NOTIFICATION    │
          │  SERVICE     │  │              │  │  SERVICE         │
          │              │  │  - Tamper-   │  │                  │
          │  - OFAC/FATF │  │    evident   │  │  - Webhook       │
          │    screening │  │    append-   │  │  - Email         │
          │  - KYC docs  │  │    only log  │  │  - Slack         │
          │  - Tier mgmt │  │  - Export    │  │  - PagerDuty     │
          └──────┬───────┘  └──────┬───────┘  └──────────────────┘
                 │                 │
                 ▼                 ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                          DATA LAYER                                             │
│                                                                                 │
│  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐  ┌──────────────┐  │
│  │  PostgreSQL    │  │  Redis Cluster │  │  TimescaleDB   │  │  S3/GCS      │  │
│  │  (Primary DB)  │  │  (Cache +      │  │  (Time-series  │  │  (Audit      │  │
│  │                │  │   Rate limits) │  │   metrics,     │  │   archives,  │  │
│  │  - Agents      │  │                │  │   spend data)  │  │   exports)   │  │
│  │  - Operators   │  │  - Session     │  │                │  │              │  │
│  │  - Policies    │  │  - Verify cache│  │  - Spend trends│  │  - Regulatory│  │
│  │  - Compliance  │  │  - Rate limits │  │  - Alert data  │  │    export    │  │
│  └────────────────┘  └────────────────┘  └────────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────────────────────────────┘
                                    │
          ┌─────────────────────────┼──────────────────────────┐
          ▼                         ▼                           ▼
┌──────────────────┐    ┌───────────────────────┐    ┌──────────────────────┐
│  STRIPE          │    │  AML SCREENING         │    │  OPERATOR DASHBOARD  │
│  INTEGRATION     │    │  THIRD PARTY           │    │  (React SPA)         │
│                  │    │                        │    │                      │
│  - OAuth2 token  │    │  Refinitiv World-Check │    │  - Policy mgmt       │
│    exchange      │    │  or SWIFT KYC Registry │    │  - Agent monitoring  │
│  - Payment intent│    │                        │    │  - Audit log viewer  │
│    annotation    │    │  (Contract SLA: <60s)  │    │  - Compliance export │
│  - Webhook recv  │    │                        │    │                      │
└──────────────────┘    └───────────────────────┘    └──────────────────────┘
```

### 1.2 Architecture Principles

**1. We Are a Signal Layer, Not a Payment Processor**  
Every architectural decision must reinforce this: we generate identity signals, enforce authorization policies, and annotate transactions. We never hold funds, execute settlements, or sit in the payment flow directly. Stripe receives a transaction; we have already signed the authorization metadata that Stripe validates. This distinction is critical for regulatory scope (we are not a PSP, MSB, or acquiring bank) and for our integration model (Stripe does not need to change their core flow).

**2. Cryptographic Proof, Not Trust-Based Assertions**  
Every agent identity claim is cryptographically signed. Every authorization decision produces a verifiable attestation JWT. Fraud platforms do not need to trust our word — they verify the signature. This eliminates man-in-the-middle risks and provides regulatory defensibility.

**3. Append-Only Audit Logs Are Non-Negotiable**  
Every state mutation (registration, authorization, revocation, policy change) produces an immutable audit log entry. This is a regulatory requirement (PSD3, SOX, GDPR) and a liability protection mechanism. Audit logs are the defense against disputes.

**4. Async-First for Non-Critical Paths**  
Transaction verification (hot path) is synchronous with sub-100ms SLA. Everything else (compliance screening, operator notifications, behavioral analytics) is asynchronous via message queue. This prevents compliance processing delays from blocking transaction flow.

**5. Defense-in-Depth at Every Layer**  
mTLS between services. API gateway enforcement. Secret rotation. Principle of least privilege for all service accounts. No service has read/write access beyond its functional scope. We do not trust internal network by default.

### 1.3 Key System Flows

**Flow A: Agent Registration (One-Time Setup)**

```
Operator             AgentIdentitySvc        AMLComplianceSvc       PostgreSQL
    │                       │                       │                    │
    ├──POST /v1/operators────►                       │                    │
    │  {legal_name,          │                       │                    │
    │   jurisdiction,        ├──Screen beneficial────►                    │
    │   beneficial_owners}   │  owners (OFAC/FATF)   │                    │
    │                        │                       ├──Return tier────── │
    │                        │◄──compliance_tier──────┤                    │
    │                        │  (VERIFIED/PENDING/    │                    │
    │                        │   BLOCKED)             │                    │
    │                        ├──Write operator────────────────────────────►
    │                        │  record + audit event  │                    │
    │◄──operator_id───────────┤                       │                    │
    │                        │                       │                    │
    ├──POST /v1/agents────────►                       │                    │
    │  {operator_id,          │                       │                    │
    │   agent_name,           ├──Validate operator────────────────────────►
    │   agent_type}           │  compliance tier       │                   │
    │                        │◄──operator verified──── │                   │
    │                        ├──Generate agent_id      │                    │
    │                        │  Generate HMAC secret   │                    │
    │                        │  Generate attestation   │                    │
    │                        │  JWT (signed RS256)     │                    │
    │                        ├──Write agent record─────────────────────────►
    │                        │  + audit event          │                    │
    │◄──agent_id, secret key──┤                        │                    │
    │   attestation JWT       │                        │                    │
```

**Flow B: Transaction Authorization (Hot Path — Target P99 < 100ms)**

```
AI Agent          API Gateway      AuthPolicySvc    AgentIdentitySvc   StripeAnnotation
    │                  │                │                  │                  │
    ├─POST /v1/────────►               │                  │                  │
    │  transactions/   │               │                  │                  │
    │  authorize       │               │                  │                  │
    │  {agent_id,      ├─Validate──────►                  │                  │
    │   amount,        │  API key +    │                  │                  │
    │   merchant_cat,  │  rate limits  │                  │                  │
    │   country,       │               ├─Verify agent─────►                  │
    │   hmac_sig}      │               │  signature        │                  │
    │                  │               │  (from Redis      │                  │
    │                  │               │   cache first)    │                  │
    │                  │               │◄─agent_status─────┤                  │
    │                  │               │  identity_score   │                  │
    │                  │               │                   │                  │
    │                  │               ├─Evaluate policies │                  │
    │                  │               │  (amount vs caps, │                  │
    │                  │               │  category rules,  │                  │
    │                  │               │  country blocks)  │                  │
    │                  │               │                   │                  │
    │                  │               ├─Generate signed───────────────────── ►
    │                  │               │  attestation JWT  │                  │
    │                  │               │  (RS256, 5-min    │                  │
    │                  │               │   TTL)            │                  │
    │                  │               │                   │                  │
    │                  │               ├─Write async───────────────────────── │
    │                  │               │  audit log entry  │                  │
    │                  │               │  (Kafka)          │                  │
    │◄─authorization───┤◄──────────────┤                   │                  │
    │  response        │               │                   │                  │
    │  {approved|      │               │                   │                  │
    │   denied|        │               │                   │                  │
    │   pending,       │               │                   │                  │
    │   attestation_jwt│               │                   │                  │
    │   decision_reason│               │                   │                  │
    │   }              │               │                   │                  │
    │                  │               │                   │                  │
    ├─Attach JWT to────────────────────────────────────────────────────────── ►
    │  Stripe PaymentIntent             │                  │                  │
    │  metadata field  │               │                   │                  │
```

**Flow C: Fraud Platform Signal Consumption (Phase 2)**

```
FraudPlatform       FraudSignalSvc     AgentIdentitySvc      AuditLogSvc
    │                    │                    │                    │
    ├─GET /v1/signals────►                    │                    │
    │  /agent/{id}        │                    │                    │
    │                     ├─Fetch current──────►                    │
    │                     │  agent status       │                    │
    │                     │  + recent txn data  │                    │
    │                     │◄─agent data──────── │                    │
    │                     │                     │                    │
    │                     ├─Compute signal──────│                    │
    │                     │  bundle:            │                    │
    │                     │  - identity_score   │                    │
    │                     │  - operator_tier    │                    │
    │                     │  - 30d_txn_velocity │                    │
    │                     │  - policy_viol_count│                    │
    │                     │  - behavior_drift   │                    │
    │◄─agent_signal_bundle┤                     │                    │
    │  (signed JWT)       │                     │                    │
    │                     ├─Log signal export────────────────────── ►
    │                     │  (async)             │                    │
    │                     │                      │                    │
    ├─Validate JWT sig────►                       │                   │
    │  (our public key)   │                       │                   │
    │◄─