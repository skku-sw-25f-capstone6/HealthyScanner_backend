# app/schemas/scan_history.py
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict


class ScanDecision(str, Enum):
    avoid = "avoid"
    caution = "caution"
    ok = "ok"


class ScanHistoryBase(BaseModel):
    scanned_at: Optional[datetime] = None  # 안 오면 서버에서 now로 채워줄 계획
    decision: Optional[ScanDecision] = None

    summary: Optional[str] = None
    ai_total_score: Optional[int] = None  # 0~100 (DB에서 더 넓게 허용하지만 논리상 0~100)

    conditions: Optional[List[str]] = None
    allergies: Optional[List[str]] = None
    habits: Optional[List[str]] = None

    ai_allergy_report: Optional[str] = None
    ai_condition_report: Optional[str] = None
    ai_alter_report: Optional[str] = None
    ai_vegan_report: Optional[str] = None
    ai_total_report: Optional[str] = None

    # [{"key":"heart_disease","level":"red"}, ...]
    caution_factors: Optional[List[Dict[str, Any]]] = None


class ScanHistoryCreate(ScanHistoryBase):
    user_id: str
    product_id: str


class ScanHistoryUpdate(BaseModel):
    scanned_at: Optional[datetime] = None
    decision: Optional[ScanDecision] = None

    summary: Optional[str] = None
    ai_total_score: Optional[int] = None

    conditions: Optional[List[str]] = None
    allergies: Optional[List[str]] = None
    habits: Optional[List[str]] = None

    ai_allergy_report: Optional[str] = None
    ai_condition_report: Optional[str] = None
    ai_alter_report: Optional[str] = None
    ai_vegan_report: Optional[str] = None
    ai_total_report: Optional[str] = None

    caution_factors: Optional[List[Dict[str, Any]]] = None

    model_config = ConfigDict(extra="forbid")


class ScanHistoryOut(ScanHistoryBase):
    id: str
    user_id: str
    product_id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
