# app/services/user_daily_score_service.py
from datetime import date, datetime, timezone
from typing import Optional, Dict, Any

from sqlalchemy.orm import Session

from app.models.user_daily_score import UserDailyScore

from app.DAL.user_daily_score_DAL import UserDailyScoreDAL
from app.DAL.scan_history_DAL import ScanHistoryDAL

from app.schemas.user_daily_score import (
    UserDailyScoreCreate,
    UserDailyScoreUpdate,
    MaxSeverity,
)
from app.schemas.scan_history import ScanDecision


class UserDailyScoreService:
    # severity 크기 비교용 랭크
    _severity_rank = {
        MaxSeverity.none: 0,
        MaxSeverity.info: 1,
        MaxSeverity.warning: 2,
        MaxSeverity.danger: 3,
    }

    def __init__(
        self,
        db: Session,
        user_daily_score_dal: UserDailyScoreDAL,
        scan_history_dal: ScanHistoryDAL,
        
    ):
        self.db = db
        self.user_daily_score_dal = user_daily_score_dal
        self.scan_history_dal = scan_history_dal

    def update_on_scan(
        self,
        *,
        user_id: str,
        local_date: date,
        severity: Optional[MaxSeverity],   # 이번 스캔의 max_severity
        decision_key: Optional[str],       # 예: "ok" / "caution" / "avoid" 등
    ):
        """
        스캔 1건이 끝났을 때, 해당 유저+날짜의 user_daily_score를 갱신한다.
        - 없으면 생성
        - 있으면 num_scans / max_severity / decision_counts만 업데이트
        - score는 여기서 계산 안 하고 dirty=1만 찍어둠
        """
        uds = self.user_daily_score_dal.get(self.db, user_id=user_id, local_date=local_date)

        # 공통: decision_counts 갱신 준비
        def _updated_decision_counts(existing: Any, key: Optional[str]) -> Dict:
            counts = dict(existing or {})
            if key:
                counts[key] = counts.get(key, 0) + 1
            return counts

        # 1) 아직 오늘 row가 없으면 새로 만든다.
        if uds is None:
            decision_counts = _updated_decision_counts(None, decision_key)

            uds_create = UserDailyScoreCreate(
                user_id=user_id,
                local_date=local_date,
                # 아직 점수 계산 안 했으니 0 + dirty=1로 두고,
                # 나중에 별도 서비스에서 재계산하도록.
                score=0,
                num_scans=1,
                max_severity=severity,
                decision_counts=decision_counts,
                formula_version=1,
                dirty=1,
                last_computed_at=None,
                sync_state=1,
            )
            return self.user_daily_score_dal.create(self.db, uds_create)

        # 2) 이미 오늘 row가 있으면 누적 업데이트
        # num_scans
        new_num_scans = (uds.num_scans or 0) + 1

        # max_severity: 더 강한 쪽으로 업데이트
        current_sev = None
        if uds.max_severity is not None:
            # DB에는 str로 저장되므로 Enum으로 다시 감쌈
            current_sev = MaxSeverity(uds.max_severity)

        new_max_severity = current_sev
        if severity is not None:
            if current_sev is None:
                new_max_severity = severity
            else:
                if self._severity_rank[severity] > self._severity_rank[current_sev]:
                    new_max_severity = severity

        # decision_counts
        new_decision_counts = _updated_decision_counts(uds.decision_counts, decision_key)

        uds_update = UserDailyScoreUpdate(
            num_scans=new_num_scans,
            max_severity=new_max_severity,
            decision_counts=new_decision_counts,
            # 점수는 아직 재계산 안 했으니 dirty=1로 표시
            dirty=1,
        )
        return self.user_daily_score_dal.update(
            self.db, user_id=user_id, local_date=local_date, uds_in=uds_update
        )

    # 얘는 홈 화면 불러오는 api에서 호출될 예정
    def recompute_score_for_day(self, *, user_id: str, local_date: date) -> UserDailyScore:
        uds = self.user_daily_score_dal.get(self.db, user_id=user_id, local_date=local_date)
        if uds is None:
            raise RuntimeError("user_daily_score not found")


        # 해당 유저+날짜의 ai_total_score 평균 가져오는 DAL임
        stats = self.scan_history_dal.get_ai_score_stats_for_day(
            self.db, user_id=user_id, local_date=local_date
        )
        # stats: {"count": int, "avg_score": float | None}

        if not stats or stats["count"] == 0 or stats["avg_score"] is None:
            score = 0
        else:
            score = int(round(max(0.0, min(100.0, stats["avg_score"]))))

        uds_update = UserDailyScoreUpdate(
            score=score,
            dirty=0,
            last_computed_at=datetime.now(timezone.utc).replace(tzinfo=None),
            formula_version=1,
        )
        return self.user_daily_score_dal.update(
            self.db, user_id=user_id, local_date=local_date, uds_in=uds_update
        )
