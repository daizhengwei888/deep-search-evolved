# Search Layer (deep-search 5.0)

## Order of preference

1. **Host-native search and fetch tools** — Claude Code `WebSearch`/`WebFetch`, Codex web search, OpenCode `websearch`/`webfetch`, ZCode `web_search`/`web_fetch` (+ optional Z.ai MCP search). They run through the host's own service and are far more reliable than fetching engines directly.
2. **Configured APIs** — any search API the user has keys for (set up outside this skill), bibliographic APIs for papers (see `references/vertical-enhancers/scholar.md`), the Hacker News Algolia API for HN.
3. **Bundled fallback** — `bash scripts/swarm-search.sh --plan plan.json`, which fetches a few keyless engines and validates every page with `scripts/serp_check.py`.

A search result page is a list of **candidate links**. Open the page and read the relevant passage before citing anything. Several engines returning the same page is still one source.

## Measured status of the 17 keyless engines (2026-10-19, user's Mac, via a proxy)

Two queries per engine ("deep research agent", "新能源车 出口 欧洲 关税"); "works" = at least 3 result titles + links could be parsed.

| Engine | English query | Chinese query | Notes | Status in 5.0 |
|---|---|---|---|---|
| Bing CN (`cn.bing.com`, `ensearch=0`) | ✅ 10 | ✅ 11 | most stable | default (all modes) |
| Qwant | ✅ 5 | ✅ 5 | — | default (general) |
| 360 (`so.com`) | ❌ 2 | ✅ 6 | weak for English | default (cn) |
| Sogou web | ✅/❌ intermittent | ✅ 40 | captcha on repeat requests | default (cn) |
| Toutiao | ✅ 3 | ✅ 3 | captcha markers present | default (cn) |
| Bing INT (`ensearch=1`) | ❌ 0 | ❌ 0 | page fetched but no parseable results | kept in general mode; validator decides |
| DuckDuckGo HTML | ❌ HTTP 202 | ❌ HTTP 202 | anti-bot challenge | replaced by DuckDuckGo Lite (untested) |
| Baidu | ❌ captcha | ❌ captcha | "百度安全验证" | manual only |
| Google / Google HK | ❌ JS redirect shell | ❌ | ~93 KB page with no results | manual only |
| Startpage | ❌ JS gate | ❌ | — | removed from rotation |
| Brave web | ❌ HTTP 429 | ❌ | captcha | removed (Brave's paid API is an option) |
| Yahoo | ❌ HTTP 500 | ❌ | — | removed |
| Ecosia | ❌ HTTP 403 | ❌ | "unusual traffic" | removed |
| WolframAlpha | ❌ captcha | ❌ | not a web search engine | removed |
| WeChat (Sogou) | ❌ JS shell | ❌ | links are short-lived | manual only |
| Jisilu | ❌ 1 | ❌ 1 | a finance forum, not general search | removed |

Re-measure any time: `python3 scripts/probe-search.py` (results depend on network, proxy and time of day).

Background (checked 2026-10): Google Search has required JavaScript since early 2025, which is why plain HTTP fetches get a redirect shell; Microsoft retired the Bing Search APIs on 2025-08-11; Google has announced that the Custom Search JSON API shuts down on 2027-01-01. Commercial search APIs exist (SERP APIs, AI-search APIs, Chinese search APIs); pick one only if the user configures a key — prices and quotas change often, so they are not hard-coded here.

## Useful operators (work in most engines)

| Operator | Example | Meaning |
|---|---|---|
| `site:` | `site:meti.go.jp export control semiconductor` | limit to a domain — best way to reach primary sources |
| `filetype:` | `filetype:pdf implementing regulation` | find official PDFs |
| `"..."` | `"Apache License 2.0"` | exact phrase |
| `-term` | `license -github` | exclude a term |

## Language of sources

Choose languages by topic, not by the language of the question. A Chinese question about Japanese export controls needs Japanese official texts and Japanese / English press, plus Chinese sources for the Chinese side.
