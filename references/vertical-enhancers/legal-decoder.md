# The Legal Decoder

**Execution Surface**: `broad_web_search` + optional `document_processing`  
**Category**: Vertical Enhancer (Legal topics)  
**Trigger**: Keywords: legal, compliance, regulation, GDPR, lawsuit, patent, ToS

---

## Unique Mandate

Legal document parsing and compliance:
- Statute interpretation
- Case law analysis
- Terms of Service deep-dive
- Compliance requirement extraction
- **Regulatory news and enforcement trends**

---

## Two-Layer Tool Stack

### Primary Layer (Legal Deep Dive)
**Capabilities**:
- `broad_web_search` for authoritative legal sources and official documents
- optional `document_processing` when PDFs or structured filings must be extracted

**Irreplaceable because**: Only direct access to legal documents provides authoritative text.

```text
Primary Layer examples:
- official ToS / privacy policy
- court filings and regulatory guidance
- statute-specific commentary from authoritative sources
```

### Base Layer (Regulatory Context)
**Capability**: `broad_web_search`
- **Purpose**: Gather regulatory news, enforcement trends, industry compliance discussions
- **Activation**: For:
  - "[regulation] enforcement action {current year}"
  - "[industry] compliance fines penalties"
  - "GDPR violation fine [company/industry]"
  - "[law] interpretation guidance update"
  - "legal expert analysis [topic]"

```bash
# Base Layer: Regulatory news and trends
bash ~/.agents/skills/deep-search/scripts/swarm-search.sh \
  "[regulation] enforcement fine {last two years}" news

bash ~/.agents/skills/deep-search/scripts/swarm-search.sh \
  "[industry] compliance violation penalty" general

bash ~/.agents/skills/deep-search/scripts/swarm-search.sh \
  "GDPR CCPA lawsuit settlement amount" news
```

---

## Analysis Framework

### Applicable Regulations (Primary Layer)
| Jurisdiction | Statute/Regulation | Section | Requirements |
|--------------|-------------------|---------|--------------|
| US | [Name] | [X.X] | [Bullet list from text] |
| EU | GDPR | [Article X] | [Bullet list from text] |
| CN | PIPL | [Article X] | [Bullet list from text] |

### Regulatory Trends (Base Layer)
| Period | Enforcement Trend | Key Cases | Source Coverage |
|--------|------------------|-----------|-----------------|
| [Year] | [Increasing/Stable/Decreasing] | [Case list] | [Primary source: regulator notice / court record] |
| [Year, to date] | [Trend] | [Case list] | [Primary source] |

### Compliance Checklist
- [ ] [Requirement 1]: [How to comply - from Primary Layer]
- [ ] [Requirement 2]: [How to comply - from Primary Layer]
- [ ] [Recent changes]: [From Base Layer regulatory news]

### Recent Precedents
| Case | Citation | Holding | Relevance | Web Coverage |
|------|----------|---------|-----------|--------------|
| [Name] | [Citation] | [Summary] | [High/Med/Low] | Independent sources: N |

---

## Collaboration Pattern

**Receives from**:
- Global Observer: General regulatory environment context
- Compliance Auditor: Financial regulatory overlap
- Oracle: Regulatory incentive structures

**Primary Layer provides**:
- Authoritative legal text (statutes, contracts, rulings)
- Exact compliance requirements
- Binding precedents

**Base Layer provides**:
- Regulatory enforcement trends ("Are they actually enforcing this?")
- Industry compliance discussions
- Legal expert interpretations from blogs/forums
- Cross-jurisdictional comparisons

---

## Output Format

```markdown
## Legal Analysis

### Applicable Regulations (Primary Layer)
| Jurisdiction | Regulation | Key Sections | Requirements |
|--------------|-----------|--------------|--------------|
| EU | GDPR | Art. 6, 7 | [Summary] |
| US | CCPA | § 1798.100 | [Summary] |

### Terms of Service Analysis (Primary Layer)
**Document**: [URL] | **Date**: [Version]
- [Clause 1]: [Analysis]
- [Red Flag]: [Concerning language identified]

### Regulatory Trends (Base Layer)
- **Enforcement intensity**: [Increasing/Stable] (based on [N] sources across engines)
- **Recent fines**: [List with amounts] (independent sources: N)
- **Industry compliance status**: [Summary from web discussions]
- **Upcoming changes**: [Proposed regulations found in news]

### Risk Assessment
**Risk Rating**: [HIGH/MEDIUM/LOW]
**Justification**: [2-3 sentences combining Primary and Base findings]

### Potential Liabilities
1. [Risk]: [Description + likelihood - from Primary text analysis]
2. [Risk]: [Trend suggesting increased risk - from Base Layer]

### Mitigation Strategies
- [Strategy 1 with legal basis from Primary Layer]
- [Strategy 2 with industry best practices from Base Layer]
```

---

## Why Two Layers?

| Aspect | Primary (Legal docs / optional extraction) | Base (`broad_web_search`) |
|--------|---------------------|---------------------------|
| **Data** | Statutes, contracts, court rulings | Regulatory news, expert analysis, trends |
| **Source** | Government databases, company sites | host web search / fallback engines |
| **Question** | "What does the LAW say?" | "How is it being ENFORCED/INTERPRETED?" |

**Example**:
- Primary: "GDPR Article 6 requires lawful basis for processing"
- Base: "[year] saw [total] in GDPR fines (cite the regulator or EDPB report, not a blog)"
- **Combined**: Legal requirement + Enforcement trend = Prioritized compliance roadmap

---

## Multi-Jurisdictional Analysis

**Primary Layer** (for each jurisdiction):
- Local statutes and regulations
- National court precedents
- Local ToS variations

**Base Layer**:
- Cross-border enforcement cooperation news
- Jurisdictional comparison articles
- "Forum shopping" discussions (where to litigate)

**Output**: Jurisdiction-by-jurisdiction risk map with enforcement reality


---

## Version / Effective Date Rule

- Quote the **current consolidated text** of a law, regulation, tariff decision or licence, and record its effective date and version.
- Trade measures (tariffs, anti-dumping / countervailing duties, export controls): use the issuing authority's official text (e.g. the EU Official Journal / Commission implementing regulation, the national customs or commerce ministry notice). News coverage is context, not the rule itself.
- Software / model licences: the licence file shipped with the **specific version** decides; licences can differ between versions of the same project. Community claims do not override the licence text.
