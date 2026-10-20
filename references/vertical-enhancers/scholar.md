# The Scholar

**Execution Surface**: `academic_research` + `broad_web_search`  
**Category**: Vertical Enhancer (Academic topics)  
**Trigger**: papers, literature, citations, arXiv, journals, systematic reviews, 论文 / 文献 / 综述

---

## Unique Mandate

Rigorous academic research:
- Literature review
- Citation analysis and **citation verification**
- Research trend identification
- Methodology validation

---

## Execution Mode

The bundled `academic-deep-research` skill was written for interactive use with three stop points. Inside deep-search:

- **Autonomous mode (default)**: when invoked as a worker, by the orchestrator, by `scripts/strict-run.py`, or when the request already has enough information. Do **not** stop to ask clarifying questions or wait for plan approval; treat the orchestrator's plan as approved, run the two research cycles, and return evidence records. Output format follows deep-search's output contract (tables are allowed).
- **Interactive mode**: only when the user calls the academic skill directly in the main conversation **and** the request is genuinely ambiguous. Ask once (questions + plan together), then run to completion.

---

## Sources (prefer bibliographic APIs over scraping)

| Source | Access (checked 2026-10) | Best for |
|---|---|---|
| Crossref `api.crossref.org/works` | Free. Since 2025-12-01: without `mailto` 5 req/s for single DOI lookups and 1 req/s for list queries (1 concurrent); with `mailto=` 10 req/s single and 3 req/s list (3 concurrent) | DOI existence, publisher metadata, retraction flags |
| OpenAlex `api.openalex.org` | Free API key required since February 2026 (`mailto` is now ignored) | Broad coverage incl. non-English venues, title / author lookups |
| Semantic Scholar Graph API | Works without a key but shared and often throttled; a free key gives a steady per-key rate | Batch metadata, citations |
| arXiv API `export.arxiv.org/api/query` | Free; keep to about one request every 3 seconds | Preprints, version history |
| PubMed E-utilities | Free; about 3 req/s without a key, 10 req/s with an NCBI key | Biomedical literature, PMID |
| Google Scholar | No official API; direct scraping is blocked | Discovery only, via a configured search provider |
| CNKI (知网) | No free public API | Chinese literature: verify via OpenAlex / DOI where possible, otherwise mark as not verified |

---

## Citation Verification Cascade

A DOI that resolves is **not** enough: fabricated references often pair a real DOI or a real author with a slightly altered title. For every cited paper:

1. **Identifier**: DOI / arXiv ID / PMID resolves to a record.
2. **Title**: the cited title matches the record's title (normalize case and punctuation; a one- or two-word difference is a red flag).
3. **Authors**: the first author's surname matches.
4. **Year / venue**: year matches (allow ±1 for preprint vs. publication); a "published in venue X" claim matches the record, not just an arXiv preprint.

Verdicts:

- **VERIFIED**: all checks pass in at least one database.
- **UNVERIFIED**: not found in one database, or the database was unreachable. One database missing a paper does **not** mean it is fake (coverage is partial and new papers lag).
- **LIKELY FABRICATED**: absent across several databases, **or** the metadata positively contradicts the identifier's record (e.g. the DOI belongs to a different title or author).

Without network access: say which references look plausible or suspicious from background knowledge, explain why (e.g. an implausible author pairing, a venue / volume / year that does not fit, a title nobody cites), and state that nothing was verified. Never "confirm" a reference offline.

Basis: Rao, Wong & Callison-Burch (2026) found 3–13% of citation URLs from LLMs and deep-research agents were hallucinated, and that URL checking in a self-correction loop cut non-resolving URLs sharply; Reizinger & Brendel's HALLMARK benchmark (2026) found DOI-only checks catch only about a quarter of fabricated references and recommends title-aware matching and flagging only on consensus absence across databases.

---

## Evidence Hierarchy (study design, for clinical / empirical claims)

1. Systematic reviews & meta-analyses
2. Randomized controlled trials
3. Cohort / longitudinal studies
4. Expert consensus / guidelines
5. Cross-sectional / observational
6. Expert opinion / editorials
7. Media reports / blogs

Judge each study by design and relevance to the exact claim, not only by venue prestige. A preprint and its journal version are one study.

---

## Output Format

```markdown
### Core Papers
| Paper | First author | Venue / ID | Year | Verification | Key finding (with locator) |
|-------|--------------|------------|------|--------------|----------------------------|
| [Title] | [Surname] | [DOI / arXiv] | 20XX | VERIFIED / UNVERIFIED | [finding, section/table] |

### Research Trends
- Emerging: [direction] — [papers]
- Contested: [question] — [papers on each side]

### Gaps
- [What the literature does not answer yet]
```

Confidence annotations follow `SKILL.md` §9 (HIGH / MEDIUM / LOW with a reason).
