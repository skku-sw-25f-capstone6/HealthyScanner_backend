# app/routers/mypage_router.py
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.models.user import User 

from app.core.database import get_db
from app.core.auth import get_current_user
from app.schemas.user import MyPageOut
from app.services.user_service import UserService

router = APIRouter(
    prefix="/v1/myPage",
    tags=["myPage"],
)

@router.get(
    "/summary",
    response_model = MyPageOut
)
def get_my_page(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = UserService(db)
    result = service.get_mypage(current_user.id)
    return result