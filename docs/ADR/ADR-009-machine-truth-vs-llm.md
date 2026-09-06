# ADR-009: Machine Truth ≠ LLM Interpretation

## Status
Accepted

## Context
Command Center manages mission-critical remote servers (PostgreSQL, Nginx, Wireguard, Docker). LLMs are generative models susceptible to hallucinations, rounding inaccuracies, and subtle prompt drift. If an LLM acts as the direct data source, monitoring answers could falsely report healthy servers when services are failing.

## Decision
1. **Machine facts are the sole source of truth:** SSH forced command outputs, system metrics, and PostgreSQL query results are captured as immutable raw facts.
2. **LLM is purely an interpretation and synthesis layer:** LLMs cannot fabricate machine metrics. If an LLM is offline or times out, the system automatically falls back to deterministic rule-based output of raw facts.
3. **Auditing without LLM:** All audit and health operations succeed even when external AI APIs are unreachable.

## Consequences
- Zero hallucinated infrastructure states.
- High resilience during network partitions.
- Machine facts can be validated independently via audit trails.
