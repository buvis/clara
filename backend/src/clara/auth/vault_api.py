import uuid
from datetime import datetime

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, ConfigDict
from sqlalchemy import select

from clara.auth.models import Vault, VaultMembership
from clara.deps import CurrentUser, Db

router = APIRouter()


class VaultRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    name: str
    created_at: datetime


class VaultCreate(BaseModel):
    name: str


@router.get("", response_model=list[VaultRead])
async def list_vaults(user: CurrentUser, db: Db):
    stmt = (
        select(Vault)
        .join(VaultMembership)
        .where(VaultMembership.user_id == user.id)
    )
    result = await db.execute(stmt)
    return [VaultRead.model_validate(v) for v in result.scalars().all()]


@router.post("", response_model=VaultRead, status_code=201)
async def create_vault(body: VaultCreate, user: CurrentUser, db: Db):
    vault = Vault(name=body.name)
    db.add(vault)
    await db.flush()
    membership = VaultMembership(
        user_id=user.id, vault_id=vault.id, role="owner"
    )
    db.add(membership)
    await db.flush()
    return VaultRead.model_validate(vault)


@router.get("/{vault_id}", response_model=VaultRead)
async def get_vault(vault_id: uuid.UUID, user: CurrentUser, db: Db):
    stmt = (
        select(Vault)
        .join(VaultMembership)
        .where(VaultMembership.user_id == user.id)
        .where(Vault.id == vault_id)
    )
    vault = (await db.execute(stmt)).scalar_one_or_none()
    if vault is None:
        raise HTTPException(status_code=404, detail="Vault not found")
    return VaultRead.model_validate(vault)
