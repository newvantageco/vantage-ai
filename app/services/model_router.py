from __future__ import annotations

from typing import Optional, Any, Callable, Awaitable

import httpx
from openai import AsyncOpenAI

from app.core.config import get_settings
import asyncio


JsonDict = dict[str, Any]


class ModelRouter:
	def __init__(self) -> None:
		settings = get_settings()
		self.primary = settings.model_router_primary or "openai:gpt-4o-mini"
		self.fallback = settings.model_router_fallback or "ollama:llama3.1"
		self.openai_api_key = None
		# Read lazily to avoid import-time env coupling
		try:
			from os import getenv
			self.openai_api_key = getenv("OPENAI_API_KEY")
		except Exception:
			self.openai_api_key = None

	async def _complete_openai(self, prompt: str, system: Optional[str]) -> Optional[str]:
		if not self.openai_api_key:
			return None
		client = AsyncOpenAI(api_key=self.openai_api_key)
		model = self.primary.split(":", 1)[1] if ":" in self.primary else self.primary
		messages = []
		if system:
			messages.append({"role": "system", "content": system})
		messages.append({"role": "user", "content": prompt})
		resp = await client.chat.completions.create(model=model, messages=messages, temperature=0.4)
		return resp.choices[0].message.content or ""

	async def _complete_ollama(self, prompt: str, system: Optional[str]) -> Optional[str]:
		model = self.fallback.split(":", 1)[1] if ":" in self.fallback else self.fallback
		payload = {"model": model, "prompt": (f"{system}\n\n{prompt}" if system else prompt)}
		async with httpx.AsyncClient(timeout=30) as client:
			resp = await client.post("http://localhost:11434/api/generate", json=payload)
			resp.raise_for_status()
			# streaming false by default returns full JSON with 'response'
			data = resp.json()
			return data.get("response")

	async def complete(self, prompt: str, system: Optional[str] = None) -> str:
		# Try primary (OpenAI) then fallback (Ollama)
		try:
			result = await self._complete_openai(prompt, system)
			if result:
				return result
		except Exception:
			pass
		try:
			result = await self._complete_ollama(prompt, system)
			if result:
				return result
		except Exception:
			pass
		return ""


class AIRouter:
    def __init__(self) -> None:
        from os import getenv
        self.model_mode = (getenv("MODEL_MODE") or "hosted").lower()
        self.hosted_model_name = getenv("HOSTED_MODEL_NAME") or "gpt-4o-mini"
        self.open_model_endpoint = getenv("OPEN_MODEL_ENDPOINT")
        self.open_model_api_key = getenv("OPEN_MODEL_API_KEY")

    async def _call_with_timeout_retry(self, func: Callable[[], Awaitable[str]], timeout_s: float = 30.0, retries: int = 1) -> str:
        last_err: Optional[Exception] = None
        for attempt in range(retries + 1):
            try:
                return await asyncio.wait_for(func(), timeout=timeout_s)
            except Exception as e:
                last_err = e
        return ""  # telemetry hooks could record last_err

    async def _stub_json(self, fields: list[str]) -> str:
        # Return minimal JSON structure when providers unset
        if "hashtags" in fields:
            return "{\"hashtags\": []}"
        if fields == ["text"]:
            return "{\"text\": \"\"}"
        if fields == ["caption"]:
            return "{\"caption\": \"\"}"
        if fields == ["alt_text"]:
            return "{\"alt_text\": \"\"}"
        if fields == ["first_comment"]:
            return "{\"first_comment\": \"\"}"
        return "{}"

    async def _hosted_complete(self, system: Optional[str], prompt: str) -> str:
        async def run() -> str:
            mr = ModelRouter()
            return await mr.complete(prompt=prompt, system=system)
        return await self._call_with_timeout_retry(run)

    async def _open_complete(self, system: Optional[str], prompt: str) -> str:
        # Minimal open provider: POST to endpoint with {prompt, system}
        if not self.open_model_endpoint or not self.open_model_api_key:
            return ""
        async def run() -> str:
            async with httpx.AsyncClient(timeout=30) as client:
                headers = {"Authorization": f"Bearer {self.open_model_api_key}"}
                resp = await client.post(self.open_model_endpoint, json={"prompt": prompt, "system": system}, headers=headers)
                resp.raise_for_status()
                data = resp.json()
                if isinstance(data, dict) and "text" in data:
                    return str(data["text"])  # generic shape
                return resp.text
        return await self._call_with_timeout_retry(run)

    async def _complete(self, system: Optional[str], prompt: str) -> str:
        if self.model_mode == "open":
            return await self._open_complete(system, prompt)
        return await self._hosted_complete(system, prompt)

    async def generate_caption(self, system: Optional[str], prompt: str) -> str:
        text = await self._complete(system, prompt)
        return text or await self._stub_json(["caption"])

    async def rewrite_to_voice(self, system: Optional[str], prompt: str) -> str:
        text = await self._complete(system, prompt)
        return text or await self._stub_json(["text"])

    async def hashtags(self, system: Optional[str], prompt: str) -> str:
        text = await self._complete(system, prompt)
        return text or await self._stub_json(["hashtags"])

    async def first_comment(self, system: Optional[str], prompt: str) -> str:
        text = await self._complete(system, prompt)
        return text or await self._stub_json(["first_comment"])


ai_router = AIRouter()


model_router = ModelRouter()


