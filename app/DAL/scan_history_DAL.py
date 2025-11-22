# app/DAL/scan_history_DAL.py
from datetime import datetime, timezone
from typing import List, Optional
from uuid import uuid4

from sqlalchemy.orm import Session

from app.models.scan_history import ScanHistory
from app.schemas.scan_history import ScanHistoryCreate, ScanHistoryUpdate


class ScanHistoryDAL:
    @staticmethod
    def create(db: Session, sh_in: ScanHistoryCreate) -> ScanHistory:
        scanned_at = sh_in.scanned_at or datetime.utcnow()

        scan = ScanHistory(
            id=str(uuid4()),
            user_id=sh_in.user_id,
            product_id=sh_in.product_id,
            scanned_at=scanned_at,
            decision=sh_in.decision.value if sh_in.decision is not None else None,
            summary=sh_in.summary,
            ai_total_score=sh_in.ai_total_score,
            conditions=sh_in.conditions,
            allergies=sh_in.allergies,
            habits=sh_in.habits,
            ai_allergy_report=sh_in.ai_allergy_report,
            ai_condition_report=sh_in.ai_condition_report,
            ai_alter_report=sh_in.ai_alter_report,
            ai_vegan_report=sh_in.ai_vegan_report,
            ai_total_report=sh_in.ai_total_report,
            caution_factors=sh_in.caution_factors,
        )
        db.add(scan)
        db.commit()
        db.refresh(scan)
        return scan

    @staticmethod
    def get(db: Session, scan_id: str) -> Optional[ScanHistory]:
        return (
            db.query(ScanHistory)
            .filter(ScanHistory.id == scan_id, ScanHistory.deleted_at.is_(None))
            .first()
        )

    @staticmethod
    def list(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        user_id: Optional[str] = None,
        product_id: Optional[str] = None,
    ) -> List[ScanHistory]:
        q = db.query(ScanHistory).filter(ScanHistory.deleted_at.is_(None))

        if user_id is not None:
            q = q.filter(ScanHistory.user_id == user_id)
        if product_id is not None:
            q = q.filter(ScanHistory.product_id == product_id)

        # 최신 스캔 먼저 보이게
        q = q.order_by(ScanHistory.scanned_at.desc())

        return q.offset(skip).limit(limit).all()

    @staticmethod
    def update(
        db: Session,
        scan_id: str,
        sh_in: ScanHistoryUpdate,
    ) -> Optional[ScanHistory]:
        scan = (
            db.query(ScanHistory)
            .filter(ScanHistory.id == scan_id, ScanHistory.deleted_at.is_(None))
            .first()
        )
        if not scan:
            return None

        data = sh_in.model_dump(exclude_unset=True)
        # Enum → 문자열 변환
        if "decision" in data and data["decision"] is not None:
            data["decision"] = data["decision"].value

        for field, value in data.items():
            setattr(scan, field, value)

        db.commit()
        db.refresh(scan)
        return scan

    @staticmethod
    def soft_delete(db: Session, scan_id: str) -> bool:
        scan = (
            db.query(ScanHistory)
            .filter(ScanHistory.id == scan_id, ScanHistory.deleted_at.is_(None))
            .first()
        )
        if not scan:
            return False

        scan.deleted_at = datetime.now(timezone.utc)
        db.commit()
        return True
