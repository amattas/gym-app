from gym_api.services.ai.provider import SummaryProvider
from gym_api.services.ai.anthropic_provider import AnthropicProvider
from gym_api.services.ai.openai_provider import OpenAIProvider


def create_summary_provider(provider_name: str, *, api_key: str, model: str) -> SummaryProvider:
    if provider_name == "anthropic":
        return AnthropicProvider(api_key=api_key, model=model)
    elif provider_name == "openai":
        return OpenAIProvider(api_key=api_key, model=model)
    else:
        raise ValueError(f"Unknown provider: {provider_name}")
