"""Database schema initialization."""
from __future__ import annotations

from app.database import db_manager

INVESTIGATIONS_SCHEMA = """
CREATE TABLE IF NOT EXISTS investigations (
    investigation_id UUID PRIMARY KEY,
    tenant_id UUID NOT NULL,
    state VARCHAR(32) NOT NULL DEFAULT 'NEW',
    priority VARCHAR(16) NOT NULL DEFAULT 'LOW',
    confidence_score INTEGER NOT NULL DEFAULT 0,
    confidence_factors JSONB DEFAULT '{}',
    explanation TEXT,
    next_action TEXT,
    related_entities TEXT[],
    missing_evidence JSONB DEFAULT '[]',
    investigation_plan JSONB DEFAULT '[]',
    next_action TEXT DEFAULT 'Collect evidence',
    confidence_history JSONB DEFAULT '[]',
    metadata JSONB NOT NULL,
    state_history JSONB DEFAULT '[]',
    actions JSONB DEFAULT '[]',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_investigations_tenant ON investigations(tenant_id);
CREATE INDEX IF NOT EXISTS idx_investigations_state ON investigations(state);
CREATE INDEX IF NOT EXISTS idx_investigations_correlation ON investigations 
    USING GIN ((metadata->'correlation_ids'));
"""

TIMELINE_EVENTS_SCHEMA = """
CREATE TABLE IF NOT EXISTS timeline_events (
    event_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    investigation_id UUID NOT NULL REFERENCES investigations(investigation_id) ON DELETE CASCADE,
    timestamp TIMESTAMPTZ NOT NULL,
    event_type VARCHAR(64) NOT NULL,
    description TEXT NOT NULL,
    evidence_refs TEXT[],
    source VARCHAR(32) DEFAULT 'deterministic',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_timeline_investigation ON timeline_events(investigation_id);
CREATE INDEX IF NOT EXISTS idx_timeline_timestamp ON timeline_events(timestamp);
"""

STATE_TRANSITIONS_SCHEMA = """
CREATE TABLE IF NOT EXISTS state_transitions (
    id BIGSERIAL PRIMARY KEY,
    investigation_id UUID NOT NULL REFERENCES investigations(investigation_id) ON DELETE CASCADE,
    from_state VARCHAR(32) NOT NULL,
    to_state VARCHAR(32) NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'
);

CREATE INDEX IF NOT EXISTS idx_transitions_investigation ON state_transitions(investigation_id);
"""

HYPOTHESES_SCHEMA = """
CREATE TABLE IF NOT EXISTS hypotheses (
    hypothesis_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    investigation_id UUID NOT NULL REFERENCES investigations(investigation_id) ON DELETE CASCADE,
    pattern_name VARCHAR(255) NOT NULL,
    pattern_version VARCHAR(32),
    confidence INTEGER NOT NULL,
    candidate_ids TEXT[],
    matched_indicators TEXT[],
    missing_indicators TEXT[],
    mitre_mapping JSONB,
    fraud_mapping JSONB,
    explanation JSONB,
    status VARCHAR(16) DEFAULT 'active',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_hypotheses_investigation ON hypotheses(investigation_id);
"""

EVIDENCE_SCHEMA = """
CREATE TABLE IF NOT EXISTS evidence (
    evidence_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    investigation_id UUID NOT NULL REFERENCES investigations(investigation_id) ON DELETE CASCADE,
    evidence_type VARCHAR(64) NOT NULL,
    timestamp TIMESTAMPTZ,
    confidence INTEGER DEFAULT 0,
    properties JSONB DEFAULT '{}',
    source VARCHAR(64) DEFAULT 'unknown',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_evidence_investigation ON evidence(investigation_id);
CREATE INDEX IF NOT EXISTS idx_evidence_type ON evidence(evidence_type);
"""

MISSING_EVIDENCE_SCHEMA = """
CREATE TABLE IF NOT EXISTS missing_evidence (
    id BIGSERIAL PRIMARY KEY,
    investigation_id UUID NOT NULL REFERENCES investigations(investigation_id) ON DELETE CASCADE,
    evidence_type VARCHAR(64) NOT NULL,
    reason TEXT NOT NULL,
    priority VARCHAR(16) DEFAULT 'MEDIUM',
    blocked BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_missing_evidence_investigation ON missing_evidence(investigation_id);
"""

RECOMMENDATIONS_SCHEMA = """
CREATE TABLE IF NOT EXISTS recommendations (
    recommendation_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    investigation_id UUID NOT NULL REFERENCES investigations(investigation_id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    required_evidence TEXT[],
    priority VARCHAR(16) DEFAULT 'MEDIUM',
    source_pattern VARCHAR(255),
    status VARCHAR(16) DEFAULT 'pending',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_recommendations_investigation ON recommendations(investigation_id);
"""

CONFIDENCE_HISTORY_SCHEMA = """
CREATE TABLE IF NOT EXISTS confidence_history (
    id BIGSERIAL PRIMARY KEY,
    investigation_id UUID NOT NULL REFERENCES investigations(investigation_id) ON DELETE CASCADE,
    timestamp TIMESTAMPTZ NOT NULL,
    score INTEGER NOT NULL,
    reason TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_confidence_history_investigation ON confidence_history(investigation_id);
"""

ALL_SCHEMAS = [
    INVESTIGATIONS_SCHEMA,
    TIMELINE_EVENTS_SCHEMA,
    STATE_TRANSITIONS_SCHEMA,
    HYPOTHESES_SCHEMA,
    EVIDENCE_SCHEMA,
    MISSING_EVIDENCE_SCHEMA,
    RECOMMENDATIONS_SCHEMA,
    CONFIDENCE_HISTORY_SCHEMA,
]


async def initialize_database() -> None:
    """Create all tables if they don't exist."""
    from app.database import db_manager
    
    pool = db_manager.pool
    async with pool.acquire() as conn:
        for schema in ALL_SCHEMAS:
            await conn.execute(schema)