import uuid
from typing import Annotated

from fastapi import APIRouter, Depends

from clara.base.schema import PaginatedResponse, PaginationMeta
from clara.contacts.repository import ContactRepository
from clara.contacts.schemas import ContactCreate, ContactRead, ContactUpdate
from clara.contacts.service import ContactService
from clara.deps import Db, VaultAccess
from clara.pagination import PaginationParams

router = APIRouter()


def get_contact_service(
    vault_id: uuid.UUID, db: Db, _access: VaultAccess
) -> ContactService:
    repo = ContactRepository(session=db, vault_id=vault_id)
    return ContactService(repo=repo)


ContactSvc = Annotated[ContactService, Depends(get_contact_service)]


@router.get("", response_model=PaginatedResponse[ContactRead])
async def list_contacts(svc: ContactSvc, pagination: PaginationParams = Depends()):
    items, total = await svc.list_contacts(
        offset=pagination.offset, limit=pagination.limit
    )
    return PaginatedResponse(
        items=[ContactRead.model_validate(c) for c in items],
        meta=PaginationMeta(
            total=total, offset=pagination.offset, limit=pagination.limit
        ),
    )


@router.get("/{contact_id}", response_model=ContactRead)
async def get_contact(contact_id: uuid.UUID, svc: ContactSvc):
    return ContactRead.model_validate(await svc.get_contact(contact_id))


@router.post("", response_model=ContactRead, status_code=201)
async def create_contact(body: ContactCreate, svc: ContactSvc):
    return ContactRead.model_validate(await svc.create_contact(body))


@router.patch("/{contact_id}", response_model=ContactRead)
async def update_contact(
    contact_id: uuid.UUID, body: ContactUpdate, svc: ContactSvc
):
    return ContactRead.model_validate(
        await svc.update_contact(contact_id, body)
    )


@router.delete("/{contact_id}", status_code=204)
async def delete_contact(contact_id: uuid.UUID, svc: ContactSvc):
    await svc.delete_contact(contact_id)
