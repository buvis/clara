import uuid

from sqlalchemy import Boolean, ForeignKey, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from clara.base.model import Base, TimestampMixin


class Vault(TimestampMixin, Base):
    __tablename__ = "vaults"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255))
    members: Mapped[list["VaultMembership"]] = relationship(back_populates="vault")


class User(TimestampMixin, Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(255), default="")
    hashed_password: Mapped[str] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    default_vault_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, ForeignKey("vaults.id"), nullable=True
    )
    memberships: Mapped[list["VaultMembership"]] = relationship(back_populates="user")


class VaultMembership(TimestampMixin, Base):
    __tablename__ = "vault_memberships"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("users.id"))
    vault_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("vaults.id"))
    role: Mapped[str] = mapped_column(String(50), default="owner")

    user: Mapped[User] = relationship(back_populates="memberships")
    vault: Mapped[Vault] = relationship(back_populates="members")
