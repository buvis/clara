from collections.abc import Sequence
from datetime import date

from sqlalchemy import func, select

from clara.base.repository import BaseRepository
from clara.tasks.models import Task


class TaskRepository(BaseRepository[Task]):
    model = Task

    async def list_by_status(
        self, status: str, *, offset: int = 0, limit: int = 50
    ) -> tuple[Sequence[Task], int]:
        base = self._base_query().where(Task.status == status)
        count_stmt = (
            select(func.count())
            .select_from(Task)
            .where(Task.vault_id == self.vault_id)
            .where(Task.deleted_at.is_(None))
            .where(Task.status == status)
        )
        total = (await self.session.execute(count_stmt)).scalar_one()
        items = (
            await self.session.execute(
                base.order_by(Task.created_at.desc()).offset(offset).limit(limit)
            )
        ).scalars().all()
        return items, total

    async def list_by_due_date_range(
        self, start: date, end: date, *, offset: int = 0, limit: int = 50
    ) -> tuple[Sequence[Task], int]:
        base = self._base_query().where(
            Task.due_date >= start, Task.due_date <= end
        )
        count_stmt = (
            select(func.count())
            .select_from(Task)
            .where(Task.vault_id == self.vault_id)
            .where(Task.deleted_at.is_(None))
            .where(Task.due_date >= start)
            .where(Task.due_date <= end)
        )
        total = (await self.session.execute(count_stmt)).scalar_one()
        items = (
            await self.session.execute(
                base.order_by(Task.due_date.asc()).offset(offset).limit(limit)
            )
        ).scalars().all()
        return items, total

    async def list_overdue(
        self, *, offset: int = 0, limit: int = 50
    ) -> tuple[Sequence[Task], int]:
        today = date.today()
        base = self._base_query().where(
            Task.due_date < today, Task.status != "done"
        )
        count_stmt = (
            select(func.count())
            .select_from(Task)
            .where(Task.vault_id == self.vault_id)
            .where(Task.deleted_at.is_(None))
            .where(Task.due_date < today)
            .where(Task.status != "done")
        )
        total = (await self.session.execute(count_stmt)).scalar_one()
        items = (
            await self.session.execute(
                base.order_by(Task.due_date.asc()).offset(offset).limit(limit)
            )
        ).scalars().all()
        return items, total
