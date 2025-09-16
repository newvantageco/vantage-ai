from __future__ import annotations

from typing import List, Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class ProviderCapabilities:
    supports_batch: bool
    max_batch_size: int
    max_tokens_per_request: int
    timeout_seconds: int
    cost_per_1k_tokens_input: float
    cost_per_1k_tokens_output: float


class OpenProvider:
    """Provider for open-source/self-hosted AI models"""
    
    def __init__(self, provider_name: str = "ollama"):
        self.provider_name = provider_name
        self.capabilities = self._get_capabilities(provider_name)
    
    def _get_capabilities(self, provider: str) -> ProviderCapabilities:
        """Get capabilities for different open providers."""
        capabilities_map = {
            "ollama": ProviderCapabilities(
                supports_batch=False,  # Most local models don't support batching
                max_batch_size=1,
                max_tokens_per_request=32000,
                timeout_seconds=120,  # Local models can be slower
                cost_per_1k_tokens_input=0.0,  # Free local hosting
                cost_per_1k_tokens_output=0.0
            ),
            "vllm": ProviderCapabilities(
                supports_batch=True,
                max_batch_size=16,
                max_tokens_per_request=128000,
                timeout_seconds=60,
                cost_per_1k_tokens_input=0.0,  # Self-hosted
                cost_per_1k_tokens_output=0.0
            ),
            "text-generation-inference": ProviderCapabilities(
                supports_batch=True,
                max_batch_size=8,
                max_tokens_per_request=64000,
                timeout_seconds=45,
                cost_per_1k_tokens_input=0.0,
                cost_per_1k_tokens_output=0.0
            ),
            "generic": ProviderCapabilities(
                supports_batch=False,
                max_batch_size=1,
                max_tokens_per_request=4096,
                timeout_seconds=30,
                cost_per_1k_tokens_input=0.0001,  # Minimal cost estimate
                cost_per_1k_tokens_output=0.0001
            )
        }
        
        return capabilities_map.get(provider, capabilities_map["generic"])
    
    def can_handle_batch(self, batch_size: int) -> bool:
        """Check if provider can handle batch of given size."""
        return (self.capabilities.supports_batch and 
                batch_size <= self.capabilities.max_batch_size)
    
    def get_max_tokens_for_task(self, task_type: str) -> int:
        """Get max tokens allowed for specific task type."""
        task_limits = {
            "caption": 500,
            "hashtags": 200,
            "alt_text": 200,
            "first_comment": 300,
            "rewrite": 1000,
            "ads_copy": 2000,
            "brief": 5000
        }
        
        task_limit = task_limits.get(task_type, 1000)
        return min(task_limit, self.capabilities.max_tokens_per_request)
    
    def estimate_cost(self, tokens_in: int, tokens_out: int) -> float:
        """Estimate cost for token usage."""
        input_cost = (tokens_in / 1000) * self.capabilities.cost_per_1k_tokens_input
        output_cost = (tokens_out / 1000) * self.capabilities.cost_per_1k_tokens_output
        return input_cost + output_cost
    
    def get_timeout_for_task(self, task_type: str) -> int:
        """Get timeout for specific task type."""
        task_timeouts = {
            "caption": 30,
            "hashtags": 15,
            "alt_text": 15,
            "first_comment": 20,
            "rewrite": 45,
            "ads_copy": 60,
            "brief": 90
        }
        
        task_timeout = task_timeouts.get(task_type, 30)
        return min(task_timeout, self.capabilities.timeout_seconds)
    
    def is_free(self) -> bool:
        """Check if this provider has zero cost."""
        return (self.capabilities.cost_per_1k_tokens_input == 0.0 and 
                self.capabilities.cost_per_1k_tokens_output == 0.0)
