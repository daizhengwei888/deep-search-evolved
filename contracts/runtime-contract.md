# Deep Search Runtime Contract (deep-search 5.0)

This document defines the platform-neutral runtime semantics for `deep-search`.

The goal is to keep the core skill architecture portable across skill-capable platforms such as Claude Code, Codex, OpenCode, ZCode, Hermes, and OpenClaw.

## Core Principle

The core skill decides:

- what the query means
- which capabilities are needed
- how evidence should be treated
- what the final output form must be (COMPACT / STANDARD / FULL)
- when research is complete, and how to degrade when tools fail

The platform adapter decides:

- how to invoke workers or tools
- how to express parallelism
- how to load platform-local skills or tools
- how to feed execution outputs back into the host system

## Runtime Stages

1. `query_normalization`
2. `plan_generation`
3. `capability_resolution` (including a check of which host-native tools actually work)
4. `provider_selection`
5. `search_execution`
6. `evidence_normalization`
7. `citation_verification`
8. `synthesis`
9. `report_output`

Stages 5–7 repeat until the completion gate in `SKILL.md` §3 holds or a limit is reached.

## Required Planner Output

Any platform adapter must be able to consume a plan with at least:

- `query`
- `intent`
- `primary_agent`
- `profile`
- `min_sources`
- `min_domains`
- `search_mode`
- `capabilities`
- `evidence_policy`
- `report_contract`
- `output_form_hint`
- `host_native_tools`

## Capability Semantics

Capabilities are platform-neutral names:

- `broad_web_search`
- `community_discussion`
- `academic_research`
- `code_intelligence`
- `document_processing`

Platform adapters must map these to platform-local tools, skills, scripts, or MCP surfaces.

Machine-readable provider mapping lives in:

- `config/capability-registry.json` via `platform_providers`
- `config/capability-registry.json` via `platform_fallback_providers`
- `adapters/<platform>/adapter.json`

## Adapter Responsibilities

Each adapter must define:

1. how `parallel workers` are expressed (or that they are unavailable)
2. which host-native search / fetch tools exist and how `providers` are invoked
3. how `missing capabilities` degrade
4. how raw search results are returned to the core evidence layer
5. whether workers can ask the user questions (usually they cannot)

## Degraded / Offline Mode

Before research begins, determine which required capabilities are actually available. If a required retrieval capability fails:

1. Retry only within the bounded retry policy, then record the failure and switch to DEGRADED mode.
2. Never simulate a successful search.
3. Never invent a URL, paper, quotation, publication date or "source" from parametric memory.
4. Treat user-provided files and successfully retrieved documents as the only verifiable evidence in the run.
5. Label statements as `VERIFIED_FROM_AVAILABLE_MATERIAL`, `MODEL_BACKGROUND_UNVERIFIED` or `CANNOT_VERIFY`.
6. For current, volatile, legal, financial, medical or other time-sensitive claims that need unavailable retrieval, say that the current status could not be verified; give the last known dated fact and where to check.
7. Continue useful analysis of available material; return a partial result that says exactly what could and could not be established.
8. Tool failure lowers coverage / completeness. It must not be hidden by lowering source-quality standards.

## What Must Stay Platform-Neutral

These concerns must remain outside adapter-specific docs:

- query routing rules
- execution profiles
- evidence policy
- evidence schema
- output contract

## What May Be Platform-Specific

- worker spawn syntax
- background execution syntax
- local skill loading syntax
- local connector or MCP naming
- host-specific installation commands

## Compatibility Rule

If platform guidance conflicts with:

- `config/query-routing.json`
- `config/capability-registry.json`
- `config/execution-profiles.json`
- `config/evidence-policy.json`
- `contracts/evidence-schema.json`
- `contracts/output-contract.md`

then the core contracts win, and the adapter must be updated.
