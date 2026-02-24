# AI Workout Summaries Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add an on-demand AI workout summary endpoint that generates a rolling recap of a client's last 5 completed workouts, with smart DB-backed caching and a provider-agnostic LLM interface.

**Architecture:** A new FastAPI endpoint queries the client's recent workouts, checks for a cached summary, and either returns the cache or calls an LLM provider to generate a fresh summary. The provider interface is abstract so Anthropic/OpenAI can be swapped via config. Summaries are persisted in a `client_workout_summary` table with cache invalidation based on workout timestamps.

**Tech Stack:** Python 3.12, FastAPI, SQLAlchemy 2.0 (async), Alembic, PostgreSQL, Anthropic Python SDK, pytest + httpx

**Design Doc:** `docs/plans/2026-02-24-ai-workout-summaries-design.md`

**Prerequisites:** This plan assumes the `gym-api` FastAPI project exists with:
- SQLAlchemy async models for `Workout`, `WorkoutExercise`, `WorkoutSet`, `WorkoutSetMeasurement`, `WorkoutAnalytics`, `Client`, `Exercise`, `Program`, `ClientProgram`
- Alembic migrations configured
- Auth middleware providing `current_user` with role/gym context
- A running PostgreSQL database
- Project structure following the layout in Task 1

If the project doesn't exist yet, Task 1 scaffolds the minimum needed.

---

### Task 1: Scaffold project structure (if needed)

Skip this task if the `gym-api` project already exists with FastAPI + SQLAlchemy + Alembic.

**Files:**
- Create: `src/gym_api/__init__.py`
- Create: `src/gym_api/main.py`
- Create: `src/gym_api/config.py`
- Create: `src/gym_api/database.py`
- Create: `src/gym_api/models/__init__.py`
- Create: `src/gym_api/routers/__init__.py`
- Create: `src/gym_api/services/__init__.py`
- Create: `pyproject.toml`
- Create: `alembic.ini`
- Create: `alembic/env.py`
- Create: `tests/conftest.py`

**Step 1: Create `pyproject.toml` with dependencies**

```toml
[project]
name = "gym-api"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = [
    "fastapi>=0.115.0",
    "uvicorn[standard]>=0.34.0",
    "sqlalchemy[asyncio]>=2.0.0",
    "asyncpg>=0.30.0",
    "alembic>=1.14.0",
    "pydantic>=2.0.0",
    "pydantic-settings>=2.0.0",
    "anthropic>=0.42.0",
    "openai>=1.60.0",
    "httpx>=0.28.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "pytest-asyncio>=0.24.0",
    "httpx>=0.28.0",
    "aiosqlite>=0.20.0",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

**Step 2: Create `src/gym_api/config.py`**

```python
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://localhost:5432/gym"
    ai_summary_provider: str = "anthropic"
    ai_summary_model: str = "claude-sonnet-4-20250514"
    anthropic_api_key: str = ""
    openai_api_key: str = ""

    model_config = {"env_prefix": "", "env_file": ".env"}


settings = Settings()
```

**Step 3: Create `src/gym_api/database.py`**

```python
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine, AsyncSession
from sqlalchemy.orm import DeclarativeBase

from gym_api.config import settings

engine = create_async_engine(settings.database_url)
async_session = async_sessionmaker(engine, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


async def get_db() -> AsyncSession:
    async with async_session() as session:
        yield session
```

**Step 4: Create `src/gym_api/main.py`**

```python
from fastapi import FastAPI

app = FastAPI(title="Gym API", version="0.1.0")


@app.get("/health")
async def health():
    return {"status": "ok"}
```

**Step 5: Create empty `__init__.py` files, set up Alembic**

Run: `pip install -e ".[dev]"` then `alembic init alembic`

**Step 6: Commit**

```bash
git add -A
git commit -m "chore: scaffold gym-api project with FastAPI + SQLAlchemy"
```

---

### Task 2: Create stub models for prerequisite entities

These are minimal stubs so the summary feature can reference them via foreign keys. Real implementations come from MVP tasks.

**Files:**
- Create: `src/gym_api/models/client.py`
- Create: `src/gym_api/models/workout.py`
- Create: `src/gym_api/models/exercise.py`
- Create: `src/gym_api/models/program.py`
- Create: `src/gym_api/models/analytics.py`
- Modify: `src/gym_api/models/__init__.py`

**Step 1: Create `src/gym_api/models/client.py`**

```python
import uuid
from datetime import datetime

from sqlalchemy import String, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from gym_api.database import Base


class Client(Base):
    __tablename__ = "clients"

    client_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    gym_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False, index=True)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
```

**Step 2: Create `src/gym_api/models/exercise.py`**

```python
import uuid
from typing import Optional

from sqlalchemy import String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from gym_api.database import Base


class Exercise(Base):
    __tablename__ = "exercises"

    exercise_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    gym_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
