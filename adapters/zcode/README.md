# ZCode Adapter

How `deep-search` maps onto ZCode (Z.ai desktop agent). Manifest: `adapters/zcode/adapter.json`.

## Skill packaging rules (from the ZCode Skill docs)

- User-level skills live in `~/.zcode/skills/<skill-name>/SKILL.md`; the folder name is the skill name.
- Frontmatter needs `name` and `description`. **A description over 1024 characters makes ZCode drop the whole skill.** Only about the first 250 characters are injected each turn, so the trigger words come first.
- A `SKILL.md` body over 100 KB is truncated when loaded. `tests/test_skill_package.py` checks both limits.
- Plugin skills must be one level deep (`skills/<name>/SKILL.md`); nested skills such as `deep-search/skills/*` are not discovered as separate skills. deep-search calls them through their scripts instead.

## Tools

- Search / fetch: the built-in `web_search` and `web_fetch` tools (names as reported by ZCode; check the live tool list). Optional Z.ai MCP servers such as `web-search-prime` and `web-reader` can also be configured.
- Prefer these over `scripts/swarm-search.sh`.
- Known local issue (2026-10-19 measurement on the user's Mac): with a proxy in TUN + fake-IP mode, `web_fetch` refused every site because domains resolved to `198.18.0.0/15`. `web_search` still worked. If `web_fetch` reports "resolves to a non-public IP address", fetch pages with shell `curl` or adjust the proxy's fake-IP filter.

## Workers

- ZCode subagents cannot spawn further subagents ("子智能体内不能再派发子智能体"). Keep delegation one level deep.
- Custom subagents live in `~/.zcode/agents/<name>.md`. If a subagent has a custom tool allow-list, every MCP tool it needs must be listed by full name (`mcp__<server>__<tool>`); wildcards are ignored, otherwise MCP tools are unavailable.
- Subagents should not wait for user input; ask clarifying questions in the main conversation first.
- Plan mode (Shift+Tab) is the natural place to show the sub-question ledger when the user wants to approve a plan first.

## Commands

```bash
python3 scripts/plan-query.py "<query>" --platform zcode --pretty
python3 scripts/probe-search.py
python3 scripts/strict-run.py "<query>" --platform zcode --output-dir /tmp/ds-run
```
