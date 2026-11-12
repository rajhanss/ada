# ADA — Security Model

**Version:** 0.1.0 | Principle: Security is a core product feature, not an afterthought.

---

## 1. Autonomy Modes

| Mode | Behaviour | Use Case |
|---|---|---|
| **Conversation** | No external actions. Dialogue only. | Sensitive contexts, untrusted input |
| **Assisted** | ADA plans and advises. User executes. | Research, drafting |
| **Supervised Execution** | ADA executes; approval policy applied per risk. | **Default** |
| **Bounded Autonomy** | ADA independently executes pre-approved low-risk tools. | Trusted workflows |

**Default: Supervised Execution.** Users promote to Bounded Autonomy explicitly per tool category.

---

## 2. Permission Categories

| Category | Risk | Default |
|---|---|---|
| Read approved files | Low | Allowed |
| Read approved folders | Low | Allowed |
| Create files in approved workspaces | Medium | Allowed in supervised |
| Modify approved project files | Medium | Requires approval |
| Delete files | High | Always requires approval |
| Run development commands | Medium | Requires approval |
| Run administrative commands | Critical | Always requires approval |
| Control applications | Medium | Requires approval |
| Browser automation (read) | Low | Allowed in supervised |
| Browser automation (write/submit) | High | Requires approval |
| Send messages on behalf of user | High | Always requires approval |
| Make purchases | Critical | Always requires explicit approval |
| Change security settings | Critical | Always requires explicit approval |
| Access screen context | Low | Allowed (explicit capture only) |
| Access mobile capabilities | Varies | Per Android permission model |

---

## 3. The Permission Engine

**Rule: An LLM must NEVER grant itself permissions.**

The permission engine is enforced server-side in Python, outside any LLM call.

```
Tool Call Requested by Agent
         │
         ▼
   Tool Registry lookup (typed schema, known tools only)
         │
         ▼
   Permission Engine check:
   - Is the tool enabled?
   - Does the user have permission for this tool?
   - Is device-scoped permission satisfied?
   - Is the autonomy mode compatible?
   - Does the specific args satisfy allowed_args constraints?
         │
    ┌────┴────┐
    │         │
  DENY      APPROVE
    │         │
    ▼         ▼
  Audit    Approval required?
  event         │
            ┌───┴───┐
            │       │
           YES      NO
            │       │
            ▼       ▼
       Create     Execute
       approval   tool
       record     directly
```

---

## 4. Tool Registry

Every tool is registered with a **typed schema**. Tools not in the registry cannot be called.

```python
class ToolDefinition(BaseModel):
    name: str                     # unique identifier
    category: str                 # 'file','system','browser','code',...
    input_schema: dict            # JSON Schema — all inputs validated before execution
    is_destructive: bool
    is_reversible: bool
    requires_approval_above: RiskLevel  # 'none','low','medium','high','critical','always'
```

---

## 5. Path Validation

All file operations validate the resolved path against user-configured allowed roots.

```python
def resolve_safe_path(path: str, write: bool = False, user_id: str) -> Path:
    target = Path(path).expanduser().resolve()
    allowed = get_allowed_roots(user_id, write=write)
    if not any(is_relative_to(target, root) for root in allowed):
        raise PermissionError(f"Path outside approved workspace: {target}")
    return target
```

No path traversal. No symlink escape. Verified before any I/O.

---

## 6. Command Allowlists

No unrestricted shell endpoint. Terminal commands require:
1. The command executable is on the user-configured allowlist.
2. The specific arguments pass the tool schema validation.
3. Permission engine approves for the current autonomy mode.

Allowlist example (development workstation profile):
```
git, python, uv, npm, npx, cargo, go, gradle, adb
```

Admin commands (e.g. `rm -rf`, `format`, `reg`) are always excluded or require critical-level approval.

---

## 7. Device-Scoped Authorization

Permissions are scoped per `(user_id, device_id)` pair.

- Desktop has file system and automation permissions.
- Mobile has its own mobile-specific permission set.
- A task dispatched from mobile to desktop runs under **desktop device permissions**, not mobile permissions.
- Each device has a `permission_profile` stored in the `devices` table.

---

## 8. Credential Storage

| Secret Type | Storage Method |
|---|---|
| User API keys (providers) | Supabase Vault (encrypted at rest) |
| Device tokens | Hashed in `device_sessions.token_hash`; raw value returned once |
| Supabase service-role key | Backend environment variable only. Never in code, never in client. |
| Supabase anon key | Frontend/clients — read-only operations only via RLS |
| Integration OAuth tokens | Supabase Vault via `integration_credentials.vault_key` |
| Desktop secure storage | Windows Credential Manager (via `keyring` library) |
| Android secure storage | Android Keystore |

Passwords and API keys are **never** stored in the memory system.

---

## 9. Authentication

- **Provider:** Supabase Auth (JWT-based).
- **Session tokens:** Short-lived (1 hour). Refresh tokens rotated on use.
- **Device tokens:** Short-lived (24 hours by default). Rotated on reconnection.
- **WebSocket auth:** `token` query param or `Authorization` header on upgrade. Validated before any message processed.
- **Rate limiting:** Applied at API gateway level. Per-user, per-endpoint limits.
- **Failed auth:** 401 response. No information about why (user vs device vs expired).

---

## 10. Prompt Injection Resistance

External content (web pages, documents, emails, tool results) is **always** treated as untrusted data.

Protections:
- External content is passed as `data`, never as part of system prompts.
- Tool results are validated against expected schema before use.
- LLM outputs that claim to be system instructions are discarded.
- Research content cannot modify tool permissions.
- Agents operate in sandboxed workflows with pre-defined tool access — no dynamic tool registration from LLM output.

---

## 11. Audit

All consequential actions produce an `audit_events` record:
- Tool executed.
- Permission denied.
- Approval granted or denied.
- Device connected or revoked.
- Task created, completed, failed, cancelled.
- Security settings changed.

Audit events are append-only and never deleted (retention period configured per deployment).

---

## 12. Transport Security

- All API communication over HTTPS (TLS 1.2+).
- WebSocket connections over WSS only.
- HSTS enforced on production domains.
- CORS configured to allowed origins only.
- No mixed-content.

---

## 13. Dependency Security

- `uv` lock file committed. No silent upgrades.
- Security audit: `uv pip audit` in CI pipeline.
- Docker base images pinned to specific digest.
- No untrusted third-party MCP servers automatically granted tool access.