```

**Step 3: Create `src/gym_api/models/program.py`**

```python
import uuid

from sqlalchemy import String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from gym_api.database import Base


class Program(Base):
    __tablename__ = "programs"

    program_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    gym_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
```

**Step 4: Create `src/gym_api/models/workout.py`**

```python
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import String, Integer, DateTime, Boolean, ForeignKey, Text, Numeric, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from gym_api.database import Base


class Workout(Base):
    __tablename__ = "workouts"

    workout_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    client_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("clients.client_id"), nullable=False, index=True)
    trainer_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)
    program_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("programs.program_id"), nullable=True)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    ended_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="in_progress")

    exercises: Mapped[list["WorkoutExercise"]] = relationship(back_populates="workout", lazy="selectin")


class WorkoutExercise(Base):
    __tablename__ = "workout_exercises"

    workout_exercise_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workout_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("workouts.workout_id"), nullable=False)
    exercise_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("exercises.exercise_id"), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="incomplete")
    order_index: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    workout: Mapped["Workout"] = relationship(back_populates="exercises")
    exercise: Mapped["Exercise"] = relationship(lazy="selectin")
    sets: Mapped[list["WorkoutSet"]] = relationship(back_populates="workout_exercise", lazy="selectin")


class WorkoutSet(Base):
    __tablename__ = "workout_sets"

    workout_set_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workout_exercise_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("workout_exercises.workout_exercise_id"), nullable=False)
    set_index: Mapped[int] = mapped_column(Integer, nullable=False)
    actual_reps: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    is_amrap: Mapped[bool] = mapped_column(Boolean, default=False)

    workout_exercise: Mapped["WorkoutExercise"] = relationship(back_populates="sets")
    measurements: Mapped[list["WorkoutSetMeasurement"]] = relationship(back_populates="workout_set", lazy="selectin")


class WorkoutSetMeasurement(Base):
    __tablename__ = "workout_set_measurements"

    measurement_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workout_set_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("workout_sets.workout_set_id"), nullable=False)
    type: Mapped[str] = mapped_column(String(20), nullable=False)
    value: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    unit: Mapped[str] = mapped_column(String(20), nullable=False)

    workout_set: Mapped["WorkoutSet"] = relationship(back_populates="measurements")
```

**Step 5: Create `src/gym_api/models/analytics.py`**

```python
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import Integer, DateTime, Numeric, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from gym_api.database import Base


class WorkoutAnalytics(Base):
    __tablename__ = "workout_analytics"

    analytics_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workout_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("workouts.workout_id"), unique=True, nullable=False)
    client_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("clients.client_id"), nullable=False, index=True)
    total_weight_lifted_lbs: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    total_reps: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    total_sets: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    duration_minutes: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    exercises_completed: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    exercises_skipped: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    completion_rate: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False, default=0)
    prs_achieved_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    volume_by_muscle_group: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    computed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
```

**Step 6: Update `src/gym_api/models/__init__.py`**

```python
from gym_api.models.client import Client
from gym_api.models.exercise import Exercise
from gym_api.models.program import Program
from gym_api.models.workout import Workout, WorkoutExercise, WorkoutSet, WorkoutSetMeasurement
from gym_api.models.analytics import WorkoutAnalytics

__all__ = [
    "Client",
    "Exercise",
    "Program",
    "Workout",
    "WorkoutExercise",
    "WorkoutSet",
    "WorkoutSetMeasurement",
    "WorkoutAnalytics",
]
```

**Step 7: Commit**

```bash
git add src/gym_api/models/
git commit -m "feat(models): add stub models for workout, client, exercise, program, analytics"
```

---

### Task 3: Create `ClientWorkoutSummary` model and migration

**Files:**
- Create: `src/gym_api/models/summary.py`
- Modify: `src/gym_api/models/__init__.py`

**Step 1: Write the failing test**

Create `tests/test_models/test_summary_model.py`:

```python
import uuid
from datetime import datetime, timezone

from gym_api.models.summary import ClientWorkoutSummary


def test_client_workout_summary_has_required_fields():
    summary = ClientWorkoutSummary(
        summary_id=uuid.uuid4(),
        client_id=uuid.uuid4(),
        gym_id=uuid.uuid4(),
        summary_text="Over the last 4 sessions, the client focused on...",
        workouts_included=[uuid.uuid4(), uuid.uuid4()],
        generated_at=datetime.now(timezone.utc),
        model_provider="anthropic",
        model_id="claude-sonnet-4-20250514",
        token_usage={"prompt_tokens": 1200, "completion_tokens": 350},
    )
    assert summary.summary_text.startswith("Over the last")
    assert summary.model_provider == "anthropic"
    assert len(summary.workouts_included) == 2
    assert summary.token_usage["prompt_tokens"] == 1200
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_models/test_summary_model.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'gym_api.models.summary'`

**Step 3: Write `src/gym_api/models/summary.py`**

```python
import uuid
from datetime import datetime

