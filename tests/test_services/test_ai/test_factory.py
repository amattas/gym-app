import pytest

from gym_api.services.ai.factory import create_summary_provider
from gym_api.services.ai.anthropic_provider import AnthropicProvider
from gym_api.services.ai.openai_provider import OpenAIProvider


def test_factory_creates_anthropic_provider():
    provider = create_summary_provider("anthropic", api_key="key", model="claude-sonnet-4-20250514")
    assert isinstance(provider, AnthropicProvider)


def test_factory_creates_openai_provider():
    provider = create_summary_provider("openai", api_key="key", model="gpt-4o")
    assert isinstance(provider, OpenAIProvider)


def test_factory_raises_on_unknown_provider():
    with pytest.raises(ValueError, match="Unknown provider"):
        create_summary_provider("gemini", api_key="key", model="gemini-pro")
