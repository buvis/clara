import uuid
from datetime import date

import vobject
from sqlalchemy.ext.asyncio import AsyncSession

from clara.contacts.models import Address, Contact, ContactMethod
from clara.contacts.repository import ContactRepository


async def import_vcard(
    session: AsyncSession, vault_id: uuid.UUID, vcard_data: str
) -> list[Contact]:
    repo = ContactRepository(session=session, vault_id=vault_id)
    created: list[Contact] = []

    for vcard in vobject.readComponents(vcard_data):
        first_name = ""
        last_name = ""
        if hasattr(vcard, "n"):
            last_name = vcard.n.value.family or ""
            first_name = vcard.n.value.given or ""
        elif hasattr(vcard, "fn"):
            parts = vcard.fn.value.split(" ", 1)
            first_name = parts[0]
            last_name = parts[1] if len(parts) > 1 else ""

        birthdate: date | None = None
        if hasattr(vcard, "bday"):
            try:
                bday_str = vcard.bday.value
                if isinstance(bday_str, str):
                    birthdate = date.fromisoformat(bday_str)
                else:
                    birthdate = bday_str
            except (ValueError, AttributeError):
                pass

        nickname: str | None = None
        if hasattr(vcard, "nickname"):
            nickname = vcard.nickname.value or None

        contact = await repo.create(
            first_name=first_name,
            last_name=last_name,
            nickname=nickname,
            birthdate=birthdate,
        )

        if hasattr(vcard, "email_list"):
            for email_entry in vcard.email_list:
                cm = ContactMethod(
                    vault_id=vault_id,
                    contact_id=contact.id,
                    type="email",
                    label=_get_type_param(email_entry),
                    value=email_entry.value,
                )
                session.add(cm)

        if hasattr(vcard, "tel_list"):
            for tel_entry in vcard.tel_list:
                cm = ContactMethod(
                    vault_id=vault_id,
                    contact_id=contact.id,
                    type="phone",
                    label=_get_type_param(tel_entry),
                    value=tel_entry.value,
                )
                session.add(cm)

        if hasattr(vcard, "adr_list"):
            for adr_entry in vcard.adr_list:
                adr = adr_entry.value
                addr = Address(
                    vault_id=vault_id,
                    contact_id=contact.id,
                    label=_get_type_param(adr_entry),
                    line1=adr.street or "",
                    city=adr.city or "",
                    postal_code=adr.code or "",
                    country=adr.country or "",
                )
                session.add(addr)

        await session.flush()
        created.append(contact)

    return created


def _get_type_param(entry) -> str:
    params = getattr(entry, "params", {})
    type_list = params.get("TYPE", [])
    if type_list:
        return type_list[0].lower()
    return ""


async def export_vcard(
    session: AsyncSession, vault_id: uuid.UUID
) -> str:
    repo = ContactRepository(session=session, vault_id=vault_id)
    contacts, _ = await repo.list(offset=0, limit=100000)
    output_parts: list[str] = []

    for contact in contacts:
        vc = vobject.vCard()

        vc.add("n")
        vc.n.value = vobject.vcard.Name(
            family=contact.last_name, given=contact.first_name
        )
        vc.add("fn")
        vc.fn.value = f"{contact.first_name} {contact.last_name}".strip()

        if contact.nickname:
            vc.add("nickname")
            vc.nickname.value = contact.nickname

        if contact.birthdate:
            vc.add("bday")
            vc.bday.value = contact.birthdate.isoformat()

        if hasattr(contact, "contact_methods"):
            for cm in contact.contact_methods:
                if cm.type == "email":
                    email = vc.add("email")
                    email.value = cm.value
                    if cm.label:
                        email.type_param = cm.label
                elif cm.type == "phone":
                    tel = vc.add("tel")
                    tel.value = cm.value
                    if cm.label:
                        tel.type_param = cm.label

        if hasattr(contact, "addresses"):
            for addr in contact.addresses:
                adr = vc.add("adr")
                adr.value = vobject.vcard.Address(
                    street=addr.line1,
                    city=addr.city,
                    code=addr.postal_code,
                    country=addr.country,
                )
                if addr.label:
                    adr.type_param = addr.label

        output_parts.append(vc.serialize())

    return "\r\n".join(output_parts)
