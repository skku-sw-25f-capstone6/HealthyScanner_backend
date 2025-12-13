# app/routers/me_router.py
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.models.user import User 

from app.core.database import get_db
from utils.auth_dependency import get_current_user
from app.schemas.user import (
    MyPageHabitIn,
    MyPageHabitOut,
    MyPageConditionIn,
    MyPageConditionOut,
    MyPageAllergiesIn,
    MyPageAllergiesOut,
)
from app.services.user_service import UserService

from app.DAL.user_DAL import UserDAL
from app.DAL.user_daily_score_DAL import UserDailyScoreDAL

from app.dependencies import (
    get_user_dal,
    get_user_daily_score_dal
)

router = APIRouter(
    prefix="/v1/me",
    tags=["me"],
)

@router.patch("/habits", response_model=MyPageHabitOut)
def update_habits(
    habit_in: MyPageHabitIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    user_dal: UserDAL = Depends(get_user_dal),
    usd_dal: UserDailyScoreDAL = Depends(get_user_daily_score_dal)
) -> MyPageHabitOut:
    habit = habit_in.habit
    current_user_id = current_user.id
    service = UserService(
        db=db,
        user_dal=user_dal,
        user_daily_score_dal=usd_dal,
    )
    return service.update_habits(current_user_id, habit)

@router.patch("/conditions", response_model=MyPageConditionOut)
def update_conditions(
    condition_in: MyPageConditionIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    user_dal: UserDAL = Depends(get_user_dal),
    usd_dal: UserDailyScoreDAL = Depends(get_user_daily_score_dal)
) -> MyPageConditionOut:
    condition = condition_in.conditions
    current_user_id = current_user.id
    service = UserService(
        db=db,
        user_dal=user_dal,
        user_daily_score_dal=usd_dal,
    )
    return service.update_conditions(current_user_id, condition)

@router.patch("/allergies", response_model=MyPageAllergiesOut)
def update_allergies(
    allergies_in: MyPageAllergiesIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    user_dal: UserDAL = Depends(get_user_dal),
    usd_dal: UserDailyScoreDAL = Depends(get_user_daily_score_dal)
) -> MyPageAllergiesOut:
    allergies = allergies_in.allergies
    current_user_id = current_user.id
    service = UserService(
        db=db,
        user_dal=user_dal,
        user_daily_score_dal=usd_dal,
    )
    return service.update_allergies(current_user_id, allergies)