from sqlalchemy import String, Text, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.orm import Mapped, mapped_column

from gym_api.database import Base


class ClientWorkoutSummary(Base):
    __tablename__ = "client_workout_summaries"

    summary_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    client_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("clients.client_id"), unique=True, nullable=False)
    gym_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False, index=True)
    summary_text: Mapped[str] = mapped_column(Text, nullable=False)
    workouts_included: Mapped[list[uuid.UUID]] = mapped_column(ARRAY(UUID(as_uuid=True)), nullable=False)
    generated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    model_provider: Mapped[str] = mapped_column(String(50), nullable=False)
    model_id: Mapped[str] = mapped_column(String(100), nullable=False)
    token_usage: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
```

**Step 4: Add to `src/gym_api/models/__init__.py`**

Add import:
```python
from gym_api.models.summary import ClientWorkoutSummary
```

Add to `__all__`: `"ClientWorkoutSummary"`

**Step 5: Run test to verify it passes**

Run: `pytest tests/test_models/test_summary_model.py -v`
Expected: PASS

**Step 6: Generate Alembic migration**

Run: `alembic revision --autogenerate -m "add client_workout_summaries table"`

Verify the migration includes:
- `client_workout_summaries` table creation
- Unique constraint on `client_id`
- Index on `gym_id`

**Step 7: Commit**

```bash
git add src/gym_api/models/summary.py src/gym_api/models/__init__.py tests/test_models/ alembic/versions/
git commit -m "feat(models): add ClientWorkoutSummary model and migration"
```

---

### Task 4: Create LLM provider interface and data types

**Files:**
- Create: `src/gym_api/services/ai/__init__.py`
- Create: `src/gym_api/services/ai/types.py`
- Create: `src/gym_api/services/ai/provider.py`
- Test: `tests/test_services/test_ai/test_types.py`

**Step 1: Write the failing test**

Create `tests/test_services/test_ai/test_types.py`:

```python
import uuid
from datetime import datetime, timezone

from gym_api.services.ai.types import WorkoutSummaryContext, WorkoutData, SummaryResult


def test_workout_summary_context_holds_client_and_workouts():
    ctx = WorkoutSummaryContext(
        client_name="John Doe",
        program_name="Beginner Strength",
        workouts=[
            WorkoutData(
                workout_id=uuid.uuid4(),
                date=datetime(2026, 2, 20, tzinfo=timezone.utc),
                duration_minutes=55,
                exercises=[{"name": "Back Squat", "sets": 3, "reps": 5, "weight_lbs": 225}],
                total_volume_lbs=3375.0,
                completion_rate=1.0,
                prs_achieved=1,
            ),
        ],
    )
    assert ctx.client_name == "John Doe"
    assert len(ctx.workouts) == 1
    assert ctx.workouts[0].total_volume_lbs == 3375.0


def test_summary_result_holds_text_and_usage():
    result = SummaryResult(
        summary_text="John has been consistent...",
        prompt_tokens=1200,
        completion_tokens=350,
    )
    assert result.summary_text.startswith("John")
    assert result.total_tokens == 1550
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_services/test_ai/test_types.py -v`
Expected: FAIL — `ModuleNotFoundError`

**Step 3: Create `src/gym_api/services/ai/types.py`**

```python
import uuid
from dataclasses import dataclass, field
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
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_services/test_ai/test_types.py -v`
Expected: PASS

**Step 5: Create `src/gym_api/services/ai/provider.py`**

```python
from abc import ABC, abstractmethod

from gym_api.services.ai.types import WorkoutSummaryContext, SummaryResult


class SummaryProvider(ABC):
    @abstractmethod
    async def generate_summary(self, context: WorkoutSummaryContext) -> SummaryResult:
        ...
```

**Step 6: Create `src/gym_api/services/ai/__init__.py`**

```python
from gym_api.services.ai.provider import SummaryProvider
from gym_api.services.ai.types import WorkoutSummaryContext, WorkoutData, SummaryResult

__all__ = ["SummaryProvider", "WorkoutSummaryContext", "WorkoutData", "SummaryResult"]
```

**Step 7: Commit**

```bash
git add src/gym_api/services/ai/ tests/test_services/
git commit -m "feat(ai): add LLM provider interface and data types"
```

---

### Task 5: Implement Anthropic provider

**Files:**
- Create: `src/gym_api/services/ai/anthropic_provider.py`
- Create: `src/gym_api/services/ai/prompt.py`
- Test: `tests/test_services/test_ai/test_anthropic_provider.py`

**Step 1: Write the failing test**

Create `tests/test_services/test_ai/test_anthropic_provider.py`:

```python
import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, patch, MagicMock

import pytest

from gym_api.services.ai.anthropic_provider import AnthropicProvider
from gym_api.services.ai.types import WorkoutSummaryContext, WorkoutData


