# ADA — Autonomous Digital Assistant

**Tagline:** Your intelligence. Everywhere.  
**Version:** 0.1.0 — Engineering Stage A (Foundation)

---

## What is ADA?

ADA is a persistent, multimodal, autonomous personal AI that operates across your Windows computer, Android phone and cloud environment.

It is not a chatbot. It is not a voice assistant. It is not a wrapper around an LLM.

It is a unified intelligent system capable of understanding context, making decisions, coordinating tools, taking action across your devices and maintaining continuity everywhere.

**One intelligence. Every device. Independent action.**

---

## Repository Structure

```
ADA/
├── backend/            # FastAPI + LangGraph cloud service (Python)
│   ├── ada/
│   │   ├── api/        # Versioned API routes
│   │   ├── agents/     # LangGraph orchestrator and agent workflows
│   │   ├── models/     # Pydantic domain models
│   │   ├── providers/  # Model gateway adapters
│   │   ├── memory/     # Memory subsystem
│   │   ├── tasks/      # Task lifecycle management
│   │   ├── devices/    # Device registry and WebSocket manager
│   │   ├── auth/       # Supabase Auth integration
│   │   ├── permissions/# Permission engine
│   │   └── tools/      # Tool registry
│   ├── migrations/     # Supabase SQL migrations
│   ├── tests/
│   ├── pyproject.toml
│   └── Dockerfile
├── desktop/            # Windows companion (PySide6, Python)
│   ├── ada_desktop/
│   │   ├── ui/         # Floating orb, panel, overlay
│   │   ├── runtime/    # Local execution engine
│   │   ├── voice/      # STT / TTS
│   │   ├── screen/     # Capture and annotation
│   │   ├── automation/ # UI Automation + Playwright
│   │   └── sync/       # Cloud WebSocket sync
│   └── tests/
├── android/            # Android companion (Kotlin + Jetpack Compose)
│   └── app/
├── web/                # Web dashboard (React + TypeScript + Vite)
│   └── src/
├── shared/             # OpenAPI contracts and generated types
└── docs/               # Architecture and design documentation
```

---

## Documentation

| Document | Description |
|---|---|
| [PRODUCT_BLUEPRINT.md](PRODUCT_BLUEPRINT.md) | Technical source of truth |
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | System architecture and diagrams |
| [docs/DATABASE_SCHEMA.md](docs/DATABASE_SCHEMA.md) | Full PostgreSQL schema |
| [docs/API_CONTRACTS.md](docs/API_CONTRACTS.md) | REST and WebSocket API design |
| [docs/MODEL_ROUTING.md](docs/MODEL_ROUTING.md) | Adaptive model gateway design |
| [docs/SECURITY.md](docs/SECURITY.md) | Security model and permissions |
| [docs/AGENTS.md](docs/AGENTS.md) | Agent roles and LangGraph workflows |
| [docs/DESKTOP_RUNTIME.md](docs/DESKTOP_RUNTIME.md) | Windows companion architecture |
| [docs/ANDROID_APP.md](docs/ANDROID_APP.md) | Android companion architecture |
| [docs/DESIGN_SYSTEM.md](docs/DESIGN_SYSTEM.md) | Design tokens, components, brand |
| [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) | Render + Supabase deployment |

---

## Technology Stack

| System | Technology |
|---|---|
| Cloud hosting | Render |
| Backend | Python 3.12 + FastAPI |
| Agent orchestration | LangGraph |
| Database | Supabase PostgreSQL + pgvector |
| Authentication | Supabase Auth |
| Desktop UI | PySide6 |
| Browser automation | Playwright |
| Local models | Ollama |
| Android | Kotlin + Jetpack Compose |
| Web | React + TypeScript + Vite + Tailwind |
| Python environment | uv |

---

## Hardware (This Machine)

| Component | Spec |
|---|---|
| RAM | 16 GB |
| GPU | NVIDIA RTX 2050 (4 GB VRAM) + Intel UHD |
| OS | Windows 11 |
| Python | 3.12.10 |
| Node | 24.19.0 |
| Docker | 29.8.2 |
| Ollama | Not installed (needed for Stage F) |

**Local model recommendations for this hardware:**
- `llama3.2:3b` — fits in 4 GB VRAM, general conversation.
- `llama3.2:1b` — ultra-lightweight fallback.
- `nomic-embed-text` — local embeddings (CPU OK).
- Avoid 7B+ parameter models in GPU mode given 4 GB VRAM.

---

## Development Setup

### Prerequisites
- Python 3.12+
- Node 20+
- uv (`pip install uv` or `winget install astral-sh.uv`)
- Docker Desktop
- Supabase CLI (`npm install -g supabase`)

### Backend

```powershell
cd C:\Projects\ADA\backend
uv sync
copy .env.example .env
# Edit .env with your Supabase credentials

# Start local Supabase
supabase start

# Apply migrations
supabase db push

# Start backend
uv run uvicorn ada.main:app --reload --port 8000
```

### Desktop

```powershell
cd C:\Projects\ADA\desktop
uv sync
uv run python -m ada_desktop
```

### Web Dashboard

```powershell
cd C:\Projects\ADA\web
npm install
npm run dev
```

---

## Engineering Stages

| Stage | Status | Description |
|---|---|---|
| **A — Foundation** | 🔄 In Progress | Backend, Supabase, auth, devices, contracts |
| **B — Intelligence Core** | ⬜ Planned | Model gateway, LangGraph, conversations, tasks |
| **C — Desktop Companion** | ⬜ Planned | PySide6, voice, screen, overlay |
| **D — Autonomous Execution** | ⬜ Planned | Tools, permissions, planning, automation |
| **E — Android Companion** | ⬜ Planned | Native Kotlin app |
| **F — Offline & Memory** | ⬜ Planned | Embeddings, Ollama, SQLite queues |
| **G — Web & Integrations** | ⬜ Planned | Dashboard, integrations |
| **H — Production** | ⬜ Planned | Render deploy, packaging, security review |
