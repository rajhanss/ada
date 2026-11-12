# ADA — Autonomous Digital Assistant

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/rajhanss/ada)

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
├── mobile/             # Android mobile companion (React Native + Expo + TypeScript)
│   └── src/
├── web/                # Web dashboard & SaaS landing page (React + TypeScript + Vite)
│   ├── public/downloads/ # Direct .exe and .apk store-free distribution packages
│   └── src/
├── shared/             # OpenAPI contracts and generated types
└── docs/               # Architecture and design documentation
```

---

## Documentation

| Document | Description |
|---|---|
| [DEPLOY_AND_RUN.md](DEPLOY_AND_RUN.md) | One-click execution, Render deployment & HeyClicky capabilities |
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
| Backend | Python 3.12 + FastAPI + LangGraph |
| AI Providers | Groq (Qwen3.8-27b), Google Gemini (Gemini 3.8 Flash) |
| Agentic Evals & Tracing | LangSmith (`LANGCHAIN_TRACING_V2`) + AgentObserver |
| Database | Supabase PostgreSQL + pgvector |
| Authentication | Supabase Auth + JWT |
| Desktop UI | PySide6 with Expressive Cybernetic Eyes & Low-Level Computer Use |
| Mobile Companion | React Native + Expo + TypeScript (Store-Free Direct APK) |
| Web Dashboard | React + TypeScript + Vite + Apple-grade Dynamic Island |
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
