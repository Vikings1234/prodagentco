# LEGAL AND COMPLIANCE BRIEF
## Agentic Commerce Payment Infrastructure Platform

**Document Version:** 1.0  
**Date:** March 2026  
**Classification:** Internal — Executive, Investment Committee, Board  
**General Counsel:** Primary Author  
**Status:** READY FOR BOARD APPROVAL WITH CONDITIONAL GATES  
**Companion Documents:** Executive Brief, PRD v1.0, Technical Specification, Financial Model

---

## EXECUTIVE SUMMARY

This brief identifies all regulatory, compliance, and legal requirements for launching the Agentic Commerce Payment Infrastructure Platform in the US, EU, UK, and Singapore jurisdictions. Our analysis separates **launch-blockers** (must resolve before production) from **post-launch obligations** (must resolve within 6–12 months post-launch).

### Key Findings

**1. Regulatory Environment: FAVORABLE BUT NOT CERTAIN**
- **US:** No specific AI agent payment regulation; operates in PSD2-equivalent grey zone. SEC/CFPB have announced frameworks but no final rules. **Risk: Low-to-Medium.** Mitigation: Position as compliance-enabler, not payment processor.
- **EU:** PSD2 compliance is mandatory (we are not a payment processor, but we facilitate transactions). PSD3 (effective May 2026) introduces strict SCA (Strong Customer Authentication) requirements with **explicit regulatory ambiguity on agent transactions.** **Risk: High.** Mitigation: Obtain regulatory interpretation from European Banking Authority (EBA) before EU launch.
- **UK:** Post-Brexit, UK applies modified PSD2 (UK-PSD2). Less certain than EU, but same SCA framework applies. **Risk: Medium.** Mitigation: FCA guidance interpretation required.
- **Singapore:** MAS (Monetary Authority of Singapore) applies Payment Services Act (PSA). Agent transactions not explicitly addressed. **Risk: Low-to-Medium.** Mitigation: Early consultation with MAS.

**2. Liability Framework: CRITICAL GAP**
- **No insurance product exists** for agent-initiated payment transactions.
- **No processor ToS explicitly permits** agent transactions; most are silent or exclusionary.
- **Chargeback liability allocation unclear:** Who is responsible if agent makes unauthorized transaction? Processor? Merchant? Us?
- **Wire fraud statute exposure:** If our system facilitates an OFAC violation, we may face criminal liability.
- **First critical decision:** Before accepting production transactions, we must execute **processor indemnification agreements** and establish **$2–5M chargeback reserve fund.**

**3. Data Privacy: MANAGEABLE WITH DESIGN**
- **GDPR:** We process agent operator personal data (beneficial owners, KYC docs). **Compliance required.** Design: Data Processing Agreement with Stripe + customers; privacy policy; data retention limits (7 years for audit only).
- **CCPA:** Applies if we have California customers. **Compliance required.** Design: Opt-out mechanism; privacy policy; service provider agreements.
- **Data minimization principle:** Collect only agent_id, operator_id, spending policies. Do not collect transaction details or behavioral data (that belongs to Stripe/processor).

**4. IP Strategy: DEFENSIBLE MOAT THROUGH PATENTS + TRADE SECRETS**
- **Patentable innovations:** Agent identity attestation protocol, cryptographic proof-of-authorization, spending policy enforcement engine. **File provisional patent (US, EU, UK) by Month 3.** Cost: $80–120K.
- **Trade secrets:** Fraud signal algorithm, behavioral baseline models, operator compliance scoring. **Protect through code obfuscation + restricted access.** Cost: Built into engineering.
- **Open-source risk:** Do not publish core authentication cryptography; publish specifications (regulatory appeal) under CC-BY-SA license (royalty-free, attribution-required).

**5. Open-Source Compliance: MINIMAL RISK WITH DESIGN**
- We use open-source libraries (JWT, OAuth2, cryptography libraries). **Risk: License compatibility.** Mitigation: Audit all dependencies for GPL/AGPL; replace any GPL dependencies with Apache 2.0/MIT equivalents.
- We publish specification documents (not code) under Creative Commons. **No risk.**
- **Action: Perform SBOM (Software Bill of Materials) audit by Month 2.** Cost: $20–30K.