def _make_context() -> WorkoutSummaryContext:
    return WorkoutSummaryContext(
        client_name="Jane Smith",
        program_name="Upper/Lower Split",
        workouts=[
            WorkoutData(
                workout_id=uuid.uuid4(),
                date=datetime(2026, 2, 20, tzinfo=timezone.utc),
                duration_minutes=50,
                exercises=[
                    {"name": "Bench Press", "sets": 3, "reps": 8, "weight_lbs": 135},
                    {"name": "Bent Over Row", "sets": 3, "reps": 8, "weight_lbs": 115},
                ],
                total_volume_lbs=6000.0,
                completion_rate=1.0,
                prs_achieved=0,
            ),
            WorkoutData(
                workout_id=uuid.uuid4(),
                date=datetime(2026, 2, 22, tzinfo=timezone.utc),
                duration_minutes=45,
                exercises=[
                    {"name": "Back Squat", "sets": 4, "reps": 5, "weight_lbs": 185},
                    {"name": "Romanian Deadlift", "sets": 3, "reps": 10, "weight_lbs": 135},
                ],
                total_volume_lbs=7750.0,
                completion_rate=0.85,
                prs_achieved=1,
            ),
        ],
    )


@pytest.mark.asyncio
async def test_anthropic_provider_calls_api_and_returns_result():
    mock_response = MagicMock()
    mock_response.content = [MagicMock(text="Jane has been training consistently...")]
    mock_response.usage.input_tokens = 800
    mock_response.usage.output_tokens = 250

    mock_client = AsyncMock()
    mock_client.messages.create = AsyncMock(return_value=mock_response)

    provider = AnthropicProvider(api_key="test-key", model="claude-sonnet-4-20250514")
    provider._client = mock_client

    result = await provider.generate_summary(_make_context())

    assert result.summary_text == "Jane has been training consistently..."
    assert result.prompt_tokens == 800
    assert result.completion_tokens == 250
    mock_client.messages.create.assert_called_once()


@pytest.mark.asyncio
async def test_anthropic_provider_passes_model_to_api():
    mock_response = MagicMock()
    mock_response.content = [MagicMock(text="Summary text")]
    mock_response.usage.input_tokens = 100
    mock_response.usage.output_tokens = 50

    mock_client = AsyncMock()
    mock_client.messages.create = AsyncMock(return_value=mock_response)

    provider = AnthropicProvider(api_key="test-key", model="claude-haiku-4-5-20251001")
    provider._client = mock_client

    await provider.generate_summary(_make_context())

    call_kwargs = mock_client.messages.create.call_args.kwargs
    assert call_kwargs["model"] == "claude-haiku-4-5-20251001"
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_services/test_ai/test_anthropic_provider.py -v`
Expected: FAIL — `ModuleNotFoundError`

**Step 3: Create `src/gym_api/services/ai/prompt.py`**

```python
from gym_api.services.ai.types import WorkoutSummaryContext


def build_summary_prompt(context: WorkoutSummaryContext) -> str:
    lines = []
    lines.append(f"Client: {context.client_name}")
    if context.program_name:
        lines.append(f"Current Program: {context.program_name}")
    lines.append(f"Number of recent sessions: {len(context.workouts)}")
    lines.append("")

    for i, w in enumerate(context.workouts, 1):
        lines.append(f"--- Session {i} ({w.date.strftime('%Y-%m-%d')}) ---")
        lines.append(f"Duration: {w.duration_minutes or 'N/A'} minutes")
        lines.append(f"Total Volume: {w.total_volume_lbs:.0f} lbs")
        lines.append(f"Completion Rate: {w.completion_rate:.0%}")
        lines.append(f"PRs Achieved: {w.prs_achieved}")
        lines.append("Exercises:")
        for ex in w.exercises:
            weight = f" @ {ex['weight_lbs']} lbs" if ex.get("weight_lbs") else ""
            lines.append(f"  - {ex['name']}: {ex.get('sets', '?')}x{ex.get('reps', '?')}{weight}")
        lines.append("")

    return "\n".join(lines)


SYSTEM_PROMPT = """You are a fitness analytics assistant for personal trainers. Given a client's recent workout data, write a concise summary (2-3 short paragraphs) covering:

1. **Recap**: What they did — exercises, volume, session frequency, completion.
2. **Trends**: Volume changes, consistency patterns, muscle group balance.
3. **Notable events**: New PRs, skipped exercises, performance changes.

Write in third person, professional but approachable tone. Be specific with numbers. Do not give recommendations or advice — only observations and insights."""
```

**Step 4: Create `src/gym_api/services/ai/anthropic_provider.py`**

```python
import anthropic

from gym_api.services.ai.provider import SummaryProvider
from gym_api.services.ai.prompt import build_summary_prompt, SYSTEM_PROMPT
from gym_api.services.ai.types import WorkoutSummaryContext, SummaryResult


