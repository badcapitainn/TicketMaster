from pydantic import BaseModel, EmailStr
from datetime import datetime
from app.models.user import UserRole


# ── Request schemas ──────────────────────────────────────────────────────────

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    role: UserRole = UserRole.standard_user


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    username: str | None = None
    email: EmailStr | None = None


class RoleUpdate(BaseModel):
    role: UserRole


# ── Response schemas ─────────────────────────────────────────────────────────

class UserOut(BaseModel):
    id: int
    username: str
    email: str
    role: UserRole
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Auth schemas ─────────────────────────────────────────────────────────────

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    user_id: int | None = None
    role: UserRole | None = None
