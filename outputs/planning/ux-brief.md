# UX BRIEF: AUTHENT — AGENTIC COMMERCE PAYMENT INFRASTRUCTURE PLATFORM

**Document Version:** 1.0
**Date:** March 2026
**Status:** APPROVED FOR DESIGN IMPLEMENTATION
**Prepared by:** Lead Product Designer
**Coverage:** PRD Epics 1–2 (Phase 1: Agent Identity Framework + Phase 2: Fraud Signal Integration)

---

## TABLE OF CONTENTS

1. [User Flows](#user-flows)
2. [Screen Wireframes](#screen-wireframes)
3. [UI Component Inventory](#ui-component-inventory)
4. [Interaction Patterns & Micro-Interactions](#interaction-patterns)
5. [Accessibility Requirements](#accessibility-requirements)
6. [Responsive Design Considerations](#responsive-design)

---

## SECTION 1: USER FLOWS

### Design Philosophy
Every flow maps to a PRD user story. Every screen reduces cognitive load by surfacing only the information relevant to the task at hand. Progressive disclosure protects non-technical personas (CFOs, Compliance Officers) from system complexity while providing depth for technical users (AI Platform Leads, Fraud PMs).

---

### Flow 1: Payment Processor Partnership Manager (Alex Chen)
**Maps to:** Story 1.1 (Agent Registration & Identity), Story 1.2 (AML/KYC)
**Entry point:** Partnership sales handoff → Partner activation email

```
[1.1] ENTRY: Partnership Activation Email
       → CTA: "Set Up Your Integration"
       → Opens: Authent Partner Portal (authenticated via SSO/SAML)
       ↓
[1.2] ONBOARDING: Partnership Configuration Wizard (4 steps)
       Step 1: Organization Profile
              → Legal name, jurisdiction, processor type, primary contact
              → Validates: legal entity format by jurisdiction
       Step 2: Technical Integration Setup
              → Select integration pattern: REST webhook | SDK | Direct API
              → Generate Partner API credentials (live + sandbox)
              → Download OpenAPI 3.0 specification
       Step 3: Compliance Configuration
              → Review SLA terms (99.95% uptime, <1s verify endpoint)
              → Accept data processing agreement (GDPR/CCPA)
              → Select AML screening tier (Standard | Enhanced)
       Step 4: Test Connection
              → Auto-trigger test agent registration
              → Auto-trigger test verify request
              → Display: success state with latency metrics
              → Or: error state with specific failure + fix guidance
       ↓
[1.3] DASHBOARD: Partner Operations Dashboard (Home)
       → Summary tiles: Active Agents | Verification Volume | Decline Rate | 
         Compliance Alerts
       → Quick action: Register New Agent | View Audit Logs | Manage Policies
       ↓
[1.4] TASK: Register Agent
       → Fill agent registration form (agent_id, operator_id, operator_legal_entity,
         agent_api_key)
       → System generates cryptographic attestation (JWT)
       → Download/copy attestation
       → View agent in agent directory
       ↓
[1.5] TASK: Verify Agent Transaction (API + Dashboard view)
       → (Primary path: API call to /v1/agents/verify/{agent_id})
       → Dashboard companion: View verification history, confidence scores,
         status changes
       ↓
[1.6] TASK: Revoke Agent
       → Locate agent in directory
       → Initiate revocation
       → Confirm with reason code
       → System propagates within 60 seconds (progress indicator)
       → Audit log entry created
       ↓
[1.7] EXIT: Ongoing Operations
       → Monitor via dashboard
       → API integration fully active
       → Alert notifications for compliance events
```

---

### Flow 2: Enterprise AI Platform Lead (Priya Kapoor)
**Maps to:** Story 1.3 (Agent Authorization Framework / Spending Policies)
**Entry point:** Authent platform invitation from partner processor OR direct sign-up

```
[2.1] ENTRY: Operator Account Creation
       → Email/SSO sign-up
       → Organization type selection: Enterprise | Startup | Individual
       → Jurisdiction selection (drives AML/KYC requirements shown)
       ↓
[2.2] ONBOARDING: Operator Compliance Verification (AML/KYC)
       → Provide: legal_name, jurisdiction, beneficial_owners, business_type
       → Upload: incorporation documents, beneficial owner IDs
       → Status: PENDING (queued for screening)
       → Email notification when compliance_tier assigned
              → VERIFIED: proceed to agent setup
              → PENDING_REVIEW: in-product prompt with estimated timeline
              → BLOCKED: in-product guidance + support contact
       ↓
[2.3] TASK: Create Spending Policy
       → Policy builder interface:
              → Policy name (internal label)
              → max_transaction_amount (currency + amount input)
              → max_daily_spend (currency + amount input)
              → max_monthly_spend (currency + amount input)
              → allowed_merchant_categories (ISO-18245 multi-select + search)
              → forbidden_countries (ISO-3166 multi-select + search)
              → transaction_approval_threshold (toggle on/off + amount)
       → Preview: policy summary card (human-readable)
       → Save policy → policy_id generated
       ↓
[2.4] TASK: Register Agent + Bind Policy
       → Enter agent_id (or generate)
       → Select spending policy (from list or create new inline)
       → Generate agent_api_key (or provide existing key)
       → Submit → System creates agent with attestation + policy binding
       → Confirmation: agent card with attestation download
       ↓
[2.5] ONGOING: Agent Operations Dashboard
       → List of agents: name, status, policy name, last transaction, 
         today's spend vs. limit
       → Click agent → Agent Detail View
              → Transaction history (last 30 days)
              → Policy violation log
              → Authorization decisions (approved/denied/pending)
              → Manual override interface (for pending_approval events)
       ↓
[2.6] TASK: Handle Pending Approval (Human-in-the-loop)
       → Alert (email + in-app notification): "Agent [name] requests approval 
         for $[X] transaction at [merchant]"
       → Open: Transaction Detail Modal
              → Amount, merchant category, country, timestamp
              → Which policy rule triggered the hold
              → Agent's spend-to-date vs. limits
       → Action: APPROVE (with optional note) | DENY (with required reason)
       → Audit log entry created with actor, decision, timestamp
       ↓
[2.7] EXIT: Compliance Export
       → Download audit log (CSV/JSON, jurisdiction-specific format)
       → Date range selector + agent filter
```

---

### Flow 3: Fraud Platform Product Manager (Michael Torres)
**Maps to:** Story 2.1 (Agent Attestation Protocol / Fraud Detection Signal)
**Entry point:** Fraud platform partnership agreement → Technical integration access

```
[3.1] ENTRY: Fraud Platform Integration Setup
       → Partner credentials issued via partner dashboard
       → Integration guide specific to platform (Sift/Kount/Feedzai template)
       ↓
[3.2] INTEGRATION: Signal Feed Configuration
       → Select signal delivery method: Webhook | Batch API | Real-time stream
       → Configure: fraud_platform_endpoint, auth_token, 
         signal_fields (select which attestation fields to receive)
       → Test signal: trigger synthetic agent transaction → 
         verify signal received at endpoint
       ↓
[3.3] DASHBOARD: Fraud Signal Operations
       → Signal volume chart: agent transactions/hour, attestation success rate
       → False positive reduction metric vs. baseline
       → Alert feed: anomalies detected in agent behavior
       ↓
[3.4] TASK: Investigate Agent Anomaly
       → Click alert in feed → Agent Anomaly Detail view
              → Attestation details (agent_id, operator, auth_scope, 
                policy_hash, confidence_score)
              → Behavioral deviation: what triggered the anomaly
                (e.g., spend velocity spike, new merchant category)
              → Transaction timeline
       → Action: Flag for review | Clear alert | Escalate to operator
       ↓
[3.5] TASK: Review Attestation Explainability
       → For any transaction: "Why was this approved/denied?"
       → Explainability panel:
              → Policy rules evaluated (pass/fail for each rule)
              → Confidence score breakdown
              → Agent compliance history
       → Export: machine-readable explainability report for regulatory review
       ↓
[3.6] EXIT: Ongoing Integration
       → Signal feed active
       → Monitor false positive rate in fraud platform
       → Monthly signal quality report (auto-generated by Authent)
```

---

### Flow 4: Compliance Officer (Dr. David Okonkwo)
**Maps to:** Story 1.2 (AML/KYC), Story 1.1 AC1.1.5 (Audit Trail)
**Entry point:** Admin invite from payment processor partner

```
[4.1] ENTRY: Compliance Admin Access
       → Invited as compliance_admin role (limited to compliance views)
       → No access to API credential management
       ↓
[4.2] COMPLIANCE DASHBOARD: Overview
       → Operator compliance summary:
              → VERIFIED count | PENDING count | BLOCKED count
       → Re-screening schedule (next run date per operator)
       → Active sanctions alerts (new matches since last login)
       → Export queue: pending regulatory submissions
       ↓
[4.3] TASK: Review Pending Operator
       → Pending operator list → click operator row
       → Operator Detail View:
              → Legal name, jurisdiction, beneficial owners
              → Screening match details (which list, match score, entity name)
              → Supporting documents uploaded
       → Action buttons: VERIFY (approve) | REQUEST DOCS | BLOCK
       → Each action requires: reason code + free-text note
       → Audit trail: all actions logged immutably
       ↓
[4.4] TASK: Export Regulatory Report
       → Select: report type (EU/PSD3 | US/FinCEN | UK/FCA | Singapore/MAS)
       → Select: date range + operator filter + agent filter
       → Format: CSV | JSON | PDF
       → Generate → Download or email delivery
       ↓
[4.5] ONGOING: Monitoring
       → Alert settings: sanctions list update → immediate email notification
       → Monthly re-screening results notification
       → Audit log immutable export at any time
```

---

### Flow 5: First-Time Developer (Secondary — Phase 2 Merchant Pilot Support)
**Maps to:** Story 1.1 AC1.1.6 (API Documentation), Story 1.3 AC1.3.7 (Dashboard)
**Entry point:** Developer documentation site

```
[5.1] ENTRY: Documentation Landing
       → Quick-start guide visible above fold
       → Interactive API explorer (Swagger/Redoc embedded)
       ↓
[5.2] SANDBOX: Test Environment Access
       → Create sandbox account (no AML/KYC required in sandbox)
       → Auto-provisioned: test agent, test operator, 
         test spending policy (pre-configured)
       → Test credentials issued immediately
       ↓
[5.3] FIRST CALL: Try Agent Registration (in-doc)
       → Pre-filled code sample (Python/Go/Node tabs)
       → Run in browser → response shown inline
       → Annotated response: each field explained
       ↓
[5.4] PROGRESSION: Try Verify + Policy Enforcement
       → Step-by-step guide builds on sandbox setup
       → Simulated fraud block → resolved with attestation
       ↓
[5.5] UPGRADE: Production Access
       → Prompt to create production account → links to Flow 2 (Operator Onboarding)
```

---

## SECTION 2: SCREEN WIREFRAMES

### Design System Notes
- **Visual language:** Clean, dense-but-not-cluttered data tables; clear hierarchy with typographic contrast; trust signals (security badges, compliance tiers) consistently placed. Reference: Stripe Dashboard (density + clarity), Linear (sidebar navigation + task focus), Figma (panel-based workspace for complex configuration).
- **Color system:** Dark navy primary (#0A1628), Electric blue accent (#1A6FFF), Semantic colors: Success green (#00C896), Warning amber (#F5A623), Error red (#E8394D), Neutral grays (50-900 scale). White backgrounds for primary content areas. Subtle slate (#F8FAFC) for sidebar/secondary panels.
- **Typography:** Inter (primary), JetBrains Mono (code/technical values). Scale: 12/14/16/20/24/32/48.

---

### Screen 1: Partner Onboarding Wizard — Step 1: Organization Profile
**Route:** `/onboarding/organization`
**Persona:** Alex (Payment Processor PM)
**User Story:** 1.1, 1.2

```
┌─────────────────────────────────────────────────────────────────────┐
│ AUTHENT                                              [Help] [Log Out]│
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌── Progress Steps ─────────────────────────────────────────────┐  │
│  │  ●─────────────○─────────────○─────────────○                  │  │
│  │  1. Organization  2. Technical  3. Compliance  4. Test         │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                                                                      │
│  Set Up Your Organization                                            │
│  ─────────────────────────────────────────────────────────────────  │
│  This information is used for compliance verification and your      │
│  legal agreement with Authent.                                       │
│                                                                      │
│  Legal Organization Name *                                           │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │ Stripe Payments Europe Limited                                │   │
│  └──────────────────────────────────────────────────────────────┘   │
│  Must match your incorporation documents.                           │
│                                                                      │
│  Primary Jurisdiction *                                             │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │ Ireland (EU)                                           [▼]    │   │
│  └──────────────────────────────────────────────────────────────┘   │
│  Determines applicable AML screening lists and regulatory exports.  │
│                                                                      │
│  Organization Type *                                                 │
│  ○  Payment Processor (Tier-1)    ○  Payment Processor (Tier-2)     │
│  ○  Merchant Acquirer             ○  Issuing Bank                   │
│  ○  Fraud Platform Partner        ○  Enterprise Operator            │
│                                                                      │
│  Primary Contact *                                                   │
│  ┌─────────────────────────────┐  ┌──────────────────────────────┐  │
│  │ First Name                  │  │ Last Name                    │  │
│  └─────────────────────────────┘  └──────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │ Work Email                                                    │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                                                                      │
│  ┌─ Security & Compliance Note ────────────────────────────────────┐│
│  │ 🔒 Your organization data is encrypted at rest and in transit.  ││
│  │    Authent is SOC 2 Type II certified. Legal docs available at  ││
│  │    authent.io/legal                                             ││
│  └─────────────────────────────────────────────────────────────────┘│
│                                                                      │
│  [← Back]                              [Continue to Technical →]    │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

**Components:** Progress stepper, text inputs (4), jurisdiction dropdown, radio button group, security callout banner, primary CTA button, secondary back button
**Interactions:** Real-time legal name format validation by jurisdiction;