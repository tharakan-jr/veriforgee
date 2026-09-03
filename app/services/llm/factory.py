from app.core.config import settings
from app.services.llm.base import LLMProvider
from app.services.llm.mock_provider import MockLLMProvider
from app.services.llm.openai_provider import OpenAILLMProvider


def get_llm_provider(provider_type: str = None) -> LLMProvider:
    provider_name = (provider_type or settings.LLM_PROVIDER).lower()

    if provider_name in ("openai", "azure", "deepseek"):
        return OpenAILLMProvider(
            api_key=settings.LLM_API_KEY,
            model=settings.LLM_MODEL,
            base_url=settings.LLM_BASE_URL
        )

    # Default to MockLLMProvider for 'mock', unknown, or empty settings
    return MockLLMProvider()
