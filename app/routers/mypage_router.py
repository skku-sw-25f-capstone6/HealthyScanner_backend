# app/routers/mypage_router.py
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.models.user import User 

from app.core.database import get_db
from app.core.auth import get_current_user
from app.schemas.user import MyPageOut
from app.services.user_service import UserService

from app.DAL.user_DAL import UserDAL
from app.DAL.user_daily_score_DAL import UserDailyScoreDAL
from app.dependencies import (
    get_user_dal,
    get_user_daily_score_dal
)

router = APIRouter(
    prefix="/v1/myPage",
    tags=["myPage"],
)

@router.get(
    "/summary",
    response_model = MyPageOut
)
def get_my_page(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    user_dal: UserDAL = Depends(get_user_dal),
    usd_dal: UserDailyScoreDAL = Depends(get_user_daily_score_dal)
):
    service = UserService(
        db=db,
        user_dal=user_dal,
        user_daily_score_dal=usd_dal,
    )

    result = service.get_mypage(current_user.id)
    return result