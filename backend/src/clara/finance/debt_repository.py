import uuid
from collections.abc import Sequence

from sqlalchemy import func, select

from clara.base.repository import BaseRepository
from clara.finance.models import Debt


class DebtRepository(BaseRepository[Debt]):
    model = Debt

    async def list_settled(
        self, settled: bool, *, offset: int = 0, limit: int = 50
    ) -> tuple[Sequence[Debt], int]:
        base = self._base_query().where(Debt.settled == settled)
        count_stmt = (
            select(func.count())
            .select_from(Debt)
            .where(Debt.vault_id == self.vault_id)
            .where(Debt.deleted_at.is_(None))
            .where(Debt.settled == settled)
        )
        total = (await self.session.execute(count_stmt)).scalar_one()
        items = (
            await self.session.execute(
                base.order_by(Debt.created_at.desc()).offset(offset).limit(limit)
            )
        ).scalars().all()
        return items, total

    async def list_by_contact(
        self, contact_id: uuid.UUID, *, offset: int = 0, limit: int = 50
    ) -> tuple[Sequence[Debt], int]:
        base = self._base_query().where(Debt.contact_id == contact_id)
        count_stmt = (
            select(func.count())
            .select_from(Debt)
            .where(Debt.vault_id == self.vault_id)
            .where(Debt.deleted_at.is_(None))
            .where(Debt.contact_id == contact_id)
        )
        total = (await self.session.execute(count_stmt)).scalar_one()
        items = (
            await self.session.execute(
                base.order_by(Debt.created_at.desc()).offset(offset).limit(limit)
            )
        ).scalars().all()
        return items, total

    async def list_by_direction(
        self, direction: str, *, offset: int = 0, limit: int = 50
    ) -> tuple[Sequence[Debt], int]:
        base = self._base_query().where(Debt.direction == direction)
        count_stmt = (
            select(func.count())
            .select_from(Debt)
            .where(Debt.vault_id == self.vault_id)
            .where(Debt.deleted_at.is_(None))
            .where(Debt.direction == direction)
        )
        total = (await self.session.execute(count_stmt)).scalar_one()
        items = (
            await self.session.execute(
                base.order_by(Debt.created_at.desc()).offset(offset).limit(limit)
            )
        ).scalars().all()
        return items, total
