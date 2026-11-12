# ADA — Desktop Runtime

**Version:** 0.1.0 | **Platform:** Windows 11 | **Framework:** PySide6

---

## 1. Architecture Principle

The desktop has **two separate processes:**

```
┌───────────────────────────────┐     IPC (Unix socket / named pipe)
│  UI Process (PySide6)        │◄────────────────────────────────────►│  Runtime Process       │
│  Floating orb                │                                       │  Tool execution        │
│  Expanded panel              │                                       │  Voice (STT/TTS)       │
│  Screen overlay              │                                       │  Screen capture        │
│  Keyboard shortcuts          │                                       │  UI Automation         │
│  Animations                  │                                       │  Playwright            │
│  ZERO business logic         │                                       │  Ollama client         │
└───────────────────────────────┘                                       │  SQLite state          │
                                                                        │  Cloud WebSocket sync  │
                                                                        └────────────────────────┘
```

**UI process:** Presentation only. All user events are forwarded to the runtime.  
**Runtime process:** All execution logic. Never blocks the UI thread.

---

## 2. Floating Presence (UI)

### Visual Design
- Frameless window, `Qt::WindowStaysOnTopHint`.
- Default position: bottom-right corner, 20px margin.
- **Idle state:** Small, unobtrusive orb — ADA brand identity (saffron gradient pulse when active).
- **Expanded state:** Panel slides up from orb. Conversation history, input field, task status.
- **Voice state:** Orb animates to indicate listening / thinking / speaking.
- Smooth transitions using `QPropertyAnimation`.

### Placement
- Configurable: top-left, top-right, bottom-left, bottom-right, or custom position.
- Remembers last position.
- Snaps to screen edges.
- Multi-monitor aware: stays on the monitor where the user is active.

### Themes
- Light and dark mode follow Windows system theme by default.
- Override available in settings.

---

## 3. Keyboard Shortcuts

| Shortcut | Action | Configurable |
|---|---|---|
| `Alt + Space` | Toggle ADA panel | Yes |
| `Ctrl + Shift + Space` | Push-to-talk | Yes |
| `Escape` | Dismiss / collapse | No |
| `Ctrl + Shift + S` | Capture screen for ADA | Yes |

Conflict detection: on startup, check if shortcut is already registered by another process. If conflict found, notify user and fall back to unregistered alternative.

Implementation: `keyboard` library for global hooks (runs in runtime process, forwarded to UI via IPC).

---

## 4. Voice System

### Components
```
Microphone
   │
   ▼
Voice Activity Detection (WebRTC VAD)
   │  (Push-to-talk: active only while key held)
   ▼
Audio buffer
   │
   ▼
STT Adapter
   ├── Online: Groq Whisper API
   └── Offline: Whisper (local via whisper.cpp or faster-whisper)
   │
   ▼
Transcript → Orchestrator
   │
   ▼ (response)
TTS Adapter
   ├── Online: Google Cloud TTS / ElevenLabs / OpenAI TTS
   └── Offline: pyttsx3 / Coqui TTS
   │
   ▼
Audio playback (sounddevice / pygame)
```

### States
- `idle` — no voice activity.
- `listening` — PTT held or VAD active.
- `processing` — STT in progress.
- `thinking` — LLM processing.
- `speaking` — TTS output playing.

UI shows current state via orb animation.

Interruption: user can press PTT during `speaking` to interrupt response.

**Always-on wake-word is NOT a default feature.** Must be explicitly enabled.

---

## 5. Screen Capture & Vision

### Capture Methods
1. **Full screen:** `mss` library — fast, low overhead.
2. **Active window:** Win32 `GetForegroundWindow` + `mss` region crop.
3. **User selection:** Overlay dimmed screen with region selector (like Win+Shift+S).

### Privacy Rules
- Screen capture **only** on explicit user invocation (hotkey or button).
- Visual indicator displayed for 3 seconds when capture occurs.
- No continuous monitoring.
- No background capture.
- Captured images are processed in memory, never auto-saved to cloud without explicit user action.