**6. Terms of Service & Privacy Policy: REQUIRED FOR LAUNCH**
- **ToS must address:**
  - Limitation of liability (cap at fees paid; exclude indirect damages)
  - Indemnification by customer for agent-initiated fraud/OFAC violations
  - Dispute resolution (arbitration preferred; jurisdiction: Delaware)
  - SLA on authorization verification (sub-100ms; 99.9% uptime guarantee)
  - Data retention and deletion (audit logs 7 years; transaction metadata 2 years)
- **Privacy Policy must address:**
  - Data processing for AML/KYC (third-party screening)
  - Retention periods for beneficial owner information
  - GDPR/CCPA rights (access, deletion, portability)
  - Cookie policy (if SPA frontend)

**7. Insurance Requirements: MANDATORY PRE-LAUNCH**
- **Professional Liability Insurance (E&O):** $5M–10M coverage. **Requirement: Essential.** Cost: $150K–250K annual premium.
- **Cyber Liability Insurance:** $3M–5M coverage (data breach, network security). **Requirement: Essential.** Cost: $100K–150K annual.
- **Directors & Officers Insurance:** $5M coverage. **Requirement: Board mandate.** Cost: $75K–100K annual.
- **Crime Insurance (Employee Dishonesty):** $2M coverage. **Requirement: Recommended for fintech.** Cost: $50K–75K annual.
- **Errors & Omissions (Payment Processing):** $5M coverage. **Requirement: Mandatory for processor integrations.** Cost: $200K–300K annual.
- **Total insurance annual cost: $575K–875K.** Budget this as operating expense, not capital.

---

## SECTION 1: REGULATORY REQUIREMENTS BY JURISDICTION

### 1.1 UNITED STATES

#### 1.1.1 Securities & Exchange Commission (SEC) — Broker-Dealer / Investment Adviser Rules

**Applicability:** LOW to MEDIUM  
**Status:** Regulatory ambiguity

**Context:**
If we facilitate payment of securities (stock purchases by agents), we may be deemed a broker-dealer under Securities Exchange Act. Currently, we are scoped to **non-securities payments only** (retail commerce, B2B payments, etc.). We explicitly do NOT facilitate:
- Equity purchases
- Options trading
- Cryptocurrency/digital asset transfers (out of scope for MVP)
- Derivatives

**Compliance Requirements IF we expand scope:**
- Register as broker-dealer with SEC + FINRA
- Maintain net capital requirements (currently N/A)
- Implement best execution policies (currently N/A)
- Obtain regulatory approval for business model (currently N/A)

**Action for MVP (Non-Securities Scope):**
- Document in ToS: "Service does not facilitate securities transactions. Prohibited use: equity purchases, derivatives, futures."
- Implement payment method blocklist: reject transactions to known securities exchanges, brokerages, crypto exchanges.
- Cost to implement: $50K (engineering) + zero regulatory cost.

**Launch-Blocker Status:** NO (if non-securities scope maintained)

---

#### 1.1.2 Financial Crimes Enforcement Network (FinCEN) — Money Laundering Prevention

**Applicability:** HIGH  
**Status:** Regulatory grey zone (agent transactions not explicitly addressed)

**Context:**
FinCEN regulates "money services businesses" (MSBs) under 31 CFR 1010.100. MSB definition includes entities that engage in "transmission of funds." The question: **Does facilitating agent payments = transmission of funds?**

**Our Position:** We are NOT a transmission intermediary. We do not:
- Hold customer funds
- Execute settlements
- Control money flow

We provide **authorization metadata** that Stripe uses to authorize transactions. Stripe is the money transmitter; we are infrastructure.

**However, FinCEN has expressed concern** about non-bank payment facilitation. Expect renewed guidance in 2026–2027.

**Compliance Requirements (Conservative Approach):**

