import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from gym_api.models.agreement import AgreementEnvelope, AgreementTemplate, EnvelopeStatus
from gym_api.utils.pagination import apply_cursor_pagination, build_pagination_meta


async def create_template(
    db: AsyncSession, *, gym_id: uuid.UUID, **kwargs
) -> AgreementTemplate:
    template = AgreementTemplate(gym_id=gym_id, **kwargs)
    db.add(template)
    await db.commit()
    await db.refresh(template)
    return template


async def get_template(
    db: AsyncSession, gym_id: uuid.UUID, template_id: uuid.UUID
) -> AgreementTemplate | None:
    result = await db.execute(
        select(AgreementTemplate).where(
            AgreementTemplate.agreement_template_id == template_id,
            AgreementTemplate.gym_id == gym_id,
        )
    )
    return result.scalar_one_or_none()


async def list_templates(
    db: AsyncSession,
    gym_id: uuid.UUID,
    *,
    is_active: bool | None = None,
    cursor: str | None = None,
    limit: int = 20,
) -> tuple[list[AgreementTemplate], dict]:
    query = select(AgreementTemplate).where(AgreementTemplate.gym_id == gym_id)
    if is_active is not None:
        query = query.where(AgreementTemplate.is_active.is_(is_active))
    query = apply_cursor_pagination(
        query, order_column=AgreementTemplate.created_at, cursor=cursor, limit=limit
    )
    result = await db.execute(query)
    items = list(result.scalars().all())
    items, pagination = build_pagination_meta(items, limit, "created_at")
    return items, pagination


async def update_template(
    db: AsyncSession, template: AgreementTemplate, **kwargs
) -> AgreementTemplate:
    for key, value in kwargs.items():
        if value is not None:
            setattr(template, key, value)
    await db.commit()
    await db.refresh(template)
    return template


async def delete_template(db: AsyncSession, template: AgreementTemplate) -> None:
    await db.delete(template)
    await db.commit()


async def send_envelope(
    db: AsyncSession, *, gym_id: uuid.UUID, **kwargs
) -> AgreementEnvelope:
    envelope = AgreementEnvelope(
        gym_id=gym_id,
        status=EnvelopeStatus.sent,
        provider="internal",
        **kwargs,
    )
    db.add(envelope)
    await db.commit()
    await db.refresh(envelope)
    return envelope


async def get_envelope(
    db: AsyncSession, envelope_id: uuid.UUID
) -> AgreementEnvelope | None:
    result = await db.execute(
        select(AgreementEnvelope).where(
            AgreementEnvelope.envelope_id == envelope_id
        )
    )
    return result.scalar_one_or_none()


async def list_envelopes(
    db: AsyncSession,
    gym_id: uuid.UUID,
    *,
    client_id: uuid.UUID | None = None,
    status: str | None = None,
    cursor: str | None = None,
    limit: int = 20,
) -> tuple[list[AgreementEnvelope], dict]:
    query = select(AgreementEnvelope).where(AgreementEnvelope.gym_id == gym_id)
    if client_id:
        query = query.where(AgreementEnvelope.client_id == client_id)
    if status:
        query = query.where(AgreementEnvelope.status == status)
    query = apply_cursor_pagination(
        query, order_column=AgreementEnvelope.created_at, cursor=cursor, limit=limit
    )
    result = await db.execute(query)
    items = list(result.scalars().all())
    items, pagination = build_pagination_meta(items, limit, "created_at")
    return items, pagination


async def update_envelope_status(
    db: AsyncSession, envelope: AgreementEnvelope, *, status: EnvelopeStatus
) -> AgreementEnvelope:
    envelope.status = status
    await db.commit()
    await db.refresh(envelope)
    return envelope
