# AI Cost Optimization & Observability Implementation

## Overview
This implementation adds comprehensive cost optimization and observability features to the VANTAGE AI platform without changing existing behavior. The system includes Redis caching, budget controls, batch processing, and detailed monitoring.

## Features Implemented

### 1. Redis Caching Layer (`app/cache/redis.py`)
- **Purpose**: Cache AI generation results to reduce costs and latency
- **Key Features**:
  - Namespaced keys with automatic hashing for long keys
  - JSON serialization/deserialization
  - Configurable TTL (default 24 hours)
  - Graceful error handling
- **Usage**: Automatically caches non-personalized content generations

### 2. AI Budget Management (`app/models/ai_budget.py`)
- **Purpose**: Track and limit AI usage per organization
- **Key Features**:
  - Daily token and cost limits
  - Automatic daily reset
  - Usage tracking and reporting
  - Soft limit enforcement (2x multiplier for critical tasks)

### 3. Budget Guard System (`app/ai/budget_guard.py`)
- **Purpose**: Enforce budget limits and route requests appropriately
- **Key Features**:
  - Critical vs non-critical task routing
  - Automatic degradation to open models when over budget
  - Usage statistics and reporting
  - Per-organization budget management

### 4. Enhanced AI Router (`app/ai/enhanced_router.py`)
- **Purpose**: Main orchestrator for AI requests with optimization features
- **Key Features**:
  - Request caching with cache key generation
  - Batch processing for multiple requests
  - Cost tracking and estimation
  - OpenTelemetry instrumentation
  - Budget-aware model selection
  - Token counting and cost calculation

### 5. Provider Adapters (`app/ai/providers/`)
- **Purpose**: Abstract provider capabilities and costs
- **Key Features**:
  - Hosted provider support (OpenAI, Anthropic, Cohere)
  - Open provider support (Ollama, vLLM, TGI)
  - Batch capability detection
  - Cost estimation per provider
  - Task-specific timeout and token limits

### 6. API Endpoints (`app/api/v1/ai_usage.py`)
- **Purpose**: Expose AI usage and budget management via REST API
- **Endpoints**:
  - `GET /api/v1/ai/usage` - Get current usage statistics
  - `GET /api/v1/ai/budget` - Get budget settings
  - `POST /api/v1/ai/budget` - Update budget limits
  - `POST /api/v1/ai/reset-daily` - Reset daily usage counters

### 7. Dev Tools Panel (`web/src/app/(dashboard)/dev/ai-usage/page.tsx`)
- **Purpose**: Visual monitoring of AI usage and costs
- **Key Features**:
  - Real-time usage statistics
  - Budget configuration interface
  - Cost and token usage visualization
  - Daily usage reset functionality
  - Over-limit warnings

### 8. Database Migration (`alembic/versions/0009_ai_budget.py`)
- **Purpose**: Add AI budget tracking table
- **Schema**: `ai_budgets` table with organization-scoped limits and usage tracking

## Configuration

### Environment Variables
```bash
# AI Cost Optimization
REDIS_URL=redis://localhost:6379
AI_CACHE_TTL_SECS=86400
DEV_TOOLS_ENABLED=false
AI_BUDGET_SOFT_LIMIT_MULTIPLIER=2.0
```

### Dependencies Added
- `redis==5.0.1` - Redis client for caching
- `opentelemetry-api==1.20.0` - OpenTelemetry instrumentation
- `opentelemetry-sdk==1.20.0` - OpenTelemetry SDK
- `opentelemetry-instrumentation-redis==0.42b0` - Redis instrumentation
- `opentelemetry-instrumentation-httpx==0.42b0` - HTTP instrumentation

## Usage Examples

### Basic AI Generation with Caching
```python
from app.ai.enhanced_router import EnhancedAIRouter, GenerationRequest

router = EnhancedAIRouter(db_session)

# This will be cached for 24 hours
request = GenerationRequest(
    task="caption",
    prompt="Write a caption about our new product",
    system="You are a social media assistant",
    org_id="org_123"
)

result = await router.generate(request)
print(f"Generated: {result.text}")
print(f"From cache: {result.from_cache}")
print(f"Cost: £{result.cost_gbp}")
```

### Batch Generation
```python
requests = [
    GenerationRequest(task="caption", prompt=f"Caption {i}", org_id="org_123")
    for i in range(5)
]

results = await router.batch_generate(requests)
```

### Budget Management
```python
from app.ai.budget_guard import BudgetGuard

budget_guard = BudgetGuard(db_session)

# Check if can use hosted model
can_use, reason = budget_guard.can_use_hosted_model("org_123", "caption")
print(f"Can use hosted: {can_use}, Reason: {reason}")

# Get usage stats
stats = budget_guard.get_usage_stats("org_123")
print(f"Tokens used: {stats['tokens_used']}/{stats['tokens_limit']}")
```

## Verification

### Testing the Implementation
Run the test script to verify functionality:
```bash
python test_ai_optimization.py
```

### Expected Behavior
1. **Caching**: Identical requests return cached results (faster, no cost)
2. **Budget Control**: Non-critical tasks use open models when over budget
3. **Cost Tracking**: All requests are tracked and costed accurately
4. **Monitoring**: Usage statistics available via API and web UI

### Cache Hit Verification
- Re-running same caption prompt shows cache hit in logs
- No new provider call for identical requests
- Cache hit rate > 50% after repeated requests

### Budget Enforcement
- With tiny org budget, non-critical generations route to open models
- Critical paths (ads copy) still use hosted models unless severely over limit
- Usage statistics show accurate token and cost tracking

## Guardrails

### Non-Breaking Changes
- All existing functionality remains unchanged
- New features are additive only
- No behavioral changes unless limits are exceeded
- Migration is add-only (no data loss)

### Safety Measures
- Critical tasks (ads copy, brand voice) always use hosted models unless severely over budget
- Budget limits are soft (2x multiplier) before blocking critical tasks
- Cache keys exclude personalized content to prevent data leakage
- All costs are estimates (actual costs may vary)

### Performance
- Redis caching reduces latency for repeated requests
- Batch processing reduces overhead for multiple requests
- OpenTelemetry spans provide detailed observability
- Provider capabilities prevent overloading

## Monitoring

### OpenTelemetry Spans
- `ai.generate.{task}` spans with attributes:
  - `ai.task`: Task type (caption, hashtags, etc.)
  - `ai.provider`: Model provider used
  - `ai.org_id`: Organization ID
  - `ai.cache_hit`: Whether result came from cache
  - `ai.tokens_in/out`: Token usage
  - `ai.cost_gbp`: Estimated cost
  - `ai.duration_ms`: Generation time

### Web UI Monitoring
- Access via `/dev/ai-usage` (when `DEV_TOOLS_ENABLED=true`)
- Real-time usage statistics
- Budget configuration
- Cost visualization
- Daily usage reset

### API Monitoring
- Usage statistics via `/api/v1/ai/usage`
- Budget management via `/api/v1/ai/budget`
- Historical usage tracking in database

## Future Enhancements

### Potential Improvements
1. **Advanced Caching**: Semantic similarity caching for similar requests
2. **Cost Optimization**: Dynamic model selection based on cost/quality tradeoffs
3. **Usage Analytics**: Historical usage patterns and predictions
4. **Alerting**: Budget threshold notifications
5. **A/B Testing**: Compare model performance and costs
6. **Rate Limiting**: Per-organization request rate limits

### Scaling Considerations
- Redis clustering for high availability
- Database partitioning for large usage datasets
- Async processing for batch operations
- CDN integration for cached content delivery
