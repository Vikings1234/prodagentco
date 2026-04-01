# FINANCIAL MODEL BRIEF
## Agentic Commerce Payment Infrastructure Platform
**Date:** March 2026  
**Scope:** Phase 1-2 MVP (Stripe-only, OAuth2 agent identity, fraud signal integration)  
**Confidence Level:** Moderate (0.64 average agent confidence; model includes sensitivity analysis on key de-risking assumptions)

---

## EXECUTIVE SUMMARY

**Investment Required:** $15–18M Series A  
**Timeline to Profitability:** 36–48 months  
**Target Revenue (Month 24):** $2–3M ARR  
**Year 1 Revenue (Months 1–12):** $150K–$400K  
**Year 2 Revenue (Months 13–24):** $1.5M–$2.5M  
**Unit Economics (Mature State):**
- CAC: $80K–$120K per processor partnership
- LTV: $2.8M–$4.2M per processor (10-year horizon)
- LTV/CAC: 28–42x (exceptional, but 24-month payback is realistic)
- Payback Period: 18–26 months
- Gross Margin: 75–82% (software + licensing)

**Profitability Inflection:** Month 36–40 (when processor licensing deals mature + transaction volume reaches critical mass)

**Key Risk:** Revenue model assumes 2–3 processor partnerships by Month 18. If processor partnerships are delayed or fail to materialize, runway extends to 48+ months.

---

## 1. PRICING MODEL

### 1.1 Pricing Strategy Rationale

We operate in a **multi-sided market** with three distinct customer segments, each with different willingness-to-pay and unit economics:

1. **Payment Processors (B2B2C)** — Highest willingness-to-pay; strategic value
2. **Enterprise Merchants (B2B)** — Medium willingness-to-pay; operational value
3. **Fraud Platforms (B2B)** — Lower willingness-to-pay; data/signal value
4. **Developers (B2C, deferred to Phase 3)** — Volume-based, low ARPU

**Our pricing philosophy:** We extract value proportional to the economic value we enable. Processors benefit from unlocking $3T agentic commerce market; merchants benefit from enabling high-velocity agent purchasing; fraud platforms benefit from improved detection accuracy. Pricing reflects each segment's value creation.

### 1.2 Pricing Model Options & Recommendation

#### **OPTION A: Pure Licensing (Recommended for Phase 1-2)**

**Processor Licensing (Primary Revenue Driver)**
- **Tier 1 (Stripe, Adyen, PayPal):** $1.2M–$2.0M annual license + 5 bps per transaction volume
  - Base covers: API access, identity framework, compliance toolkit, 24/7 support
  - Volume-based component kicks in at $10M+ agent transaction volume/month
  - 3-year contract with minimum annual commitment

- **Tier 2 (Square, WorldPay, regional processors):** $500K–$800K annual + 5 bps
  - Same features as Tier 1; lower base due to smaller processor scale

- **Tier 3 (Payment networks, SWIFT, emerging processors):** $250K–$500K annual + 7 bps
  - Regulatory specification access; no transactional data sharing

**Merchant Licensing (Secondary Revenue Driver)**
- **Enterprise merchants (Fortune 500 + large cap retailers):** $200K–$500K annual
  - Includes: Agent identity framework, authorization policy engine, audit logging, fraud integration
  - Price varies by: number of agents (0–100 base; $1K per additional agent), transaction volume

- **Mid-market merchants (Series B+ startups, regional retailers):** $50K–$150K annual
  - Freemium tier available ($0–10 agents, <$10M agent txn volume/year)

**Fraud Platform Licensing (Tertiary Revenue Driver)**
- **Tier 1 (Sift, Kount, Feedzai):** $300K–$600K annual for signal integration
  - Includes: Agent identity signal feed, behavioral baseline access, explainability toolkit
  - Price based on: fraud platform's customer base size, integration scope

- **Tier 2 (Regional fraud platforms, specialized providers):** $100K–$250K annual

**Rationale:**
- Aligns with SaaS licensing precedent (Stripe, Twilio charge licensing + usage)
- Encourages processor adoption (low base; volume upside if agentic commerce scales)
- Defensible moat: once integrated, switching cost is high
- Regulatory compliance: licensing model positions us as infrastructure provider, not payment processor

#### **OPTION B: Pure Transaction Fees (Not Recommended for Phase 1-2)**

- 1–3 bps on all agent transaction volume
- Merchants pay per transaction (pass-through from processors)
- **Pros:** Aligns incentives with agent commerce growth
- **Cons:** No revenue until transaction volume scales (18–24 months); creates dependency on agent adoption velocity; harder to forecast; underprices early-stage value creation

