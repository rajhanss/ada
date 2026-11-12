# ADA — Database Schema

**Version:** 0.1.0 | **Platform:** Supabase PostgreSQL + pgvector  
**All tables use Row-Level Security (RLS). Service-role key never exposed to clients.**

---

## Extensions

```sql
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "vector";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";  -- for memory text search
```

---

## 1. profiles

```sql
CREATE TABLE profiles (
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
```

---

## 2. devices

```sql
CREATE TABLE devices (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id         UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    device_type     TEXT NOT NULL CHECK (device_type IN ('desktop','mobile','web')),
    display_name    TEXT NOT NULL,
    -- display_name is NEVER used as security identity
    app_version     TEXT,
    platform        TEXT,         -- 'windows', 'android', 'web'
    capabilities    JSONB NOT NULL DEFAULT '[]',
    permission_profile JSONB NOT NULL DEFAULT '{}',
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    last_seen_at    TIMESTAMPTZ,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_devices_user_id ON devices(user_id);
CREATE INDEX idx_devices_active ON devices(user_id, is_active);
```

---

## 3. device_sessions

```sql
CREATE TABLE device_sessions (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    device_id       UUID NOT NULL REFERENCES devices(id) ON DELETE CASCADE,
    user_id         UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    -- Hashed token stored; raw token returned only once at creation
    token_hash      TEXT NOT NULL UNIQUE,
    expires_at      TIMESTAMPTZ NOT NULL,
    revoked_at      TIMESTAMPTZ,
    connection_state TEXT NOT NULL DEFAULT 'disconnected'
                    CHECK (connection_state IN ('connected','disconnected','reconnecting')),
    remote_ip       TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_ping_at    TIMESTAMPTZ
);

CREATE INDEX idx_device_sessions_device ON device_sessions(device_id);
CREATE INDEX idx_device_sessions_expires ON device_sessions(expires_at);
```

---

## 4. conversations

```sql
CREATE TABLE conversations (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id         UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    device_id       UUID REFERENCES devices(id),
    title           TEXT,
    summary         TEXT,         -- updated periodically by memory agent
    is_archived     BOOLEAN NOT NULL DEFAULT FALSE,
    metadata        JSONB NOT NULL DEFAULT '{}',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_conversations_user ON conversations(user_id, created_at DESC);
```

---

## 5. messages

```sql
CREATE TABLE messages (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    user_id         UUID NOT NULL REFERENCES auth.users(id),
    role            TEXT NOT NULL CHECK (role IN ('user','assistant','system','tool')),
    content         TEXT,
    content_type    TEXT NOT NULL DEFAULT 'text'
                    CHECK (content_type IN ('text','image','audio','tool_call','tool_result')),
    tool_name       TEXT,         -- set when role='tool'
    tool_call_id    TEXT,
    metadata        JSONB NOT NULL DEFAULT '{}',
    model_provider  TEXT,
    model_id        TEXT,
    input_tokens    INTEGER,
    output_tokens   INTEGER,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_messages_conversation ON messages(conversation_id, created_at);
```

---

## 6. tasks

```sql
CREATE TABLE tasks (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id         UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    conversation_id UUID REFERENCES conversations(id),
    device_id       UUID REFERENCES devices(id),  -- target device for execution
    title           TEXT NOT NULL,
    description     TEXT,
    status          TEXT NOT NULL DEFAULT 'created'
                    CHECK (status IN (
                        'created','planning','pending_approval','queued',
                        'running','paused','verifying','recovering',
                        'succeeded','failed','cancelled'
                    )),
    autonomy_mode   TEXT NOT NULL,
    priority        INTEGER NOT NULL DEFAULT 50,  -- 0 (highest) to 100 (lowest)
    plan            JSONB,            -- LangGraph plan snapshot
    current_step_id UUID,
    result          JSONB,
    error           TEXT,
    idempotency_key TEXT UNIQUE,
    parent_task_id  UUID REFERENCES tasks(id),   -- for sub-tasks
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    started_at      TIMESTAMPTZ,
    completed_at    TIMESTAMPTZ
);

CREATE INDEX idx_tasks_user_status ON tasks(user_id, status);
CREATE INDEX idx_tasks_device ON tasks(device_id, status);
```

---

## 7. task_steps

```sql
CREATE TABLE task_steps (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    task_id         UUID NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    user_id         UUID NOT NULL REFERENCES auth.users(id),
    step_index      INTEGER NOT NULL,
    agent_role      TEXT NOT NULL,   -- 'orchestrator','research','computer','coding', etc.
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

CREATE INDEX idx_task_steps_task ON task_steps(task_id, step_index);
```

