import json
from abc import ABC, abstractmethod
from typing import List, Dict, Any

import httpx
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type

from prompt_optimizer.models import ModelConfig
from prompt_optimizer.config import ApiConfig


class LLMClient(ABC):
    @abstractmethod
    async def complete(
        self,
        model_config: ModelConfig,
        messages: List[Dict[str, str]],
        temperature: float,
    ) -> str:
        pass


class OpenAILikeClient(LLMClient):
    def __init__(self, api_config: ApiConfig):
        self.api_config = api_config
        self.client = httpx.AsyncClient(timeout=api_config.timeout_seconds)

    async def complete(
        self,
        model_config: ModelConfig,
        messages: List[Dict[str, str]],
        temperature: float,
    ) -> str:

        @retry(
            wait=wait_exponential(multiplier=1, min=self.api_config.retry_initial_seconds, max=self.api_config.retry_max_seconds),
            stop=stop_after_attempt(self.api_config.retry_attempts),
            retry=retry_if_exception_type((httpx.RequestError, httpx.HTTPStatusError)),
            reraise=True
        )
        async def _call_api():
            headers = {
                "Authorization": f"Bearer {model_config.api_key}",
                "Content-Type": "application/json"
            }

            payload = {
                "model": model_config.model,
                "messages": messages,
                "temperature": temperature,
            }

            response = await self.client.post(
                f"{model_config.base_url.rstrip('/')}/chat/completions",
                headers=headers,
                json=payload
            )
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]

        return await _call_api()


class MockLLMClient(LLMClient):
    """
    MockClient für deterministische Tests ohne externe API.
    Reagiert auf bestimmte Prompt-Inhalte.
    """
    async def complete(
        self,
        model_config: ModelConfig,
        messages: List[Dict[str, str]],
        temperature: float,
    ) -> str:
        # Finde System- und User-Prompt
        sys_msg = next((m["content"] for m in messages if m["role"] == "system"), "")
        user_msg = next((m["content"] for m in messages if m["role"] == "user"), "")

        # Judge Mock: Liefere JSON zurück
        if "Du bist ein strenger Evaluator" in sys_msg or "Du bist ein strenger Evaluator" in user_msg:
            # Wenn "improved" im Model Output steht, bewerte besser
            if "[IMPROVED]" in user_msg:
                score = 9.0
            else:
                score = 5.0
            return json.dumps({
                "overall": score,
                "content": score,
                "style": score,
                "structure": score,
                "rationale": "Mock Judge Bewertung"
            })

        # Optimizer Mock: Liefere verbesserten Prompt
        if "Du optimierst Prompts für ein Zielmodell" in sys_msg or "Du optimierst Prompts für ein Zielmodell" in user_msg:
            return json.dumps({
                "prompt_text": "Verbesserter Prompt [IMPROVED]",
                "rationale": "Weil er besser ist."
            })

        # Target Model Mock: Standardantwort
        if "[IMPROVED]" in sys_msg or "[IMPROVED]" in user_msg:
            return f"Mock Output [IMPROVED] for model {model_config.model}"
        return f"Mock Output for model {model_config.model}"
