from datetime import datetime, timezone, date, timedelta
from typing import Dict, Any, List, Optional, cast

from sqlalchemy.orm import Session

from app.services.user_daily_score_service import UserDailyScoreService
from app.DAL.scan_history_DAL import ScanHistoryDAL
from app.models.scan_history import ScanHistory


class HomeService:
    def __init__(
        self,
        db: Session,
        user_daily_score_service: UserDailyScoreService,
        scan_history_dal: ScanHistoryDAL,
    ):
        self.db = db
        self.user_daily_score_service = user_daily_score_service
        self.scan_history_dal = scan_history_dal

    @staticmethod
    def _decision_to_risk_level(decision: Any) -> str:
        value = getattr(decision, "value", decision)
        if value == "avoid":
            return "red"
        if value == "caution":
            return "yellow"
        return "green"

    def get_home(self, user_id: str) -> Dict[str, Any]:
        kst = timezone(timedelta(hours=9))
        now_kst = datetime.now(kst)
        today_start_kst = now_kst.replace(hour=0, minute=0, second=0, microsecond=0)
        today_end_kst = today_start_kst + timedelta(days=1)

        # 2. 이를 UTC 시각으로 변환 (필터링 기준)
        start_utc = today_start_kst.astimezone(timezone.utc).replace(tzinfo=None)
        end_utc = today_end_kst.astimezone(timezone.utc).replace(tzinfo=None)
        today: date = datetime.now(kst).date()

        # 오늘 점수
        uds = self.user_daily_score_service.user_daily_score_dal.get(
            self.db, user_id=user_id, local_date=today
        )

        if uds is None or bool(cast(Optional[int], uds.dirty)):
            uds = self.user_daily_score_service.recompute_score_for_day(
                user_id=user_id,
                local_date=today,
            )

        today_score = uds.score if uds else 0

        # 모든 스캔 (최신순)
        all_scans: List[ScanHistory] = (
            self.db.query(ScanHistory)
            .filter(
                ScanHistory.user_id == user_id,
                ScanHistory.scanned_at >= start_utc,
                ScanHistory.scanned_at < end_utc
            )
            .order_by(ScanHistory.scanned_at.desc())
            .all()
        )

        # product_id 기준 대표 스캔 선정
        representative: dict[str, ScanHistory] = {}

        for scan in all_scans:
            key = scan.product_id or scan.id
            if key not in representative:
                representative[key] = scan

        scan_items: List[Dict[str, Any]] = []

        for scan in list(representative.values())[:2]:
            scan_items.append(
                {
                    "name": scan.product_name if not scan.dirty else scan.display_name,
                    "category": scan.display_category,
                    "scanID": scan.id,
                    "riskLevel": self._decision_to_risk_level(scan.decision),
                    "summary": scan.summary,
                    "url": scan.image_url,
                }
            )

        return {
            "scan": scan_items,
            "todayScore": today_score,
        }