**Verdict: Not recommended.** Transaction fees alone do not generate material revenue until agent commerce reaches $100B+ annual volume (not expected until 2028–2029). Licensing model provides earlier cash flow and de-risks on processor partnerships.

#### **OPTION C: Hybrid (Licensing + Transaction Fees) — RECOMMENDED PRIMARY MODEL**

- **Base licensing:** Tiers as defined in Option A
- **Transaction fee overlay:** 3–5 bps on agent transaction volume, only after processor integration reaches $100M+ monthly volume
- **Rationale:** Early cash flow from licensing (Months 6–18); upside from transaction fees (Months 18–36+) as volume scales

**Verdict: Recommended.** Hybrid model balances early revenue (licensing) with upside (transaction fees). Conservative assumption: transaction fees begin flowing in Month 18–20.

---

### 1.3 Recommended Pricing Model (Adopted for Financial Projections)

**PRIMARY REVENUE STREAM: Processor Licensing (Months 1–24)**

| Processor Tier | Year 1 Count | Year 2 Count | Annual License | Transaction Fees (5 bps) | Est. Year 1 Revenue | Est. Year 2 Revenue |
|---|---|---|---|---|---|---|
| Tier 1 (Stripe, Adyen) | 0.5 (pilot) | 1.5 | $1.5M | 5 bps @ $500M mo volume | $750K (Year 1) | $2M (Year 2) |
| Tier 2 (Square, WorldPay) | 0 | 1.5 | $650K | 5 bps @ $200M mo volume | $0 | $1.2M |
| Tier 3 (SWIFT, networks) | 0 | 1 | $400K | 7 bps @ $100M mo volume | $0 | $0.8M |

**SECONDARY REVENUE STREAM: Merchant Licensing (Months 6–24)**

| Merchant Segment | Year 1 Count | Year 2 Count | Avg Annual Contract | Est. Year 1 Revenue | Est. Year 2 Revenue |
|---|---|---|---|---|---|
| Enterprise (Fortune 500) | 2–3 | 8–12 | $350K | $700K–$1M | $2.8M–$4.2M |
| Mid-market | 5–8 | 20–30 | $75K | $375K–$600K | $1.5M–$2.25M |
| Freemium (conversion rate 5%) | 100–200 | 500–800 | $20K (paid convert) | $100K–$200K | $500K–$800K |

**TERTIARY REVENUE STREAM: Fraud Platform Licensing (Months 9–24)**

| Fraud Platform Tier | Year 1 Count | Year 2 Count | Avg Annual License | Est. Year 1 Revenue | Est. Year 2 Revenue |
|---|---|---|---|---|---|
| Tier 1 (Sift, Kount, Feedzai) | 0 | 3–4 | $450K | $0 | $1.35M–$1.8M |
| Tier 2 (Regional) | 0 | 2–3 | $150K | $0 | $300K–$450K |

**TOTAL ESTIMATED REVENUE (BASE CASE)**

| Period | Processor Licensing | Merchant Licensing | Fraud Platform | Transaction Fees | **Total ARR** |
|---|---|---|---|---|---|
| Month 6 (Year 1 mid-point) | $250K | $200K | $0 | $0 | **$450K annualized** |
| Month 12 (Year 1 end) | $750K | $400K | $0 | $0 | **$1.15M annualized** |
| Month 18 (Year 2 mid-point) | $1.5M | $1M | $500K | $100K | **$3.1M annualized** |
| Month 24 (Year 2 end) | $2.8M | $2M | $1.8M | $400K | **$7.0M annualized** |

**Key assumptions baked into revenue model:**
- Stripe pilot signed Month 4, generates partial-year license revenue
- 1.5–2 additional processor partnerships close by end of Year 2
- Merchant ARR grows from $2–3 customers (Month 6) to 40–50 customers (Month 24)
- Fraud platform partnerships close Months 9–15
- Transaction fee base does not materialize until Month 18+

---

## 2. UNIT ECONOMICS

### 2.1 Processor Partnerships (Primary Unit of Analysis)

**Customer Acquisition Cost (CAC) — Per Processor Partnership**

| Cost Component | Month 1–4 | Month 5–12 | Cumulative |
|---|---|---|---|
| Sales/BD headcount (1 FTE, fully loaded) | $150K | $150K | $300K |
| Legal/contract negotiation (external counsel + ops time) | $75K | $50K | $125K |
| Technical integration (engineering 4 FTE for 3 months) | $200K | $100K | $300K |
| Travel/events for processor relationships | $30K | $20K | $50K |
| Marketing/thought leadership (processor conferences, whitepapers) | $20K | $15K | $35K |
| **Total CAC per processor deal** | | | **$810K–$900K** |

