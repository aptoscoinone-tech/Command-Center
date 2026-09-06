-- PostgreSQL Schema: M0 - M2.2 Foundation & Observability
-- Target: PostgreSQL 18

CREATE TABLE IF NOT EXISTS tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    task_type VARCHAR(64) NOT NULL,
    status VARCHAR(32) NOT NULL DEFAULT 'PENDING',
    params JSONB NOT NULL DEFAULT '{}',
    result JSONB DEFAULT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    finished_at TIMESTAMPTZ DEFAULT NULL
);

CREATE TABLE IF NOT EXISTS executions (
    execution_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    task_id UUID REFERENCES tasks(id) ON DELETE CASCADE,
    worker_type VARCHAR(64) NOT NULL,
    server_id VARCHAR(64) NOT NULL,
    status VARCHAR(32) NOT NULL DEFAULT 'RUNNING',
    started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    heartbeat_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    finished_at TIMESTAMPTZ DEFAULT NULL,
    cancel_reason TEXT DEFAULT NULL,
    metadata JSONB DEFAULT '{}',
    lease_expires_at TIMESTAMPTZ NOT NULL,
    last_heartbeat_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS server_health (
    server_id VARCHAR(64) PRIMARY KEY,
    status VARCHAR(16) NOT NULL DEFAULT 'UNKNOWN',
    last_check TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_success TIMESTAMPTZ DEFAULT NULL,
    consecutive_failures INT NOT NULL DEFAULT 0,
    details JSONB NOT NULL DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS circuit_breaker (
    server_id VARCHAR(64) PRIMARY KEY,
    state VARCHAR(16) NOT NULL DEFAULT 'CLOSED',
    failures_in_window INT NOT NULL DEFAULT 0,
    window_start TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    opened_at TIMESTAMPTZ DEFAULT NULL,
    half_open_attempts INT NOT NULL DEFAULT 0,
    last_failure_type VARCHAR(32) DEFAULT NULL
);

CREATE TABLE IF NOT EXISTS budgets (
    server_id VARCHAR(64) PRIMARY KEY,
    daily_limit NUMERIC(10, 4) NOT NULL,
    monthly_limit NUMERIC(10, 4) NOT NULL,
    current_usage NUMERIC(10, 4) NOT NULL DEFAULT 0.00
);

CREATE TABLE IF NOT EXISTS audit (
    id BIGSERIAL PRIMARY KEY,
    server_id VARCHAR(64) NOT NULL,
    facts JSONB NOT NULL,
    llm_summary TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
