# ADR-012: Declarative Capability Registry

## Status
Accepted

## Context
Hardcoding capability execution logic inside bot routers leads to tight coupling, making the platform fragile and difficult to port to new infrastructure environments.

## Decision
All capabilities are declared in a centralized `capabilities.yaml` registry with:
- `description`: Human and LLM readable purpose.
- `risk`: GREEN (read-only), YELLOW (compute / non-destructive write), RED (destructive / state mutation).
- `executor`: Concrete class implementing execution contract.
- `input_schema` & `output_schema`: Explicit typed parameters.
- `requires_policy_check`: Enforces Policy Engine gatekeeping.

The Orchestrator dispatches actions purely via registry entries without hardcoding workflow paths.
