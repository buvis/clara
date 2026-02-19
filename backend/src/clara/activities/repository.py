import uuid
from collections.abc import Sequence

from sqlalchemy import Select, select
from sqlalchemy.orm import selectinload

from clara.activities.models import Activity, ActivityParticipant, ActivityType
from clara.base.repository import BaseRepository


class ActivityTypeRepository(BaseRepository[ActivityType]):
    model = ActivityType


class ActivityRepository(BaseRepository[Activity]):
    model = Activity

    def _base_query(self) -> Select[tuple[Activity]]:
        return (
            super()
            ._base_query()
            .options(selectinload(Activity.participants))
            .order_by(Activity.happened_at.desc())
        )

    async def list_by_contact(
        self, contact_id: uuid.UUID, *, offset: int = 0, limit: int = 50
    ) -> Sequence[Activity]:
        stmt = (
            self._base_query()
            .join(ActivityParticipant)
            .where(ActivityParticipant.contact_id == contact_id)
            .offset(offset)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return result.scalars().unique().all()


class ActivityParticipantRepository(BaseRepository[ActivityParticipant]):
    model = ActivityParticipant

    async def delete_by_activity(self, activity_id: uuid.UUID) -> None:
        stmt = (
            select(ActivityParticipant)
            .where(ActivityParticipant.activity_id == activity_id)
            .where(ActivityParticipant.vault_id == self.vault_id)
            .where(ActivityParticipant.deleted_at.is_(None))
        )
        result = await self.session.execute(stmt)
        for p in result.scalars().all():
            await self.session.delete(p)
        await self.session.flush()
