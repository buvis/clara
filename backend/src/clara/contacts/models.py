import uuid
from datetime import date

from sqlalchemy import Boolean, Date, ForeignKey, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from clara.base.model import VaultScopedModel


class Contact(VaultScopedModel):
    __tablename__ = "contacts"

    first_name: Mapped[str] = mapped_column(String(255))
    last_name: Mapped[str] = mapped_column(String(255), default="")
    nickname: Mapped[str | None] = mapped_column(String(255))
    birthdate: Mapped[date | None] = mapped_column(Date)
    gender: Mapped[str | None] = mapped_column(String(50))
    pronouns: Mapped[str | None] = mapped_column(String(100))
    notes_summary: Mapped[str | None] = mapped_column(Text)
    favorite: Mapped[bool] = mapped_column(Boolean, default=False)
    photo_file_id: Mapped[uuid.UUID | None] = mapped_column(Uuid, nullable=True)
    template_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, ForeignKey("templates.id"), nullable=True
    )

    contact_methods: Mapped[list["ContactMethod"]] = relationship(
        back_populates="contact", cascade="all, delete-orphan"
    )
    addresses: Mapped[list["Address"]] = relationship(
        back_populates="contact", cascade="all, delete-orphan"
    )
    tags: Mapped[list["Tag"]] = relationship(
        secondary="contact_tags", back_populates="contacts"
    )
    pets: Mapped[list["Pet"]] = relationship(
        back_populates="contact", cascade="all, delete-orphan"
    )


class ContactMethod(VaultScopedModel):
    __tablename__ = "contact_methods"

    contact_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("contacts.id")
    )
    type: Mapped[str] = mapped_column(String(50))
    label: Mapped[str] = mapped_column(String(100), default="")
    value: Mapped[str] = mapped_column(String(500))

    contact: Mapped[Contact] = relationship(back_populates="contact_methods")


class Address(VaultScopedModel):
    __tablename__ = "addresses"

    contact_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("contacts.id")
    )
    label: Mapped[str] = mapped_column(String(100), default="")
    line1: Mapped[str] = mapped_column(String(500), default="")
    line2: Mapped[str | None] = mapped_column(String(500))
    city: Mapped[str] = mapped_column(String(255), default="")
    postal_code: Mapped[str] = mapped_column(String(50), default="")
    country: Mapped[str] = mapped_column(String(100), default="")

    contact: Mapped[Contact] = relationship(back_populates="addresses")


class RelationshipType(VaultScopedModel):
    __tablename__ = "relationship_types"

    name: Mapped[str] = mapped_column(String(100))
    inverse_name: Mapped[str] = mapped_column(String(100))


class ContactRelationship(VaultScopedModel):
    __tablename__ = "contact_relationships"

    contact_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("contacts.id")
    )
    other_contact_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("contacts.id")
    )
    relationship_type_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("relationship_types.id")
    )


class Tag(VaultScopedModel):
    __tablename__ = "tags"

    name: Mapped[str] = mapped_column(String(100))
    color: Mapped[str] = mapped_column(String(7), default="#6b7280")

    contacts: Mapped[list[Contact]] = relationship(
        secondary="contact_tags", back_populates="tags"
    )


class ContactTag(VaultScopedModel):
    __tablename__ = "contact_tags"

    contact_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("contacts.id")
    )
    tag_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("tags.id")
    )


class Pet(VaultScopedModel):
    __tablename__ = "pets"

    contact_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("contacts.id")
    )
    name: Mapped[str] = mapped_column(String(255))
    species: Mapped[str] = mapped_column(String(100), default="")
    birthdate: Mapped[date | None] = mapped_column(Date)
    notes: Mapped[str | None] = mapped_column(Text)

    contact: Mapped[Contact] = relationship(back_populates="pets")
