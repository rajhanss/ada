# ADA — API Contracts

**Version:** 0.1.0 | **Base path:** `/api/v1` | **Format:** JSON over HTTPS

---

## 1. Conventions

- All timestamps: ISO 8601 UTC (e.g. `"2026-11-12T07:30:00Z"`).
- All IDs: UUIDs (string).
- Error response format:
  ```json
  { "error": { "code": "ERROR_CODE", "message": "Human readable.", "details": {} } }
  ```
- Authentication: `Authorization: Bearer <supabase_jwt>` on all protected endpoints.
- Rate limits: `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset` headers.
- Pagination: `?cursor=<uuid>&limit=<int>` where applicable.

---

## 2. Authentication

| Endpoint | Method | Description |
|---|---|---|
| `/api/v1/auth/signup` | POST | Handled by Supabase Auth SDK on client |
| `/api/v1/auth/login` | POST | Handled by Supabase Auth SDK on client |
| `/api/v1/auth/me` | GET | Returns current user profile |

---

## 3. Devices

```
POST   /api/v1/devices/register
GET    /api/v1/devices
GET    /api/v1/devices/{device_id}
PATCH  /api/v1/devices/{device_id}
DELETE /api/v1/devices/{device_id}      -- revokes and disconnects
POST   /api/v1/devices/{device_id}/pair  -- QR pairing flow initiation
```

**Register Device:**
```json
// Request
{
  "device_type": "desktop",
  "display_name": "Singh's Laptop",
  "platform": "windows",
  "app_version": "0.1.0",
  "capabilities": ["automation", "screen_capture", "voice", "local_models"]
}

// Response 201
{
  "device_id": "uuid",
  "device_token": "short-lived-token",  // returned ONCE; store in secure storage
  "expires_at": "2026-11-13T07:30:00Z"
}
```

---

## 4. WebSocket — Device Session

```
WSS /ws/device?token={device_token}
```

**Message envelope:**
```json
{
  "id": "uuid",          // message ID for ACK
  "type": "event_type",
  "payload": {}
}
```

**Client → Server message types:**
```
ping              → { "type": "ping" }
task_event        → { "task_id": "uuid", "event_type": "step_completed", "payload": {} }
task_result       → { "task_id": "uuid", "result": {}, "status": "succeeded" }
capability_update → { "capabilities": [] }
```

**Server → Client message types:**
```
pong              → { "type": "pong" }
task_dispatch     → { "task_id": "uuid", "plan": {}, "tool_permissions": {} }
task_cancel       → { "task_id": "uuid" }
config_update     → { "settings": {} }
ack               → { "id": "uuid", "status": "ok" }
```

---

## 5. Conversations

```
POST  /api/v1/conversations
GET   /api/v1/conversations
GET   /api/v1/conversations/{id}
PATCH /api/v1/conversations/{id}
DELETE /api/v1/conversations/{id}

POST  /api/v1/conversations/{id}/messages
GET   /api/v1/conversations/{id}/messages
```

**Send Message:**
```json
// Request
{
  "content": "Run my tests",
  "content_type": "text",
  "device_id": "uuid"      // optional — context about which device the user is on
}

// Response 201 — streaming via SSE or single response
{
  "message_id": "uuid",
  "role": "assistant",
  "content": "Running tests on your project...",
  "task_id": "uuid"        // set if a task was created
}
```

---

## 6. Tasks

```
POST  /api/v1/tasks
GET   /api/v1/tasks
GET   /api/v1/tasks/{id}
PATCH /api/v1/tasks/{id}

POST  /api/v1/tasks/{id}/pause
POST  /api/v1/tasks/{id}/resume
POST  /api/v1/tasks/{id}/cancel

GET   /api/v1/tasks/{id}/steps
GET   /api/v1/tasks/{id}/events
```

**Create Task:**
```json
// Request
{
  "title": "Run test suite on Acumen project",
  "device_id": "desktop-device-uuid",
  "conversation_id": "uuid",
  "autonomy_mode": "supervised_execution"
}

// Response 201
{
  "task_id": "uuid",
  "status": "planning",
  "created_at": "..."
}
```

---

## 7. Approvals

```
GET  /api/v1/approvals?status=pending
GET  /api/v1/approvals/{id}
POST /api/v1/approvals/{id}/approve
POST /api/v1/approvals/{id}/deny
```

**Approval object:**
```json
{
  "id": "uuid",
  "task_id": "uuid",
  "prompt": "ADA wants to delete 3 files in ~/Documents/old-project",
  "tool_name": "delete_files",
  "tool_args": { "paths": ["file1.txt", "file2.txt", "file3.txt"] },
  "risk_level": "high",
  "status": "pending",
  "expires_at": "2026-11-12T07:35:00Z"
}
```

---

## 8. Memory

```
GET    /api/v1/memories?type=episodic&query=python+project
POST   /api/v1/memories
GET    /api/v1/memories/{id}
PATCH  /api/v1/memories/{id}
DELETE /api/v1/memories/{id}
```

---

## 9. Model Configuration

```
GET   /api/v1/models/providers
GET   /api/v1/models/registry
GET   /api/v1/models/health
POST  /api/v1/models/providers/{id}/test
GET   /api/v1/models/usage?period=30d
```

---

## 10. Permissions

```
GET   /api/v1/permissions
PATCH /api/v1/permissions/{tool_id}
GET   /api/v1/permissions/devices/{device_id}
```

---

## 11. Health

```
GET /health           → 200 OK — no auth required
GET /api/v1/health    → 200 OK with component status
```

---

## 12. Error Codes

| Code | HTTP | Meaning |
|---|---|---|
| `UNAUTHORIZED` | 401 | Missing or invalid token |
| `FORBIDDEN` | 403 | Authenticated but not permitted |
| `NOT_FOUND` | 404 | Resource does not exist |
| `VALIDATION_ERROR` | 422 | Invalid request body |
| `RATE_LIMITED` | 429 | Too many requests |
| `TASK_CONFLICT` | 409 | Task in incompatible state for requested action |
| `DEVICE_OFFLINE` | 503 | Target device not connected |
| `MODEL_UNAVAILABLE` | 503 | No model satisfies capability requirement |
| `PERMISSION_DENIED` | 403 | Tool permission not granted |
| `APPROVAL_REQUIRED` | 202 | Action queued pending approval |
| `APPROVAL_EXPIRED` | 410 | Approval window passed |
