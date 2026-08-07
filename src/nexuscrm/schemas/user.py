"""Pydantic schemas for User & Auth."""

from typing import Optional
from pydantic import BaseModel, EmailStr, ConfigDict
from nexuscrm.models.user import UserRole


class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    role: UserRole = UserRole.SALES_REP


class UserCreate(UserBase):
    password: str


class UserResponse(UserBase):
    id: str
    is_active: bool

    model_config = ConfigDict(from_attributes=True)



class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    email: Optional[str] = None
