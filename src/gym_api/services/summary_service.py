import uuid
from datetime import datetime, timezone

from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from gym_api.models.summary import ClientWorkoutSummary
from gym_api.services.ai.provider import SummaryProvider
from gym_api.services.ai.types import WorkoutSummaryContext, WorkoutData


class SummaryService:
    def __init__(self, provider: SummaryProvider, provider_name: str, model_id: str):
        self._provider = provider
        self._provider_name = provider_name
        self._model_id = model_id

    async def get_summary(
        self,
        db: AsyncSession,
        client_id: uuid.UUID,
        gym_id: uuid.UUID,
        workouts: list,
        analytics: dict,
        client_name: str,
        program_name: str | None,
        cached_summary: ClientWorkoutSummary | None,
    ) -> ClientWorkoutSummary:
        if cached_summary is not None:
            return cached_summary

        context = self._build_context(client_name, program_name, workouts, analytics)
        result = await self._provider.generate_summary(context)

        summary = ClientWorkoutSummary(
            summary_id=uuid.uuid4(),
            client_id=client_id,
            gym_id=gym_id,
            summary_text=result.summary_text,
            workouts_included=[w.workout_id for w in workouts],
            generated_at=datetime.now(timezone.utc),
            model_provider=self._provider_name,
            model_id=self._model_id,
            token_usage={"prompt_tokens": result.prompt_tokens, "completion_tokens": result.completion_tokens},
        )

        await db.execute(
            delete(ClientWorkoutSummary).where(ClientWorkoutSummary.client_id == client_id)
        )
        db.add(summary)
        await db.commit()
        await db.refresh(summary)

        return summary

    def _build_context(self, client_name, program_name, workouts, analytics):
        workout_data = []
        for w in workouts:
            exercises = []
            for we in w.exercises:
                ex_data = {"name": we.exercise.name, "sets": len(we.sets), "status": we.status}
                for s in we.sets:
                    for m in s.measurements:
                        if m.type == "weight":
                            ex_data["weight_lbs"] = float(m.value)
                    ex_data["reps"] = s.actual_reps
                exercises.append(ex_data)

            a = analytics.get(w.workout_id)
            workout_data.append(
                WorkoutData(
                    workout_id=w.workout_id,
                    date=w.started_at,
                    duration_minutes=a.duration_minutes if a else None,
                    exercises=exercises,
                    total_volume_lbs=float(a.total_weight_lifted_lbs) if a else 0,
                    completion_rate=float(a.completion_rate) if a else 0,
                    prs_achieved=a.prs_achieved_count if a else 0,
                )
            )

        return WorkoutSummaryContext(
            client_name=client_name,
            program_name=program_name,
            workouts=workout_data,
        )
