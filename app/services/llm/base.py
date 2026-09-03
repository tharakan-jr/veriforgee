from abc import ABC, abstractmethod


class LLMProvider(ABC):
    """
    Abstract Base Class for LLM providers.
    Ensures the review engine can easily swap LLM backends (OpenAI, Gemini, Ollama, Mock, etc.).
    """

    @abstractmethod
    async def generate(self, prompt: str, system_prompt: str) -> str:
        """
        Generate raw response string from LLM provider given prompt and system_prompt.
        """
        pass
