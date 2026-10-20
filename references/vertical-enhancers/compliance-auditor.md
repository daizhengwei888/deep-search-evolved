# The Compliance Auditor

**Execution Surface**: `broad_web_search` + optional `document_processing`  
**Category**: Vertical Enhancer (Business topics)  
**Trigger**: Keywords: startup, funding, valuation, SEC, compliance, financial

---

## Unique Mandate

Business and financial due diligence:
- SEC filings analysis
- Hidden fees identification
- Ponzi structure detection
- Regulatory compliance check
- **Market sentiment and news context**

---

## Two-Layer Tool Stack

### Primary Layer (Financial Deep Dive)
**Capabilities**:
- `broad_web_search` for SEC filings, official disclosures, regulatory coverage
- optional `document_processing` for extracted filings and statements

**Irreplaceable because**: Only direct SEC access provides legally-required disclosures.

```text
Primary Layer examples:
- SEC EDGAR filing lookup (data.sec.gov requires a descriptive User-Agent with contact info)
- annual report / 20-F / S-1 discovery
- China A-share disclosures: cninfo (巨潮资讯网, the CSRC-designated disclosure site) announcements and annual-report PDFs
- official regulator disclosures
```

Prefer the filing itself over articles about the filing. Revenue, margins and risk factors come from the audited statements; press coverage is context.

### Base Layer (Market Context)
**Capability**: `broad_web_search`
- **Purpose**: Gather market sentiment, news analysis, investor discussions
- **Activation**: For:
  - "[company] stock analysis investment thesis"
  - "[startup] funding valuation news"
  - "[company] regulatory investigation news"
  - "[company] layoffs financial trouble"
  - "[crypto] scam warning red flags"

```bash
# Base Layer: Market sentiment and news
bash ~/.agents/skills/deep-search/scripts/swarm-search.sh \
  "[company] stock analysis bull bear case" general

bash ~/.agents/skills/deep-search/scripts/swarm-search.sh \
  "[startup] funding round valuation latest" general

bash ~/.agents/skills/deep-search/scripts/swarm-search.sh \
  "[company] investigation regulatory fine" news
```

---

## Analysis Framework

### Financial Health (Primary Layer)
| Metric | Value | Trend | Risk Level |
|--------|-------|-------|------------|
| Revenue | $X | ↑/↓/→ | 🟢🟡🔴 |
| Burn rate | $Y/month | ↑/↓/→ | 🟢🟡🔴 |
| Runway | Z months | ↑/↓/→ | 🟢🟡🔴 |

### Market Sentiment (Base Layer)
| Source | Sentiment | Key Points | Engine Count |
|--------|-----------|------------|--------------|
| Financial blogs | [Bullish/Bearish] | [Summary] | Independent sources: N |
| Investment forums | [Bullish/Bearish] | [Summary] | Independent sources: N |
| News analysis | [Bullish/Bearish] | [Summary] | Independent sources: N |

### Red Flags Checklist
- [ ] Unrealistic promises (Primary + Base Layer cross-check)
- [ ] Hidden fees disclosed? (Primary Layer)
- [ ] Regulatory warnings? (Primary Layer)
- [ ] **Market skepticism**? (Base Layer — found on multiple engines?)
- [ ] Multi-level marketing structure? (Primary Layer)

---

## Collaboration Pattern

**Receives from**:
- Global Observer: General business context
- Oracle: Stakeholder and incentive analysis
- Underground OSINT: Employee/investor community discussions

**Primary Layer provides**:
- Legally-mandated financial disclosures
- Official regulatory filings
- Hard financial metrics

**Base Layer provides**:
- Market sentiment validation ("Does the street believe the numbers?")
- Independent reporting (is this reported by outlets that did their own reporting?)
- Investor discussion trends

---

## Output Format

Risk assessment with primary sources and market context:
```markdown
## Compliance Assessment

### Risk Rating: [HIGH/MEDIUM/LOW]
**Justification**: [2-3 sentences with evidence]

### Key Findings (Primary Layer)
1. **Finding**: [Financial metric or regulatory issue]
   **Evidence**: [SEC filing #, clause, URL]
   **Impact**: [Financial/Legal/Reputational]

### Market Context (Base Layer)
- **Cross-engine coverage**: Independent lineages: [N] (repeats of one wire story count once)
- **Sentiment trend**: [Bullish/Neutral/Bearish]
- **Key concerns from web**: [Summary of market discussions]
- **Validation**: Primary findings corroborated by [N] independent sources

### Recommendations
- [Action 1 with specific timeline]
- [Action 2 with specific timeline]
```

---

## Why Two Layers?

| Aspect | Primary (SEC/filings) | Base (`broad_web_search`) |
|--------|----------------------|---------------------------|
| **Data** | Hard financials, legal disclosures | Market sentiment, news analysis |
| **Source** | Government regulatory database | host web search / fallback engines |
| **Question** | "What do they HAVE to disclose?" | "What does the market THINK?" |

**Example**:
- Primary: "Company reports $100M revenue in 10-K"
- Base: "3 investment blogs question revenue recognition; 2 forums mention whistleblower"
- **Combined**: Official numbers + Market skepticism = Deeper risk assessment

---

## Scam Detection Checklist

**Primary Layer (Hard evidence)**:
- [ ] No SEC filings for US company offering investments
- [ ] Promised returns > market average with "no risk"
- [ ] Pressure tactics ("limited time", "exclusive opportunity")

**Base Layer (Market intelligence)**:
- [ ] "[company] scam" appears on multiple engines
- [ ] Complaints found across forums/blogs
- [ ] No independent third-party verification

**Combined verdict**: Primary + Base agreement = High confidence assessment