class AnthropicProvider(SummaryProvider):
    def __init__(self, api_key: str, model: str):
        self._client = anthropic.AsyncAnthropic(api_key=api_key)
        self._model = model

    async def generate_summary(self, context: WorkoutSummaryContext) -> SummaryResult:
        user_message = build_summary_prompt(context)
        response = await self._client.messages.create(
            model=self._model,
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_message}],
        )
        return SummaryResult(
            summary_text=response.content[0].text,
            prompt_tokens=response.usage.input_tokens,
            completion_tokens=response.usage.output_tokens,
        )
```

**Step 5: Run test to verify it passes**

Run: `pytest tests/test_services/test_ai/test_anthropic_provider.py -v`
Expected: PASS

**Step 6: Commit**

```bash
git add src/gym_api/services/ai/prompt.py src/gym_api/services/ai/anthropic_provider.py tests/test_services/test_ai/test_anthropic_provider.py
git commit -m "feat(ai): implement Anthropic summary provider with prompt template"
```

---

### Task 6: Implement OpenAI provider

**Files:**
- Create: `src/gym_api/services/ai/openai_provider.py`
- Test: `tests/test_services/test_ai/test_openai_provider.py`

**Step 1: Write the failing test**

Create `tests/test_services/test_ai/test_openai_provider.py`:

```python
import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest

from gym_api.services.ai.openai_provider import OpenAIProvider
from gym_api.services.ai.types import WorkoutSummaryContext, WorkoutData


@pytest.mark.asyncio
async def test_openai_provider_calls_api_and_returns_result():
    ctx = WorkoutSummaryContext(
        client_name="John Doe",
        program_name="Push/Pull",
        workouts=[
            WorkoutData(
                workout_id=uuid.uuid4(),
                date=datetime(2026, 2, 20, tzinfo=timezone.utc),
                duration_minutes=45,
                exercises=[{"name": "Bench Press", "sets": 3, "reps": 8, "weight_lbs": 185}],
                total_volume_lbs=4440.0,
                completion_rate=1.0,
                prs_achieved=0,
            ),
        ],
    )

    mock_choice = MagicMock()
    mock_choice.message.content = "John completed one session..."

    mock_response = MagicMock()
    mock_response.choices = [mock_choice]
    mock_response.usage.prompt_tokens = 900
    mock_response.usage.completion_tokens = 200

    mock_client = AsyncMock()
    mock_client.chat.completions.create = AsyncMock(return_value=mock_response)

    provider = OpenAIProvider(api_key="test-key", model="gpt-4o")
    provider._client = mock_client

    result = await provider.generate_summary(ctx)

    assert result.summary_text == "John completed one session..."
    assert result.prompt_tokens == 900
    assert result.completion_tokens == 200
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_services/test_ai/test_openai_provider.py -v`
Expected: FAIL — `ModuleNotFoundError`

**Step 3: Create `src/gym_api/services/ai/openai_provider.py`**

```python
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
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_services/test_ai/test_openai_provider.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/gym_api/services/ai/openai_provider.py tests/test_services/test_ai/test_openai_provider.py
git commit -m "feat(ai): implement OpenAI summary provider"
```

---

### Task 7: Create provider factory

**Files:**
- Create: `src/gym_api/services/ai/factory.py`
- Test: `tests/test_services/test_ai/test_factory.py`

**Step 1: Write the failing test**

Create `tests/test_services/test_ai/test_factory.py`:

```python
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
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_services/test_ai/test_factory.py -v`
Expected: FAIL — `ModuleNotFoundError`

**Step 3: Create `src/gym_api/services/ai/factory.py`**

```python
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
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_services/test_ai/test_factory.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/gym_api/services/ai/factory.py tests/test_services/test_ai/test_factory.py
git commit -m "feat(ai): add provider factory for LLM selection"
```

---

### Task 8: Implement summary service (data gathering + caching logic)

**Files:**
- Create: `src/gym_api/services/summary_service.py`
- Test: `tests/test_services/test_summary_service.py`

**Step 1: Write the failing test — cache miss triggers generation**

Create `tests/test_services/test_summary_service.py`:

```python
import uuid
from datetime import datetime, timezone, timedelta
from unittest.mock import AsyncMock, MagicMock

import pytest

from gym_api.services.summary_service import SummaryService
from gym_api.services.ai.types import SummaryResult


def _make_workout_row(client_id, ended_at, exercises=None):
    """Create a mock workout row with nested exercises/sets/measurements."""
    workout = MagicMock()
    workout.workout_id = uuid.uuid4()
    workout.client_id = client_id
    workout.started_at = ended_at - timedelta(minutes=50)
    workout.ended_at = ended_at
    workout.status = "completed"
    workout.program_id = None

    if exercises is None:
        ex = MagicMock()
        ex.exercise.name = "Back Squat"
        ex.status = "complete"
        ex.order_index = 0
        s = MagicMock()
        s.set_index = 1
        s.actual_reps = 5
        m = MagicMock()
        m.type = "weight"
        m.value = 225.0
        m.unit = "lbs"
        s.measurements = [m]
        ex.sets = [s]
        workout.exercises = [ex]
    else:
        workout.exercises = exercises

    return workout


