from abc import ABC, abstractmethod

from gym_api.services.ai.types import WorkoutSummaryContext, SummaryResult


class SummaryGenerationError(Exception):
    pass


class SummaryProvider(ABC):
    @abstractmethod
    async def generate_summary(self, context: WorkoutSummaryContext) -> SummaryResult:
        ...
