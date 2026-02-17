import uuid
from datetime import UTC, datetime
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import delete, select

from clara.base.repository import BaseRepository
from clara.contacts.models import (
    Address,
    Contact,
    ContactMethod,
    ContactRelationship,
    Pet,
    RelationshipType,
    Tag,
    contact_tags,
)
from clara.contacts.sub_schemas import (
    AddressCreate,
    AddressRead,
    AddressUpdate,
    ContactMethodCreate,
    ContactMethodRead,
    ContactMethodUpdate,
    ContactRelationshipCreate,
    ContactRelationshipRead,
    ContactTagAttach,
    PetCreate,
    PetRead,
    PetUpdate,
    TagCreate,
    TagRead,
)
from clara.deps import Db, VaultAccess
from clara.exceptions import NotFoundError


class ContactMethodRepository(BaseRepository[ContactMethod]):
    model = ContactMethod

    async def list_for_contact(self, contact_id: uuid.UUID) -> list[ContactMethod]:
        stmt = (
            self._base_query()
            .where(ContactMethod.contact_id == contact_id)
            .order_by(ContactMethod.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_for_contact(
        self, contact_id: uuid.UUID, method_id: uuid.UUID
    ) -> ContactMethod | None:
        stmt = self._base_query().where(
            ContactMethod.contact_id == contact_id,
            ContactMethod.id == method_id,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()


class AddressRepository(BaseRepository[Address]):
    model = Address

    async def list_for_contact(self, contact_id: uuid.UUID) -> list[Address]:
        stmt = (
            self._base_query()
            .where(Address.contact_id == contact_id)
            .order_by(Address.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_for_contact(
        self, contact_id: uuid.UUID, address_id: uuid.UUID
    ) -> Address | None:
        stmt = self._base_query().where(
            Address.contact_id == contact_id,
            Address.id == address_id,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()


class RelationshipRepository(BaseRepository[ContactRelationship]):
    model = ContactRelationship

    async def list_for_contact(
        self, contact_id: uuid.UUID
    ) -> list[ContactRelationship]:
        stmt = (
            self._base_query()
            .where(ContactRelationship.contact_id == contact_id)
            .order_by(ContactRelationship.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_for_contact(
        self, contact_id: uuid.UUID, relationship_id: uuid.UUID
    ) -> ContactRelationship | None:
        stmt = self._base_query().where(
            ContactRelationship.contact_id == contact_id,
            ContactRelationship.id == relationship_id,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()


class PetRepository(BaseRepository[Pet]):
    model = Pet

    async def list_for_contact(self, contact_id: uuid.UUID) -> list[Pet]:
        stmt = (
            self._base_query()
            .where(Pet.contact_id == contact_id)
            .order_by(Pet.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_for_contact(
        self, contact_id: uuid.UUID, pet_id: uuid.UUID
    ) -> Pet | None:
        stmt = self._base_query().where(
            Pet.contact_id == contact_id,
            Pet.id == pet_id,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()


class TagRepository(BaseRepository[Tag]):
    model = Tag

    async def list_all(self) -> list[Tag]:
        stmt = self._base_query().order_by(Tag.created_at.desc())
        result = await self.session.execute(stmt)
        return list(result.scalars().all())


async def _get_contact_or_404(
    db: Db, vault_id: uuid.UUID, contact_id: uuid.UUID
) -> Contact:
    stmt = select(Contact).where(
        Contact.id == contact_id,
        Contact.vault_id == vault_id,
        Contact.deleted_at.is_(None),
    )
    contact = (await db.execute(stmt)).scalar_one_or_none()
    if contact is None:
        raise NotFoundError("Contact", contact_id)
    return contact


async def _require_contact(
    vault_id: uuid.UUID, contact_id: uuid.UUID, db: Db, _access: VaultAccess
) -> Contact:
    return await _get_contact_or_404(db=db, vault_id=vault_id, contact_id=contact_id)


def get_contact_method_repo(
    vault_id: uuid.UUID, db: Db, _access: VaultAccess
) -> ContactMethodRepository:
    return ContactMethodRepository(session=db, vault_id=vault_id)


def get_address_repo(
    vault_id: uuid.UUID, db: Db, _access: VaultAccess
) -> AddressRepository:
    return AddressRepository(session=db, vault_id=vault_id)


def get_relationship_repo(
    vault_id: uuid.UUID, db: Db, _access: VaultAccess
) -> RelationshipRepository:
    return RelationshipRepository(session=db, vault_id=vault_id)


def get_pet_repo(vault_id: uuid.UUID, db: Db, _access: VaultAccess) -> PetRepository:
    return PetRepository(session=db, vault_id=vault_id)


def get_tag_repo(vault_id: uuid.UUID, db: Db, _access: VaultAccess) -> TagRepository:
    return TagRepository(session=db, vault_id=vault_id)


RequiredContact = Annotated[Contact, Depends(_require_contact)]
MethodRepo = Annotated[ContactMethodRepository, Depends(get_contact_method_repo)]
AddressRepo = Annotated[AddressRepository, Depends(get_address_repo)]
RelRepo = Annotated[RelationshipRepository, Depends(get_relationship_repo)]
PetRepo = Annotated[PetRepository, Depends(get_pet_repo)]
TagsRepo = Annotated[TagRepository, Depends(get_tag_repo)]

methods_router = APIRouter()
addresses_router = APIRouter()
relationships_router = APIRouter()
pets_router = APIRouter()
contact_tags_router = APIRouter()
vault_tags_router = APIRouter()


@methods_router.get("", response_model=list[ContactMethodRead])
async def list_contact_methods(
    contact_id: uuid.UUID, _contact: RequiredContact, repo: MethodRepo
):
    items = await repo.list_for_contact(contact_id)
    return [ContactMethodRead.model_validate(item) for item in items]


@methods_router.post("", response_model=ContactMethodRead, status_code=201)
async def create_contact_method(
    contact_id: uuid.UUID,
    body: ContactMethodCreate,
    _contact: RequiredContact,
    repo: MethodRepo,
):
    item = await repo.create(contact_id=contact_id, **body.model_dump())
    return ContactMethodRead.model_validate(item)


@methods_router.patch("/{method_id}", response_model=ContactMethodRead)
async def update_contact_method(
    contact_id: uuid.UUID,
    method_id: uuid.UUID,
    body: ContactMethodUpdate,
    _contact: RequiredContact,
    repo: MethodRepo,
):
    item = await repo.get_for_contact(contact_id, method_id)
    if item is None:
        raise NotFoundError("ContactMethod", method_id)
    for key, value in body.model_dump(exclude_unset=True).items():
        setattr(item, key, value)
    await repo.session.flush()
    return ContactMethodRead.model_validate(item)


@methods_router.delete("/{method_id}", status_code=204)
async def delete_contact_method(
    contact_id: uuid.UUID,
    method_id: uuid.UUID,
    _contact: RequiredContact,
    repo: MethodRepo,
):
    item = await repo.get_for_contact(contact_id, method_id)
    if item is None:
        raise NotFoundError("ContactMethod", method_id)
    item.deleted_at = datetime.now(UTC)
    await repo.session.flush()


@addresses_router.get("", response_model=list[AddressRead])
async def list_addresses(
    contact_id: uuid.UUID, _contact: RequiredContact, repo: AddressRepo
):
    items = await repo.list_for_contact(contact_id)
    return [AddressRead.model_validate(item) for item in items]


@addresses_router.post("", response_model=AddressRead, status_code=201)
async def create_address(
    contact_id: uuid.UUID,
    body: AddressCreate,
    _contact: RequiredContact,
    repo: AddressRepo,
):
    item = await repo.create(contact_id=contact_id, **body.model_dump())
    return AddressRead.model_validate(item)


@addresses_router.patch("/{address_id}", response_model=AddressRead)
async def update_address(
    contact_id: uuid.UUID,
    address_id: uuid.UUID,
    body: AddressUpdate,
    _contact: RequiredContact,
    repo: AddressRepo,
):
    item = await repo.get_for_contact(contact_id, address_id)
    if item is None:
        raise NotFoundError("Address", address_id)
    for key, value in body.model_dump(exclude_unset=True).items():
        setattr(item, key, value)
    await repo.session.flush()
    return AddressRead.model_validate(item)


@addresses_router.delete("/{address_id}", status_code=204)
async def delete_address(
    contact_id: uuid.UUID,
    address_id: uuid.UUID,
    _contact: RequiredContact,
    repo: AddressRepo,
):
    item = await repo.get_for_contact(contact_id, address_id)
    if item is None:
        raise NotFoundError("Address", address_id)
    item.deleted_at = datetime.now(UTC)
    await repo.session.flush()


@relationships_router.get("", response_model=list[ContactRelationshipRead])
async def list_relationships(
    contact_id: uuid.UUID, _contact: RequiredContact, repo: RelRepo
):
    items = await repo.list_for_contact(contact_id)
    return [ContactRelationshipRead.model_validate(item) for item in items]


@relationships_router.post(
    "", response_model=ContactRelationshipRead, status_code=201
)
async def create_relationship(
    vault_id: uuid.UUID,
    contact_id: uuid.UUID,
    body: ContactRelationshipCreate,
    db: Db,
    _contact: RequiredContact,
    repo: RelRepo,
):
    await _get_contact_or_404(
        db=db, vault_id=vault_id, contact_id=body.other_contact_id
    )

    relationship_type = await db.get(RelationshipType, body.relationship_type_id)
    if relationship_type is None or relationship_type.vault_id != vault_id:
        raise NotFoundError("RelationshipType", body.relationship_type_id)
    if relationship_type.deleted_at is not None:
        raise NotFoundError("RelationshipType", body.relationship_type_id)

    relationship = await repo.create(
        contact_id=contact_id,
        other_contact_id=body.other_contact_id,
        relationship_type_id=body.relationship_type_id,
    )
    if relationship_type.inverse_type_id is not None:
        await repo.create(
            contact_id=body.other_contact_id,
            other_contact_id=contact_id,
            relationship_type_id=relationship_type.inverse_type_id,
        )
    return ContactRelationshipRead.model_validate(relationship)


@relationships_router.delete("/{relationship_id}", status_code=204)
async def delete_relationship(
    contact_id: uuid.UUID,
    relationship_id: uuid.UUID,
    db: Db,
    _contact: RequiredContact,
    repo: RelRepo,
):
    relationship = await repo.get_for_contact(contact_id, relationship_id)
    if relationship is None:
        raise NotFoundError("ContactRelationship", relationship_id)

    relationship_type = await db.get(
        RelationshipType, relationship.relationship_type_id
    )
    relationship.deleted_at = datetime.now(UTC)

    if (
        relationship_type is not None
        and relationship_type.inverse_type_id is not None
    ):
        inverse_stmt = repo._base_query().where(
            ContactRelationship.contact_id == relationship.other_contact_id,
            ContactRelationship.other_contact_id == relationship.contact_id,
            ContactRelationship.relationship_type_id
            == relationship_type.inverse_type_id,
        )
        inverse_relationships = (await db.execute(inverse_stmt)).scalars().all()
        now = datetime.now(UTC)
        for inverse in inverse_relationships:
            inverse.deleted_at = now
    await repo.session.flush()


@pets_router.get("", response_model=list[PetRead])
async def list_pets(contact_id: uuid.UUID, _contact: RequiredContact, repo: PetRepo):
    items = await repo.list_for_contact(contact_id)
    return [PetRead.model_validate(item) for item in items]


@pets_router.post("", response_model=PetRead, status_code=201)
async def create_pet(
    contact_id: uuid.UUID,
    body: PetCreate,
    _contact: RequiredContact,
    repo: PetRepo,
):
    item = await repo.create(contact_id=contact_id, **body.model_dump())
    return PetRead.model_validate(item)


@pets_router.patch("/{pet_id}", response_model=PetRead)
async def update_pet(
    contact_id: uuid.UUID,
    pet_id: uuid.UUID,
    body: PetUpdate,
    _contact: RequiredContact,
    repo: PetRepo,
):
    item = await repo.get_for_contact(contact_id, pet_id)
    if item is None:
        raise NotFoundError("Pet", pet_id)
    for key, value in body.model_dump(exclude_unset=True).items():
        setattr(item, key, value)
    await repo.session.flush()
    return PetRead.model_validate(item)


@pets_router.delete("/{pet_id}", status_code=204)
async def delete_pet(
    contact_id: uuid.UUID,
    pet_id: uuid.UUID,
    _contact: RequiredContact,
    repo: PetRepo,
):
    item = await repo.get_for_contact(contact_id, pet_id)
    if item is None:
        raise NotFoundError("Pet", pet_id)
    item.deleted_at = datetime.now(UTC)
    await repo.session.flush()


@contact_tags_router.get("", response_model=list[TagRead])
async def list_contact_tags(
    contact_id: uuid.UUID,
    _contact: RequiredContact,
    repo: TagsRepo,
):
    stmt = (
        repo._base_query()
        .join(contact_tags, contact_tags.c.tag_id == Tag.id)
        .where(contact_tags.c.contact_id == contact_id)
        .order_by(Tag.created_at.desc())
    )
    items = (await repo.session.execute(stmt)).scalars().all()
    return [TagRead.model_validate(item) for item in items]


@contact_tags_router.post("", response_model=TagRead, status_code=201)
async def attach_tag(
    contact_id: uuid.UUID,
    body: ContactTagAttach,
    _contact: RequiredContact,
    repo: TagsRepo,
):
    tag = await repo.get_by_id(body.tag_id)
    if tag is None:
        raise NotFoundError("Tag", body.tag_id)

    exists_stmt = select(contact_tags.c.tag_id).where(
        contact_tags.c.contact_id == contact_id,
        contact_tags.c.tag_id == body.tag_id,
    )
    existing = (await repo.session.execute(exists_stmt)).scalar_one_or_none()
    if existing is None:
        await repo.session.execute(
            contact_tags.insert().values(contact_id=contact_id, tag_id=body.tag_id)
        )
    return TagRead.model_validate(tag)


@contact_tags_router.delete("/{tag_id}", status_code=204)
async def detach_tag(
    contact_id: uuid.UUID,
    tag_id: uuid.UUID,
    _contact: RequiredContact,
    repo: TagsRepo,
):
    await repo.session.execute(
        delete(contact_tags).where(
            contact_tags.c.contact_id == contact_id,
            contact_tags.c.tag_id == tag_id,
        )
    )


@vault_tags_router.get("", response_model=list[TagRead])
async def list_tags(repo: TagsRepo):
    items = await repo.list_all()
    return [TagRead.model_validate(item) for item in items]


@vault_tags_router.post("", response_model=TagRead, status_code=201)
async def create_tag(body: TagCreate, repo: TagsRepo):
    item = await repo.create(**body.model_dump())
    return TagRead.model_validate(item)
