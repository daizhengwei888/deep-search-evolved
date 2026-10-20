# Deep Search Executor (deep-search 5.0)

## Ownership

This file is the executor strategy layer. It may change agent allocation, scaling heuristics, timeouts and retry policy. It must not change:

- trigger behavior in `SKILL.md`
- output forms in `contracts/output-contract.md`
- evidence normalization in `contracts/evidence-schema.json`
- evidence weighting and conflict rules in `config/evidence-policy.json`

Host-specific worker syntax lives in `adapters/<platform>/README.md`.

## Loop

```
plan (sub-question ledger)
  → retrieve (host-native search/fetch → configured APIs → bundled scripts)
  → read sources, record evidence (claim + excerpt + verification status)
  → update ledger, pick next action by priority
  → review passes over collected evidence:
       official-source check · community/user view · incentives & bias · contradiction review
  → stop when the completion gate holds, or stop because of a limit
  → write the chosen output form
```

Priority for the next action: missing required coverage → material contradiction → weak support for an important claim → verification of a surprising/high-impact claim → optional enrichment.

## Allocation

Agent count follows the plan, not a fixed number.

| Situation | Suggested effort (heuristic) |
|---|---|
| Narrow factual lookup | 1 agent, a few targeted searches |
| Direct comparison on a few criteria | 1 agent, or about 2–4 parallel workers if the axes are independent |
| Broad research with many independent sub-questions | more workers only when each has a non-overlapping deliverable |

Each delegated task states: objective, scope and exclusions, expected evidence, output format, boundaries with other workers, completion condition. Workers return evidence records (`contracts/evidence-schema.json`), not polished prose. The orchestrator keeps worker evidence tables intact when synthesizing.

Workers cannot reliably ask the user questions. Clarify before delegating.

## Retrieval Policy

- Prefer host-native search and fetch tools (listed per host in `config/capability-registry.json` → `host_native_tools`).
- Use `scripts/swarm-search.sh` only as a fallback. It validates each result page and marks captcha pages, redirect shells and empty pages as failures; only `valid` engines count.
- Search-engine coverage is not source independence. One page found by several engines is one source.
- Bounded retries: retry a failed call at most twice, then record the failure and continue in degraded mode.

## Tunables

| Setting | Default | Where |
|---|---|---|
| Network timeout per request | 15–30 s | `DS_CONNECT_TIMEOUT`, `DS_MAX_TIME` for `swarm-search.sh` |
| Results directory | `/tmp/omo-deep-search` | `DS_RESULTS_ROOT` |
| Marginal-gain stop | about 2 targeted rounds without material gain | judgment, not a contract number |
| Soft source alert | fewer than `min_sources` independent sources on open, complex questions | `config/execution-profiles.json` |

## Strict Lane

`scripts/strict-run.py` runs planner → contract check → fallback search → community fetch → artifact synthesis. It records real result domains and parsed result counts, writes deviations, and marks stages `partial` when deviations exist. Its report describes search-layer coverage only; it does not verify claims, so its confidence never exceeds MEDIUM.
