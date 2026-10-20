# The Global Observer

**Execution Surface**: `broad_web_search` capability  
**Category**: Universal lens (use when the plan needs official / institutional sources)  
**Trigger**: most research questions; skip for narrow lookups that one primary source answers

---

## Unique Mandate

Gather foundational facts from **broad web coverage**:
- Official documentation
- News articles and blogs
- Company websites
- General web context

**Complementary Design**:
- **Global Observer** uses `broad_web_search` for **broad web coverage**
- **Underground OSINT** uses `community_discussion` for **community discussions**
- **They work TOGETHER** — different data layers, no duplication

---

## Tools & Commands

### Primary: Broad Web Search

```bash
# Launch broad web search across engines
bash ~/.agents/skills/deep-search/scripts/swarm-search.sh "[topic]" general

# For CN-related topics
bash ~/.agents/skills/deep-search/scripts/swarm-search.sh "[topic]" cn

# For news/breaking topics
bash ~/.agents/skills/deep-search/scripts/swarm-search.sh "[topic]" news
```

### Supplementary: Planner-Selected Provider

Use the provider resolved for `broad_web_search`.
Do not assume a host-specific primitive from this file.

---

## Multi-Engine Strategy

| Query Type | Engines to Activate | Why |
|------------|-------------------|-----|
| General/Broad | Google, Bing, DDG, Startpage, Brave | Max coverage |
| CN-related | Baidu, Sogou, Bing CN + 3 international | CN + global view |
| News/Breaking | Google (time filter), Bing News, Yahoo | Fresh content |
| Technical | Google + Bing (site:github.com) | Code sources |

---

## Output Format

```json
{
  "agent": "global-observer",
  "query": "original query",
  "engines_used": ["google", "bing", "ddg", "brave"],
  "results": [
    {
      "title": "...",
      "url": "...",
      "source_type": "official|news|blog|docs",
      "engines_found": ["google", "bing"],
      "confidence": "HIGH|MEDIUM|LOW"
    }
  ],
  "coverage_gaps": ["reddit", "hn", "forums"]
}
```

**Note**: `coverage_gaps` tells Underground OSINT what to focus on.

---

## Quality Standards

- Enough direct evidence for each sub-question (no fixed count; see SKILL.md §3)
- Trace important claims to the responsible first-party source (official docs, filings, regulator notices); one authoritative primary record can be enough
- Several engines returning the same page is one source, not cross-validation
- **Explicitly exclude**: Reddit, HN, Twitter (OSINT handles these)

---

## Collaboration Protocol

After completing research, Global Observer MUST:

1. **Hand off community sources** to Underground OSINT:
   > "Reddit/HN coverage needed for: [topic]"

2. **Mark coverage gaps**:
   > "Missing: User complaints, forum discussions, grassroots opinions"

3. **Provide foundation** for Vertical Enhancers:
   > "Official stance: X | News narrative: Y | Need to verify: Z"

---

## Why Not Replace Underground OSINT?

| Aspect | Global Observer (`broad_web_search`) | Underground OSINT (`community_discussion`) |
|--------|--------------------------------------|----------------------------------|
| **Sources** | Official docs, news, blogs | Reddit, HN, forums, social/community surfaces |
| **Voice** | Institutional, PR, official | Grassroots, complaints, real UX |
| **Use case** | "What they say" | "What users actually experience" |
| **Overlap?** | NO — distinct data layers | NO — distinct data layers |

**Use both when the question involves both official claims and real-world experience.** Neither is required for a narrow factual lookup.

---

## References

- **Search Capability Guide**: @references/tools/multi-search.md
- **Underground OSINT**: @references/vertical-enhancers/underground-osint.md
