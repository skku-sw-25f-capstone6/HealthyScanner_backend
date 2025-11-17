# app/routers/me_router.py
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.models.user import User 

from app.core.database import get_db
from app.core.auth import get_current_user
from app.schemas.user import MyPageOut
from app.services.user_service import UserService

router = APIRouter(
    prefix="/v1/me",
    tags=["me"],
)
"""
@router.patch(
    "/habits",
    
)
"""