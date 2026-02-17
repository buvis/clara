import uuid
from collections.abc import Sequence
from datetime import date

from sqlalchemy import func, select

from clara.base.repository import BaseRepository
from clara.reminders.models import Reminder, StayInTouchConfig


class ReminderRepository(BaseRepository[Reminder]):
    model = Reminder

    async def list_by_status(
        self,
        status: str,
        *,
        offset: int = 0,
        limit: int = 50,
    ) -> tuple[Sequence[Reminder], int]:
        base = self._base_query().where(Reminder.status == status)
        count_stmt = (
            select(func.count())
            .select_from(Reminder)
            .where(Reminder.vault_id == self.vault_id)
            .where(Reminder.deleted_at.is_(None))
            .where(Reminder.status == status)
        )
        total = (await self.session.execute(count_stmt)).scalar_one()
        items_stmt = (
            base
            .order_by(Reminder.next_expected_date.asc())
            .offset(offset)
            .limit(limit)
        )
        result = await self.session.execute(items_stmt)
        return result.scalars().all(), total

    async def list_by_contact(
        self,
        contact_id: uuid.UUID,
        *,
        offset: int = 0,
        limit: int = 50,
    ) -> tuple[Sequence[Reminder], int]:
        base = self._base_query().where(Reminder.contact_id == contact_id)
        count_stmt = (
            select(func.count())
            .select_from(Reminder)
            .where(Reminder.vault_id == self.vault_id)
            .where(Reminder.deleted_at.is_(None))
            .where(Reminder.contact_id == contact_id)
        )
        total = (await self.session.execute(count_stmt)).scalar_one()
        items_stmt = (
            base
            .order_by(Reminder.next_expected_date.asc())
            .offset(offset)
            .limit(limit)
        )
        result = await self.session.execute(items_stmt)
        return result.scalars().all(), total

    async def list_upcoming(
        self,
        as_of: date,
        *,
        offset: int = 0,
        limit: int = 50,
    ) -> tuple[Sequence[Reminder], int]:
        base = (
            self._base_query()
            .where(Reminder.status == "active")
            .where(Reminder.next_expected_date >= as_of)
        )
        count_stmt = (
            select(func.count())
            .select_from(Reminder)
            .where(Reminder.vault_id == self.vault_id)
            .where(Reminder.deleted_at.is_(None))
            .where(Reminder.status == "active")
            .where(Reminder.next_expected_date >= as_of)
        )
        total = (await self.session.execute(count_stmt)).scalar_one()
        items_stmt = (
            base
            .order_by(Reminder.next_expected_date.asc())
            .offset(offset)
            .limit(limit)
        )
        result = await self.session.execute(items_stmt)
        return result.scalars().all(), total

    async def list_overdue(
        self,
        as_of: date,
        *,
        offset: int = 0,
        limit: int = 50,
    ) -> tuple[Sequence[Reminder], int]:
        base = (
            self._base_query()
            .where(Reminder.status == "active")
            .where(Reminder.next_expected_date < as_of)
        )
        count_stmt = (
            select(func.count())
            .select_from(Reminder)
            .where(Reminder.vault_id == self.vault_id)
            .where(Reminder.deleted_at.is_(None))
            .where(Reminder.status == "active")
            .where(Reminder.next_expected_date < as_of)
        )
        total = (await self.session.execute(count_stmt)).scalar_one()
        items_stmt = (
            base
            .order_by(Reminder.next_expected_date.asc())
            .offset(offset)
            .limit(limit)
        )
        result = await self.session.execute(items_stmt)
        return result.scalars().all(), total


class StayInTouchRepository(BaseRepository[StayInTouchConfig]):
    model = StayInTouchConfig

    async def get_by_contact(
        self, contact_id: uuid.UUID
    ) -> StayInTouchConfig | None:
        stmt = (
            self._base_query()
            .where(StayInTouchConfig.contact_id == contact_id)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
