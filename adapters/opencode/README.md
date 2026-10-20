# OpenCode Adapter

How `deep-search` maps onto OpenCode. Manifest: `adapters/opencode/adapter.json`.

## Role

OpenCode is one supported host. The core stays platform-neutral; OpenCode syntax lives only here.

## Planner

```bash
python3 scripts/plan-query.py "<query>" --platform opencode --pretty
```

## Search tools

Prefer the built-in `websearch` / `webfetch` tools when they are enabled (see `permission` settings in `opencode.json`). Fall back to `bash scripts/swarm-search.sh --plan plan.json`.

## Parallel workers — check which `task` tool you actually have

Inspect the `task` tool schema before delegating. Two different setups exist:

1. **Plain OpenCode**: `task` takes a `subagent_type` naming one of the configured agents (for example the built-in general-purpose agent). There is no `category` parameter.
2. **OpenCode with the oh-my-opencode / oh-my-openagent plugin**: the plugin's `task` also accepts `category` (e.g. `"quick"`, `"deep"`), `load_skills` and `run_in_background`, with results collected through the plugin's background-output tool. The old deep-search rule "use `category`, never `subagent_type`, or the worker deadlocks" came from this plugin. Follow the plugin's current documentation; it is not a rule for other hosts.

Either way: give each worker a non-overlapping deliverable (see `DEEP_SEARCH_EXECUTOR.md`), and do not expect workers to ask the user questions.

## Provider loading

- `broad_web_search` -> host `websearch`/`webfetch`, then `multi-search-engine` scripts
- `community_discussion` -> `news-aggregator-skill` scripts or site: searches
- `academic_research` -> `academic-deep-research` (autonomous mode) + bibliographic APIs
- `code_intelligence` -> `gh` CLI or fallback search
- `document_processing` -> local extractors

```bash
bash scripts/swarm-search.sh --platform opencode "<query>" general
```

## Adapter Rule

Do not move OpenCode-specific invocation syntax back into `contracts/`, `config/` or `SKILL.md`.
