"""AI Providers package — Factory and base class."""
from app.services.ai_providers.base import BaseAIProvider
from app.services.ai_providers.gemini import GeminiProvider
from app.services.ai_providers.ollama import OllamaProvider


def get_provider(provider_name: str, model_name: str = None) -> BaseAIProvider:
    """Factory to instantiate the correct AI provider."""
    if provider_name == "gemini":
        return GeminiProvider(model_name=model_name)
    elif provider_name == "ollama":
        return OllamaProvider(model_name=model_name)
    else:
        raise ValueError(f"Unknown AI provider: {provider_name}")


__all__ = ["BaseAIProvider", "GeminiProvider", "OllamaProvider", "get_provider"]