### Vision Pipeline
```
Screenshot (PIL Image)
   │
   ▼
Pre-process (resize if > 2048px, convert to JPEG for API efficiency)
   │
   ▼
Model Gateway → vision-capable model (e.g. Gemini Flash)
   │
   ▼
Structured understanding:
  - Current application
  - Visible text (key content)
  - Interactive elements
  - Visible errors
  - Workflow context
```

---

## 6. Screen Overlay

A **separate, transparent, always-on-top window** (not part of the main UI).

Purpose: Visual guidance annotations (arrows, highlights, circles, step numbers).

```python
class AnnotationOverlay(QWidget):
    # WA_TranslucentBackground, WindowStaysOnTopHint, FramelessWindowHint
    # Mouse events PASS THROUGH (WA_TransparentForMouseEvents = True)
    # Only active when annotations are displayed
```

Annotations:
- `Arrow(start, end, label)` — directional guidance.
- `Highlight(rect, color)` — region emphasis.
- `Circle(center, radius, label)` — element callout.
- `StepMarker(position, number, text)` — step-by-step walkthrough.

**Overlay is always dismissible** — user can press `Escape` or click a close button at any time.

Overlay content comes from verified agent output only. Raw LLM string output is never directly rendered as executable UI instructions.

---

## 7. Local SQLite State

Path: `%APPDATA%\ADA\local.db`

Schema (local only):
```sql
CREATE TABLE offline_queue (
    id          TEXT PRIMARY KEY,
    event_type  TEXT NOT NULL,
    payload     TEXT NOT NULL,       -- JSON
    created_at  TEXT NOT NULL,
    attempts    INTEGER DEFAULT 0,
    ack_at      TEXT                 -- set when acknowledged by server
);

CREATE TABLE local_tasks (
    task_id     TEXT PRIMARY KEY,
    status      TEXT NOT NULL,
    payload     TEXT NOT NULL,
    updated_at  TEXT NOT NULL
);

CREATE TABLE local_memories (
    id          TEXT PRIMARY KEY,
    content     TEXT NOT NULL,
    created_at  TEXT NOT NULL,
    synced_at   TEXT                 -- NULL until synced to cloud
);

CREATE TABLE settings (
    key         TEXT PRIMARY KEY,
    value       TEXT NOT NULL
);
```

WAL mode enabled. All writes are transactional.

---

## 8. Cloud Synchronization

```python
class DeviceSyncManager:
    async def connect(self):
        # Authenticate → get device_token
        # Open WSS /ws/device?token={device_token}
        # Start heartbeat (30s ping/pong)
        # Start offline queue flusher
    
    async def on_disconnect(self):
        # Exponential backoff: 1s, 2s, 4s, 8s, 16s, 32s, max 60s
        # Queue events locally during outage
    
    async def flush_queue(self):
        # Upload unacked events in order
        # Mark each as acked after server ACK
        # Never replay side-effecting events that may have already executed
    
    async def dispatch_task(self, task_dispatch: TaskDispatch):
        # Received from cloud → route to local execution engine
        # Send task_events back to cloud as execution proceeds
```

---

## 9. Automation Stack

Priority order for desktop automation:

1. **Windows UI Automation (UIA)** — `comtypes` or `pywinauto` for accessibility tree.
2. **Application-specific API** — COM interfaces (Office, Adobe), native APIs.
3. **Playwright** — for browser automation (Chromium, Firefox, Edge).
4. **Screenshot + coordinate** — last resort, with state revalidation before each action.

**Rule:** Never assume a screen coordinate remains valid after a window moves, resizes, or updates. Revalidate before consequential actions.

---

## 10. Packaging (Windows)

| Aspect | Implementation |
|---|---|
| Executable | PyInstaller or Nuitka — single-folder dist |
| Installer | NSIS or Inno Setup |
| Auto-start | Optional Windows startup registry entry |
| Configuration | `%APPDATA%\ADA\config.json` |
| Credentials | Windows Credential Manager (`keyring` library) |
| Logs | `%APPDATA%\ADA\logs\` — structured JSON (rotating, max 50 MB) |
| Crash reporting | Sentry SDK (optional, user consent required) |
| Updates | Background update check via GitHub releases or Render-hosted manifest |
| Uninstall | Clean removal of all app data, registry entries, credentials (with user confirmation) |

No requirement to manually start multiple processes. Launcher starts both UI and runtime.
