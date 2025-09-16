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


class HostedProvider:
    """Provider for hosted AI models (OpenAI, Anthropic, etc.)"""
    
    def __init__(self, provider_name: str = "openai"):
        self.provider_name = provider_name
        self.capabilities = self._get_capabilities(provider_name)
    
    def _get_capabilities(self, provider: str) -> ProviderCapabilities:
        """Get capabilities for different hosted providers."""
        capabilities_map = {
            "openai": ProviderCapabilities(
                supports_batch=True,
                max_batch_size=8,
                max_tokens_per_request=128000,
                timeout_seconds=60,
                cost_per_1k_tokens_input=0.00015,  # GPT-4o-mini input
                cost_per_1k_tokens_output=0.0006   # GPT-4o-mini output
            ),
            "anthropic": ProviderCapabilities(
                supports_batch=False,
                max_batch_size=1,
                max_tokens_per_request=200000,
                timeout_seconds=90,
                cost_per_1k_tokens_input=0.003,
                cost_per_1k_tokens_output=0.015
            ),
            "cohere": ProviderCapabilities(
                supports_batch=True,
                max_batch_size=5,
                max_tokens_per_request=4096,
                timeout_seconds=30,
                cost_per_1k_tokens_input=0.0001,
                cost_per_1k_tokens_output=0.0001
            )
        }
        
        return capabilities_map.get(provider, capabilities_map["openai"])
    
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
