# app/services/user_service.py
from typing import Optional, List
from sqlalchemy.orm import Session
from datetime import date
from fastapi import HTTPException

from app.DAL.user_DAL import UserDAL
from app.DAL.user_daily_score_DAL import UserDailyScoreDAL
from app.schemas.user import MyPageOut


class UserService:
    def __init__(self, db: Session):
        self.db = db
        self.user_DAL = UserDAL()
        self.user_daily_score_DAL = UserDailyScoreDAL()

    def get_mypage(self, user_id: str) -> MyPageOut:
        today = date.today()
        user = self.user_DAL.get(db=self.db, user_id=user_id)
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
        
        user_daily_score = self.user_daily_score_DAL.get(
            db = self.db,
            user_id = user_id,
            local_date = today)
        
        scan_count = user_daily_score.num_scans if user_daily_score else 0
        return MyPageOut(
            name = user.name,
            scan_count = scan_count,
            profile_image_url = user.profile_image_url
        )
    
