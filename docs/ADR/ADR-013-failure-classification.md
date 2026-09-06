# ADR-013: Four-Way Failure Classification

## Status
Accepted

## Context
Treating every failure identically leads to false circuit breaker trips and operator alert fatigue. A local disk full condition on the control plane should not trip the remote SSH circuit breaker for server apricot.

## Decision
All errors are classified into four distinct classes:
1. **TRANSIENT:** Network blips, SSH connection timeouts, temporary upstream packet loss.
   - *Action:* Increments circuit breaker failure window counter. If threshold exceeded -> trips to OPEN.
2. **SECURITY:** Host key mismatches, unauthorized key access, authentication rejection.
   - *Action:* Immediate high-priority alert. Do NOT count towards transient circuit breaker.
3. **LOCAL_RESOURCE:** CC host OOM, local disk full (10GB VPS threshold), local pool exhaustion.
   - *Action:* Alert admin immediately. Do NOT count towards remote circuit breaker.
4. **POLICY_VIOLATION:** Kill switch blocking operation (e.g. attempting audit in READ_ONLY mode).
   - *Action:* Return explanation to user. Zero circuit breaker impact.
