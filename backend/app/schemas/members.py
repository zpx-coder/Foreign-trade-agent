"""成员管理 Pydantic Schema — Phase 7"""

import uuid
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class MemberResponse(BaseModel):
    id: uuid.UUID
    email: str
    name: str
    role: str
    is_active: bool
    last_login_at: Optional[datetime] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class MemberListResponse(BaseModel):
    items: List[MemberResponse]
    total: int


class InviteMemberRequest(BaseModel):
    email: str = Field(min_length=1, max_length=255)
    name: str = Field(min_length=1, max_length=100)
    password: str = Field(min_length=8, max_length=128)
    role: str = Field(default="sales", pattern="^(sales|readonly)$")


class UpdateMemberRequest(BaseModel):
    role: Optional[str] = Field(default=None, pattern="^(admin|sales|readonly)$")
    is_active: Optional[bool] = None


class ChangePasswordRequest(BaseModel):
    old_password: str = Field(min_length=1)
    new_password: str = Field(min_length=8, max_length=128)
    confirm_password: str = Field(min_length=8, max_length=128)


class SmtpConfigRequest(BaseModel):
    host: str = Field(default="smtp.gmail.com", max_length=255)
    port: int = Field(default=465, ge=1, le=65535)
    username: str = Field(min_length=1, max_length=255)
    password: str = Field(default="", max_length=255)
    from_name: str = Field(default="", max_length=100)
    from_email: str = Field(default="", max_length=255)


class SmtpConfigResponse(BaseModel):
    host: str
    port: int
    username: str
    password: str = ""  # 返回时脱敏，设为空或星号
    from_name: str
    from_email: str
