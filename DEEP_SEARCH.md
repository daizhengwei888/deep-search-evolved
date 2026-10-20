---
name: deep-search-contract
description: Stable execution contract for deep-search
version: 5.0.0
---

# Deep Search Stable Contract (deep-search 5.0)

## Ownership

This file defines the stable execution contract for `deep-search`.

It owns:
- contract boundaries
- planner-first execution order
- capability and evidence policy authority
- research completion, verification and degraded-mode guarantees
- required user-facing output guarantees

It does not own:
- concrete agent counts
- timeout tuning
- host-specific task syntax
- temporary execution heuristics

Those belong in:
- `DEEP_SEARCH_EXECUTOR.md`
- `adapters/<platform>/README.md`

Strict execution entrypoint:
- `scripts/strict-run.py`

All files in this repository share one version: the `version` in `SKILL.md`.

## Source Of Truth

- `SKILL.md` (behavioral rules: completion gate, output forms, citation verification, degraded mode, conflicts, confidence)
- `contracts/runtime-contract.md`
- `contracts/output-contract.md`
- `contracts/evidence-schema.json`
- `config/query-routing.json`
- `config/execution-profiles.json`
- `config/capability-registry.json`
- `config/evidence-policy.json`
- `scripts/plan-query.py`

If examples elsewhere disagree with these files, these files win.

## Execution Order

1. Normalize the user request and decide the output form (COMPACT / STANDARD / FULL).
2. Build a machine-readable plan with `python3 scripts/plan-query.py "<query>"` when scripts can run.
3. Resolve intent and soft guardrails from `config/query-routing.json` and `config/execution-profiles.json`.
4. Resolve capabilities, host-native tools and fallbacks from `config/capability-registry.json`.
5. Maintain the sub-question ledger; retrieve evidence in priority order (host-native tools → configured APIs → bundled scripts).
6. Normalize and verify evidence per `contracts/evidence-schema.json` and `config/evidence-policy.json`.
7. Stop only when the completion gate in `SKILL.md` §3 is met, or stop because of a limit and report remaining gaps.
8. Synthesize while preserving `contracts/output-contract.md`.

Strict runs must also emit the artifacts defined by `contracts/execution-artifact-schema.json`.

## Planner Contract

Minimum planner outputs:
- `intent`
- `primary_agent`
- `profile`
- `min_sources` (soft guardrail, not a completion condition)
- `min_domains` (soft guardrail, not a completion condition)
- `search_mode`
- `capabilities`
- `evidence_policy`
- `report_contract`
- `output_form_hint`

The planner provides defaults. The executing agent may override intent or output form when the question clearly needs it, and must state why.

## Capability Contract

Core capabilities:
- `broad_web_search`
- `community_discussion`
- `academic_research`
- `code_intelligence`
- `document_processing`

Rules:
- Capability selection comes from `config/capability-registry.json`.
- Host-native tools are preferred when available; bundled scripts are fallbacks.
- Optional external providers must be documented as optional, not assumed.
- When a provider is unavailable, use a declared fallback or report the capability as unavailable. Never simulate success.
- A search-engine result page is a list of candidate links, not evidence.

## Host Boundary

Allowed here: planner entrypoints, config authority, capability rules, output guarantees.

Not allowed here: host-specific worker syntax, platform-only agent categories, fixed agent counts, runtime-specific pseudocode. Those belong in `DEEP_SEARCH_EXECUTOR.md` and `adapters/<platform>/README.md` (claude-code, codex, opencode, zcode, hermes, openclaw).

## Evidence Contract

Evidence handling must preserve:
- provenance (URL or document identity, retrieval time, publication time when available)
- verification status (`FETCHED` / `IDENTITY_VERIFIED` / `SUPPORT_VERIFIED` / `FAILED`)
- evidence independence (repeats of one underlying source count once)
- explicit confidence with a reason when not obvious
- separation between evidence and inference
- limitations and unresolved conflicts

Defined by `contracts/evidence-schema.json` and `config/evidence-policy.json`.

## Required Behavioral Guarantees

Every deep-search run must:
- cite only material actually obtained in this run
- never fabricate URLs, papers, quotes, dates or numbers
- separate direct evidence from inference
- handle conflicts by normalizing definitions and tracing provenance, not by counting sources
- preserve uncertainty instead of hiding it
- degrade honestly when tools fail (see `contracts/runtime-contract.md`)
- use the smallest output form that fully answers the question, without lowering evidence standards

## Vertical Enhancers

Files under `references/vertical-enhancers/` are optional domain lenses. They may suggest search strategy, source classes and review checks. They must not redefine capability authority, assume unavailable providers, override planner routing, or introduce host-specific syntax.

## Recommended Entrypoints

```bash
python3 scripts/plan-query.py "<query>" --platform <host> --pretty
bash scripts/swarm-search.sh --plan /path/to/plan.json
python3 scripts/probe-search.py          # which fallback engines work right now
python3 scripts/strict-run.py "<query>" --platform <host> --output-dir <dir>
```

## Verification Requirements

`scripts/verify-contracts.sh` is the minimum verification surface: required files exist, JSON parses, planner routing samples pass, optional providers are declared, unit tests pass.

## Change Policy

Change this file only when changing stable contract semantics. Runtime strategy belongs in `DEEP_SEARCH_EXECUTOR.md`.
