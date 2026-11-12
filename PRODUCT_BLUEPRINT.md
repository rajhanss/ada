# ADA — Product Blueprint
## Autonomous Digital Assistant | Technical Source of Truth

**Version:** 0.1.0  
**Status:** Foundation — Engineering Stage A  
**Last updated:** 2026-11-12

---

## 1. What ADA Is

ADA is a persistent, multimodal, autonomous personal AI that operates across:

- **Windows Desktop** — primary execution environment
- **Android Mobile** — portable command interface
- **Web Dashboard** — management and monitoring workspace
- **Cloud Intelligence** — persistent coordination and intelligence layer

These are interfaces to **one shared intelligence**, not independent assistants.

**Tagline:** Your intelligence. Everywhere.  
**Philosophy:** One intelligence. Every device. Independent action.

---

## 2. What ADA Is Not

- Not a chatbot wrapper around an LLM.
- Not a voice assistant.
- Not a collection of disconnected agents.
- Not a browser automation script.
- Not a remote-control application.
- Not a model-switching interface.

---

## 3. The Central Interaction Loop

```
Understand → Contextualize → Plan → Authorize → Execute → Verify → Remember
```

ADA must close the loop between user intention and verified outcome.

---

## 4. Core Capability Domains

| Domain | Description |
|---|---|
| Conversation Intelligence | Natural language, voice, text, continuity, memory |
| Screen Intelligence | Explicit screen capture, OCR, accessibility metadata |
| Visual Guidance | Transparent overlay: arrows, highlights, step indicators |
| Computer Intelligence | UI Automation, file ops, app control, browser automation |
| Research Intelligence | Web search, source inspection, structured findings |
| Coding Intelligence | Repo inspection, code editing, test execution |
| Task Intelligence | Full lifecycle: create → plan → execute → verify → history |
| Proactive Intelligence | Configurable alerts, task monitoring, approval reminders |

---

## 5. Autonomy Modes

| Mode | Description |
|---|---|
| **Conversation** | No external actions. Pure dialogue. |
| **Assisted** | ADA prepares plans and instructions only. |
| **Supervised Execution** | ADA executes; approval policy is enforced. **(Default)** |
| **Bounded Autonomy** | ADA independently performs explicitly permitted low-risk tasks. |

---

## 6. Technology Constitution

| System | Technology |
|---|---|
| Cloud hosting | Render |
| Backend | Python 3.12 + FastAPI |
| Validation | Pydantic v2 |
| Agent orchestration | LangGraph |
| Database | Supabase PostgreSQL + pgvector |
| Authentication | Supabase Auth |
| Storage | Supabase Storage |
| Desktop UI | PySide6 |
| Desktop automation | Windows UI Automation (comtypes/pywinauto) |
| Browser automation | Playwright |
| Local state | SQLite (WAL mode) |
| Local models | Ollama |
| Android | Kotlin + Jetpack Compose |
| Web | React + TypeScript + Vite + Tailwind CSS |
| Contracts | OpenAPI 3.1 |
| Python environment | uv |
| Containers | Docker |
| Version control | GitHub |

**Architecture rule:** Modular monolith for the cloud backend. No premature microservices.

---

## 7. Memory Categories

1. **Profile memory** — User identity, preferences, working style.
2. **Episodic memory** — Past interactions and completed tasks.
3. **Semantic memory** — Domain knowledge and learned facts.
4. **Procedural memory** — Workflow patterns and tool sequences.
5. **Working memory** — Active conversation and task context.

Storage: Supabase PostgreSQL with pgvector. Never store credentials in memory.

---

## 8. Model Providers (Initial)

- Google Gemini
- Groq
- OpenRouter
- Ollama (local)

Agents request **capabilities**, not hardcoded model names. The gateway selects.

---

## 9. Device Communication Pattern

```
Mobile / Web  →  HTTPS API  →  Cloud Backend
Desktop       →  WebSocket (outbound, authenticated)  →  Cloud Backend
Cloud         →  Push Notification  →  Mobile
```

Desktop never exposes inbound public ports. All connections are outbound from devices.

---

## 10. Security Principles

- Least privilege.
- Permission enforcement **outside** the LLM — LLMs never grant themselves permissions.
- Typed tool registry with allowlists.
- Path validation on all file operations.
- Database row-level security (Supabase RLS).
- Short-lived tokens, credential rotation, device revocation.
- Never expose service-role keys to clients.
- Treat all external content (web pages, documents, tool results) as untrusted data.

---

## 11. Engineering Stages

| Stage | Focus |
|---|---|
| **A — Foundation** | Monorepo, FastAPI, Supabase, auth, devices, contracts, tests |
| **B — Intelligence Core** | Model gateway, LangGraph, conversations, task lifecycle, memory |
| **C — Desktop Companion** | PySide6, floating UI, voice, screen, overlay, local runtime |
| **D — Autonomous Execution** | Tool registry, permissions, planning, browser/file/coding tools |
| **E — Android Companion** | Native app, voice, remote dispatch, approvals |
| **F — Offline & Memory** | Persistent memory, embeddings, Ollama, SQLite queues, sync |
| **G — Web & Integrations** | Dashboard, device mgmt, model config, usage, integrations |
| **H — Production** | Render deploy, monitoring, packaging, security review, polish |

---

## 12. Definition of Done

A feature is complete when it:
1. Works as intended.
2. Has been tested (unit + integration where applicable).
3. Has an honest implementation status.
4. Has updated documentation.

No placeholder implementations. No claimed completions without verification.
