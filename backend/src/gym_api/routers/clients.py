import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from gym_api.database import get_db
from gym_api.dependencies.gym_scope import get_gym_context
from gym_api.schemas.client import (
    ClientCreate,
    ClientResponse,
    ClientUpdate,
    EmergencyContactUpdate,
)
from gym_api.services import client_service

router = APIRouter(prefix="/v1/clients", tags=["clients"])


@router.post("", status_code=201, response_model=dict)
async def create_client(
    body: ClientCreate,
    gym_id: uuid.UUID = Depends(get_gym_context),
    db: AsyncSession = Depends(get_db),
):
    client = await client_service.create_client(db, gym_id=gym_id, **body.model_dump())
    return {"data": ClientResponse.model_validate(client)}


@router.get("", response_model=dict)
async def list_clients(
    cursor: str | None = Query(None),
    limit: int = Query(20, ge=1, le=100),
    gym_id: uuid.UUID = Depends(get_gym_context),
    db: AsyncSession = Depends(get_db),
):
    items, pagination = await client_service.list_clients(db, gym_id, cursor=cursor, limit=limit)
    return {
        "data": [ClientResponse.model_validate(c) for c in items],
        "pagination": pagination,
    }


@router.get("/{client_id}", response_model=dict)
async def get_client(
    client_id: uuid.UUID,
    gym_id: uuid.UUID = Depends(get_gym_context),
    db: AsyncSession = Depends(get_db),
):
    client = await client_service.get_client(db, gym_id, client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    return {"data": ClientResponse.model_validate(client)}


@router.patch("/{client_id}", response_model=dict)
async def update_client(
    client_id: uuid.UUID,
    body: ClientUpdate,
    gym_id: uuid.UUID = Depends(get_gym_context),
    db: AsyncSession = Depends(get_db),
):
    client = await client_service.get_client(db, gym_id, client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    client = await client_service.update_client(db, client, **body.model_dump(exclude_unset=True))
    return {"data": ClientResponse.model_validate(client)}


@router.delete("/{client_id}", status_code=204)
async def delete_client(
    client_id: uuid.UUID,
    gym_id: uuid.UUID = Depends(get_gym_context),
    db: AsyncSession = Depends(get_db),
):
    client = await client_service.get_client(db, gym_id, client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    await client_service.delete_client(db, client)


@router.get("/{client_id}/emergency-contact", response_model=dict)
async def get_emergency_contact(
    client_id: uuid.UUID,
    gym_id: uuid.UUID = Depends(get_gym_context),
    db: AsyncSession = Depends(get_db),
):
    client = await client_service.get_client(db, gym_id, client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    return {
        "data": {
            "emergency_contact_name": client.emergency_contact_name,
            "emergency_contact_phone": client.emergency_contact_phone,
        }
    }


@router.put("/{client_id}/emergency-contact", response_model=dict)
async def update_emergency_contact(
    client_id: uuid.UUID,
    body: EmergencyContactUpdate,
    gym_id: uuid.UUID = Depends(get_gym_context),
    db: AsyncSession = Depends(get_db),
):
    client = await client_service.get_client(db, gym_id, client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    client = await client_service.update_client(db, client, **body.model_dump())
    return {
        "data": {
            "emergency_contact_name": client.emergency_contact_name,
            "emergency_contact_phone": client.emergency_contact_phone,
        }
    }
