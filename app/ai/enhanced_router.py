from __future__ import annotations

import json
import hashlib
import time
from typing import Optional, Any, List, Dict, Tuple
from dataclasses import dataclass
from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode

from app.cache.redis import cache
from app.ai.budget_guard import BudgetGuard
from app.services.model_router import ModelRouter, AIRouter
from app.core.config import get_settings


@dataclass
class GenerationRequest:
    task: str
    prompt: str
    system: Optional[str] = None
    org_id: Optional[str] = None
    is_critical: bool = False
    model_preference: Optional[str] = None


@dataclass
class GenerationResult:
    text: str
    provider: str
    tokens_in: int
    tokens_out: int
    cost_gbp: float
    from_cache: bool = False
    duration_ms: int = 0


class EnhancedAIRouter:
    def __init__(self, db_session=None) -> None:
        self.model_router = ModelRouter()
        self.ai_router = AIRouter()
        self.settings = get_settings()
        self.budget_guard = BudgetGuard(db_session) if db_session else None
        self.tracer = trace.get_tracer(__name__)

    def _estimate_tokens(self, text: str) -> int:
        """Rough token estimation (4 chars per token average)."""
        return len(text) // 4

    def _estimate_cost(self, provider: str, tokens_in: int, tokens_out: int) -> float:
        """Estimate cost in GBP based on provider and token usage."""
        # Rough cost estimates per 1K tokens
        costs = {
            "openai:gpt-4o-mini": {"input": 0.00015, "output": 0.0006},  # USD converted to GBP
            "openai:gpt-4o": {"input": 0.005, "output": 0.015},
            "ollama:llama3.1": {"input": 0.0, "output": 0.0},  # Free local model
            "open": {"input": 0.0001, "output": 0.0001},  # Generic open model
        }
        
        provider_costs = costs.get(provider, costs["open"])
        input_cost = (tokens_in / 1000) * provider_costs["input"]
        output_cost = (tokens_out / 1000) * provider_costs["output"]
        return input_cost + output_cost

    def _make_cache_key(self, request: GenerationRequest) -> str:
        """Create cache key for request."""
        # Don't cache personalized content (when org_id affects output)
        if request.org_id and request.is_critical:
            return None
        
        key_data = f"{request.task}:{request.prompt}:{request.system or ''}"
        return f"ai:{request.task}:{hashlib.sha256(key_data.encode()).hexdigest()[:16]}"

    async def _get_from_cache(self, cache_key: str) -> Optional[GenerationResult]:
        """Get result from cache if available."""
        if not cache_key:
            return None
        
        cached_data = await cache.get("ai_generation", cache_key)
        if cached_data:
            return GenerationResult(**cached_data)
        return None

    async def _save_to_cache(self, cache_key: str, result: GenerationResult) -> None:
        """Save result to cache."""
        if not cache_key:
            return
        
        cache_data = {
            "text": result.text,
            "provider": result.provider,
            "tokens_in": result.tokens_out,
            "tokens_out": result.tokens_out,
            "cost_gbp": result.cost_gbp,
            "from_cache": True,
            "duration_ms": result.duration_ms
        }
        await cache.set("ai_generation", cache_key, cache_data)

    async def _generate_single(self, request: GenerationRequest) -> GenerationResult:
        """Generate single result using appropriate model."""
        start_time = time.time()
        
        # Check budget constraints
        if self.budget_guard and request.org_id:
            can_use_hosted, reason = self.budget_guard.can_use_hosted_model(
                request.org_id, request.task
            )
            
            if not can_use_hosted and not request.is_critical:
                # Use open model for non-critical tasks when over budget
                provider = "open"
                text = await self.ai_router._open_complete(request.system, request.prompt)
            else:
                # Use hosted model
                provider = self.settings.model_router_primary or "openai:gpt-4o-mini"
                text = await self.model_router.complete(request.prompt, request.system)
        else:
            # No budget guard - use default routing
            provider = self.settings.model_router_primary or "openai:gpt-4o-mini"
            text = await self.model_router.complete(request.prompt, request.system)

        duration_ms = int((time.time() - start_time) * 1000)
        
        # Estimate tokens and cost
        tokens_in = self._estimate_tokens(f"{request.system or ''}\n{request.prompt}")
        tokens_out = self._estimate_tokens(text)
        cost_gbp = self._estimate_cost(provider, tokens_in, tokens_out)
        
        result = GenerationResult(
            text=text,
            provider=provider,
            tokens_in=tokens_in,
            tokens_out=tokens_out,
            cost_gbp=cost_gbp,
            duration_ms=duration_ms
        )
        
        # Record usage for budget tracking
        if self.budget_guard and request.org_id:
            self.budget_guard.record_usage(request.org_id, tokens_in + tokens_out, cost_gbp)
        
        return result

    async def generate(self, request: GenerationRequest) -> GenerationResult:
        """Generate content with caching and budget awareness."""
        with self.tracer.start_as_current_span(f"ai.generate.{request.task}") as span:
            span.set_attributes({
                "ai.task": request.task,
                "ai.provider": request.model_preference or "auto",
                "ai.org_id": request.org_id or "none",
                "ai.is_critical": request.is_critical
            })
            
            # Try cache first
            cache_key = self._make_cache_key(request)
            if cache_key:
                cached_result = await self._get_from_cache(cache_key)
                if cached_result:
                    span.set_attributes({
                        "ai.cache_hit": True,
                        "ai.duration_ms": cached_result.duration_ms
                    })
                    return cached_result
            
            # Generate new content
            result = await self._generate_single(request)
            
            # Save to cache
            if cache_key:
                await self._save_to_cache(cache_key, result)
            
            span.set_attributes({
                "ai.cache_hit": False,
                "ai.provider": result.provider,
                "ai.tokens_in": result.tokens_in,
                "ai.tokens_out": result.tokens_out,
                "ai.cost_gbp": result.cost_gbp,
                "ai.duration_ms": result.duration_ms
            })
            
            if result.duration_ms > 10000:  # > 10 seconds
                span.set_status(Status(StatusCode.ERROR, "Slow generation"))
            
            return result

    async def batch_generate(self, requests: List[GenerationRequest]) -> List[GenerationResult]:
        """Generate multiple requests in batch when possible."""
        if len(requests) > 8:
            # Split large batches
            results = []
            for i in range(0, len(requests), 8):
                batch = requests[i:i+8]
                batch_results = await self._process_batch(batch)
                results.extend(batch_results)
            return results
        
        return await self._process_batch(requests)

    async def _process_batch(self, requests: List[GenerationRequest]) -> List[GenerationResult]:
        """Process a batch of requests."""
        # For now, process sequentially (can be optimized with provider-specific batching)
        results = []
        for request in requests:
            result = await self.generate(request)
            results.append(result)
        return results

    async def get_usage_stats(self, org_id: str) -> Dict[str, Any]:
        """Get AI usage statistics for organization."""
        if not self.budget_guard:
            return {"error": "Budget guard not available"}
        
        return self.budget_guard.get_usage_stats(org_id)
