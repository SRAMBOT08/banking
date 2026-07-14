from app.config.settings import Settings
from app.providers.base import BaseLLMProvider
from app.providers.gemini import GeminiProvider
from app.providers.mock import MockLLMProvider


class LLMProviderFactory:
    @staticmethod
    def create(settings: Settings) -> BaseLLMProvider:
        if settings.llm_provider.casefold() == "gemini":
            return GeminiProvider(settings)
        if settings.llm_provider.casefold() == "mock":
            return MockLLMProvider()
        raise ValueError(f"unsupported LLM_PROVIDER: {settings.llm_provider}")
