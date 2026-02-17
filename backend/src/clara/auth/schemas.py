import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    name: str = ""


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    email: str
    name: str
    is_active: bool
    locale: str
    timezone: str
    default_vault_id: uuid.UUID | None
    created_at: datetime


class AuthResponse(BaseModel):
    user: UserRead
    access_token: str
    vault_id: uuid.UUID | None
