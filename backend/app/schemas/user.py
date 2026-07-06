from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from enum import Enum


class UserRoleEnum(str, Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    RELATIONSHIP_MANAGER = "relationship_manager"
    TELLER = "teller"
    VIEWER = "viewer"


# ── Auth ──
class UserCreate(BaseModel):
    employee_id: str
    full_name: str
    email: EmailStr
    phone: Optional[str] = None
    password: str
    role: UserRoleEnum = UserRoleEnum.RELATIONSHIP_MANAGER
    branch: Optional[str] = None
    region: Optional[str] = None


class UserResponse(BaseModel):
    id: int
    employee_id: str
    full_name: str
    email: str
    phone: Optional[str]
    role: UserRoleEnum
    branch: Optional[str]
    region: Optional[str]
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class LoginRequest(BaseModel):
    employee_id: str
    password: str
