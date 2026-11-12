# ADA — Agent Roles & Workflows

**Version:** 0.1.0 | **Orchestration:** LangGraph StateGraph

---

## 1. Central Orchestrator

The orchestrator is the entry point for every user request. It is a LangGraph `StateGraph` with the following node sequence:

```
START
  │
  ▼
classify_intent          → Determine: conversation / research / action / multi-step / approval_needed
  │
  ▼
retrieve_context         → Active tasks, device state, recent conversation
  │
  ▼
retrieve_memory          → Relevant profile / episodic / semantic memories
  │
  ▼
assess_complexity        → Simple (direct response) vs Complex (planning required)
  │
  ├─► SIMPLE ──► direct_response ──► update_working_memory ──► END
  │
  └─► COMPLEX
        │
        ▼
      plan_task            → Planner agent decomposes into steps
        │
        ▼
      evaluate_permissions → Permission engine check (outside LLM)
        │
        ├─► DENIED ──► explain_denial ──► END
        │
        └─► APPROVED (or approval_requested)
              │
              ▼
            delegate       → Select agent role(s), parallelize where safe
              │
              ▼
            execute        → Run agent workflow(s)
              │
              ▼
            verify         → Verifier agent checks outcomes
              │
              ▼
            synthesize     → Compose final response
              │
              ▼
            update_memory  → Memory agent extracts and stores useful facts
              │
              ▼
            END
```

---

## 2. Agent Roles

All roles are **LangGraph workflows** using the Model Gateway. No separate model deployments.

### 2.1 Orchestrator
- **Responsible for:** Intent, context, planning, delegation, synthesis.
- **Model capability:** `chat`, `function_calling`, `structured_output`, `reasoning` (for complex tasks).
- **Tools:** Memory retrieval, context fetching, task creation.

### 2.2 Planner
- **Responsible for:** Decomposing complex tasks into ordered, dependency-aware steps.
- **Model capability:** `chat`, `reasoning`, `function_calling`.
- **Output:** `TaskPlan` — ordered list of `TaskStep` with dependencies.
- **Rule:** Plans are verified against the permission engine before execution begins. Planner never executes.

### 2.3 Research Agent
- **Responsible for:** Web search, source inspection, information synthesis.
- **Model capability:** `chat`, `search`, `reasoning`.
- **Tools:** `web_search`, `fetch_url`, `extract_text`, `save_research_artifact`.
- **Safety:** All retrieved content is treated as untrusted data. Research cannot modify system state.

### 2.4 Computer Agent
- **Responsible for:** Desktop UI interaction, application control, file operations.
- **Model capability:** `chat`, `vision`, `function_calling`.
- **Tools:** `launch_app`, `click_element`, `type_text`, `read_screen`, `capture_screenshot`, `manage_file`.
- **Priority:** UI Automation API → Application-specific API → Playwright → Screenshot+coordinate (last resort).
- **Safety:** Every UI action revalidates state before execution. No stale coordinate assumptions.

### 2.5 Coding Agent
- **Responsible for:** Repository inspection, code editing, test execution, debugging.
- **Model capability:** `chat`, `code`, `function_calling`.
- **Tools:** `read_file`, `write_file`, `run_tests`, `run_command` (allowlisted), `inspect_diff`, `search_codebase`.
- **Rule:** Never claims code works without running relevant tests.

### 2.6 System Agent
- **Responsible for:** Approved local system operations.
- **Model capability:** `chat`, `function_calling`.
- **Tools:** `run_command` (allowlisted only), `manage_process`, `read_system_info`.
- **Safety:** No unrestricted shell. Allowlist enforced in tool registry.

### 2.7 Memory Agent
- **Responsible for:** Memory extraction, organization, retrieval.
- **Model capability:** `chat`, `structured_output`, `embeddings`.
- **Tools:** `search_memories`, `store_memory`, `update_memory`, `delete_memory`.
- **Rule:** Memory extraction is a **separate operation** from conversation. Not every message triggers storage.

### 2.8 Analyst
- **Responsible for:** Data analysis, reporting, structured output.
- **Model capability:** `chat`, `code`, `structured_output`.
- **Tools:** `query_data`, `generate_chart`, `export_report`.

### 2.9 Verifier
- **Responsible for:** Independent outcome verification. Separate from execution.
- **Model capability:** `chat`, `function_calling`.
- **Outputs one of:** `verified_success` | `partial_success` | `unverified` | `failed` | `unknown`.
- **Rule:** A successful tool invocation is NOT automatic proof of success. Verifier inspects actual state.

---

## 3. Verification Examples

| Action | Verification Method |
|---|---|
| File created | Check file exists and size > 0 |
| Code changed | Inspect diff, run test suite |
| Application launched | Check process list or visible window |
| Browser action | Inspect resulting URL/DOM state |
| Task sent to desktop | Receive task_event acknowledgement from device |
| Email sent | Check sent folder or delivery receipt |
| Memory stored | Query retrieval returns the stored content |

---

## 4. LangGraph State Schema

```python
class OrchestratorState(TypedDict):
    # Input
    user_id: str
    conversation_id: str
    device_id: str | None
    messages: list[Message]
    
    # Classified
    intent: IntentClassification | None
    complexity: Literal["simple", "complex"] | None
    
    # Context
    active_tasks: list[Task]
    relevant_memories: list[Memory]
    
    # Planning
    task_plan: TaskPlan | None
    permission_result: PermissionResult | None
    
    # Execution
    delegated_to: list[str]       # agent role names
    step_results: list[StepResult]
    
    # Verification
    verification: VerificationResult | None
    
    # Output
    response: str | None
    task_id: str | None
    new_memories: list[MemoryCandidate]
    
    # Control
    error: str | None
    requires_approval: ApprovalRequest | None
```

---

## 5. Delegation Rules

| Condition | Action |
|---|---|
| Pure question, no action | Direct response — no agent delegation |
| Single-domain task | Delegate to relevant specialist |
| Multi-domain task | Planner decomposes → parallel or sequential execution |
| Task requires device | Queue for target device via WebSocket dispatch |
| Task requires approval | Create approval record, notify user, pause execution |
| Offline mode | Use local-capable agents only; queue cloud tasks |
| Unknown/unsafe request | Explain limitation, do NOT attempt workaround |

---

## 6. Task Persistence

LangGraph checkpoints are stored in Supabase (via `AsyncPostgresSaver`).

This means:
- Tasks survive backend restarts.
- Long-running tasks resume from the last checkpoint.
- Task history is queryable.
- No task state lives only in memory.

Checkpoint table: managed by LangGraph's PostgreSQL checkpoint implementation.
