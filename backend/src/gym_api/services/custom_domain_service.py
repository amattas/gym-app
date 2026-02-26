import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from gym_api.models.custom_domain import CustomDomain, DomainStatus


async def create_domain(
    db: AsyncSession, *, gym_id: uuid.UUID, **kwargs
) -> CustomDomain:
    domain = CustomDomain(gym_id=gym_id, **kwargs)
    domain.dns_records = _generate_dns_records(domain.domain, domain.domain_type.value)
    db.add(domain)
    await db.commit()
    await db.refresh(domain)
    return domain


async def get_domain(
    db: AsyncSession, gym_id: uuid.UUID, domain_id: uuid.UUID
) -> CustomDomain | None:
    result = await db.execute(
        select(CustomDomain).where(
            CustomDomain.domain_id == domain_id,
            CustomDomain.gym_id == gym_id,
        )
    )
    return result.scalar_one_or_none()


async def list_domains(
    db: AsyncSession, gym_id: uuid.UUID
) -> list[CustomDomain]:
    result = await db.execute(
        select(CustomDomain)
        .where(CustomDomain.gym_id == gym_id)
        .order_by(CustomDomain.created_at.desc())
    )
    return list(result.scalars().all())


async def verify_domain(
    db: AsyncSession, domain: CustomDomain
) -> CustomDomain:
    domain.status = DomainStatus.verifying
    await db.commit()
    await db.refresh(domain)
    return domain


async def activate_domain(
    db: AsyncSession, domain: CustomDomain
) -> CustomDomain:
    domain.status = DomainStatus.active
    await db.commit()
    await db.refresh(domain)
    return domain


async def delete_domain(db: AsyncSession, domain: CustomDomain) -> None:
    await db.delete(domain)
    await db.commit()


def _generate_dns_records(domain: str, domain_type: str) -> dict:
    if domain_type == "email":
        return {
            "records": [
                {
                    "type": "TXT",
                    "name": domain,
                    "value": "v=spf1 include:_spf.gymapi.com ~all",
                },
                {
                    "type": "CNAME",
                    "name": f"mail.{domain}",
                    "value": "mail.gymapi.com",
                },
            ]
        }
    return {
        "records": [
            {
                "type": "CNAME",
                "name": domain,
                "value": "login.gymapi.com",
            },
        ]
    }
