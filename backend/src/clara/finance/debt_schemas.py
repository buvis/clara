import uuid
from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class DebtRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    vault_id: uuid.UUID
    contact_id: uuid.UUID
    direction: str
    amount: Decimal
    currency: str
    due_date: date | None
    settled: bool
    notes: str | None
    created_at: datetime
    updated_at: datetime


class DebtCreate(BaseModel):
    contact_id: uuid.UUID
    direction: str
    amount: Decimal
    currency: str = "USD"
    due_date: date | None = None
    settled: bool = False
    notes: str | None = None


class DebtUpdate(BaseModel):
    contact_id: uuid.UUID | None = None
    direction: str | None = None
    amount: Decimal | None = None
    currency: str | None = None
    due_date: date | None = None
    settled: bool | None = None
    notes: str | None = None
