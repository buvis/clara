from sqlalchemy import or_
from sqlalchemy.orm import selectinload

from clara.base.repository import BaseRepository
from clara.contacts.models import Contact


class ContactRepository(BaseRepository[Contact]):
    model = Contact

    def _base_query(self):
        return super()._base_query().options(
            selectinload(Contact.contact_methods),
            selectinload(Contact.addresses),
            selectinload(Contact.tags),
            selectinload(Contact.pets),
        )

    async def search(self, query: str, *, offset: int = 0, limit: int = 50):
        pattern = f"%{query}%"
        stmt = (
            self._base_query()
            .where(
                or_(
                    Contact.first_name.ilike(pattern),
                    Contact.last_name.ilike(pattern),
                    Contact.nickname.ilike(pattern),
                )
            )
            .offset(offset)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()
