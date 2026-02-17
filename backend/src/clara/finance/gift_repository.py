import uuid
from collections.abc import Sequence

from sqlalchemy import func, select

from clara.base.repository import BaseRepository
from clara.finance.models import Gift


class GiftRepository(BaseRepository[Gift]):
    model = Gift

    async def list_by_direction(
        self, direction: str, *, offset: int = 0, limit: int = 50
    ) -> tuple[Sequence[Gift], int]:
        base = self._base_query().where(Gift.direction == direction)
        count_stmt = (
            select(func.count())
            .select_from(Gift)
            .where(Gift.vault_id == self.vault_id)
            .where(Gift.deleted_at.is_(None))
            .where(Gift.direction == direction)
        )
        total = (await self.session.execute(count_stmt)).scalar_one()
        items = (
            await self.session.execute(
                base.order_by(Gift.created_at.desc()).offset(offset).limit(limit)
            )
        ).scalars().all()
        return items, total

    async def list_by_contact(
        self, contact_id: uuid.UUID, *, offset: int = 0, limit: int = 50
    ) -> tuple[Sequence[Gift], int]:
        base = self._base_query().where(Gift.contact_id == contact_id)
        count_stmt = (
            select(func.count())
            .select_from(Gift)
            .where(Gift.vault_id == self.vault_id)
            .where(Gift.deleted_at.is_(None))
            .where(Gift.contact_id == contact_id)
        )
        total = (await self.session.execute(count_stmt)).scalar_one()
        items = (
            await self.session.execute(
                base.order_by(Gift.created_at.desc()).offset(offset).limit(limit)
            )
        ).scalars().all()
        return items, total
