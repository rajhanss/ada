# ADA — Autonomous Digital Assistant
## Deployment, Architecture & Quickstart Guide

---

## 1. Quickstart — Running ADA Locally

ADA can be run in seconds using the one-click launcher batch files in the repository root:

### 1.1 Start the Backend Cloud / Workstation Server
```cmd
start_backend.bat
```
- Starts the FastAPI runtime on `http://localhost:8000`.
- Health check: `http://localhost:8000/health`.
- Interactive API Docs: `http://localhost:8000/docs`.
- Connected to live **Groq** (`qwen/qwen3.8-27b`, ~380ms response) and **Google Gemini** (`gemini-3.8-flash`) with automatic failover and local mock fallback.

### 1.2 Start the React Web Dashboard & SaaS Landing Page
```cmd
start_web.bat
```
- Launches the Vite dev server on `http://localhost:3000`.
- Features the **Apple-grade Dynamic Island** with pupil cursor tracking, scanning visor, and direct workstation actions.
- Includes the SaaS marketing page with direct download links for Windows and Android.
- Click **"Open Assistant"** to switch into the authenticated full-screen management console.

### 1.3 Start the Windows Desktop Companion
```cmd
start_desktop.bat
```
- Or run the pre-built standalone executable at `web/public/downloads/ada-desktop-setup.exe`.
- Launches the native **PySide6 cybernetic floating orb** with expressive animated eyes, pupil tracking, scanning visor, and transparent visual guidance overlay.
- Full computer use engine: mouse clicks, cursor movement, scrolling, typing, and window focus via Windows `user32` ctypes.

### 1.4 Start the React Native Mobile Companion
```cmd
start_mobile.bat
```
- Launches Expo for the React Native companion.
- Run on Android emulator or real phone via Expo Go or direct APK sideloading.

---

## 2. Reverse-Engineering HeyClicky: Core Capabilities

| Capability | HeyClicky Feature | ADA Implementation | Location |
|---|---|---|---|
| **Dynamic Floating Entity** | Floating sphere with reactive eyes | Apple-grade Dynamic Island + Cybernetic Eyes that blink, track mouse cursor, and transform into a scanning visor | `web/src/components/DynamicIsland.tsx`<br>`desktop/ada_desktop/ui/orb.py` |
| **Computer Use** | Autonomous mouse clicks, typing, window focus | Direct Windows `user32` ctypes API: `mouse_click`, `mouse_move`, `mouse_scroll`, `keyboard_type`, `focus_window` | `desktop/ada_desktop/runtime/computer_use.py` |
| **Screen Reading** | Real-time vision-based screen understanding | High-performance `mss` capture + PIL image encoding + Gemini Vision prompt pipeline | `desktop/ada_desktop/screen/capture.py`<br>`backend/ada/providers/gemini.py` |
| **Internet Exploration** | Web search and live page extraction | Search engine crawler + HTML readability extractor (clean text up to 5,000 tokens) | `backend/ada/tools/web_search.py` |
| **Direct Distribution** | Store-free execution for unrestricted OS permissions | Standalone Windows `.exe` and sideloadable Android `.apk` (bypassing Microsoft/Google Play sandboxes) | `web/public/downloads/`<br>`desktop/build_exe.py` |
| **Safety & Autonomy** | Bounded autonomy with explicit confirmation | 5 Autonomy Modes (conversation, assisted, supervised, bounded, autonomous) with risk scoring | `backend/ada/permissions/engine.py` |
| **Observability** | Agentic evals & tracing | LangSmith tracing (`LANGCHAIN_TRACING_V2`) + Run latency, token counts, cost telemetry, and accuracy scoring | `backend/ada/evals/tracer.py` |

---

## 3. Direct Store-Free Distribution

Traditional app store sandboxes (Google Play, Microsoft Store) strictly prohibit applications from:
- Injecting low-level OS mouse and keyboard events.
- Capturing screens in the background.
- Spawning local developer CLI processes (`git`, `pytest`, `npm`).

ADA is distributed directly:
1. **Windows Standalone Executable**:
   - Packaged with PyInstaller into `web/public/downloads/ada-desktop-setup.exe` and portable zip `ada-desktop-windows-x64.zip`.
   - Run `python desktop/build_exe.py` to rebuild anytime.
2. **Android Standalone APK**:
   - Distributed via direct sideloading (`web/public/downloads/ada-mobile.apk`).
   - Run `mobile/build_apk.bat` or `python mobile/package_mobile.py` to package updates.

---

## 4. Live Render Cloud Deployment

ADA Backend is **LIVE IN PRODUCTION** on Render:

- **Live URL**: `https://ada-backend-hpbg.onrender.com`
- **Health Check**: `https://ada-backend-hpbg.onrender.com/health` (`{"status":"healthy","version":"0.1.0","environment":"production"}`)
- **API Health Check**: `https://ada-backend-hpbg.onrender.com/api/v1/health`
- **Dashboard**: [Render Service Dashboard](https://dashboard.render.com/web/srv-dbqqthdbedkc73efic5g)

### Connecting Clients to Render Cloud:
- **Desktop Companion**: Set `ADA_DESKTOP_BACKEND_URL=https://ada-backend-hpbg.onrender.com` in `desktop/.env`.
- **Web Dashboard**: Set `VITE_BACKEND_URL=https://ada-backend-hpbg.onrender.com` in `web/.env`.

---

## 5. Render Blueprint Setup (For Re-deploying)

1. **Push your repository to GitHub**:
   ```bash
   git add .
   git commit -m "feat: ADA autonomous assistant release"
   git push origin main
   ```
2. **Log into Render.com**:
   - Go to [dashboard.render.com](https://dashboard.render.com/).
   - Click **New +** -> **Blueprint**.
   - Connect your GitHub repository containing `render.yaml`.
3. **Configure Environment Variables in Render**:
   - `ADA_GOOGLE_API_KEY`: Your Gemini API key.
   - `ADA_GROQ_API_KEY`: Your Groq API key.
   - `LANGCHAIN_API_KEY` (Optional): Your LangSmith API key for agent telemetry.
   - `ADA_SUPABASE_URL` & `ADA_SUPABASE_SERVICE_ROLE_KEY`: If using Supabase for persistent cloud storage.
4. **Deploy**:
   - Render automatically provisions the Docker container via `backend/Dockerfile` and exposes the API with automatic SSL.

---

## 5. Agentic Evals & Observability

Observability is handled by `AgentObserver` in `backend/ada/evals/tracer.py`:
- Every agent invocation records:
  - `run_id`: Unique trace ID.
  - `latency_ms`: Execution time in milliseconds.
  - `provider` & `model`: Routed LLM (e.g. `groq/qwen3.8-27b`).
  - `token_usage`: Prompt, completion, and total tokens.
  - `cost_usd`: Estimated running cost.
  - `eval_score`: Autonomous verification score (0.0 to 1.0).
- Compatible with **LangSmith** by setting:
  ```env
  LANGCHAIN_TRACING_V2=true
  LANGCHAIN_API_KEY=lsv2_pt_...
  LANGCHAIN_PROJECT=ada-production
  ```
