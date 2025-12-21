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
    display_name:  Optional[str] = None
    display_category: Optional[str] = None
    image_url: Optional[str] = None
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

    ai_vegan_brief: Optional[str] = None
    ai_allergy_brief: Optional[str] = None
    ai_condition_brief: Optional[str] = None
    ai_alter_brief: Optional[str] = None

    product_name: Optional[str] = None
    product_ingredient: Optional[str] = None
    product_nutrition: Optional[Dict[str, Any]] = None

    dirty: Optional[bool] = False

    # [{"key":"heart_disease","level":"red"}, ...]
    caution_factors: Optional[List[Dict[str, Any]]] = None


class ScanHistoryCreate(ScanHistoryBase):
    user_id: str
    product_id: str | None


class ScanHistoryUpdate(ScanHistoryBase):
    model_config = ConfigDict(extra="forbid")


class ScanHistoryOut(ScanHistoryBase):
    id: str
    user_id: str
    product_id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class ScanHistoryNameCategoryIn(BaseModel):
    name: str
    category: str

class ScanHistoryNameCategoryOut(BaseModel):
    name: str | None
    category: str | None
    updated_at: datetime | None

class RiskLevel(str, Enum):
    green = "green"
    yellow = "yellow"
    red = "red"

class FaceType(str, Enum):
    GOOD = "GOOD"
    NO = "NO"
    NOT_BAD = "NOT BAD"

class ReportBlock(BaseModel):
    brief_report: Optional[str] = None
    face: FaceType
    report: Optional[str] = None

class AlternativeReport(ReportBlock):
    """필요하면 나중에 필드 추가할 용도, 지금은 ReportBlock과 동일"""
    pass

class CautionFactor(BaseModel):
    factor: str          # 예: "hypertension"
    evaluation: str      # 예: "NO"

class ScanReports(BaseModel):
    allergies: Optional[ReportBlock] = None
    condition: Optional[ReportBlock] = None
    alternatives: List[AlternativeReport] = []
    vegan: Optional[ReportBlock] = None


class ScanDetailOut(BaseModel):
    summary: str
    risk_level: RiskLevel
    reports: ScanReports
    caution_factors: List[CautionFactor] = []

class ScanSummaryOut(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    scanID: Optional[str] = None
    riskLevel: Optional[str] = None
    summary: Optional[str] = None
    url: Optional[str] = None


class ScanHistoryListOut(BaseModel):
    scan: List[ScanSummaryOut]