# app/routers/auth_user_router.py

from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User
from utils.jwt_handler import decode_jwt

router = APIRouter()


@router.get("/user/me")
def get_my_profile(
    authorization: str = Header(None),
    db: Session = Depends(get_db),
):

    # 1) Authorization 헤더 검증
    if authorization is None:
        raise HTTPException(status_code=401, detail="Authorization header missing")

    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization format")

    token = authorization.replace("Bearer ", "").strip()

    # 2) JWT 검증
    decoded = decode_jwt(token)
    if decoded is None:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    user_id = decoded["user_id"]

    # 3) DB에서 사용자 조회
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # 4) 필요한 정보만 반환 (원하면 커스터마이징 가능)
    return {
        "user_id": user.id,
        "name": user.name,
        "profile_image_url": user.profile_image_url,
        "created_at": user.created_at,
    }
