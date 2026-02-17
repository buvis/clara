import uuid
from collections.abc import Sequence

from sqlalchemy import func, select

from clara.base.repository import BaseRepository
from clara.notes.models import Note


class NoteRepository(BaseRepository[Note]):
    model = Note

    async def list_by_contact(
        self,
        contact_id: uuid.UUID,
        *,
        offset: int = 0,
        limit: int = 50,
    ) -> tuple[Sequence[Note], int]:
        base = self._base_query().where(Note.contact_id == contact_id)
        count_stmt = (
            select(func.count())
            .select_from(Note)
            .where(Note.vault_id == self.vault_id)
            .where(Note.deleted_at.is_(None))
            .where(Note.contact_id == contact_id)
        )
        total = (await self.session.execute(count_stmt)).scalar_one()
        items_stmt = base.offset(offset).limit(limit)
        result = await self.session.execute(items_stmt)
        return result.scalars().all(), total

    async def list_by_activity(
        self,
        activity_id: uuid.UUID,
        *,
        offset: int = 0,
        limit: int = 50,
    ) -> tuple[Sequence[Note], int]:
        base = self._base_query().where(Note.activity_id == activity_id)
        count_stmt = (
            select(func.count())
            .select_from(Note)
            .where(Note.vault_id == self.vault_id)
            .where(Note.deleted_at.is_(None))
            .where(Note.activity_id == activity_id)
        )
        total = (await self.session.execute(count_stmt)).scalar_one()
        items_stmt = base.offset(offset).limit(limit)
        result = await self.session.execute(items_stmt)
        return result.scalars().all(), total
