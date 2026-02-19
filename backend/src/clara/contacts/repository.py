import uuid
from collections.abc import Sequence
from datetime import date
from typing import Any

from sqlalchemy import Select, func, or_, select
from sqlalchemy.orm import selectinload

from clara.base.repository import BaseRepository
from clara.contacts.models import Contact, contact_tags


class ContactRepository(BaseRepository[Contact]):
    model = Contact

    def _base_query(self) -> Select[tuple[Contact]]:
        return super()._base_query().options(
            selectinload(Contact.contact_methods),
            selectinload(Contact.addresses),
            selectinload(Contact.tags),
            selectinload(Contact.pets),
            selectinload(Contact.relationships),
        )

    def _apply_filters(
        self,
        stmt: Select[Any],
        *,
        q: str | None = None,
        tag_ids: list[uuid.UUID] | None = None,
        favorites: bool | None = None,
        birthday_from: date | None = None,
        birthday_to: date | None = None,
    ) -> Select[Any]:
        if q:
            pattern = f"%{q}%"
            stmt = stmt.where(
                or_(
                    Contact.first_name.ilike(pattern),
                    Contact.last_name.ilike(pattern),
                    Contact.nickname.ilike(pattern),
                )
            )
        if tag_ids:
            stmt = stmt.join(
                contact_tags, contact_tags.c.contact_id == Contact.id
            ).where(contact_tags.c.tag_id.in_(tag_ids))
        if favorites is not None:
            stmt = stmt.where(Contact.favorite.is_(favorites))
        if birthday_from is not None:
            stmt = stmt.where(Contact.birthdate >= birthday_from)
        if birthday_to is not None:
            stmt = stmt.where(Contact.birthdate <= birthday_to)
        return stmt

    async def list_filtered(
        self,
        *,
        offset: int = 0,
        limit: int = 50,
        q: str | None = None,
        tag_ids: list[uuid.UUID] | None = None,
        favorites: bool | None = None,
        birthday_from: date | None = None,
        birthday_to: date | None = None,
    ) -> tuple[Sequence[Contact], int]:
        count_stmt = self._apply_filters(
            select(func.count(func.distinct(self.model.id)))
            .select_from(self.model)
            .where(self.model.vault_id == self.vault_id)
            .where(self.model.deleted_at.is_(None)),
            q=q, tag_ids=tag_ids, favorites=favorites,
            birthday_from=birthday_from, birthday_to=birthday_to,
        )
        total: int = (await self.session.execute(count_stmt)).scalar_one()
        items_stmt = self._apply_filters(
            self._base_query(),
            q=q, tag_ids=tag_ids, favorites=favorites,
            birthday_from=birthday_from, birthday_to=birthday_to,
        )
        if tag_ids:
            items_stmt = items_stmt.distinct()
        items_stmt = (
            items_stmt.offset(offset)
            .limit(limit)
            .order_by(Contact.created_at.desc())
        )
        result = await self.session.execute(items_stmt)
        return result.scalars().all(), total

    async def search(
        self, query: str, *, offset: int = 0, limit: int = 50
    ) -> tuple[Sequence[Contact], int]:
        return await self.list_filtered(q=query, offset=offset, limit=limit)