def _make_analytics_row(workout_id):
    a = MagicMock()
    a.workout_id = workout_id
    a.total_weight_lifted_lbs = 3375.0
    a.total_reps = 15
    a.total_sets = 3
    a.duration_minutes = 50
    a.exercises_completed = 3
    a.exercises_skipped = 0
    a.completion_rate = 1.0
    a.prs_achieved_count = 0
    a.volume_by_muscle_group = {"legs": 3375.0}
    return a


@pytest.mark.asyncio
async def test_get_summary_generates_on_cache_miss():
    client_id = uuid.uuid4()
    gym_id = uuid.uuid4()
    now = datetime.now(timezone.utc)

    workouts = [_make_workout_row(client_id, now - timedelta(days=i)) for i in range(3)]
    analytics = [_make_analytics_row(w.workout_id) for w in workouts]

    mock_db = AsyncMock()
    # Query for cached summary — returns None
    # Query for latest workout ended_at — not needed on cache miss
    # Query for workouts — returns workouts
    # Query for analytics — returns analytics
    # Query for client — returns client
    # Query for program — returns None

    mock_provider = AsyncMock()
    mock_provider.generate_summary = AsyncMock(
        return_value=SummaryResult(
            summary_text="Client has been consistent...",
            prompt_tokens=1000,
            completion_tokens=300,
        )
    )

    service = SummaryService(provider=mock_provider, provider_name="anthropic", model_id="test-model")
    result = await service.get_summary(
        db=mock_db,
        client_id=client_id,
        gym_id=gym_id,
        workouts=workouts,
        analytics={a.workout_id: a for a in analytics},
        client_name="Test Client",
        program_name=None,
        cached_summary=None,
    )

    assert result.summary_text == "Client has been consistent..."
    mock_provider.generate_summary.assert_called_once()


@pytest.mark.asyncio
async def test_get_summary_returns_cache_when_valid():
    mock_provider = AsyncMock()

    cached = MagicMock()
    cached.summary_id = uuid.uuid4()
    cached.client_id = uuid.uuid4()
    cached.summary_text = "Cached summary text"
    cached.workouts_included = [uuid.uuid4()]
    cached.generated_at = datetime.now(timezone.utc)
    cached.model_provider = "anthropic"
    cached.model_id = "test-model"
    cached.token_usage = {"prompt_tokens": 500, "completion_tokens": 200}

    service = SummaryService(provider=mock_provider, provider_name="anthropic", model_id="test-model")
    result = await service.get_summary(
        db=AsyncMock(),
        client_id=cached.client_id,
        gym_id=uuid.uuid4(),
        workouts=[],
        analytics={},
        client_name="Test",
        program_name=None,
        cached_summary=cached,
    )

    assert result.summary_text == "Cached summary text"
    mock_provider.generate_summary.assert_not_called()
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_services/test_summary_service.py -v`
Expected: FAIL — `ModuleNotFoundError`

**Step 3: Create `src/gym_api/services/summary_service.py`**

```python
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

        # Upsert: delete old then insert new
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
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_services/test_summary_service.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/gym_api/services/summary_service.py tests/test_services/test_summary_service.py
git commit -m "feat(summary): implement summary service with cache-or-generate logic"
```

---

### Task 9: Create the API endpoint

**Files:**
- Create: `src/gym_api/routers/summaries.py`
- Modify: `src/gym_api/main.py`
- Test: `tests/test_routers/test_summaries.py`

**Step 1: Write the failing test**

Create `tests/test_routers/test_summaries.py`:

```python
import uuid
from datetime import datetime, timezone, timedelta
from unittest.mock import AsyncMock, patch, MagicMock

import pytest
from httpx import ASGITransport, AsyncClient

from gym_api.main import app


@pytest.fixture
def client_id():
    return uuid.uuid4()


@pytest.fixture
def gym_id():
    return uuid.uuid4()


@pytest.mark.asyncio
async def test_get_workout_summary_returns_cached(client_id, gym_id):
    cached = MagicMock()
    cached.summary_id = uuid.uuid4()
    cached.client_id = client_id
    cached.gym_id = gym_id
    cached.summary_text = "Cached summary"
    cached.workouts_included = [uuid.uuid4()]
    cached.generated_at = datetime.now(timezone.utc)
    cached.model_provider = "anthropic"
    cached.model_id = "test"
    cached.token_usage = {"prompt_tokens": 100, "completion_tokens": 50}

    with patch("gym_api.routers.summaries.get_cached_summary", new_callable=AsyncMock, return_value=cached), \
         patch("gym_api.routers.summaries.get_latest_workout_ended_at", new_callable=AsyncMock, return_value=cached.generated_at - timedelta(hours=1)), \
         patch("gym_api.routers.summaries.get_db", new_callable=AsyncMock):

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            resp = await ac.get(f"/v1/gyms/{gym_id}/clients/{client_id}/workout-summary")

        assert resp.status_code == 200
        body = resp.json()
        assert body["data"]["summary_text"] == "Cached summary"
        assert body["data"]["is_cached"] is True


