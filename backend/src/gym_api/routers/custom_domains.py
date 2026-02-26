import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from gym_api.database import get_db
from gym_api.dependencies.auth import get_current_user
from gym_api.dependencies.gym_scope import get_gym_context
from gym_api.schemas.custom_domain import CustomDomainCreate, CustomDomainResponse
from gym_api.services import custom_domain_service

router = APIRouter(prefix="/v1/domains", tags=["domains"])


@router.post("", status_code=201, response_model=dict)
async def create_domain(
    body: CustomDomainCreate,
    gym_id: uuid.UUID = Depends(get_gym_context),
    db: AsyncSession = Depends(get_db),
    _user=Depends(get_current_user),
):
    domain = await custom_domain_service.create_domain(
        db, gym_id=gym_id, **body.model_dump()
    )
    return {"data": CustomDomainResponse.model_validate(domain)}


@router.get("", response_model=dict)
async def list_domains(
    gym_id: uuid.UUID = Depends(get_gym_context),
    db: AsyncSession = Depends(get_db),
    _user=Depends(get_current_user),
):
    domains = await custom_domain_service.list_domains(db, gym_id)
    return {"data": [CustomDomainResponse.model_validate(d) for d in domains]}


@router.get("/{domain_id}", response_model=dict)
async def get_domain(
    domain_id: uuid.UUID,
    gym_id: uuid.UUID = Depends(get_gym_context),
    db: AsyncSession = Depends(get_db),
    _user=Depends(get_current_user),
):
    domain = await custom_domain_service.get_domain(db, gym_id, domain_id)
    if not domain:
        raise HTTPException(status_code=404, detail="Domain not found")
    return {"data": CustomDomainResponse.model_validate(domain)}


@router.post("/{domain_id}/verify", response_model=dict)
async def verify_domain(
    domain_id: uuid.UUID,
    gym_id: uuid.UUID = Depends(get_gym_context),
    db: AsyncSession = Depends(get_db),
    _user=Depends(get_current_user),
):
    domain = await custom_domain_service.get_domain(db, gym_id, domain_id)
    if not domain:
        raise HTTPException(status_code=404, detail="Domain not found")
    domain = await custom_domain_service.verify_domain(db, domain)
    return {"data": CustomDomainResponse.model_validate(domain)}


@router.delete("/{domain_id}", status_code=204)
async def delete_domain(
    domain_id: uuid.UUID,
    gym_id: uuid.UUID = Depends(get_gym_context),
    db: AsyncSession = Depends(get_db),
    _user=Depends(get_current_user),
):
    domain = await custom_domain_service.get_domain(db, gym_id, domain_id)
    if not domain:
        raise HTTPException(status_code=404, detail="Domain not found")
    await custom_domain_service.delete_domain(db, domain)
