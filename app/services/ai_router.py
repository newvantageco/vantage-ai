"""
AI Router Service with Provider Fallback Logic

Supports multiple AI providers (OpenAI, Anthropic, Cohere, Ollama) with intelligent
fallback based on policy, cost, and quota constraints.
"""

from __future__ import annotations

import asyncio
import json
import time
from typing import Optional, Dict, Any, List, Tuple
from dataclasses import dataclass
from enum import Enum

import httpx
from openai import AsyncOpenAI
from anthropic import AsyncAnthropic
import cohere

from app.core.config import get_settings


class ProviderType(Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    COHERE = "cohere"
    OLLAMA = "ollama"


@dataclass
class AIResponse:
    """Structured response from AI providers"""
    text: str
    provider: str
    tokens_in: int
    tokens_out: int
    ms_elapsed: int
    cost_usd_estimate: float
    json_mode: bool = False


@dataclass
class ProviderConfig:
    """Configuration for AI providers"""
    enabled: bool
    api_key: Optional[str]
    base_url: Optional[str]
    model: str
    max_tokens: int
    timeout: int
    cost_per_1k_input: float
    cost_per_1k_output: float


class AIProvider:
    """Base class for AI providers"""
    
    def __init__(self, config: ProviderConfig):
        self.config = config
        self.client = None
    
    async def complete(
        self, 
        prompt: str, 
        system: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        json_mode: bool = False
    ) -> AIResponse:
        """Complete a prompt and return structured response"""
        raise NotImplementedError
    
    def estimate_cost(self, tokens_in: int, tokens_out: int) -> float:
        """Estimate cost based on token usage"""
        input_cost = (tokens_in / 1000) * self.config.cost_per_1k_input
        output_cost = (tokens_out / 1000) * self.config.cost_per_1k_output
        return input_cost + output_cost
    
    def estimate_tokens(self, text: str) -> int:
        """Rough token estimation (4 chars per token average)"""
        return len(text) // 4


class OpenAIProvider(AIProvider):
    """OpenAI provider implementation"""
    
    async def complete(
        self, 
        prompt: str, 
        system: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        json_mode: bool = False
    ) -> AIResponse:
        if not self.client:
            self.client = AsyncOpenAI(api_key=self.config.api_key)
        
        start_time = time.time()
        
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        
        # Prepare completion parameters
        completion_params = {
            "model": self.config.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens or self.config.max_tokens,
        }
        
        if json_mode:
            completion_params["response_format"] = {"type": "json_object"}
        
        try:
            response = await self.client.chat.completions.create(**completion_params)
            
            text = response.choices[0].message.content or ""
            tokens_in = response.usage.prompt_tokens
            tokens_out = response.usage.completion_tokens
            
            ms_elapsed = int((time.time() - start_time) * 1000)
            cost_estimate = self.estimate_cost(tokens_in, tokens_out)
            
            return AIResponse(
                text=text,
                provider=f"openai:{self.config.model}",
                tokens_in=tokens_in,
                tokens_out=tokens_out,
                ms_elapsed=ms_elapsed,
                cost_usd_estimate=cost_estimate,
                json_mode=json_mode
            )
        except Exception as e:
            raise Exception(f"OpenAI API error: {str(e)}")


class AnthropicProvider(AIProvider):
    """Anthropic provider implementation"""
    
    async def complete(
        self, 
        prompt: str, 
        system: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        json_mode: bool = False
    ) -> AIResponse:
        if not self.client:
            self.client = AsyncAnthropic(api_key=self.config.api_key)
        
        start_time = time.time()
        
        # Anthropic uses different message format
        full_prompt = f"{system}\n\n{prompt}" if system else prompt
        
        try:
            response = await self.client.messages.create(
                model=self.config.model,
                max_tokens=max_tokens or self.config.max_tokens,
                temperature=temperature,
                messages=[{"role": "user", "content": full_prompt}]
            )
            
            text = response.content[0].text if response.content else ""
            
            # Anthropic doesn't provide token counts in response, estimate
            tokens_in = self.estimate_tokens(full_prompt)
            tokens_out = self.estimate_tokens(text)
            
            ms_elapsed = int((time.time() - start_time) * 1000)
            cost_estimate = self.estimate_cost(tokens_in, tokens_out)
            
            return AIResponse(
                text=text,
                provider=f"anthropic:{self.config.model}",
                tokens_in=tokens_in,
                tokens_out=tokens_out,
                ms_elapsed=ms_elapsed,
                cost_usd_estimate=cost_estimate,
                json_mode=json_mode
            )
        except Exception as e:
            raise Exception(f"Anthropic API error: {str(e)}")


class CohereProvider(AIProvider):
    """Cohere provider implementation"""
    
    async def complete(
        self, 
        prompt: str, 
        system: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        json_mode: bool = False
    ) -> AIResponse:
        if not self.client:
            self.client = cohere.AsyncClient(api_key=self.config.api_key)
        
        start_time = time.time()
        
        # Cohere uses different format
        full_prompt = f"{system}\n\n{prompt}" if system else prompt
        
        try:
            response = await self.client.generate(
                model=self.config.model,
                prompt=full_prompt,
                max_tokens=max_tokens or self.config.max_tokens,
                temperature=temperature,
                return_likelihoods="NONE"
            )
            
            text = response.generations[0].text if response.generations else ""
            
            # Cohere provides token counts
            tokens_in = response.meta.billed_tokens.input_tokens
            tokens_out = response.meta.billed_tokens.output_tokens
            
            ms_elapsed = int((time.time() - start_time) * 1000)
            cost_estimate = self.estimate_cost(tokens_in, tokens_out)
            
            return AIResponse(
                text=text,
                provider=f"cohere:{self.config.model}",
                tokens_in=tokens_in,
                tokens_out=tokens_out,
                ms_elapsed=ms_elapsed,
                cost_usd_estimate=cost_estimate,
                json_mode=json_mode
            )
        except Exception as e:
            raise Exception(f"Cohere API error: {str(e)}")


class OllamaProvider(AIProvider):
    """Ollama local provider implementation"""
    
    async def complete(
        self, 
        prompt: str, 
        system: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        json_mode: bool = False
    ) -> AIResponse:
        start_time = time.time()
        
        # Ollama uses HTTP API
        full_prompt = f"{system}\n\n{prompt}" if system else prompt
        
        payload = {
            "model": self.config.model,
            "prompt": full_prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens or self.config.max_tokens
            }
        }
        
        if json_mode:
            payload["format"] = "json"
        
        try:
            async with httpx.AsyncClient(timeout=self.config.timeout) as client:
                response = await client.post(
                    f"{self.config.base_url}/api/generate",
                    json=payload
                )
                response.raise_for_status()
                data = response.json()
                
                text = data.get("response", "")
                
                # Ollama doesn't provide token counts, estimate
                tokens_in = self.estimate_tokens(full_prompt)
                tokens_out = self.estimate_tokens(text)
                
                ms_elapsed = int((time.time() - start_time) * 1000)
                cost_estimate = self.estimate_cost(tokens_in, tokens_out)  # Should be 0 for local
                
                return AIResponse(
                    text=text,
                    provider=f"ollama:{self.config.model}",
                    tokens_in=tokens_in,
                    tokens_out=tokens_out,
                    ms_elapsed=ms_elapsed,
                    cost_usd_estimate=cost_estimate,
                    json_mode=json_mode
                )
        except Exception as e:
            raise Exception(f"Ollama API error: {str(e)}")


