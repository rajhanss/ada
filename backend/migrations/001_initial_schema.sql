-- ADA Database Migration 001 — Initial Schema
-- Apply with: supabase db push
-- Platform: Supabase PostgreSQL

-- ============================================================
-- Extensions
-- ============================================================

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "vector";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- ============================================================
-- profiles
-- ============================================================

CREATE TABLE IF NOT EXISTS profiles (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id         UUID NOT NULL UNIQUE REFERENCES auth.users(id) ON DELETE CASCADE,
    display_name    TEXT,
    avatar_url      TEXT,
    timezone        TEXT DEFAULT 'UTC',
    language        TEXT DEFAULT 'en',
    autonomy_mode   TEXT NOT NULL DEFAULT 'supervised_execution'
                    CHECK (autonomy_mode IN ('conversation','assisted','supervised_execution','bounded_autonomy')),
    preferences     JSONB NOT NULL DEFAULT '{}',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ============================================================
-- devices
-- ============================================================

CREATE TABLE IF NOT EXISTS devices (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id         UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    device_type     TEXT NOT NULL CHECK (device_type IN ('desktop','mobile','web')),
    display_name    TEXT NOT NULL,
    app_version     TEXT,
    platform        TEXT,
    capabilities    JSONB NOT NULL DEFAULT '[]',
    permission_profile JSONB NOT NULL DEFAULT '{}',
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    last_seen_at    TIMESTAMPTZ,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_devices_user_id ON devices(user_id);
CREATE INDEX IF NOT EXISTS idx_devices_active ON devices(user_id, is_active);

-- ============================================================
-- device_sessions
-- ============================================================

CREATE TABLE IF NOT EXISTS device_sessions (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    device_id       UUID NOT NULL REFERENCES devices(id) ON DELETE CASCADE,
    user_id         UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    token_hash      TEXT NOT NULL UNIQUE,
    expires_at      TIMESTAMPTZ NOT NULL,
    revoked_at      TIMESTAMPTZ,
    connection_state TEXT NOT NULL DEFAULT 'disconnected'
                    CHECK (connection_state IN ('connected','disconnected','reconnecting')),
    remote_ip       TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_ping_at    TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_device_sessions_device ON device_sessions(device_id);
CREATE INDEX IF NOT EXISTS idx_device_sessions_expires ON device_sessions(expires_at);

-- ============================================================
-- conversations
-- ============================================================

CREATE TABLE IF NOT EXISTS conversations (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id         UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    device_id       UUID REFERENCES devices(id),
    title           TEXT,
    summary         TEXT,
    is_archived     BOOLEAN NOT NULL DEFAULT FALSE,
    metadata        JSONB NOT NULL DEFAULT '{}',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_conversations_user ON conversations(user_id, created_at DESC);

-- ============================================================
-- messages
-- ============================================================

CREATE TABLE IF NOT EXISTS messages (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    user_id         UUID NOT NULL REFERENCES auth.users(id),
    role            TEXT NOT NULL CHECK (role IN ('user','assistant','system','tool')),
    content         TEXT,
    content_type    TEXT NOT NULL DEFAULT 'text'
                    CHECK (content_type IN ('text','image','audio','tool_call','tool_result')),
    tool_name       TEXT,
    tool_call_id    TEXT,
    metadata        JSONB NOT NULL DEFAULT '{}',
    model_provider  TEXT,
    model_id        TEXT,
    input_tokens    INTEGER,
    output_tokens   INTEGER,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_messages_conversation ON messages(conversation_id, created_at);

-- ============================================================
-- tasks
-- ============================================================

CREATE TABLE IF NOT EXISTS tasks (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id         UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    conversation_id UUID REFERENCES conversations(id),
    device_id       UUID REFERENCES devices(id),
    title           TEXT NOT NULL,
    description     TEXT,
    status          TEXT NOT NULL DEFAULT 'created'
                    CHECK (status IN (
                        'created','planning','pending_approval','queued',
                        'running','paused','verifying','recovering',
                        'succeeded','failed','cancelled'
                    )),
    autonomy_mode   TEXT NOT NULL DEFAULT 'supervised_execution',
    priority        INTEGER NOT NULL DEFAULT 50,
    plan            JSONB,
    current_step_id UUID,
    result          JSONB,
    error           TEXT,
    idempotency_key TEXT UNIQUE,
    parent_task_id  UUID REFERENCES tasks(id),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    started_at      TIMESTAMPTZ,
    completed_at    TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_tasks_user_status ON tasks(user_id, status);
CREATE INDEX IF NOT EXISTS idx_tasks_device ON tasks(device_id, status);

-- ============================================================
-- task_steps
-- ============================================================

CREATE TABLE IF NOT EXISTS task_steps (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    task_id         UUID NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    user_id         UUID NOT NULL REFERENCES auth.users(id),
    step_index      INTEGER NOT NULL,
    agent_role      TEXT NOT NULL,
    description     TEXT NOT NULL,
    status          TEXT NOT NULL DEFAULT 'pending'
                    CHECK (status IN ('pending','running','succeeded','failed','skipped')),
    tool_calls      JSONB NOT NULL DEFAULT '[]',
    result          JSONB,
    error           TEXT,
    started_at      TIMESTAMPTZ,
    completed_at    TIMESTAMPTZ,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_task_steps_task ON task_steps(task_id, step_index);

-- ============================================================
-- task_events
-- ============================================================

CREATE TABLE IF NOT EXISTS task_events (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    task_id         UUID NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    user_id         UUID NOT NULL REFERENCES auth.users(id),
    device_id       UUID REFERENCES devices(id),
    event_type      TEXT NOT NULL,
    payload         JSONB NOT NULL DEFAULT '{}',
    acknowledged    BOOLEAN NOT NULL DEFAULT FALSE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_task_events_task ON task_events(task_id, created_at);
CREATE INDEX IF NOT EXISTS idx_task_events_unacked ON task_events(device_id, acknowledged)
    WHERE NOT acknowledged;

-- ============================================================
-- approvals
-- ============================================================

CREATE TABLE IF NOT EXISTS approvals (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    task_id         UUID NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    user_id         UUID NOT NULL REFERENCES auth.users(id),
    step_id         UUID REFERENCES task_steps(id),
    prompt          TEXT NOT NULL,
    tool_name       TEXT,
    tool_args       JSONB,
    risk_level      TEXT NOT NULL DEFAULT 'medium'
                    CHECK (risk_level IN ('low','medium','high','critical')),
    status          TEXT NOT NULL DEFAULT 'pending'
                    CHECK (status IN ('pending','approved','denied','expired')),
    decision_at     TIMESTAMPTZ,
    expires_at      TIMESTAMPTZ NOT NULL,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_approvals_user_pending ON approvals(user_id, status)
    WHERE status = 'pending';

-- ============================================================
-- memories
-- ============================================================

CREATE TABLE IF NOT EXISTS memories (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id         UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    memory_type     TEXT NOT NULL
                    CHECK (memory_type IN ('profile','episodic','semantic','procedural','working')),
    content         TEXT NOT NULL,
    summary         TEXT,
    importance      FLOAT NOT NULL DEFAULT 0.5 CHECK (importance BETWEEN 0 AND 1),
    confidence      FLOAT NOT NULL DEFAULT 0.8 CHECK (confidence BETWEEN 0 AND 1),
    source          TEXT,
    source_id       UUID,
    tags            TEXT[] NOT NULL DEFAULT '{}',
    is_deleted      BOOLEAN NOT NULL DEFAULT FALSE,
    expires_at      TIMESTAMPTZ,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_memories_user_type ON memories(user_id, memory_type)
    WHERE NOT is_deleted;
CREATE INDEX IF NOT EXISTS idx_memories_tags ON memories USING GIN(tags);

-- ============================================================
-- memory_embeddings
-- ============================================================

CREATE TABLE IF NOT EXISTS memory_embeddings (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    memory_id       UUID NOT NULL UNIQUE REFERENCES memories(id) ON DELETE CASCADE,
    user_id         UUID NOT NULL REFERENCES auth.users(id),
    embedding       vector(768),
    model_id        TEXT NOT NULL,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_memory_embeddings_ivfflat ON memory_embeddings
    USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

-- ============================================================
-- model_providers
-- ============================================================

CREATE TABLE IF NOT EXISTS model_providers (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id         UUID REFERENCES auth.users(id),
    name            TEXT NOT NULL,
    display_name    TEXT NOT NULL,
    base_url        TEXT,
    is_enabled      BOOLEAN NOT NULL DEFAULT TRUE,
    is_local        BOOLEAN NOT NULL DEFAULT FALSE,
    health_status   TEXT NOT NULL DEFAULT 'unknown'
                    CHECK (health_status IN ('healthy','degraded','down','unknown')),
    last_health_check TIMESTAMPTZ,
    config          JSONB NOT NULL DEFAULT '{}',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(user_id, name)
);

-- ============================================================
-- model_registry
-- ============================================================

CREATE TABLE IF NOT EXISTS model_registry (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    provider_id     UUID NOT NULL REFERENCES model_providers(id),
    model_id        TEXT NOT NULL,
    display_name    TEXT NOT NULL,
    capabilities    TEXT[] NOT NULL DEFAULT '{}',
    context_window  INTEGER,
    max_output_tokens INTEGER,
    cost_per_1k_input_tokens  NUMERIC(12,8),
    cost_per_1k_output_tokens NUMERIC(12,8),
    is_enabled      BOOLEAN NOT NULL DEFAULT TRUE,
    is_default_for  TEXT[],
    metadata        JSONB NOT NULL DEFAULT '{}',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(provider_id, model_id)
);

CREATE INDEX IF NOT EXISTS idx_model_registry_caps ON model_registry USING GIN(capabilities);

-- ============================================================
-- model_usage
-- ============================================================

CREATE TABLE IF NOT EXISTS model_usage (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id         UUID NOT NULL REFERENCES auth.users(id),
    task_id         UUID REFERENCES tasks(id),
    conversation_id UUID REFERENCES conversations(id),
    provider_id     UUID NOT NULL REFERENCES model_providers(id),
    model_registry_id UUID NOT NULL REFERENCES model_registry(id),
    request_type    TEXT NOT NULL,
    input_tokens    INTEGER,
    output_tokens   INTEGER,
    estimated_cost_usd NUMERIC(12,8),
    latency_ms      INTEGER,
    was_fallback    BOOLEAN NOT NULL DEFAULT FALSE,
    fallback_from   UUID REFERENCES model_registry(id),
    error           TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_model_usage_user_date ON model_usage(user_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_model_usage_task ON model_usage(task_id);

-- ============================================================
-- tools
-- ============================================================

CREATE TABLE IF NOT EXISTS tools (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name            TEXT NOT NULL UNIQUE,
    display_name    TEXT NOT NULL,
    description     TEXT NOT NULL,
    category        TEXT NOT NULL,
    input_schema    JSONB NOT NULL,
    is_enabled      BOOLEAN NOT NULL DEFAULT TRUE,
    requires_approval_above TEXT DEFAULT 'none'
                    CHECK (requires_approval_above IN ('none','low','medium','high','critical','always')),
    is_destructive  BOOLEAN NOT NULL DEFAULT FALSE,
    is_reversible   BOOLEAN NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ============================================================
-- tool_permissions
-- ============================================================

CREATE TABLE IF NOT EXISTS tool_permissions (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id         UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    device_id       UUID REFERENCES devices(id) ON DELETE CASCADE,
    tool_id         UUID NOT NULL REFERENCES tools(id),
    is_allowed      BOOLEAN NOT NULL DEFAULT FALSE,
    allowed_args    JSONB,
    granted_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    granted_by      TEXT NOT NULL DEFAULT 'user',
    expires_at      TIMESTAMPTZ,
    UNIQUE(user_id, device_id, tool_id)
);

-- ============================================================
-- integrations
-- ============================================================

CREATE TABLE IF NOT EXISTS integrations (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id         UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    service         TEXT NOT NULL,
    display_name    TEXT NOT NULL,
    is_connected    BOOLEAN NOT NULL DEFAULT FALSE,
    scopes          TEXT[] NOT NULL DEFAULT '{}',
    metadata        JSONB NOT NULL DEFAULT '{}',
    connected_at    TIMESTAMPTZ,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(user_id, service)
);

-- ============================================================
-- integration_credentials
-- ============================================================

CREATE TABLE IF NOT EXISTS integration_credentials (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    integration_id  UUID NOT NULL UNIQUE REFERENCES integrations(id) ON DELETE CASCADE,
    vault_key       TEXT NOT NULL,
    token_type      TEXT,
    expires_at      TIMESTAMPTZ,
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ============================================================
-- audit_events
-- ============================================================

CREATE TABLE IF NOT EXISTS audit_events (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id         UUID NOT NULL REFERENCES auth.users(id),
    device_id       UUID REFERENCES devices(id),
    task_id         UUID REFERENCES tasks(id),
    event_type      TEXT NOT NULL,
    actor           TEXT NOT NULL,
    resource_type   TEXT,
    resource_id     TEXT,
    details         JSONB NOT NULL DEFAULT '{}',
    ip_address      INET,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_audit_user_date ON audit_events(user_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_audit_task ON audit_events(task_id);

-- ============================================================
-- Row-Level Security
-- ============================================================

ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE devices ENABLE ROW LEVEL SECURITY;
ALTER TABLE device_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE conversations ENABLE ROW LEVEL SECURITY;
ALTER TABLE messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE tasks ENABLE ROW LEVEL SECURITY;
ALTER TABLE task_steps ENABLE ROW LEVEL SECURITY;
ALTER TABLE task_events ENABLE ROW LEVEL SECURITY;
ALTER TABLE approvals ENABLE ROW LEVEL SECURITY;
ALTER TABLE memories ENABLE ROW LEVEL SECURITY;
ALTER TABLE memory_embeddings ENABLE ROW LEVEL SECURITY;
ALTER TABLE model_providers ENABLE ROW LEVEL SECURITY;
ALTER TABLE model_registry ENABLE ROW LEVEL SECURITY;
ALTER TABLE model_usage ENABLE ROW LEVEL SECURITY;
ALTER TABLE tool_permissions ENABLE ROW LEVEL SECURITY;
ALTER TABLE integrations ENABLE ROW LEVEL SECURITY;
ALTER TABLE integration_credentials ENABLE ROW LEVEL SECURITY;
ALTER TABLE audit_events ENABLE ROW LEVEL SECURITY;

-- Users access only their own data
CREATE POLICY "own_profile"       ON profiles       FOR ALL USING (auth.uid() = user_id);
CREATE POLICY "own_devices"       ON devices        FOR ALL USING (auth.uid() = user_id);
CREATE POLICY "own_sessions"      ON device_sessions FOR ALL USING (auth.uid() = user_id);
CREATE POLICY "own_conversations" ON conversations   FOR ALL USING (auth.uid() = user_id);
CREATE POLICY "own_messages"      ON messages        FOR ALL USING (auth.uid() = user_id);
CREATE POLICY "own_tasks"         ON tasks           FOR ALL USING (auth.uid() = user_id);
CREATE POLICY "own_task_steps"    ON task_steps      FOR ALL USING (auth.uid() = user_id);
CREATE POLICY "own_task_events"   ON task_events     FOR ALL USING (auth.uid() = user_id);
CREATE POLICY "own_approvals"     ON approvals       FOR ALL USING (auth.uid() = user_id);
CREATE POLICY "own_memories"      ON memories        FOR ALL USING (auth.uid() = user_id);
CREATE POLICY "own_embeddings"    ON memory_embeddings FOR ALL USING (auth.uid() = user_id);
CREATE POLICY "own_model_prefs"   ON model_providers  FOR ALL USING (auth.uid() = user_id OR user_id IS NULL);
CREATE POLICY "own_usage"         ON model_usage      FOR ALL USING (auth.uid() = user_id);
CREATE POLICY "own_permissions"   ON tool_permissions FOR ALL USING (auth.uid() = user_id);
CREATE POLICY "own_integrations"  ON integrations     FOR ALL USING (auth.uid() = user_id);
CREATE POLICY "own_credentials"   ON integration_credentials
    FOR ALL USING (
        EXISTS (SELECT 1 FROM integrations WHERE id = integration_id AND user_id = auth.uid())
    );
CREATE POLICY "own_audit"         ON audit_events    FOR SELECT USING (auth.uid() = user_id);
-- audit_events: insert allowed from service role only (backend)
