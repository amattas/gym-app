from abc import ABC, abstractmethod

from gym_api.services.ai.types import WorkoutSummaryContext, SummaryResult


class SummaryProvider(ABC):
    @abstractmethod
    async def generate_summary(self, context: WorkoutSummaryContext) -> SummaryResult:
        ...
