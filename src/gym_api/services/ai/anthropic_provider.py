import anthropic

from gym_api.services.ai.provider import SummaryProvider, SummaryGenerationError
from gym_api.services.ai.prompt import build_summary_prompt, SYSTEM_PROMPT
from gym_api.services.ai.types import WorkoutSummaryContext, SummaryResult


class AnthropicProvider(SummaryProvider):
    def __init__(self, api_key: str, model: str):
        self._client = anthropic.AsyncAnthropic(api_key=api_key)
        self._model = model

    async def generate_summary(self, context: WorkoutSummaryContext) -> SummaryResult:
        user_message = build_summary_prompt(context)
        try:
            response = await self._client.messages.create(
                model=self._model,
                max_tokens=1024,
                system=SYSTEM_PROMPT,
                messages=[{"role": "user", "content": user_message}],
            )
        except Exception as e:
            raise SummaryGenerationError(f"Anthropic API error: {e}") from e

        if not response.content or not response.content[0].text:
            raise SummaryGenerationError("Anthropic returned empty response")

        return SummaryResult(
            summary_text=response.content[0].text,
            prompt_tokens=response.usage.input_tokens,
            completion_tokens=response.usage.output_tokens,
        )
