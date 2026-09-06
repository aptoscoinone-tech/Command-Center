-- PostgreSQL Schema: M2.5 - M6 Capabilities, Approval & Memory
-- Target: PostgreSQL 18

CREATE TABLE IF NOT EXISTS approval_requests (
    request_id VARCHAR(64) PRIMARY KEY,
    capability VARCHAR(128) NOT NULL,
    risk VARCHAR(16) NOT NULL,
    params JSONB NOT NULL DEFAULT '{}',
    initiated_by VARCHAR(64) NOT NULL,
    status VARCHAR(32) NOT NULL DEFAULT 'PENDING',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    expires_at TIMESTAMPTZ NOT NULL,
    resolved_at TIMESTAMPTZ DEFAULT NULL,
    resolved_by VARCHAR(64) DEFAULT NULL
);

CREATE TABLE IF NOT EXISTS memory_facts (
    key VARCHAR(256) PRIMARY KEY,
    fact TEXT NOT NULL,
    metadata JSONB DEFAULT '{}',
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS conversation_history (
    id BIGSERIAL PRIMARY KEY,
    user_id VARCHAR(64) NOT NULL,
    user_message TEXT NOT NULL,
    bot_response TEXT NOT NULL,
    intent VARCHAR(64),
    risk VARCHAR(16),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS alerts_log (
    id VARCHAR(64) PRIMARY KEY,
    severity VARCHAR(16) NOT NULL,
    source VARCHAR(64) NOT NULL,
    message TEXT NOT NULL,
    dedup_key VARCHAR(128) NOT NULL,
    status VARCHAR(16) NOT NULL DEFAULT 'ACTIVE',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    resolved_at TIMESTAMPTZ DEFAULT NULL
);

CREATE INDEX IF NOT EXISTS idx_conversation_user_created ON conversation_history(user_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_alerts_status ON alerts_log(status, severity);