class AIRouter:
    """Main AI router with provider fallback logic"""
    
    def __init__(self):
        self.settings = get_settings()
        self.providers: Dict[ProviderType, AIProvider] = {}
        self._initialize_providers()
    
    def _initialize_providers(self):
        """Initialize available providers based on environment configuration"""
        
        # OpenAI
        if self.settings.openai_api_key:
            self.providers[ProviderType.OPENAI] = OpenAIProvider(ProviderConfig(
                enabled=True,
                api_key=self.settings.openai_api_key,
                base_url=None,
                model="gpt-4o-mini",
                max_tokens=4096,
                timeout=60,
                cost_per_1k_input=0.00015,
                cost_per_1k_output=0.0006
            ))
        
        # Anthropic
        anthropic_key = getattr(self.settings, 'anthropic_api_key', None)
        if anthropic_key:
            self.providers[ProviderType.ANTHROPIC] = AnthropicProvider(ProviderConfig(
                enabled=True,
                api_key=anthropic_key,
                base_url=None,
                model="claude-3-haiku-20240307",
                max_tokens=4096,
                timeout=90,
                cost_per_1k_input=0.00025,
                cost_per_1k_output=0.00125
            ))
        
        # Cohere
        cohere_key = getattr(self.settings, 'cohere_api_key', None)
        if cohere_key:
            self.providers[ProviderType.COHERE] = CohereProvider(ProviderConfig(
                enabled=True,
                api_key=cohere_key,
                base_url=None,
                model="command",
                max_tokens=4096,
                timeout=30,
                cost_per_1k_input=0.0001,
                cost_per_1k_output=0.0001
            ))
        
        # Ollama (local)
        ollama_url = getattr(self.settings, 'ollama_base_url', 'http://localhost:11434')
        self.providers[ProviderType.OLLAMA] = OllamaProvider(ProviderConfig(
            enabled=True,
            api_key=None,
            base_url=ollama_url,
            model="llama3.1",
            max_tokens=4096,
            timeout=120,
            cost_per_1k_input=0.0,
            cost_per_1k_output=0.0
        ))
    
    def _get_provider_priority(self) -> List[ProviderType]:
        """Get provider priority order based on configuration"""
        primary = getattr(self.settings, 'ai_primary_provider', 'openai')
        fallback = getattr(self.settings, 'ai_fallback_provider', 'ollama')
        
        priority = []
        
        # Add primary provider first
        if primary == 'openai' and ProviderType.OPENAI in self.providers:
            priority.append(ProviderType.OPENAI)
        elif primary == 'anthropic' and ProviderType.ANTHROPIC in self.providers:
            priority.append(ProviderType.ANTHROPIC)
        elif primary == 'cohere' and ProviderType.COHERE in self.providers:
            priority.append(ProviderType.COHERE)
        elif primary == 'ollama' and ProviderType.OLLAMA in self.providers:
            priority.append(ProviderType.OLLAMA)
        
        # Add fallback providers
        for provider_type in [ProviderType.OPENAI, ProviderType.ANTHROPIC, ProviderType.COHERE, ProviderType.OLLAMA]:
            if provider_type not in priority and provider_type in self.providers:
                priority.append(provider_type)
        
        return priority
    
    async def complete(
        self,
        prompt: str,
        system: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        json_mode: bool = False,
        preferred_provider: Optional[str] = None
    ) -> AIResponse:
        """
        Complete a prompt using the best available provider with fallback logic.
        
        Args:
            prompt: The input prompt
            system: Optional system message
            temperature: Sampling temperature (0.0 to 1.0)
            max_tokens: Maximum tokens to generate
            json_mode: Whether to force JSON output format
            preferred_provider: Preferred provider name (e.g., 'openai', 'anthropic')
        
        Returns:
            AIResponse with structured output including provider used, costs, etc.
        """
        if not self.providers:
            raise Exception("No AI providers configured")
        
        # Get provider priority
        provider_priority = self._get_provider_priority()
        
        # If preferred provider specified, try it first
        if preferred_provider:
            preferred_type = None
            if preferred_provider.lower() == 'openai':
                preferred_type = ProviderType.OPENAI
            elif preferred_provider.lower() == 'anthropic':
                preferred_type = ProviderType.ANTHROPIC
            elif preferred_provider.lower() == 'cohere':
                preferred_type = ProviderType.COHERE
            elif preferred_provider.lower() == 'ollama':
                preferred_type = ProviderType.OLLAMA
            
            if preferred_type and preferred_type in self.providers:
                provider_priority = [preferred_type] + [p for p in provider_priority if p != preferred_type]
        
        # Try providers in order
        last_error = None
        for provider_type in provider_priority:
            try:
                provider = self.providers[provider_type]
                response = await provider.complete(
                    prompt=prompt,
                    system=system,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    json_mode=json_mode
                )
                return response
            except Exception as e:
                last_error = e
                # Log the error but continue to next provider
                print(f"Provider {provider_type.value} failed: {str(e)}")
                continue
        
        # If all providers failed, raise the last error
        raise Exception(f"All AI providers failed. Last error: {str(last_error)}")
    
    async def batch_complete(
        self,
        requests: List[Dict[str, Any]]
    ) -> List[AIResponse]:
        """
        Complete multiple prompts in batch.
        Currently processes sequentially, but can be optimized per provider.
        """
        results = []
        for request in requests:
            try:
                response = await self.complete(
                    prompt=request["prompt"],
                    system=request.get("system"),
                    temperature=request.get("temperature", 0.7),
                    max_tokens=request.get("max_tokens"),
                    json_mode=request.get("json_mode", False),
                    preferred_provider=request.get("preferred_provider")
                )
                results.append(response)
            except Exception as e:
                # Create error response
                error_response = AIResponse(
                    text=f"Error: {str(e)}",
                    provider="error",
                    tokens_in=0,
                    tokens_out=0,
                    ms_elapsed=0,
                    cost_usd_estimate=0.0
                )
                results.append(error_response)
        
        return results
    
    def get_available_providers(self) -> List[str]:
        """Get list of available provider names"""
        return [provider_type.value for provider_type in self.providers.keys()]
    
    def get_provider_costs(self) -> Dict[str, Dict[str, float]]:
        """Get cost information for all providers"""
        costs = {}
        for provider_type, provider in self.providers.items():
            costs[provider_type.value] = {
                "input_per_1k": provider.config.cost_per_1k_input,
                "output_per_1k": provider.config.cost_per_1k_output
            }
        return costs


# Global instance
ai_router = AIRouter()
