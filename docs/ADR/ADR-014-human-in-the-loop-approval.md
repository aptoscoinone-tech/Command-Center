# ADR-014: Human-in-the-Loop Interactive Approval (M5)

## Status
Accepted

## Context
Autonomous execution of risky actions (restarting critical databases, applying schema changes, running untrusted code) poses risk to high-availability environments.

## Decision
1. Capabilities tagged with RED risk (or YELLOW when policy configured) cannot execute automatically.
2. The Orchestrator halts execution and generates an `approval_request` with interactive Telegram buttons ([Approve] / [Deny]).
3. A 60-second countdown timer runs; if no authorized operator approves within the window, the request auto-denies safely.
4. Approvals are logged with operator ID and timestamp in the PostgreSQL audit log.
