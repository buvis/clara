import uuid
from datetime import UTC, datetime
from typing import Annotated

from fastapi import APIRouter, Depends

from clara.base.repository import BaseRepository
from clara.contacts.models import RelationshipType
from clara.contacts.sub_schemas import (
    RelationshipTypeCreate,
    RelationshipTypeRead,
    RelationshipTypeUpdate,
)
from clara.deps import Db, VaultAccess
from clara.exceptions import NotFoundError

router = APIRouter()


class RelationshipTypeRepository(BaseRepository[RelationshipType]):
    model = RelationshipType

    async def list_all(self) -> list[RelationshipType]:
        stmt = self._base_query().order_by(RelationshipType.created_at.desc())
        result = await self.session.execute(stmt)
        return list(result.scalars().all())


def get_repo(
    vault_id: uuid.UUID, db: Db, _access: VaultAccess
) -> RelationshipTypeRepository:
    return RelationshipTypeRepository(session=db, vault_id=vault_id)


Repo = Annotated[RelationshipTypeRepository, Depends(get_repo)]


@router.get("", response_model=list[RelationshipTypeRead])
async def list_relationship_types(repo: Repo):
    items = await repo.list_all()
    return [RelationshipTypeRead.model_validate(item) for item in items]


@router.post("", response_model=RelationshipTypeRead, status_code=201)
async def create_relationship_type(body: RelationshipTypeCreate, repo: Repo):
    item = await repo.create(**body.model_dump())
    return RelationshipTypeRead.model_validate(item)


@router.get("/{type_id}", response_model=RelationshipTypeRead)
async def get_relationship_type(type_id: uuid.UUID, repo: Repo):
    item = await repo.get_by_id(type_id)
    if item is None:
        raise NotFoundError("RelationshipType", type_id)
    return RelationshipTypeRead.model_validate(item)


@router.patch("/{type_id}", response_model=RelationshipTypeRead)
async def update_relationship_type(
    type_id: uuid.UUID, body: RelationshipTypeUpdate, repo: Repo
):
    item = await repo.get_by_id(type_id)
    if item is None:
        raise NotFoundError("RelationshipType", type_id)
    for key, value in body.model_dump(exclude_unset=True).items():
        setattr(item, key, value)
    await repo.session.flush()
    await repo.session.refresh(item)
    return RelationshipTypeRead.model_validate(item)


@router.delete("/{type_id}", status_code=204)
async def delete_relationship_type(type_id: uuid.UUID, repo: Repo):
    item = await repo.get_by_id(type_id)
    if item is None:
        raise NotFoundError("RelationshipType", type_id)
    item.deleted_at = datetime.now(UTC)
    await repo.session.flush()
