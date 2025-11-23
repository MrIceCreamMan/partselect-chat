import httpx
from typing import List, Dict, Any, Optional, AsyncGenerator
import json
import logging
from config import settings

logger = logging.getLogger(__name__)


class DeepseekClient:
    def __init__(self):
        self.api_key = settings.DEEPSEEK_API_KEY
        self.base_url = settings.DEEPSEEK_BASE_URL
        self.model = settings.DEEPSEEK_MODEL
        self.client = httpx.AsyncClient(timeout=60.0)

    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        tools: Optional[List[Dict[str, Any]]] = None,
        temperature: float = None,
        max_tokens: int = None,
        stream: bool = False,
    ) -> Dict[str, Any]:
        """
        Send chat completion request to Deepseek
        """
        if temperature is None:
            temperature = settings.TEMPERATURE
        if max_tokens is None:
            max_tokens = settings.MAX_TOKENS

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": stream,
        }

        if tools:
            payload["tools"] = tools
            payload["tool_choice"] = "auto"

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        try:
            response = await self.client.post(
                f"{self.base_url}/v1/chat/completions", json=payload, headers=headers
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Deepseek API error: {e}")
            raise

    async def stream_chat_completion(
        self,
        messages: List[Dict[str, str]],
        tools: Optional[List[Dict[str, Any]]] = None,
        temperature: float = None,
        max_tokens: int = None,
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Stream chat completion from Deepseek
        """
        if temperature is None:
            temperature = settings.TEMPERATURE
        if max_tokens is None:
            max_tokens = settings.MAX_TOKENS

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": True,
        }

        if tools:
            payload["tools"] = tools
            payload["tool_choice"] = "auto"

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        try:
            async with self.client.stream(
                "POST",
                f"{self.base_url}/v1/chat/completions",
                json=payload,
                headers=headers,
            ) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data = line[6:]  # Remove "data: " prefix
                        if data.strip() == "[DONE]":
                            break
                        try:
                            chunk = json.loads(data)
                            yield chunk
                        except json.JSONDecodeError:
                            continue
        except httpx.HTTPError as e:
            logger.error(f"Deepseek streaming error: {e}")
            raise

    async def simple_completion(self, prompt: str) -> str:
        """Simple text completion for utility functions"""
        messages = [{"role": "user", "content": prompt}]
        response = await self.chat_completion(messages, max_tokens=100)
        return response["choices"][0]["message"]["content"]

    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()


# Global instance
_deepseek_client = None


def get_deepseek_client() -> DeepseekClient:
    global _deepseek_client
    if _deepseek_client is None:
        _deepseek_client = DeepseekClient()
    return _deepseek_client