---

## 8. task_events

```sql
CREATE TABLE task_events (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    task_id         UUID NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    user_id         UUID NOT NULL REFERENCES auth.users(id),
    device_id       UUID REFERENCES devices(id),
    event_type      TEXT NOT NULL,   -- 'step_started','step_completed','approval_required', etc.
    payload         JSONB NOT NULL DEFAULT '{}',
    acknowledged    BOOLEAN NOT NULL DEFAULT FALSE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_task_events_task ON task_events(task_id, created_at);
CREATE INDEX idx_task_events_unacked ON task_events(device_id, acknowledged) WHERE NOT acknowledged;
```

---

## 9. approvals

```sql
CREATE TABLE approvals (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    task_id         UUID NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    user_id         UUID NOT NULL REFERENCES auth.users(id),
    step_id         UUID REFERENCES task_steps(id),
    prompt          TEXT NOT NULL,   -- human-readable description of what requires approval
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

CREATE INDEX idx_approvals_user_pending ON approvals(user_id, status) WHERE status = 'pending';
```

---

## 10. memories

```sql
CREATE TABLE memories (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id         UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    memory_type     TEXT NOT NULL
                    CHECK (memory_type IN ('profile','episodic','semantic','procedural','working')),
    content         TEXT NOT NULL,
    summary         TEXT,
    importance      FLOAT NOT NULL DEFAULT 0.5 CHECK (importance BETWEEN 0 AND 1),
    confidence      FLOAT NOT NULL DEFAULT 0.8 CHECK (confidence BETWEEN 0 AND 1),
    source          TEXT,          -- 'conversation','task','user_explicit'
    source_id       UUID,          -- conversation_id or task_id
    tags            TEXT[] NOT NULL DEFAULT '{}',
    is_deleted      BOOLEAN NOT NULL DEFAULT FALSE,
    expires_at      TIMESTAMPTZ,   -- NULL = no expiration
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_memories_user_type ON memories(user_id, memory_type) WHERE NOT is_deleted;
CREATE INDEX idx_memories_tags ON memories USING GIN(tags);
```

---

## 11. memory_embeddings

```sql
CREATE TABLE memory_embeddings (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    memory_id       UUID NOT NULL UNIQUE REFERENCES memories(id) ON DELETE CASCADE,
    user_id         UUID NOT NULL REFERENCES auth.users(id),
    embedding       vector(768),    -- 768-dim for text-embedding-004 or equivalent
    model_id        TEXT NOT NULL,  -- embedding model used (consistency constraint)
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- IVFFlat index for approximate nearest-neighbor search
CREATE INDEX idx_memory_embeddings_ivfflat ON memory_embeddings
    USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
```

---

## 12. model_providers

```sql
CREATE TABLE model_providers (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id         UUID REFERENCES auth.users(id),  -- NULL = system default
    name            TEXT NOT NULL,   -- 'gemini','groq','openrouter','ollama'
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
```

---

## 13. model_registry

```sql
CREATE TABLE model_registry (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    provider_id     UUID NOT NULL REFERENCES model_providers(id),
    model_id        TEXT NOT NULL,   -- e.g. 'gemini-2.0-flash'
    display_name    TEXT NOT NULL,
    capabilities    TEXT[] NOT NULL DEFAULT '{}',
    -- capability values: 'chat','vision','function_calling','structured_output',
    --                    'code','embeddings','stt','tts','reasoning'
    context_window  INTEGER,
    max_output_tokens INTEGER,
    cost_per_1k_input_tokens  NUMERIC(12,8),
    cost_per_1k_output_tokens NUMERIC(12,8),
    is_enabled      BOOLEAN NOT NULL DEFAULT TRUE,
    is_default_for  TEXT[],  -- workload types this is default for
    metadata        JSONB NOT NULL DEFAULT '{}',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(provider_id, model_id)
);

CREATE INDEX idx_model_registry_caps ON model_registry USING GIN(capabilities);
```

---

## 14. model_usage

```sql
CREATE TABLE model_usage (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id         UUID NOT NULL REFERENCES auth.users(id),
    task_id         UUID REFERENCES tasks(id),
    conversation_id UUID REFERENCES conversations(id),
    provider_id     UUID NOT NULL REFERENCES model_providers(id),
    model_registry_id UUID NOT NULL REFERENCES model_registry(id),
    request_type    TEXT NOT NULL,   -- 'chat','embed','stt','tts'
    input_tokens    INTEGER,
    output_tokens   INTEGER,
    estimated_cost_usd NUMERIC(12,8),
    latency_ms      INTEGER,
    was_fallback    BOOLEAN NOT NULL DEFAULT FALSE,
    fallback_from   UUID REFERENCES model_registry(id),
    error           TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_model_usage_user_date ON model_usage(user_id, created_at DESC);
CREATE INDEX idx_model_usage_task ON model_usage(task_id);
```

