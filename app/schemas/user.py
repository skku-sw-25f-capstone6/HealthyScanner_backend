# app/schemas/user.py
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict


class UserBase(BaseModel):
    name: Optional[str] = None
    habits: Optional[List[str]] = None
    conditions: Optional[List[str]] = None
    allergies: Optional[List[str]] = None


class UserCreate(UserBase):
    # 지금은 별도 필수 필드 없음 (id는 서버에서 생성)
    pass


class UserUpdate(BaseModel):
    name: Optional[str] = None
    habits: Optional[List[str]] = None
    conditions: Optional[List[str]] = None
    allergies: Optional[List[str]] = None

    model_config = ConfigDict(extra="forbid")  # 이상한 필드는 막기


class UserOut(BaseModel):
    id: str
    name: Optional[str]
    habits: Optional[list[str]]
    conditions: Optional[list[str]]
    allergies: Optional[list[str]]
    profile_image_url: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class MyPageOut(BaseModel):
    name: str
    scan_count: int
    profile_image_url: Optional[str] = None