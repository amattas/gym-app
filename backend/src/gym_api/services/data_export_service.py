import json
import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from gym_api.models.check_in import GymCheckIn
from gym_api.models.client import Client
from gym_api.models.client_membership import ClientMembership
from gym_api.models.data_request import DataExportRequest, ExportStatus
from gym_api.models.goal import ClientGoal
from gym_api.models.measurement import Measurement
from gym_api.models.note import Note
from gym_api.models.workout import Workout, WorkoutExercise, WorkoutSet


async def create_export_request(
    db: AsyncSession,
    *,
    gym_id: uuid.UUID,
    client_id: uuid.UUID,
    format: str = "json",
) -> DataExportRequest:
    request = DataExportRequest(
        gym_id=gym_id,
        client_id=client_id,
        format=format,
    )
    db.add(request)
    await db.commit()
    await db.refresh(request)
    return request


async def get_export_request(
    db: AsyncSession, export_id: uuid.UUID
) -> DataExportRequest | None:
    result = await db.execute(
        select(DataExportRequest).where(DataExportRequest.export_id == export_id)
    )
    return result.scalar_one_or_none()


def _serialize(obj) -> dict | str:
    if isinstance(obj, uuid.UUID):
        return str(obj)
    if isinstance(obj, datetime):
        return obj.isoformat()
    return str(obj)


def _row_to_dict(row) -> dict:
    data = {}
    for col in row.__table__.columns:
        val = getattr(row, col.name)
        if val is None:
            data[col.name] = None
        elif isinstance(val, (uuid.UUID, datetime)):
            data[col.name] = _serialize(val)
        else:
            data[col.name] = val
    return data


async def generate_export_data(
    db: AsyncSession, gym_id: uuid.UUID, client_id: uuid.UUID
) -> dict:
    export = {}

    result = await db.execute(
        select(Client).where(Client.client_id == client_id, Client.gym_id == gym_id)
    )
    client = result.scalar_one_or_none()
    if client:
        export["profile"] = _row_to_dict(client)

    result = await db.execute(
        select(Measurement).where(Measurement.client_id == client_id)
    )
    export["measurements"] = [_row_to_dict(m) for m in result.scalars().all()]

    result = await db.execute(
        select(Workout).where(Workout.client_id == client_id)
    )
    workouts = result.scalars().all()
    workout_data = []
    for w in workouts:
        wd = _row_to_dict(w)
        ex_result = await db.execute(
            select(WorkoutExercise).where(WorkoutExercise.workout_id == w.workout_id)
        )
        exercises = ex_result.scalars().all()
        ex_data = []
        for ex in exercises:
            exd = _row_to_dict(ex)
            set_result = await db.execute(
                select(WorkoutSet).where(
                    WorkoutSet.workout_exercise_id == ex.workout_exercise_id
                )
            )
            exd["sets"] = [_row_to_dict(s) for s in set_result.scalars().all()]
            ex_data.append(exd)
        wd["exercises"] = ex_data
        workout_data.append(wd)
    export["workouts"] = workout_data

    result = await db.execute(
        select(ClientMembership).where(ClientMembership.client_id == client_id)
    )
    export["memberships"] = [_row_to_dict(m) for m in result.scalars().all()]

    result = await db.execute(
        select(ClientGoal).where(ClientGoal.client_id == client_id)
    )
    export["goals"] = [_row_to_dict(g) for g in result.scalars().all()]

    result = await db.execute(
        select(GymCheckIn).where(GymCheckIn.client_id == client_id)
    )
    export["check_ins"] = [_row_to_dict(c) for c in result.scalars().all()]

    result = await db.execute(
        select(Note).where(Note.notable_type == "client", Note.notable_id == str(client_id))
    )
    export["notes"] = [_row_to_dict(n) for n in result.scalars().all()]

    return export


async def process_export(
    db: AsyncSession, export_id: uuid.UUID
) -> DataExportRequest | None:
    request = await get_export_request(db, export_id)
    if not request or request.status != ExportStatus.pending:
        return request

    request.status = ExportStatus.processing
    await db.commit()

    try:
        data = await generate_export_data(db, request.gym_id, request.client_id)
        content = json.dumps(data, default=str, indent=2)
        request.download_url = f"data:application/json;base64,{_encode_base64(content)}"
        request.status = ExportStatus.completed
        request.completed_at = datetime.now(timezone.utc)
    except Exception:
        request.status = ExportStatus.failed

    await db.commit()
    await db.refresh(request)
    return request


def _encode_base64(content: str) -> str:
    import base64
    return base64.b64encode(content.encode()).decode()