1. **AML/KYC Program (Internal):**
   - Designate AML Compliance Officer
   - Implement Customer Identification Program (CIP): Know the operator (legal name, beneficial owners, business type)
   - Implement Suspicious Activity Reporting (SAR): Flag operators if transaction patterns suggest money laundering (rapid fund cycling, structuring, high-risk jurisdictions)
   - Implement Sanctions Screening: Block operators on OFAC/FATF watchlists
   - Maintain audit trail: Document all CIP/SAR decisions

2. **Recordkeeping:**
   - Maintain records of operator identity, KYC docs, screening results for 5 years
   - Exportable in format required by FinCEN upon request

3. **Reporting:**
   - File Suspicious Activity Reports (SARs) with FinCEN if any operator triggers high-risk flags
   - Report threshold: transactions >$5,000 if suspicious activity detected
   - Filing deadline: 30 days from detection

4. **Operator Screening (Mandatory):**
   - All operators screened against OFAC SDN list before account activation
   - All beneficial owners screened against FATF PEP (Politically Exposed Persons) list
   - Monthly re-screening of high-risk operators
   - Automated blocking of sanctioned entities

5. **FinCEN Registration (Optional but Recommended):**
   - Voluntary BSA e-filing registration with FinCEN (no cost)
   - Demonstrates proactive compliance posture
   - Required if FinCEN later determines we are an MSB

**Estimated Compliance Cost:**
- AML/KYC platform integration (Refinitiv, Lexis-Nexis, or equivalent): $100K setup + $30K/month
- AML Compliance Officer (0.5 FTE): $75K/year
- Legal/compliance audit: $50K annually
- **Total Year 1: $455K**

**Launch-Blocker Status:** YES — AML/KYC program must be operational before accepting first operator. (Target: Month 1–2)

---

#### 1.1.3 Comptroller of the Currency (OCC) — Fintech Charter Exemption

**Applicability:** LOW  
**Status:** Exemption likely applies

**Context:**
OCC issued guidance (May 2021) permitting non-bank financial services companies to operate without bank charter if they do not take deposits, make loans, or issue payment instruments.

We fit the exemption: we do not take deposits, make loans, or issue payment instruments.

**Compliance Requirement:** Document our business model in response to any OCC inquiry. No proactive filing required.

**Launch-Blocker Status:** NO

---

#### 1.1.4 Federal Trade Commission (FTC) — Standards for Safeguarding Nonpublic Information

**Applicability:** MEDIUM  
**Status:** Mandatory (16 CFR 314)

**Context:**
FTC Safeguards Rule (updated 2023) requires all companies maintaining nonpublic information about customers to implement comprehensive information security program.

