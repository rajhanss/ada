# ADA — Model Routing

**Version:** 0.1.0 | Principle: Agents request capabilities. The gateway selects models.

---

## 1. Gateway Responsibilities

The Model Gateway is the **only** place where model names appear. Agents never reference providers or model IDs directly.

| Responsibility | Implementation |
|---|---|
| Provider abstraction | Adapter pattern — one class per provider |
| Capability registry | Per-model capability list (see §4) |
| Model selection | Constraint filter → scoring → selection |
| Health monitoring | Periodic ping, latency tracking |
| Quota tracking | Per-user, per-provider usage counters |
| Cost tracking | Input/output tokens × per-model pricing |
| Retry policy | Exponential backoff for transient errors |
| Fallback | Capability-compatible alternative on failure |
| Usage recording | Every call written to `model_usage` table |

---

## 2. Capability Taxonomy

```python
class ModelCapability(str, Enum):
    CHAT              = "chat"           # basic conversation
    VISION            = "vision"         # image/screen understanding
    FUNCTION_CALLING  = "function_calling"
    STRUCTURED_OUTPUT = "structured_output"
    CODE              = "code"           # code generation and analysis
    REASONING         = "reasoning"      # extended chain-of-thought
    EMBEDDINGS        = "embeddings"     # text embedding vectors
    STT               = "stt"            # speech-to-text
    TTS               = "tts"            # text-to-speech
    SEARCH            = "search"         # web search grounding
    LOCAL             = "local"          # runs on-device via Ollama
```

---

## 3. Workload → Capability Mapping

| Workload | Required Capabilities | Preferred Traits |
|---|---|---|
| Simple conversation | `chat` | Low latency, low cost |
| Intent classification | `chat`, `structured_output` | Fastest model |
| Complex planning | `chat`, `reasoning`, `function_calling` | Strongest reasoning |
| Code generation/review | `chat`, `code`, `function_calling` | Code-specialized |
| Screen understanding | `vision`, `chat` | Multimodal |
| Web research | `chat`, `search`, `reasoning` | Search-grounded |
| Memory extraction | `chat`, `structured_output` | Reliable JSON output |
| Summarization | `chat` | Low cost |
| Embedding generation | `embeddings` | Consistent model (never switch mid-collection) |
| Speech recognition | `stt` | Low latency |
| Speech synthesis | `tts` | Natural voice |
| Offline tasks | `local` | Hardware-compatible |

---

## 4. Initial Model Registry

| Provider | Model | Capabilities | Notes |
|---|---|---|---|
| Gemini | gemini-2.0-flash | chat, vision, function_calling, structured_output | Fast, default for most tasks |
| Gemini | gemini-2.0-flash-thinking | chat, reasoning, function_calling | Complex planning |
| Gemini | text-embedding-004 | embeddings | **Fixed for memory collection** |
| Groq | llama-3.3-70b-versatile | chat, function_calling, structured_output | Fast inference |
| Groq | llama-3.1-8b-instant | chat | Ultra-low latency classification |
| Groq | whisper-large-v3-turbo | stt | Speech recognition |
| OpenRouter | anthropic/claude-sonnet | chat, reasoning, code, function_calling | Fallback for complex tasks |
| OpenRouter | (various) | varies | Configured per user |
| Ollama | llama3.2:3b | chat, local | Default offline model |
| Ollama | llama3.2:1b | chat, local | Low-resource offline |
| Ollama | nomic-embed-text | embeddings, local | Local embedding fallback |

---

## 5. Selection Algorithm

```python
def select_model(
    required_capabilities: list[ModelCapability],
    workload: WorkloadType,
    context: SelectionContext,
) -> ModelRegistryEntry:
    
    # Step 1: Hard constraints (MUST pass all)
    candidates = [
        m for m in model_registry.enabled_models()
        if all(cap in m.capabilities for cap in required_capabilities)
        and m.provider.is_healthy()
        and not quota_exceeded(m.provider, context.user_id)
        and (not context.offline_only or ModelCapability.LOCAL in m.capabilities)
        and m.context_window >= context.estimated_tokens
    ]
    
    if not candidates:
        raise ModelUnavailableError(f"No model satisfies: {required_capabilities}")
    
    # Step 2: Score remaining candidates
    scored = [(model, score(model, workload, context)) for model in candidates]
    scored.sort(key=lambda x: x[1], reverse=True)
    
    return scored[0][0]

def score(model, workload, context) -> float:
    # Weighted scoring: capability match, latency, cost, provider health
    capability_score = capability_match_score(model, workload)   # 0-1
    latency_score    = 1 - normalize(model.p50_latency_ms)       # 0-1 (lower=better)
    cost_score       = 1 - normalize(model.estimated_cost)       # 0-1 (lower=better)
    health_score     = model.provider.health_score               # 0-1

    return (
        capability_score * 0.40 +
        latency_score    * 0.25 +
        cost_score       * 0.20 +
        health_score     * 0.15
    )
```

---

## 6. Fallback Policy

```
Model call fails
       │
       ▼
  Classify failure:
  - TRANSIENT (rate limit, timeout, 503) → retry with backoff (max 3)
  - QUOTA_EXCEEDED → skip provider entirely for this session
  - COMPATIBILITY (output format error) → try next candidate
  - PERMANENT (auth failure, model removed) → mark provider degraded
       │
       ▼
  Identify fallback candidate (must satisfy same required_capabilities)
       │
       ▼
  Was the failed call a side-effecting tool operation?
       │
   ┌───┴───┐
  YES      NO
   │        │
   ▼        ▼
  Do NOT   Retry with
  replay   fallback model
  tool call
       │
       ▼
  Record fallback in model_usage (was_fallback=true, fallback_from=original_model_id)
       │
       ▼
  No fallback available → raise ModelUnavailableError → surface to user
```

**Critical rule:** Never blindly replay a tool that may have already executed (file creation, message send, etc.).

---

## 7. Provider Adapters

Each provider implements a common interface:

```python
class BaseModelAdapter(ABC):
    @abstractmethod
    async def chat(self, request: ChatRequest) -> ChatResponse: ...
    
    @abstractmethod
    async def embed(self, texts: list[str]) -> list[list[float]]: ...
    
    @abstractmethod
    async def health_check(self) -> ProviderHealth: ...
    
    @abstractmethod
    def supports_capability(self, cap: ModelCapability) -> bool: ...
```

Implementations: `GeminiAdapter`, `GroqAdapter`, `OpenRouterAdapter`, `OllamaAdapter`.

Provider-specific code (auth headers, response parsing, retry semantics) lives **entirely** inside its adapter. Zero provider-specific code in agent workflows.

---

## 8. Cost Intelligence

```python
class UsageRecord(BaseModel):
    provider: str
    model_id: str
    request_type: str          # 'chat','embed','stt','tts'
    input_tokens: int | None
    output_tokens: int | None
    estimated_cost_usd: Decimal | None
    latency_ms: int
    was_fallback: bool
    error: str | None
    user_id: UUID
    task_id: UUID | None
    conversation_id: UUID | None
```

Every call writes to `model_usage`. Daily/monthly aggregates are queryable for the dashboard.

Budget limits: users can set a soft monthly budget cap per provider. When exceeded, the gateway switches to lower-cost alternatives or surfaces a warning.

---

## 9. Embedding Consistency Rule

> **A vector collection must always use the same embedding model.**

If the embedding model for `memory_embeddings` changes:
1. A new collection is created.
2. All existing memories are re-embedded.
3. The old collection is retired.

Never mix embeddings from different models in the same `ivfflat` index.
