# app/DAL/user_daily_score_DAL.py
from datetime import date, datetime, timezone
from typing import List, Optional

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.models.user_daily_score import UserDailyScore
from app.schemas.user_daily_score import UserDailyScoreCreate, UserDailyScoreUpdate


class UserDailyScoreDAL:
    @staticmethod
    def create(db: Session, uds_in: UserDailyScoreCreate) -> UserDailyScore:
        # max_severity Enum -> str
        max_severity = uds_in.max_severity.value if uds_in.max_severity else None

        uds = UserDailyScore(
            user_id=uds_in.user_id,
            local_date=uds_in.local_date,
            score=uds_in.score,
            num_scans=uds_in.num_scans,
            max_severity=max_severity,
            decision_counts=uds_in.decision_counts,
            formula_version=uds_in.formula_version,
            dirty=uds_in.dirty,
            last_computed_at=uds_in.last_computed_at,
            sync_state=uds_in.sync_state,
        )
        db.add(uds)
        db.commit()
        db.refresh(uds)
        return uds

    @staticmethod
    def get(
        db: Session,
        user_id: str,
        local_date: date,
    ) -> Optional[UserDailyScore]:
        return (
            db.query(UserDailyScore)
            .filter(
                UserDailyScore.user_id == user_id,
                UserDailyScore.local_date == local_date,
                UserDailyScore.deleted_at.is_(None),
            )
            .first()
        )

    @staticmethod
    def create_or_get(db: Session, uds_in: UserDailyScoreCreate) -> UserDailyScore:
        max_severity = uds_in.max_severity.value if uds_in.max_severity else None

        uds = UserDailyScore(
            user_id=uds_in.user_id,
            local_date=uds_in.local_date,
            score=uds_in.score,
            num_scans=uds_in.num_scans,
            max_severity=max_severity,
            decision_counts=uds_in.decision_counts,
            formula_version=uds_in.formula_version,
            dirty=uds_in.dirty,
            last_computed_at=uds_in.last_computed_at,
            sync_state=uds_in.sync_state,
        )
        try:
            db.add(uds)
            db.commit()
            db.refresh(uds)
            return uds
        except IntegrityError:
            db.rollback()
            # 이미 누가 만들었으면 그 row를 반환
            return UserDailyScoreDAL.get(
                db, user_id=uds_in.user_id, local_date=uds_in.local_date
            )

    @staticmethod
    def list(
        db: Session,
        user_id: Optional[str] = None,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[UserDailyScore]:
        q = db.query(UserDailyScore).filter(UserDailyScore.deleted_at.is_(None))

        if user_id is not None:
            q = q.filter(UserDailyScore.user_id == user_id)
        if date_from is not None:
            q = q.filter(UserDailyScore.local_date >= date_from)
        if date_to is not None:
            q = q.filter(UserDailyScore.local_date <= date_to)

        # 최근 날짜 먼저
        q = q.order_by(
            UserDailyScore.user_id.asc(),
            UserDailyScore.local_date.desc(),
        )

        return q.offset(skip).limit(limit).all()

    @staticmethod
    def update(
        db: Session,
        user_id: str,
        local_date: date,
        uds_in: UserDailyScoreUpdate,
    ) -> Optional[UserDailyScore]:
        uds = (
            db.query(UserDailyScore)
            .filter(
                UserDailyScore.user_id == user_id,
                UserDailyScore.local_date == local_date,
                UserDailyScore.deleted_at.is_(None),
            )
            .first()
        )
        if not uds:
            return None

        data = uds_in.model_dump(exclude_unset=True)

        # Enum -> str 변환
        if "max_severity" in data and data["max_severity"] is not None:
            data["max_severity"] = data["max_severity"].value

        for field, value in data.items():
            setattr(uds, field, value)

        db.commit()
        db.refresh(uds)
        return uds

    @staticmethod
    def soft_delete(
        db: Session,
        user_id: str,
        local_date: date,
    ) -> bool:
        uds = (
            db.query(UserDailyScore)
            .filter(
                UserDailyScore.user_id == user_id,
                UserDailyScore.local_date == local_date,
                UserDailyScore.deleted_at.is_(None),
            )
            .first()
        )
        if not uds:
            return False

        uds.deleted_at = datetime.now()
        db.commit()
        return True
