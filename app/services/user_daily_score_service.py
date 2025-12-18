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

    # -------------------------------------------------
    # 스캔 1건 발생 시 호출 (점수는 계산 안 함)
    # -------------------------------------------------
    def update_on_scan(
        self,
        *,
        user_id: str,
        local_date: date,
        severity: Optional[MaxSeverity],
        decision_key: Optional[str],
    ):
        uds = self.user_daily_score_dal.get(
            self.db, user_id=user_id, local_date=local_date
        )

        def _updated_decision_counts(existing: Any, key: Optional[str]) -> Dict:
            counts = dict(existing or {})
            if key:
                counts[key] = counts.get(key, 0) + 1
            return counts

        # 오늘 row가 없으면 생성
        if uds is None:
            uds_create = UserDailyScoreCreate(
                user_id=user_id,
                local_date=local_date,
                score=0,              # 점수는 홈에서 계산
                num_scans=1,
                max_severity=severity,
                decision_counts=_updated_decision_counts(None, decision_key),
                formula_version=1,
                dirty=1,
                last_computed_at=None,
                sync_state=1,
            )
            return self.user_daily_score_dal.create(self.db, uds_create)

        # 이미 있으면 누적
        new_num_scans = (uds.num_scans or 0) + 1

        current_sev = (
            MaxSeverity(uds.max_severity)
            if uds.max_severity is not None
            else None
        )

        new_max_severity = current_sev
        if severity is not None:
            if current_sev is None or (
                self._severity_rank[severity]
                > self._severity_rank[current_sev]
            ):
                new_max_severity = severity

        uds_update = UserDailyScoreUpdate(
            num_scans=new_num_scans,
            max_severity=new_max_severity,
            decision_counts=_updated_decision_counts(
                uds.decision_counts, decision_key
            ),
            dirty=1,
        )

        return self.user_daily_score_dal.update(
            self.db,
            user_id=user_id,
            local_date=local_date,
            uds_in=uds_update,
        )

    # -------------------------------------------------
    # 홈 화면 진입 시: 점수 재계산 (유일한 score 계산 지점)
    # -------------------------------------------------
    def recompute_score_for_day(
        self,
        *,
        user_id: str,
        local_date: date,
    ) -> UserDailyScore:
        uds = self.user_daily_score_dal.get(
            self.db, user_id=user_id, local_date=local_date
        )

        # 1️⃣ 홈 첫 진입: row 자체가 없으면 77로 생성
        if uds is None:
            uds_create = UserDailyScoreCreate(
                user_id=user_id,
                local_date=local_date,
                score=77,              # ⭐ 초기 고정 점수
                num_scans=0,
                max_severity=None,
                decision_counts={},
                formula_version=1,
                dirty=0,
                last_computed_at=datetime.now(timezone.utc).replace(tzinfo=None),
                sync_state=1,
            )
            return self.user_daily_score_dal.create(self.db, uds_create)

        # 2️⃣ 오늘 스캔 점수 통계
        stats = self.scan_history_dal.get_ai_score_stats_for_day(
            self.db, user_id=user_id, local_date=local_date
        )
        # stats = {"count": int, "avg_score": float | None}

        # 3️⃣ 초기 상태 보정
        # - 오늘 스캔이 0개면 무조건 77
        if (uds.num_scans or 0) == 0:
            score = 77
        elif not stats or stats["count"] == 0 or stats["avg_score"] is None:
            score = 77
        else:
            score = int(round(max(0.0, min(100.0, stats["avg_score"]))))

        uds_update = UserDailyScoreUpdate(
            score=score,
            dirty=0,
            formula_version=1,
            last_computed_at=datetime.now(timezone.utc).replace(tzinfo=None),
        )

        return self.user_daily_score_dal.update(
            self.db,
            user_id=user_id,
            local_date=local_date,
            uds_in=uds_update,
        )
