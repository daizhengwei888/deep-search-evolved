# Codex Adapter

This adapter explains how `deep-search` maps onto Codex-style runtime behavior.

Machine-readable adapter manifest:

- `adapters/codex/adapter.json`

## Role

Codex consumes the same core planning and contract files as any other host.

The platform-specific part is how execution surfaces are expressed:

- shell scripts
- subagents where available
- MCP tools where available
- local file outputs

## Mapping

### Planner

Primary entrypoint:

```bash
python3 scripts/plan-query.py "<query>" --pretty
```

### Search execution

Current lowest-level search entrypoint:

```bash
bash scripts/swarm-search.sh --plan /path/to/plan.json
```

Direct platform-aware execution:

```bash
bash scripts/swarm-search.sh --platform codex "<query>" general
```

### Host tools and workers

- Search: the built-in web search tool when it is enabled for the session; otherwise shell `curl` plus `scripts/swarm-search.sh`.
- Workers: use whatever subagent / parallel mechanism the installed Codex version exposes; if none, run the plan sequentially. Workers return evidence records (JSON) through files or stdout.
- Workers generally cannot ask the user questions. Clarify first.

### Capability mapping

- `broad_web_search` -> host web search, then local search scripts
- `community_discussion` -> platform-accessible news/community skill or fallback search
- `academic_research` -> academic research skill or fallback search
- `code_intelligence` -> local code search / GitHub surface / fallback broad search
- `document_processing` -> local parser or extractor tools

## Codex-Specific Guidance

- Prefer consuming the planner output instead of manually re-deciding intent
- Prefer shell or MCP execution surfaces that can be inspected and replayed
- Keep platform-specific orchestration instructions here rather than in the core runtime contract

## Adapter Rule

If Codex orchestration differs from OpenCode, Hermes, or OpenClaw, document that here without changing the core contracts.
