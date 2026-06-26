"""认证相关 Pydantic Schema"""

import uuid
import re
from typing import List
from pydantic import BaseModel, Field, field_validator


_EMAIL_PATTERN = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")


def _validate_email(v: str) -> str:
    if not _EMAIL_PATTERN.match(v):
        raise ValueError("邮箱格式不正确")
    return v


# ── 用户端 ──


class UserRegisterRequest(BaseModel):
    email: str
    password: str = Field(min_length=8, max_length=128)
    name: str = Field(min_length=1, max_length=100)
    company_name: str = Field(min_length=1, max_length=255)

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        if not _EMAIL_PATTERN.match(v):
            raise ValueError("邮箱格式不正确")
        return v


class UserLoginRequest(BaseModel):
    email: str
    password: str

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        if not _EMAIL_PATTERN.match(v):
            raise ValueError("邮箱格式不正确")
        return v


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TenantInfo(BaseModel):
    id: uuid.UUID
    name: str
    plan_type: str
    status: str

    model_config = {"from_attributes": True}


class UserInfo(BaseModel):
    id: uuid.UUID
    email: str
    name: str
    role: str
    is_active: bool

    model_config = {"from_attributes": True}


class UserLoginResponse(BaseModel):
    user: UserInfo
    tenant: TenantInfo
    token: TokenResponse


class UserMeResponse(BaseModel):
    user: UserInfo
    tenant: TenantInfo
    permissions: List[str]


class RefreshRequest(BaseModel):
    refresh_token: str


# ── 管理后台 ──


class AdminLoginRequest(BaseModel):
    email: str
    password: str

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        if not _EMAIL_PATTERN.match(v):
            raise ValueError("邮箱格式不正确")
        return v


class AdminInfo(BaseModel):
    id: uuid.UUID
    email: str
    name: str
    role: str

    model_config = {"from_attributes": True}


class AdminLoginResponse(BaseModel):
    admin: AdminInfo
    token: TokenResponse
