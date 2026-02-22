import uuid
from datetime import UTC, datetime

from fastapi import APIRouter, HTTPException
from sqlalchemy import func, select, update

from clara.deps import CurrentUser, Db, VaultAccess
from clara.notifications.models import Notification
from clara.notifications.schemas import (
    NotificationMarkRead,
    NotificationRead,
    UnreadCount,
)

router = APIRouter()


@router.get("", response_model=list[NotificationRead])
async def list_notifications(
    vault_id: uuid.UUID, user: CurrentUser, db: Db, _access: VaultAccess
) -> list[NotificationRead]:
    stmt = (
        select(Notification)
        .where(
            Notification.vault_id == vault_id,
            Notification.user_id == user.id,
            Notification.deleted_at.is_(None),
        )
        .order_by(Notification.read.asc(), Notification.created_at.desc())
        .limit(100)
    )
    items = (await db.execute(stmt)).scalars().all()
    return [NotificationRead.model_validate(n) for n in items]


@router.get("/unread-count", response_model=UnreadCount)
async def unread_count(
    vault_id: uuid.UUID, user: CurrentUser, db: Db, _access: VaultAccess
) -> UnreadCount:
    stmt = (
        select(func.count())
        .select_from(Notification)
        .where(
            Notification.vault_id == vault_id,
            Notification.user_id == user.id,
            Notification.read.is_(False),
            Notification.deleted_at.is_(None),
        )
    )
    count = (await db.execute(stmt)).scalar_one()
    return UnreadCount(count=count)


@router.patch("/{notification_id}", response_model=NotificationRead)
async def mark_notification(
    vault_id: uuid.UUID,
    notification_id: uuid.UUID,
    body: NotificationMarkRead,
    user: CurrentUser,
    db: Db,
    _access: VaultAccess,
) -> NotificationRead:
    stmt = select(Notification).where(
        Notification.id == notification_id,
        Notification.vault_id == vault_id,
        Notification.user_id == user.id,
        Notification.deleted_at.is_(None),
    )
    notification = (await db.execute(stmt)).scalar_one_or_none()
    if notification is None:
        raise HTTPException(status_code=404, detail="Notification not found")
    notification.read = body.read
    await db.flush()
    return NotificationRead.model_validate(notification)


@router.post("/mark-all-read", status_code=204)
async def mark_all_read(
    vault_id: uuid.UUID, user: CurrentUser, db: Db, _access: VaultAccess
) -> None:
    stmt = (
        update(Notification)
        .where(
            Notification.vault_id == vault_id,
            Notification.user_id == user.id,
            Notification.read.is_(False),
            Notification.deleted_at.is_(None),
        )
        .values(read=True)
    )
    await db.execute(stmt)
    await db.flush()


@router.delete("/clear-read", status_code=204)
async def clear_read_notifications(
    vault_id: uuid.UUID, user: CurrentUser, db: Db, _access: VaultAccess
) -> None:
    stmt = (
        update(Notification)
        .where(
            Notification.vault_id == vault_id,
            Notification.user_id == user.id,
            Notification.read.is_(True),
            Notification.deleted_at.is_(None),
        )
        .values(deleted_at=datetime.now(UTC))
    )
    await db.execute(stmt)
    await db.flush()


@router.delete("/{notification_id}", status_code=204)
async def delete_notification(
    vault_id: uuid.UUID,
    notification_id: uuid.UUID,
    user: CurrentUser,
    db: Db,
    _access: VaultAccess,
) -> None:
    stmt = select(Notification).where(
        Notification.id == notification_id,
        Notification.vault_id == vault_id,
        Notification.user_id == user.id,
        Notification.deleted_at.is_(None),
    )
    notification = (await db.execute(stmt)).scalar_one_or_none()
    if notification is None:
        raise HTTPException(status_code=404, detail="Notification not found")
    notification.deleted_at = datetime.now(UTC)
    await db.flush()
