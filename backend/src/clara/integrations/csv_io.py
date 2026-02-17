import csv
import io
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from clara.contacts.models import Contact
from clara.contacts.repository import ContactRepository

DEFAULT_FIELD_MAP = {
    "first_name": "first_name",
    "last_name": "last_name",
    "nickname": "nickname",
    "gender": "gender",
    "pronouns": "pronouns",
}


async def import_csv(
    session: AsyncSession,
    vault_id: uuid.UUID,
    csv_data: str,
    field_map: dict[str, str] | None = None,
) -> list[Contact]:
    mapping = field_map or DEFAULT_FIELD_MAP
    repo = ContactRepository(session=session, vault_id=vault_id)
    created: list[Contact] = []

    reader = csv.DictReader(io.StringIO(csv_data))
    for row in reader:
        kwargs: dict[str, str] = {}
        for csv_col, model_field in mapping.items():
            value = row.get(csv_col, "").strip()
            if value:
                kwargs[model_field] = value

        if not kwargs.get("first_name"):
            continue

        contact = await repo.create(**kwargs)
        created.append(contact)

    return created


async def export_csv(
    session: AsyncSession, vault_id: uuid.UUID
) -> str:
    repo = ContactRepository(session=session, vault_id=vault_id)
    contacts, _ = await repo.list(offset=0, limit=100000)

    columns = [
        "first_name",
        "last_name",
        "nickname",
        "birthdate",
        "gender",
        "pronouns",
        "favorite",
    ]

    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=columns)
    writer.writeheader()

    for contact in contacts:
        writer.writerow(
            {
                "first_name": contact.first_name,
                "last_name": contact.last_name,
                "nickname": contact.nickname or "",
                "birthdate": (
                    contact.birthdate.isoformat()
                    if contact.birthdate
                    else ""
                ),
                "gender": contact.gender or "",
                "pronouns": contact.pronouns or "",
                "favorite": str(contact.favorite),
            }
        )

    return output.getvalue()
