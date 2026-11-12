# ADA — Mobile Companion (React Native / Expo)

**Version:** 0.1.0 | **Platform:** Android & iOS  
**Stack:** React Native + TypeScript + Expo + Shared TypeScript Contracts

---

## 1. Architecture

```
React Native UI Layer (Screens: Home, Tasks, Approvals, Devices)
        │
        ▼
Shared Hooks & State (useAdaWebSocket, AuthState)
        │
        ▼
Shared Contracts (types.ts shared across Web & Mobile)
        │
   ┌────┴────┐
   ▼         ▼
REST Client WebSocket Client
(Fetch)    (Native WS)
```

---

## 2. Core Screens

| Screen | Purpose |
|---|---|
| **Home / Conversation** | Primary chat interface, voice input button |
| **Voice** | Full-screen voice interaction mode |
| **Active Tasks** | Live task monitoring, step-by-step progress |
| **Device Management** | Paired devices, connection status |
| **Approvals** | Pending approval requests with approve/deny |
| **Memory** | Inspect and manage ADA's stored memories |
| **Settings** | Account, permissions, model preferences, notifications |

---

## 3. Remote Dispatch Flow

```
User on phone: "Open my project on my laptop and run tests"
         │
         ▼
Android app → POST /api/v1/tasks
{
  "title": "Open project and run tests",
  "device_id": "<desktop_device_id>",
  "conversation_id": "<current_conversation>"
}
         │
         ▼
Cloud backend creates task, dispatches via WebSocket to desktop
         │
         ▼
Desktop executes → sends task_events to cloud
         │
         ▼
Cloud pushes FCM notification to phone: "Step 2/4 — Running test suite"
         │
         ▼
Phone updates task UI: status, current step, progress
         │
         ▼
Completion: FCM notification + in-app result display
```

**Task status displayed on phone:**
- Target device name and connection state
- Task status (planning / running / awaiting approval / succeeded / failed)
- Current step description
- Approval prompts with Approve / Deny buttons
- Error details on failure

---

## 4. Voice Interaction

```
RecordButton (hold) → MediaRecorder → WAV buffer
         │
         ▼
Upload to backend: POST /api/v1/stt
         │
         ▼
Backend → Groq Whisper (or local Whisper if Ollama available)
         │
         ▼
Transcript → Orchestrator → Response text
         │
         ▼
Android TTS (TextToSpeech API) or backend TTS stream
```

For offline voice: on-device Whisper via ML Kit or whisper.android (future).

---

## 5. Android Permissions (Supported APIs Only)

| Capability | Android API | Notes |
|---|---|---|
| Microphone | `RECORD_AUDIO` | Required for voice input |
| Notifications | `POST_NOTIFICATIONS` (Android 13+) | Task updates |
| Internet | `INTERNET` | Always required |
| Camera | `CAMERA` | Optional — for sharing images to ADA |
| File read | `READ_EXTERNAL_STORAGE` / Storage Access Framework | User-initiated only |
| Contacts | `READ_CONTACTS` | Optional integration |
| Notification listener | `NotificationListenerService` | Requires explicit user enable in Settings |

**Explicitly NOT promised:**
- Unrestricted background execution (respects Doze mode).
- Access to other apps' data without user action.
- System-level phone controls without accessibility service user enablement.

The app will never advertise capabilities the OS will not permit.

---

## 6. Local Room Database

```kotlin
@Entity(tableName = "conversations")
data class ConversationEntity(
    @PrimaryKey val id: String,
    val title: String?,
    val updatedAt: Long,
    val syncedAt: Long?
)

@Entity(tableName = "messages")
data class MessageEntity(
    @PrimaryKey val id: String,
    val conversationId: String,
    val role: String,
    val content: String,
    val createdAt: Long,
    val syncedAt: Long?
)

@Entity(tableName = "tasks")
data class TaskEntity(
    @PrimaryKey val id: String,
    val status: String,
    val title: String,
    val deviceId: String?,
    val updatedAt: Long
)
```

---

## 7. Offline Behaviour

| Feature | Offline Behaviour |
|---|---|
| View conversation history | ✅ Available (cached in Room) |
| View task history | ✅ Available (cached) |
| New conversation | ❌ Requires connectivity |
| Voice input | ❌ Requires STT endpoint |
| Remote dispatch | ❌ Requires connectivity |
| Approvals | ❌ Requires connectivity |

Offline state clearly indicated in UI. No silent failures.

---

## 8. Push Notifications (FCM)

Events that trigger push notifications:
- Task started on desktop.
- Task step completed.
- Approval required (high priority).
- Task completed (success or failure).
- Device connected / disconnected.
- Security alert (new device login).

Notification payload structure:
```json
{
  "task_id": "uuid",
  "event_type": "approval_required",
  "title": "ADA needs your approval",
  "body": "Delete 3 files in ~/Documents/old-project?",
  "deep_link": "ada://approvals/uuid"
}
```

Deep links open the relevant screen directly.

---

## 9. Security

- Authentication via Supabase Auth JWT, refreshed automatically.
- Tokens stored in Android Keystore (via EncryptedSharedPreferences).
- Certificate pinning for the ADA API domain.
- Biometric authentication option for app unlock.
- Device pairing uses a QR code flow: desktop displays QR → phone scans → pairing token exchanged over HTTPS.
