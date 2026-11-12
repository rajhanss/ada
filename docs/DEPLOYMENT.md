# ADA — Deployment

**Version:** 0.1.0 | Cloud: Render + Supabase

---

## 1. Environment Overview

| Environment | Backend | Database | Purpose |
|---|---|---|---|
| `development` | Local (`uv run uvicorn`) | Local Supabase (`supabase start`) | Daily development |
| `staging` | Render (free/starter tier) | Supabase staging project | Integration testing |
| `production` | Render (paid, always-on) | Supabase production project | Live users |

---

## 2. Cloud Backend (Render)

### Service Configuration

```yaml
# render.yaml
services:
  - type: web
    name: ada-backend
    runtime: docker
    dockerfilePath: ./backend/Dockerfile
    plan: starter          # upgrade to standard for production
    region: singapore      # closest to India
    envVars:
      - key: ENVIRONMENT
        value: production
      - key: SUPABASE_URL
        sync: false        # set in Render dashboard — never in code
      - key: SUPABASE_SERVICE_ROLE_KEY
        sync: false
      - key: SUPABASE_ANON_KEY
        sync: false
      - key: SECRET_KEY
        generateValue: true
      - key: ALLOWED_ORIGINS
        sync: false
    healthCheckPath: /health
    autoDeploy: true       # deploy on push to main
```

### Key Render Rules

- **No durable storage on Render filesystem.** All persistent data goes to Supabase.
- **Free tier sleeps after inactivity.** For production, use a paid always-on plan or implement a keep-alive ping strategy.
- **Logs:** Structured JSON to Render log stream. Never log secrets.
- **Restart policy:** Always restart on failure. Task state is in Supabase, so restarts are safe.

---

## 3. Supabase Configuration

### Projects

| Project | Slug | Purpose |
|---|---|---|
| ada-dev | local | Local development |
| ada-staging | ada-staging | Staging environment |
| ada-prod | ada-prod | Production |

### Services Used

- **PostgreSQL** — primary database (all 19 domain tables).
- **pgvector** — memory embeddings.
- **Auth** — user authentication + JWT.
- **Storage** — uploaded files, screenshots, research artifacts.
- **Vault** — encrypted credential storage for integrations.
- **Realtime** — optional for web dashboard live updates.

### Critical Rules

- **Service-role key:** Backend environment variable only. Never in frontend, mobile, or any client-side code.
- **Anon key:** Frontend/mobile only, relies on RLS to restrict access.
- **RLS:** Enabled on all tables. Tested before every deployment.
- **Migrations:** Applied via `supabase db push` from `backend/migrations/`. Never applied in app startup.
- **Backups:** Supabase Pro includes daily backups. For production: enable PITR (Point-in-Time Recovery).

---

## 4. Docker Configuration

```dockerfile
# backend/Dockerfile
FROM python:3.12-slim

WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Copy dependency files first (layer caching)
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

# Copy application code
COPY ada/ ./ada/

# Non-root user
RUN useradd --create-home appuser
USER appuser

EXPOSE 8000

CMD ["uv", "run", "uvicorn", "ada.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
```

---

## 5. Environment Variables

| Variable | Required | Description |
|---|---|---|
| `ENVIRONMENT` | Yes | `development`, `staging`, `production` |
| `SUPABASE_URL` | Yes | Supabase project URL |
| `SUPABASE_SERVICE_ROLE_KEY` | Yes | Backend-only. Never expose. |
| `SUPABASE_ANON_KEY` | Yes | For client-validated operations |
| `SECRET_KEY` | Yes | JWT signing key (generated, min 32 chars) |
| `ALLOWED_ORIGINS` | Yes | CORS origins (comma-separated) |
| `GEMINI_API_KEY` | Conditional | Required if Gemini provider enabled |
| `GROQ_API_KEY` | Conditional | Required if Groq provider enabled |
| `OPENROUTER_API_KEY` | Conditional | Required if OpenRouter enabled |
| `FCM_SERVER_KEY` | Conditional | Required for push notifications |
| `LOG_LEVEL` | No | Default: `INFO` |
| `MAX_CONNECTIONS` | No | WebSocket connection limit |

No `.env` files in production. All configured in Render dashboard.

---

## 6. Health Checks

```python
# GET /health → 200 OK
{
  "status": "healthy",
  "version": "0.1.0",
  "environment": "production",
  "database": "connected",
  "timestamp": "2026-11-12T07:30:00Z"
}
```

Render pings `/health` every 30 seconds. Unhealthy responses trigger alerts and potential restart.

---

## 7. Observability

| Metric | Method |
|---|---|
| Application errors | Structured logs → Render log stream → alert on ERROR level |
| API latency | Middleware timing headers + logs |
| Model latency | `model_usage.latency_ms` per request |
| Provider failures | Log + `model_usage.error` field |
| Task failures | `tasks.status = 'failed'` count |
| Device connectivity | `device_sessions.connection_state` |
| WebSocket connections | Custom counter in connection manager |

Future: integrate Sentry for error tracking, Grafana for metrics dashboards.

---

## 8. Desktop Update Strategy

```
Desktop app startup
      │
      ▼
Check: GET https://api.ada.app/api/v1/releases/latest
      │
      ▼
Compare local version vs latest
      │
  ┌───┴───┐
  │       │
Current  New version available
  │       │
  └──────►│
          ▼
   Notify user (non-blocking)
   "ADA v0.2.0 is available. Update now?"
          │
      User confirms
          │
          ▼
   Download installer in background
          │
          ▼
   Launch installer on next app restart
```

No silent auto-updates. User controls when updates are applied.

---

## 9. Android Release

| Item | Configuration |
|---|---|
| Build | `./gradlew bundleRelease` |
| Signing | Keystore in CI secrets (never committed) |
| Distribution | Google Play Internal Test → Closed Beta → Production |
| API endpoint | `BuildConfig.API_BASE_URL` per build variant |
| Min SDK | 26 (Android 8.0) |
| Target SDK | Latest stable |

---

## 10. CI/CD Pipeline (GitHub Actions)

```yaml
# On push to main:
1. Run backend tests (pytest)
2. Run type checks (mypy)
3. Run security audit (uv pip audit)
4. Build Docker image
5. Push to Render (auto-deploy via webhook)

# On pull request:
1. Run all tests
2. Run lint (ruff)
3. Check migration compatibility
4. Preview deployment on staging
```
