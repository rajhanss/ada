# ADA — Architecture

**Version:** 0.1.0 | **Stage:** A — Foundation

---

## 1. System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        USER INTERFACES                          │
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │  Windows     │  │   Android    │  │    Web Dashboard     │  │
│  │  Desktop     │  │   Mobile     │  │  React + TypeScript  │  │
│  │  PySide6     │  │  Kotlin+     │  │  Vite + Tailwind     │  │
│  │              │  │  Compose     │  │                      │  │
│  └──────┬───────┘  └──────┬───────┘  └──────────┬───────────┘  │
│         │ WebSocket       │ HTTPS               │ HTTPS         │
│         │ (outbound)      │                     │               │
└─────────┼─────────────────┼─────────────────────┼───────────────┘
          │                 │                     │
          ▼                 ▼                     ▼
┌─────────────────────────────────────────────────────────────────┐
│                   CLOUD BACKEND (Render)                        │
│                   FastAPI + LangGraph                           │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                   API Gateway Layer                      │   │
│  │   /api/v1/*  (HTTPS)  │  /ws/device  (WebSocket)        │   │
│  │   Auth middleware  │  Rate limiting  │  Input validation │   │
│  └───────────────────────────────────────────────────────── ┘   │
│                                                                 │
│  ┌────────────────────┐  ┌─────────────────────────────────┐   │
│  │  Orchestrator      │  │  Model Gateway                  │   │
│  │  (LangGraph)       │  │  - Provider adapters            │   │
│  │  - Intent          │  │  - Capability routing           │   │
│  │  - Planning        │  │  - Fallback                     │   │
│  │  - Delegation      │  │  - Cost tracking                │   │
│  │  - Verification    │  │  - Quota management             │   │
│  └────────────────────┘  └─────────────────────────────────┘   │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                 Domain Services                          │   │
│  │  Conversations │ Tasks │ Devices │ Memory │ Permissions  │   │
│  │  Approvals │ Audit │ Integrations │ Usage                │   │
│  └─────────────────────────────────────────────────────────┘   │
└──────────────────────────────┬──────────────────────────────────┘
                               │
              ┌────────────────┴────────────────┐
              ▼                                 ▼
┌─────────────────────────┐       ┌─────────────────────────┐
│   Supabase PostgreSQL   │       │   Model Providers       │
│   + pgvector            │       │   Gemini │ Groq         │
│   + Auth                │       │   OpenRouter │ Ollama   │
│   + Storage             │       └─────────────────────────┘
└─────────────────────────┘
```

---

## 2. Desktop Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                   Windows Desktop Companion                      │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                     UI Layer (PySide6)                   │   │
│  │  Floating Orb  │  Expanded Panel  │  Screen Overlay     │   │
│  │  Shortcuts (Alt+Space, Ctrl+Shift+Space)                 │   │
│  └──────────────────────────┬──────────────────────────────┘   │
│                             │ Qt signals / slots                │
│  ┌──────────────────────────▼──────────────────────────────┐   │
│  │                 Local Runtime (separate process)         │   │
│  │  Tool Executor │ Screen Capture │ Voice (STT/TTS)       │   │
│  │  UI Automation │ Playwright │ File Ops │ Offline Queue   │   │
│  │  Local SQLite state │ Ollama client                      │   │
│  └──────────────────────────┬──────────────────────────────┘   │
│                             │ Authenticated WebSocket           │
│  ┌──────────────────────────▼──────────────────────────────┐   │
│  │              Cloud Sync / Device Session                 │   │
│  │  Reconnect │ Backoff │ ACK │ Offline queue flush         │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

**Key principles:**
- UI layer contains **zero** business logic.
- Local runtime is a separate process communicating via IPC.
- All tool execution is validated against the permission engine before dispatch.
- Desktop never exposes inbound network ports.

---

## 3. Android Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                   Android Companion                             │
│                                                                 │
│  Screens: Home/Chat │ Voice │ Tasks │ Devices │ Approvals      │
│           Memory │ Settings                                     │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  ViewModel Layer (Kotlin Coroutines + StateFlow)         │   │
│  └──────────────────────────┬──────────────────────────────┘   │
│                             │                                   │
│  ┌──────────────────────────▼──────────────────────────────┐   │
│  │  Repository Layer                                        │   │
│  │  HTTPS API client (Ktor) │ Local Room DB │ Push (FCM)   │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 4. Agent Architecture

```
User Request
     │
     ▼
┌──────────────────────────────────────┐
│          Central Orchestrator        │
│  (LangGraph StateGraph)              │
│  1. Intent classification            │
│  2. Context + memory retrieval       │
│  3. Task classification              │
│  4. Planning (Planner agent)         │
│  5. Permission evaluation            │
│  6. Delegation decision              │
│  7. Execution coordination           │
│  8. Progress monitoring              │
│  9. Verification (Verifier agent)    │
│  10. Memory update                   │
└──────────────────────────────────────┘
     │            │            │
     ▼            ▼            ▼
┌─────────┐ ┌──────────┐ ┌──────────┐
│Research │ │Computer  │ │  Coding  │
│ Agent   │ │  Agent   │ │  Agent   │
└─────────┘ └──────────┘ └──────────┘
     │            │            │
     ▼            ▼            ▼
┌─────────┐ ┌──────────┐ ┌──────────┐
│ System  │ │ Memory   │ │ Analyst  │
│  Agent  │ │  Agent   │ │  Agent   │
└─────────┘ └──────────┘ └──────────┘
```

Agent roles are **LangGraph workflows** sharing the Model Gateway. No separate model deployments.

---

## 5. Task Lifecycle

```
CREATED → PLANNING → PENDING_APPROVAL → QUEUED → RUNNING
                                                     │
                              ┌──────────────────────┤
                              │                      │
                           PAUSED              VERIFYING
                              │                      │
                              └──────────────────────┤
                                                     │
                         ┌───────────────────────────┤
                         │           │               │
                      FAILED    CANCELLED      SUCCEEDED
                         │
                      RECOVERING → QUEUED (retry)
```

Task state is **persisted in Supabase** after every transition. In-memory state is never the source of truth.

---

## 6. Device Communication

```
Device Registration:
  Desktop → POST /api/v1/devices/register → { device_id, device_token }

WebSocket Connection:
  Desktop → WSS /ws/device?token={device_token} → Authenticated session

Heartbeat:
  Desktop → { type: "ping" } every 30s
  Server  → { type: "pong" }

Remote Dispatch:
  Mobile  → POST /api/v1/tasks (creates task for device)
  Server  → { type: "task_dispatch", payload } over device WebSocket
  Desktop → executes task locally
  Desktop → { type: "task_event", task_id, event } over WebSocket
  Server  → updates task state in DB
  Server  → Push notification to mobile (FCM)
```

---

## 7. Model Gateway Flow

```
Agent requests { capability: "vision+reasoning", complexity: "high" }
        │
        ▼
  Constraint filter (required capability must be present)
        │
        ▼
  Rank eligible models (cost × latency × quota × health)
        │
        ▼
  Select model → call provider adapter
        │
        ├─ Success → return response, record usage
        │
        └─ Failure → classify (transient/quota/permanent)
                     │
                     └─ Fallback: select next eligible model
                                  (do NOT replay side-effecting tools)
```

---

## 8. Offline Operation

ADA Desktop stores task state and event queue in SQLite (WAL mode).

On disconnection:
- Locally executable tasks continue via Ollama.
- Cloud-requiring tasks are queued.

On reconnection:
1. Re-authenticate.
2. Upload event queue (idempotent, keyed by event_id).
3. Reconcile task state.
4. Synchronize memory changes.
5. Resume only tasks safe to resume.

---

## 9. Key Architectural Decisions

| Decision | Choice | Reason |
|---|---|---|
| Backend structure | Modular monolith | Avoid premature microservices overhead |
| Primary DB | Supabase PostgreSQL + pgvector | Single store for relational + vector data |
| Task persistence | DB-first (Supabase) | Survive restarts and crashes |
| Local state | SQLite WAL | Fast, offline-capable, no server needed |
| Desktop UI | PySide6 | Native Windows, Python ecosystem, GPU-accelerated |
| Agent orchestration | LangGraph | Explicit state, branching, checkpoints |
| Device auth | Short-lived JWT, device_token rotation | Never expose durable secrets over wire |
| Model selection | Capability-based routing | Agents never hardcode model names |
