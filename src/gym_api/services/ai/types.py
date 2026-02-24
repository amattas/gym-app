import uuid
from dataclasses import dataclass
from datetime import datetime


@dataclass
class WorkoutData:
    workout_id: uuid.UUID
    date: datetime
    duration_minutes: int | None
    exercises: list[dict]
    total_volume_lbs: float
    completion_rate: float
    prs_achieved: int


@dataclass
class WorkoutSummaryContext:
    client_name: str
    program_name: str | None
    workouts: list[WorkoutData]


@dataclass
class SummaryResult:
    summary_text: str
    prompt_tokens: int
    completion_tokens: int

    @property
    def total_tokens(self) -> int:
        return self.prompt_tokens + self.completion_tokens
