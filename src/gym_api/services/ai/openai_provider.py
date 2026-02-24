import openai

from gym_api.services.ai.provider import SummaryProvider
from gym_api.services.ai.prompt import build_summary_prompt, SYSTEM_PROMPT
from gym_api.services.ai.types import WorkoutSummaryContext, SummaryResult


class OpenAIProvider(SummaryProvider):
    def __init__(self, api_key: str, model: str):
        self._client = openai.AsyncOpenAI(api_key=api_key)
        self._model = model

    async def generate_summary(self, context: WorkoutSummaryContext) -> SummaryResult:
        user_message = build_summary_prompt(context)
        response = await self._client.chat.completions.create(
            model=self._model,
            max_tokens=1024,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_message},
            ],
        )
        return SummaryResult(
            summary_text=response.choices[0].message.content,
            prompt_tokens=response.usage.prompt_tokens,
            completion_tokens=response.usage.completion_tokens,
        )
