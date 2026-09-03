import httpx
from typing import Optional
from app.services.llm.base import LLMProvider


class OpenAILLMProvider(LLMProvider):
    """
    OpenAI-compatible HTTP provider using httpx.
    Works with OpenAI, Azure, DeepSeek, or local compatible API servers.
    """

    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4o-mini", base_url: Optional[str] = None):
        self.api_key = api_key or ""
        self.model = model
        self.base_url = (base_url or "https://api.openai.com/v1").rstrip("/")

    async def generate(self, prompt: str, system_prompt: str) -> str:
        if not self.api_key:
            raise ValueError("LLM_API_KEY is not configured for OpenAILLMProvider.")

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            "response_format": {"type": "json_object"},
            "temperature": 0.2
        }

        url = f"{self.base_url}/chat/completions"

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]
