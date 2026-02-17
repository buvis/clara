from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from clara.base.model import VaultScopedModel
from clara.base.repository import BaseRepository


class FakeModel(VaultScopedModel):
    __tablename__ = "fake_for_test"
    name: Mapped[str] = mapped_column(String(255))


class FakeRepo(BaseRepository[FakeModel]):
    model = FakeModel


def test_repo_has_model():
    assert FakeRepo.model is FakeModel