@pytest.mark.asyncio
async def test_get_workout_summary_returns_404_when_no_workouts(client_id, gym_id):
    with patch("gym_api.routers.summaries.get_cached_summary", new_callable=AsyncMock, return_value=None), \
         patch("gym_api.routers.summaries.get_latest_workout_ended_at", new_callable=AsyncMock, return_value=None), \
         patch("gym_api.routers.summaries.get_db", new_callable=AsyncMock):

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            resp = await ac.get(f"/v1/gyms/{gym_id}/clients/{client_id}/workout-summary")

        assert resp.status_code == 404
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_routers/test_summaries.py -v`
Expected: FAIL — `ModuleNotFoundError`

**Step 3: Create `src/gym_api/routers/summaries.py`**

```python
import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from gym_api.config import settings
from gym_api.database import get_db
from gym_api.models.summary import ClientWorkoutSummary
from gym_api.models.workout import Workout, WorkoutExercise, WorkoutSet, WorkoutSetMeasurement
from gym_api.models.analytics import WorkoutAnalytics
from gym_api.models.client import Client
from gym_api.models.program import Program
from gym_api.services.ai.factory import create_summary_provider
from gym_api.services.summary_service import SummaryService

router = APIRouter(prefix="/v1/gyms/{gym_id}/clients/{client_id}", tags=["summaries"])

WORKOUT_HISTORY_LIMIT = 5


async def get_cached_summary(db: AsyncSession, client_id: uuid.UUID) -> ClientWorkoutSummary | None:
    result = await db.execute(
        select(ClientWorkoutSummary).where(ClientWorkoutSummary.client_id == client_id)
    )
    return result.scalar_one_or_none()


async def get_latest_workout_ended_at(db: AsyncSession, client_id: uuid.UUID) -> datetime | None:
    result = await db.execute(
        select(func.max(Workout.ended_at)).where(
            Workout.client_id == client_id,
            Workout.status == "completed",
        )
    )
    return result.scalar_one_or_none()


