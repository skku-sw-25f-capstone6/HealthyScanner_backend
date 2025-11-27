# app/services/user_service.py
from datetime import date
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.DAL.user_DAL import UserDAL
from app.DAL.user_daily_score_DAL import UserDailyScoreDAL
from app.schemas.user import MyPageOut


class UserService:
    def __init__(
        self,
        db: Session,
        user_dal: UserDAL,
        user_daily_score_dal: UserDailyScoreDAL,
    ):
        self.db = db
        self.user_dal = user_dal
        self.user_daily_score_dal = user_daily_score_dal

    def get_mypage(self, user_id: str) -> MyPageOut:
        today = date.today()

        user = self.user_dal.get(db=self.db, user_id=user_id)
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")

        user_daily_score = self.user_daily_score_dal.get(
            db=self.db,
            user_id=user_id,
            local_date=today,
        )

        if user_daily_score is None or user_daily_score.num_scans is None:
            scan_count: int = 0
        else:
            scan_count: int = user_daily_score.num_scans

        return MyPageOut(
            name=str(user.name),
            scan_count=scan_count,
            profile_image_url=str(user.profile_image_url),
        )
