# ADR-015: Low-Overhead Observability for 1 CPU / 4GB VPS (M6)

## Status
Accepted

## Context
Standard enterprise observability stacks (Prometheus + Grafana + OpenTelemetry collectors) consume upwards of 1.5GB of RAM and significant continuous CPU cycles, leaving insufficient capacity on a single-core VPS with 4GB RAM and 1.5GB free disk.

## Decision
1. **Lightweight In-Process Collector:** Python memory buffers (deque) for latency percentiles (avg, p95) and error counters.
2. **Periodic Snapshots:** Telemetry aggregated at 5-minute intervals.
3. **Multi-Channel Dashboards:**
   - Monospaced ASCII dashboards for immediate `/dashboard` Telegram output.
   - Rich interactive web metrics view for deep visual inspection.
4. **Deduplicated Alerting:** Threshold evaluations with 5-minute sliding deduplication windows to prevent alert storms.