@router.get("/workout-summary")
async def get_workout_summary(
    gym_id: uuid.UUID,
    client_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    # 1. Check for cached summary
    cached = await get_cached_summary(db, client_id)

    # 2. Check latest workout timestamp
    latest_ended_at = await get_latest_workout_ended_at(db, client_id)

    if latest_ended_at is None:
        raise HTTPException(status_code=404, detail="No completed workouts found for this client")

    # 3. If cache is valid, return it
    if cached and cached.generated_at >= latest_ended_at:
        return _format_response(cached, is_cached=True)

    # 4. Cache miss or stale — gather data and generate
    workouts_result = await db.execute(
        select(Workout)
        .where(Workout.client_id == client_id, Workout.status == "completed")
        .options(
            selectinload(Workout.exercises)
            .selectinload(WorkoutExercise.exercise),
            selectinload(Workout.exercises)
            .selectinload(WorkoutExercise.sets)
            .selectinload(WorkoutSet.measurements),
        )
        .order_by(Workout.ended_at.desc())
        .limit(WORKOUT_HISTORY_LIMIT)
    )
    workouts = list(workouts_result.scalars().all())

    if not workouts:
        raise HTTPException(status_code=404, detail="No completed workouts found for this client")

    workout_ids = [w.workout_id for w in workouts]
    analytics_result = await db.execute(
        select(WorkoutAnalytics).where(WorkoutAnalytics.workout_id.in_(workout_ids))
    )
    analytics = {a.workout_id: a for a in analytics_result.scalars().all()}

    # Get client name
    client_result = await db.execute(select(Client).where(Client.client_id == client_id))
    client = client_result.scalar_one_or_none()
    client_name = f"{client.first_name} {client.last_name}" if client else "Unknown"

    # Get program name (from most recent workout)
    program_name = None
    if workouts[0].program_id:
        program_result = await db.execute(
            select(Program).where(Program.program_id == workouts[0].program_id)
        )
        program = program_result.scalar_one_or_none()
        program_name = program.name if program else None

    # Generate summary
    provider = create_summary_provider(
        settings.ai_summary_provider,
        api_key=settings.anthropic_api_key if settings.ai_summary_provider == "anthropic" else settings.openai_api_key,
        model=settings.ai_summary_model,
    )
    service = SummaryService(
        provider=provider,
        provider_name=settings.ai_summary_provider,
        model_id=settings.ai_summary_model,
    )
    summary = await service.get_summary(
        db=db,
        client_id=client_id,
        gym_id=gym_id,
        workouts=workouts,
        analytics=analytics,
        client_name=client_name,
        program_name=program_name,
        cached_summary=None,
    )

    return _format_response(summary, is_cached=False)


def _format_response(summary: ClientWorkoutSummary, is_cached: bool) -> dict:
    return {
        "data": {
            "summary_id": str(summary.summary_id),
            "client_id": str(summary.client_id),
            "summary_text": summary.summary_text,
            "workouts_included": [str(w) for w in summary.workouts_included],
            "generated_at": summary.generated_at.isoformat(),
            "is_cached": is_cached,
        },
        "meta": {},
    }
```

**Step 4: Register router in `src/gym_api/main.py`**

Add to `main.py`:

```python
from gym_api.routers.summaries import router as summaries_router

app.include_router(summaries_router)
```

**Step 5: Run test to verify it passes**

Run: `pytest tests/test_routers/test_summaries.py -v`
Expected: PASS

**Step 6: Commit**

```bash
git add src/gym_api/routers/summaries.py src/gym_api/main.py tests/test_routers/
git commit -m "feat(api): add GET workout-summary endpoint with cache-or-generate logic"
```

---

### Task 10: Add prompt template tests

**Files:**
- Test: `tests/test_services/test_ai/test_prompt.py`

**Step 1: Write the tests**

Create `tests/test_services/test_ai/test_prompt.py`:

```python
import uuid
from datetime import datetime, timezone

from gym_api.services.ai.prompt import build_summary_prompt, SYSTEM_PROMPT
from gym_api.services.ai.types import WorkoutSummaryContext, WorkoutData


def test_prompt_includes_client_name():
    ctx = WorkoutSummaryContext(
        client_name="Jane Smith",
        program_name="Push/Pull",
        workouts=[
            WorkoutData(
                workout_id=uuid.uuid4(),
                date=datetime(2026, 2, 20, tzinfo=timezone.utc),
                duration_minutes=45,
                exercises=[{"name": "Bench Press", "sets": 3, "reps": 8, "weight_lbs": 135}],
                total_volume_lbs=3240.0,
                completion_rate=1.0,
                prs_achieved=0,
            ),
        ],
    )
    prompt = build_summary_prompt(ctx)
    assert "Jane Smith" in prompt
    assert "Push/Pull" in prompt
    assert "Bench Press" in prompt
    assert "3240" in prompt


def test_prompt_handles_no_program():
    ctx = WorkoutSummaryContext(
        client_name="John",
        program_name=None,
        workouts=[
            WorkoutData(
                workout_id=uuid.uuid4(),
                date=datetime(2026, 2, 20, tzinfo=timezone.utc),
                duration_minutes=30,
                exercises=[],
                total_volume_lbs=0,
                completion_rate=0,
                prs_achieved=0,
            ),
        ],
    )
    prompt = build_summary_prompt(ctx)
    assert "John" in prompt
    assert "Program" not in prompt


def test_system_prompt_forbids_recommendations():
    assert "Do not give recommendations" in SYSTEM_PROMPT
```

**Step 2: Run tests**

Run: `pytest tests/test_services/test_ai/test_prompt.py -v`
Expected: PASS

**Step 3: Commit**

```bash
git add tests/test_services/test_ai/test_prompt.py
git commit -m "test(ai): add prompt template tests"
```

---

### Task 11: Run full test suite and verify

**Step 1: Run all tests**

Run: `pytest tests/ -v --tb=short`
Expected: All tests pass

**Step 2: Run linter (if configured)**

Run: `ruff check src/ tests/`
Expected: Clean or minor style issues

**Step 3: Fix any issues found, commit**

```bash
git add -A
git commit -m "fix: address linting and test issues"
```

---

## Summary

| Task | Description | Key Files |
|------|-------------|-----------|
| 1 | Project scaffold | `pyproject.toml`, `main.py`, `config.py`, `database.py` |
| 2 | Stub prerequisite models | `models/client.py`, `workout.py`, `exercise.py`, `program.py`, `analytics.py` |
| 3 | ClientWorkoutSummary model | `models/summary.py` + migration |
| 4 | LLM types + provider interface | `services/ai/types.py`, `provider.py` |
| 5 | Anthropic provider | `services/ai/anthropic_provider.py`, `prompt.py` |
| 6 | OpenAI provider | `services/ai/openai_provider.py` |
| 7 | Provider factory | `services/ai/factory.py` |
| 8 | Summary service | `services/summary_service.py` |
| 9 | API endpoint | `routers/summaries.py` |
| 10 | Prompt tests | `tests/test_services/test_ai/test_prompt.py` |
| 11 | Full test suite verification | All tests green |