**Note:** Above assumes 1.5 processor deals close in Year 1 (Stripe pilot + 1 additional). CAC per deal = $1.35M total spend / 1.5 deals ≈ **$900K/processor.**

**Lifetime Value (LTV) — Per Processor Partnership (10-Year Horizon)**

| Revenue Component | Year 1 | Year 2 | Year 3–10 (Annual) | Total 10-Year |
|---|---|---|---|---|
| License fee (Tier 1) | $750K | $1.5M | $1.5M | $750K + $1.5M + $1.5M × 8 = $14.25M |
| Transaction fees (5 bps, ramp) | $0 | $100K | $300K | $0 + $100K + $300K × 8 = $2.5M |
| **Total LTV (10-year)** | | | | **$16.75M** |

**Conservative scenario (assumes processor relationship maturity slower):**
- License fees plateau at $1.2M Year 3+
- Transaction fees reach 10 bps (higher volume = more valuable) by Year 5
- **Revised LTV = $13.5M–$14.2M**

**LTV/CAC Ratio = $14.2M / $0.9M = 15.8x** (exceptional by SaaS standards; benchmark is 3–5x)

**Note:** High LTV/CAC is credible because:
1. Processor partnerships are sticky (switching cost = re-engineering payment flow)
2. Revenue is annuity-based (recurring license) + growth-based (transaction fees scale with agentic commerce)
3. Our marginal cost per processor (engineering support, infrastructure, fraud platform integrations) is ~$50–70K/year, so gross margin stays >75% even at $1.5M+ annual spend

### 2.2 Enterprise Merchant Unit Economics

**Customer Acquisition Cost (CAC) — Per Enterprise Merchant**

| Cost Component | Year 1 | Year 2 |
|---|---|---|
| Sales/AE cost (0.5 FTE → 1.5 FTE for Year 2) | $75K | $150K |
| Marketing/events | $20K | $30K |
| Technical onboarding | $10K | $15K |
| **CAC per enterprise customer** | | **$35K–$65K** |

**Average across 2–3 Year 1 customers: $50K–$70K/customer**

**Lifetime Value — Enterprise Merchant (5-Year Horizon)**

| Year | Avg Annual Contract | Retention | Upsell | Cumulative LTV |
|---|---|---|---|---|
| Year 1 | $350K | 90% | $0 | $350K |
| Year 2 | $350K | 95% | $50K | $750K |
| Year 3 | $380K | 95% | $70K | $1.2M |
| Year 4 | $400K | 95% | $80K | $1.76M |
| Year 5 | $420K | 95% | $100K | $2.36M |

**LTV (5-year) = $2.36M**  
**LTV/CAC = $2.36M / $0.06M = 39x** (again, exceptional)

**Payback Period = $350K annual contract / $60K CAC ≈ 2.5 months** (very fast; industry benchmark is 12+ months)

**Rationale for fast payback:**
- Merchant customers have urgent pain (agents blocked from transacting)
- Switching cost is high (re-building payment policy logic)
- Gross margin is 80%+ (mostly software)

### 2.3 Gross Margin Analysis

**Per Processor Partnership (Steady-State Year 3+)**

| Cost Category | Annual Cost | As % of Revenue |
|---|---|---|
| **Revenue Base** | $1.5M | 100% |
| Infrastructure (AWS, database, fraud platform integrations) | $100K | 6.7% |
| Customer support (1 FTE for processor) | $150K | 10% |
| Compliance/regulatory (shared cost allocation) | $80K | 5.3% |
| Fraud platform licensing pass-through | $50K | 3.3% |
| **Total COGS** | **$380K** | **25.3%** |
| **Gross Profit** | **$1.12M** | **74.7%** |

**Per Enterprise Merchant (Steady-State Year 3+)**

| Cost Category | Annual Cost | As % of Revenue |
|---|---|---|
| **Revenue Base** | $400K | 100% |
| Infrastructure (shared, allocated) | $15K | 3.75% |
| Customer support (0.2 FTE) | $50K | 12.5% |
| Compliance/audit support | $15K | 3.75% |
| **Total COGS** | **$80K** | **20%** |
| **Gross Profit** | **$320K** | **80%** |

**Blended Gross Margin (Portfolio Assumption):**
- Processor partnerships (60% of revenue by Year 2) = 75% margin
- Merchant customers (35% of revenue by Year 2) = 80% margin
- Fraud platforms (5% of revenue by Year 2) = 70% margin

**Blended Portfolio Gross Margin = 0.60 × 0.75 + 0.35 × 0.80 + 0.05 × 0.70 = 76% (mature state)**

### 2.4 Customer Acquisition Efficiency (Magic Number)

**Year 1 Magic Number = (New ARR gained in period) / (Sales & Marketing spend in prior period)**

- Year 1 New ARR: $1.15M (by