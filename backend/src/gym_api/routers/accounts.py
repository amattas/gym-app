import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from gym_api.database import get_db
from gym_api.dependencies.gym_scope import get_gym_context
from gym_api.schemas.account import (
    AccountCreate,
    AccountMemberAdd,
    AccountResponse,
    AccountUpdate,
)
from gym_api.schemas.client import ClientResponse
from gym_api.services import account_service

router = APIRouter(prefix="/v1/accounts", tags=["accounts"])


@router.post("", status_code=201, response_model=dict)
async def create_account(
    body: AccountCreate,
    gym_id: uuid.UUID = Depends(get_gym_context),
    db: AsyncSession = Depends(get_db),
):
    account = await account_service.create_account(db, gym_id=gym_id, **body.model_dump())
    return {"data": AccountResponse.model_validate(account)}


@router.get("/{account_id}", response_model=dict)
async def get_account(
    account_id: uuid.UUID,
    gym_id: uuid.UUID = Depends(get_gym_context),
    db: AsyncSession = Depends(get_db),
):
    account = await account_service.get_account(db, gym_id, account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    return {"data": AccountResponse.model_validate(account)}


@router.get("/{account_id}/members", response_model=dict)
async def list_members(
    account_id: uuid.UUID,
    gym_id: uuid.UUID = Depends(get_gym_context),
    db: AsyncSession = Depends(get_db),
):
    members = await account_service.list_account_members(
        db, gym_id, account_id
    )
    return {
        "data": [ClientResponse.model_validate(m) for m in members]
    }


@router.post(
    "/{account_id}/members", status_code=201, response_model=dict
)
async def add_member(
    account_id: uuid.UUID,
    body: AccountMemberAdd,
    gym_id: uuid.UUID = Depends(get_gym_context),
    db: AsyncSession = Depends(get_db),
):
    account = await account_service.get_account(
        db, gym_id, account_id
    )
    if not account:
        raise HTTPException(
            status_code=404, detail="Account not found"
        )
    client = await account_service.add_member(
        db, account_id=account_id, client_id=body.client_id
    )
    if not client:
        raise HTTPException(
            status_code=404, detail="Client not found"
        )
    return {"data": ClientResponse.model_validate(client)}


@router.delete(
    "/{account_id}/members/{client_id}", status_code=204
)
async def remove_member(
    account_id: uuid.UUID,
    client_id: uuid.UUID,
    gym_id: uuid.UUID = Depends(get_gym_context),
    db: AsyncSession = Depends(get_db),
):
    account = await account_service.get_account(
        db, gym_id, account_id
    )
    if not account:
        raise HTTPException(
            status_code=404, detail="Account not found"
        )
    client = await account_service.remove_member(
        db, account_id=account_id, client_id=client_id
    )
    if not client:
        raise HTTPException(
            status_code=404, detail="Client not found"
        )


@router.patch("/{account_id}", response_model=dict)
async def update_account(
    account_id: uuid.UUID,
    body: AccountUpdate,
    gym_id: uuid.UUID = Depends(get_gym_context),
    db: AsyncSession = Depends(get_db),
):
    existing = await account_service.get_account(
        db, gym_id, account_id
    )
    if not existing:
        raise HTTPException(
            status_code=404, detail="Account not found"
        )
    account = await account_service.update_account(
        db,
        account_id=account_id,
        gym_id=gym_id,
        **body.model_dump(exclude_unset=True),
    )
    return {"data": AccountResponse.model_validate(account)}
