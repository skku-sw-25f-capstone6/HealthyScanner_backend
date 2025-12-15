# app/services/home_service.py
from datetime import datetime, timezone, date
from typing import Dict, Any, List, Optional, cast

from sqlalchemy.orm import Session

from app.services.user_daily_score_service import UserDailyScoreService
from app.DAL.scan_history_DAL import ScanHistoryDAL
from app.DAL.product_DAL import ProductDAL
from app.models.scan_history import ScanHistory
from app.schemas.scan_history import ScanDecision  # Enum이라고 가정


class HomeService:
    def __init__(
        self,
        db: Session,
        user_daily_score_service: UserDailyScoreService,
        scan_history_dal: ScanHistoryDAL,
        product_dal: ProductDAL,
    ):
        self.db = db
        self.user_daily_score_service = user_daily_score_service
        self.scan_history_dal = scan_history_dal
        self.product_dal = product_dal

    @staticmethod
    def _decision_to_risk_level(decision: Any) -> str:
        # Enum이면 .value, 문자열이면 그대로
        value = getattr(decision, "value", decision)

        if value == "avoid":
            return "red"
        if value == "caution":
            return "yellow"
        return "green"

    def get_home(self, user_id: str) -> Dict[str, Any]:
        today: date = datetime.now(timezone.utc).date()

        uds = self.user_daily_score_service.user_daily_score_dal.get(
            self.db, user_id=user_id, local_date=today
        )

        needs_recompute = False
        if uds is None:
            needs_recompute = True
        else:
            # uds.dirty: Column[int] 라고 인식되니까 한 번 캐스팅
            dirty: Optional[int] = cast(Optional[int], uds.dirty)
            needs_recompute = bool(dirty)

        if needs_recompute:
            uds = self.user_daily_score_service.recompute_score_for_day(
                user_id=user_id,
                local_date=today,
            )
        
        if uds is None:
            today_score = 0
        else:
            today_score = uds.score

        scans: List[ScanHistory] = self.scan_history_dal.get_recent_scans_for_user(
            self.db, user_id=user_id, limit=2
        )

        scan_items: List[Dict[str, Any]] = []
        for s in scans:
            # --- 여기서 한 번 캐스팅해서 Column 타입 떼어내기 ---
            product_id: Optional[str] = cast(Optional[str], getattr(s, "product_id", None))
            decision_any: Any = getattr(s, "decision", None)

            product = None
            if product_id is not None:
                product = self.product_dal.get(self.db, product_id)
            # 이 부분의 product_id가 None일 경우에 대해 scan_history 테이블에서 알잘딱하게 가져오는 게 필요함
            scan_items.append(
                {
                    "name": getattr(product, "name", None),
                    "category": getattr(product, "category", None),
                    "riskLevel": self._decision_to_risk_level(decision_any),
                    "summary": getattr(s, "summary", None),
                    "url": getattr(product, "image_url", None),
                }
            )

        return {
            "scan": scan_items,
            "todayScore": today_score,
        }