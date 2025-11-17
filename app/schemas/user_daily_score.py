# app/schemas/user_daily_score.py
from datetime import date, datetime
from enum import Enum
from typing import Dict, Optional

from pydantic import BaseModel, ConfigDict


class MaxSeverity(str, Enum):
    none = "none"
    info = "info"
    warning = "warning"
    danger = "danger"


class UserDailyScoreBase(BaseModel):
    score: int  # 0~100

    num_scans: int = 0
    max_severity: Optional[MaxSeverity] = None
    decision_counts: Optional[Dict[str, int]] = None

    formula_version: int = 1
    dirty: int = 0
    last_computed_at: Optional[datetime] = None

    sync_state: int = 1


class UserDailyScoreCreate(UserDailyScoreBase):
    user_id: str
    local_date: date


class UserDailyScoreUpdate(BaseModel):
    score: Optional[int] = None
    num_scans: Optional[int] = None
    max_severity: Optional[MaxSeverity] = None
    decision_counts: Optional[Dict[str, int]] = None
    formula_version: Optional[int] = None
    dirty: Optional[int] = None
    last_computed_at: Optional[datetime] = None
    sync_state: Optional[int] = None

    model_config = ConfigDict(extra="forbid")


class UserDailyScoreOut(UserDailyScoreBase):
    user_id: str
    local_date: date
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