---

## 15. tools

```sql
CREATE TABLE tools (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name            TEXT NOT NULL UNIQUE,
    display_name    TEXT NOT NULL,
    description     TEXT NOT NULL,
    category        TEXT NOT NULL,  -- 'file','system','browser','code','communication','data'
    input_schema    JSONB NOT NULL,  -- JSON Schema for validated inputs
    is_enabled      BOOLEAN NOT NULL DEFAULT TRUE,
    requires_approval_above TEXT DEFAULT 'none'
                    CHECK (requires_approval_above IN ('none','low','medium','high','critical','always')),
    is_destructive  BOOLEAN NOT NULL DEFAULT FALSE,
    is_reversible   BOOLEAN NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

---

## 16. tool_permissions

```sql
CREATE TABLE tool_permissions (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id         UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    device_id       UUID REFERENCES devices(id) ON DELETE CASCADE,
    tool_id         UUID NOT NULL REFERENCES tools(id),
    is_allowed      BOOLEAN NOT NULL DEFAULT FALSE,
    allowed_args    JSONB,       -- partial arg constraints (e.g. allowed paths)
    granted_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    granted_by      TEXT NOT NULL DEFAULT 'user',
    expires_at      TIMESTAMPTZ,
    UNIQUE(user_id, device_id, tool_id)
);
```

---

## 17. integrations

```sql
CREATE TABLE integrations (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id         UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    service         TEXT NOT NULL,   -- 'github','google_calendar','notion', etc.
    display_name    TEXT NOT NULL,
    is_connected    BOOLEAN NOT NULL DEFAULT FALSE,
    scopes          TEXT[] NOT NULL DEFAULT '{}',
    metadata        JSONB NOT NULL DEFAULT '{}',
    connected_at    TIMESTAMPTZ,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(user_id, service)
);
```

---

## 18. integration_credentials

```sql
-- Credentials are stored encrypted at rest via Supabase Vault
-- This table stores references, not plaintext secrets
CREATE TABLE integration_credentials (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    integration_id  UUID NOT NULL UNIQUE REFERENCES integrations(id) ON DELETE CASCADE,
    vault_key       TEXT NOT NULL,    -- Supabase Vault secret reference
    token_type      TEXT,             -- 'oauth2','api_key','basic'
    expires_at      TIMESTAMPTZ,
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

---

## 19. audit_events

```sql
CREATE TABLE audit_events (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id         UUID NOT NULL REFERENCES auth.users(id),
    device_id       UUID REFERENCES devices(id),
    task_id         UUID REFERENCES tasks(id),
    event_type      TEXT NOT NULL,
    -- e.g. 'tool_executed','permission_denied','task_approved','device_connected'
    actor           TEXT NOT NULL,   -- 'user','agent:<role>','system'
    resource_type   TEXT,
    resource_id     TEXT,
    details         JSONB NOT NULL DEFAULT '{}',
    ip_address      INET,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_audit_user_date ON audit_events(user_id, created_at DESC);
CREATE INDEX idx_audit_task ON audit_events(task_id);
-- Audit events are NEVER deleted; retention policy applies at application level
```

---

## Row-Level Security Policies (Template)

```sql
-- Enable RLS on all tables
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE devices ENABLE ROW LEVEL SECURITY;
-- ... (all tables)

-- Users can only access their own data
CREATE POLICY "users_own_profile" ON profiles
    FOR ALL USING (auth.uid() = user_id);

CREATE POLICY "users_own_devices" ON devices
    FOR ALL USING (auth.uid() = user_id);

CREATE POLICY "users_own_conversations" ON conversations
    FOR ALL USING (auth.uid() = user_id);

-- Service role bypasses RLS (backend only — never exposed to clients)
```

---

## Migration Strategy

- Migrations live in `backend/migrations/` as numbered SQL files.
- Applied in order via Supabase CLI: `supabase db push`.
- Each migration is idempotent where practical (`CREATE TABLE IF NOT EXISTS`, `CREATE INDEX IF NOT EXISTS`).
- Destructive migrations require an explicit review gate before deployment.
- Never apply raw SQL in application startup code.