We maintain:
- Operator personal data (beneficial owners' names, addresses, ID numbers)
- API keys and cryptographic secrets
- Transaction metadata (amounts, merchant categories)

**Compliance Requirements:**

1. **Information Security Program:**
   - Designated Chief Information Security Officer (CISO)
   - Risk assessment: Identify vulnerabilities in systems storing nonpublic info
   - Safeguards implementation: Encrypt data in transit and at rest; implement access controls; monitor for intrusions
   - Incident response plan: Procedures for detecting, responding to, and reporting breaches
   - Third-party risk assessment: Audit Stripe, AML screening vendor, fraud platform vendors for security

2. **Breach Notification (if applicable):**
   - Notify affected operators within 30 days of breach discovery
   - Notify FTC if breach affects >500 individuals
   - Maintain breach notification log (5-year retention)

3. **Annual Certification:**
   - CEO/CFO must certify annually that information security program is implemented and effective

**Estimated Compliance Cost:**
- CISO hire (1 FTE, full-loaded): $200K/year
- Security audit (external firm, annual): $80K
- Incident response retainer: $50K/year
- **Total Year 1: $330K**

**Launch-Blocker Status:** YES — Security program must be operational before launch. (Target: Month 2–3)

---

#### 1.1.5 California Consumer Privacy Act (CCPA) & Privacy Rights

**Applicability:** HIGH (if any California customers)  
**Status:** Mandatory

**Context:**
CCPA (effective Jan 1, 2020) grants California residents rights over personal data collection and use. Operators who are California residents have rights to:
- Know what data we collect
- Delete personal data
- Opt out of data sales
- Access personal data in portable format

We expect 15–20% of merchant customers to be California-based.

**Compliance Requirements:**

1. **Privacy Policy (Web-facing):**
   - List data categories collected (operator names, beneficial owner info, transaction metadata)
   - List data use purposes (fraud prevention, compliance screening, service delivery)
   - Disclose third-party sharing (Stripe, AML screening vendors)
   - Explain CCPA rights: right to access, delete, opt-out, portability
   - Designate contact for privacy inquiries

2. **Data Deletion Process:**
   - Implement mechanism for customers to request deletion of personal data
   - Delete data within 45 days of verified request (unless legal hold applies)
   - Document deletion requests and completions

3. **Data Opt-Out Mechanism:**
   - CCPA defines "sale" broadly (includes sharing for business purposes)
   - If we share operator data with third parties for any purpose beyond service delivery, provide opt-out link
   - Recommended: Minimize data sharing; default to opt-out

4. **Service Provider Agreements:**
   - Stripe, AML vendors, fraud platforms must execute Data Processing Agreements (DPAs) committing to CCPA compliance
   - Audit vendors annually for CCPA compliance

**Estimated Compliance Cost:**
- Privacy policy drafting (external counsel): $20K
- Technical implementation (deletion/opt-out tools): $30K
- Annual audit: $15K
- **Total Year 1: $65K**

**Launch-Blocker Status:** CONDITIONAL — Privacy policy must be published before launch. Deletion/opt-out tools can be implemented post-launch (Month 1–3).

---

### 1.2 EUROPEAN UNION

#### 1.2.1 Payment Services Directive 2 (PSD2) — Core Compliance Framework

**Applicability:** CRITICAL for EU operations  
**Status:** Mandatory (effective January 13, 2018; already in force)

**Context:**
PSD2 (2015/2366/EU) regulates payment services in the EU. Its core requirement: **Strong Customer Authentication (SCA)** for electronic payment transactions.

**SCA Definition (Article 4(30)):**
"Authentication based on two or more elements categorized as knowledge (something only the user knows), possession (something only the user has), and inherence (something the user is) that are independent, in that the breach of one does not compromise the others."

**Examples of SCA:**
- Password + SMS code (knowledge + possession)
- Biometric + PIN (inherence + knowledge)
- Hardware token + password (possession + knowledge)

**The Agent Problem:**
An autonomous AI agent cannot:
- Enter a password (no knowledge)
- Provide biometric (no biometric)
- Manage a hardware token (no possession)

**Therefore, agent transactions as currently designed VIOLATE PSD2 SCA requirements.**

**Current Workarounds (and their limitations):**
1. **Low-Risk Exemption (Article 17):** Transactions <€30 are exempt from SCA (exemption applies only if merchant authorizes)
   - **Problem:** Enterprise agents need to transact >€30; exemption is insufficient
   
2. **Exemption for CTP (Customer-Initiated Transaction):** If the human customer pre-authorizes spending via SCA, subsequent agent transactions can proceed without SCA (delegation of authority)
   - **Status:** UNCLEAR whether this applies to agents; regulators are silent
   - **Risk:** Processors may reject agent transactions on narrow reading

3. **Mark as "Merchant-Not-Authenticated" (CHP):** Merchant can submit transaction as "customer-not-present" and apply rules-based fraud scoring instead of SCA
   - **Problem:** High compliance risk; regulators increasingly scrutinizing CHP exemptions

**European Banking Authority (EBA) Regulatory Ambiguity:**
- EBA has NOT issued explicit guidance on whether agent transactions require SCA
- EBA does NOT explicitly permit agent transactions as valid under any exemption
- **This is the critical gap:** Regulatory uncertainty creates processor reluctance

**Our Compliance Approach (Conservative):**

**Option