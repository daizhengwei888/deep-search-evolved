# Claude Code Adapter

This adapter explains how `deep-search` maps onto Claude Code style runtime behavior.

Machine-readable adapter manifest:

- `adapters/claude-code/adapter.json`

## Role

Claude Code is a supported host surface, not the core runtime definition.

The `deep-search` core still lives in:

- `contracts/`
- `config/`
- `scripts/plan-query.py`

This adapter only describes how Claude Code should consume that core.

## Mapping

### Planner

Primary entrypoint:

```bash
python3 scripts/plan-query.py "<query>" --pretty
```

### Execution Surface

Claude Code typically favors:

- shell commands
- local scripts
- tool calls available in the host environment
- staged reasoning over opaque prompt-only orchestration

### Search Execution

Current lowest-level search entrypoint:

```bash
bash scripts/swarm-search.sh --plan /path/to/plan.json
```

### Host Tools And Workers

- Search / fetch: built-in `WebSearch` and `WebFetch`. Prefer them over `scripts/swarm-search.sh`.
- PDFs: the built-in `Read` tool can read PDF pages; local Python extractors are the fallback.
- Workers: the built-in agent / task tool (its exact name and parameters depend on the Claude Code version; read the tool schema). Give each worker a non-overlapping deliverable and ask for evidence records back.
- Workers generally cannot ask the user questions. Clarify in the main conversation before delegating.
- The main session tends to compress long worker reports; keep worker evidence tables intact when synthesizing.

### Capability Mapping

- `broad_web_search` -> `WebSearch` / `WebFetch`, then local search scripts
- `community_discussion` -> community/news skill or fallback web search
- `academic_research` -> academic research skill or fallback broad search
- `code_intelligence` -> repository/code search surfaces or fallback broad search
- `document_processing` -> local extractors or parser tools

## Claude Code Guidance

- Prefer consuming planner output directly rather than re-deciding intent inline
- Prefer reproducible shell/script steps over prompt-only orchestration
- Keep host-specific tool syntax here rather than inside the core runtime contract

## Adapter Rule

If Claude Code introduces host-specific worker or tool syntax, document it here without changing:

- `contracts/runtime-contract.md`
- `contracts/output-contract.md`
- `contracts/evidence-schema.json`
- `config/*.json`
