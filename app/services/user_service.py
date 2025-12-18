# app/services/user_service.py
from datetime import date
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.DAL.user_DAL import UserDAL
from app.DAL.user_daily_score_DAL import UserDailyScoreDAL
from app.schemas.user import (
    MyPageOut,
    MyPageHabitOut,
    MyPageAllergiesOut,
    MyPageConditionOut
)

from typing import List

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

        habit = user.habits
        conditions = user.conditions
        allergies = user.allergies

        return MyPageOut(
            name=str(user.name),
            scan_count=scan_count,
            profile_image_url=str(user.profile_image_url),
            habit=habit or [],
            conditions=conditions or [],
            allergies=allergies or []
        )
    
    def update_habits(self, user_id: str, habit: str) -> MyPageHabitOut:
        user = self.user_dal.get(db=self.db, user_id=user_id)
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
        
        user.habits = [habit]

        self.db.commit()
        self.db.refresh(user)

        return MyPageHabitOut(habit=habit, updated_at=user.updated_at)

    def update_conditions(self, user_id: str, conditions: List[str]) -> MyPageConditionOut:
        user = self.user_dal.get(db=self.db, user_id=user_id)
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
        
        user.conditions = conditions
        self.db.commit()
        self.db.refresh(user)

        return MyPageConditionOut(conditions=conditions, updated_at=user.updated_at)
    
    def update_allergies(self, user_id: str, allergies: List[str]) -> MyPageAllergiesOut:
        user = self.user_dal.get(db=self.db, user_id=user_id)
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
        
        user.allergies = allergies

        self.db.commit()
        self.db.refresh(user)

        return MyPageAllergiesOut(allergies=allergies, updated_at=user.updated_at)
