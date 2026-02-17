import uuid

from clara.base.repository import BaseRepository
from clara.files.models import File, FileLink


class FileRepository(BaseRepository[File]):
    model = File


class FileLinkRepository(BaseRepository[FileLink]):
    model = FileLink

    async def list_by_file(self, file_id: uuid.UUID) -> list[FileLink]:
        stmt = self._base_query().where(FileLink.file_id == file_id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def list_by_target(
        self, target_type: str, target_id: uuid.UUID
    ) -> list[FileLink]:
        stmt = (
            self._base_query()
            .where(FileLink.target_type == target_type)
            .where(FileLink.target_id == target_id)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
