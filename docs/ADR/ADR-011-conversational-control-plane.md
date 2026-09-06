# ADR-011: Conversational Control Plane with Emergency Slash Escape

## Status
Accepted

## Context
Operators and developers interact primarily via Telegram on mobile devices. Rigid command syntaxes (`/check_server --name apricot --mode verbose`) hinder fast incident response and natural operations.

## Decision
1. **Natural Language Primary:** Free-text messages ("Как дела у apricot?", "Проведи аудит", "Что с дисками?") are parsed by Intent Router.
2. **Slash Commands for Emergency / Debug Only:**
   - `/stop_all`: Triggers EMERGENCY_STOP kill switch instantly.
   - `/resume`: Reverts kill switch to NORMAL.
   - `/read_only`: Enforces safe read-only operations.
   - `/snapshot`, `/health`, `/dashboard`: Rapid debug outputs without natural language roundtrips.

## Consequences
- Operator can ask questions naturally from anywhere.
- Emergency controls are immediate and deterministic with 0ms LLM dependency.
