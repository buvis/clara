from datetime import date, timedelta

from dateutil.relativedelta import relativedelta
from sqlalchemy import select

from clara.jobs.sync_db import get_sync_session
from clara.reminders.models import Reminder, StayInTouchConfig


def _next_date(today: date, freq: str, n: int) -> date:
    if freq == "week":
        return today + timedelta(weeks=n)
    if freq == "month":
        return today + relativedelta(months=n)
    if freq == "year":
        return today + relativedelta(years=n)
    return today + timedelta(days=30 * n)


def evaluate_reminders():
    """Daily job: trigger due reminders, compute next occurrence for recurring."""
    session = get_sync_session()
    try:
        today = date.today()
        stmt = select(Reminder).where(
            Reminder.next_expected_date <= today,
            Reminder.status == "active",
            Reminder.deleted_at.is_(None),
        )
        reminders = session.execute(stmt).scalars().all()
        for r in reminders:
            r.last_triggered_at = today
            if r.frequency_type == "one_time":
                r.status = "completed"
            else:
                r.next_expected_date = _next_date(
                    today, r.frequency_type, r.frequency_number
                )
        session.commit()
    finally:
        session.close()


def evaluate_stay_in_touch():
    """Daily job: create reminders for contacts not contacted recently."""
    session = get_sync_session()
    try:
        today = date.today()
        configs = (
            session.execute(
                select(StayInTouchConfig).where(
                    StayInTouchConfig.deleted_at.is_(None)
                )
            )
            .scalars()
            .all()
        )
        for config in configs:
            if config.last_contacted_at is None:
                overdue = True
            else:
                days_since = (today - config.last_contacted_at.date()).days
                overdue = days_since >= config.target_interval_days
            if overdue:
                existing = session.execute(
                    select(Reminder).where(
                        Reminder.contact_id == config.contact_id,
                        Reminder.vault_id == config.vault_id,
                        Reminder.status == "active",
                        Reminder.title.like("Stay in touch%"),
                    )
                ).scalar_one_or_none()
                if existing is None:
                    reminder = Reminder(
                        vault_id=config.vault_id,
                        contact_id=config.contact_id,
                        title="Stay in touch",
                        next_expected_date=today,
                        frequency_type="one_time",
                        status="active",
                    )
                    session.add(reminder)
        session.commit()
    finally:
        session.close()
