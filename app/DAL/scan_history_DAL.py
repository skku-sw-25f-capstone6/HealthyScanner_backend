# app/DAL/scan_history_DAL.py
from datetime import datetime, timezone, date
from typing import List, Optional, Dict, Any
from uuid import uuid4
from sqlalchemy import func, desc, asc
from sqlalchemy.orm import Session

from app.models.scan_history import ScanHistory
from app.schemas.scan_history import ScanHistoryCreate, ScanHistoryUpdate


class ScanHistoryDAL:
    @staticmethod
    def create(db: Session, sh_in: ScanHistoryCreate) -> ScanHistory:
        scanned_at = sh_in.scanned_at or datetime.now(timezone.utc).replace(tzinfo=None)

        scan = ScanHistory(
            id=str(uuid4()),
            user_id=sh_in.user_id,
            product_id=sh_in.product_id,
            scanned_at=scanned_at,
            display_name=sh_in.display_name,
            display_category=sh_in.display_category,
            image_url=sh_in.image_url,
            decision=sh_in.decision,
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
            product_name=sh_in.product_name,
            product_nutrition=sh_in.product_nutrition,
            product_ingredient=sh_in.product_ingredient
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
    def get_by_date(db: Session, user_id: str, date: datetime):
        return (
            db.query(ScanHistory)
            .filter(
                ScanHistory.user_id == user_id,
                func.date(ScanHistory.scanned_at) == date.date(),
                ScanHistory.deleted_at.is_(None),
            )
            .order_by(ScanHistory.scanned_at.desc())
            .all()
        )

    @staticmethod
    def count_scans_date(
        db: Session,
        user_id: str,
        local_date: date,
    ) -> int:
        """
        특정 user + 날짜에 대한 스캔 개수 반환
        """
        count = (
            db.query(func.count(ScanHistory.id))
            .filter(
                ScanHistory.user_id == user_id,
                # scanned_at의 날짜 부분이 local_date와 같은 것만
                func.date(ScanHistory.scanned_at) == local_date,
            )
            .scalar()
        )

        return int(count or 0)

    @staticmethod
    def get_scan_order_for_day(
        db: Session,
        user_id: str,
        local_date: date,
        scan_id: str,
    ) -> int:
        """
        특정 user + 날짜에서, scan_id가 몇 번째 스캔인지(1-based index) 반환
        """
        rows = (
            db.query(ScanHistory.id)
            .filter(
                ScanHistory.user_id == user_id,
                func.date(ScanHistory.scanned_at) == local_date,
                ScanHistory.deleted_at.is_(None),
            )
            .order_by(asc(ScanHistory.scanned_at), asc(ScanHistory.id))
            .all()
        )

        ids = [row[0] for row in rows]
        try:
            idx = ids.index(scan_id)
        except ValueError:
            # 혹시 리스트에 없으면 일단 맨 뒤라고 가정
            idx = len(ids) - 1 if ids else 0

        return idx + 1  # 1번부터 시작

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

    @staticmethod
    def get_ai_score_stats_for_day(
        db: Session,
        user_id: str,
        local_date: date,
    ) -> Dict[str, Any]:
        """
        특정 user + 날짜에 대한 ai_total_score 개수 / 평균값 반환
        반환 예: {"count": 3, "avg_score": 72.3}
        """
        count, avg_score = (
            db.query(
                func.count(ScanHistory.id),
                func.avg(ScanHistory.ai_total_score),
            )
            .filter(
                ScanHistory.user_id == user_id,
                # scanned_at의 날짜 부분이 local_date와 같은 것만
                func.date(ScanHistory.scanned_at) == local_date,
            )
            .one()
        )

        return {
            "count": int(count or 0),
            "avg_score": float(avg_score) if avg_score is not None else None,
        }
        
    @staticmethod
    def get_recent_scans_for_user(
        db: Session,
        user_id: str,
        limit: int = 2,
    ) -> List[ScanHistory]:
        return (
            db.query(ScanHistory)
            .filter(ScanHistory.user_id == user_id)
            .order_by(desc(ScanHistory.scanned_at))
            .limit(limit)
            .all()
        )
