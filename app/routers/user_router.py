# app/routers/user_router.py
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.models.user import User
from app.core.database import get_db
from app.core.auth import get_current_user
from app.DAL.user_DAL import UserDAL
from app.schemas.user import (
    UserCreate, UserUpdate, UserOut
)

router = APIRouter(
    prefix="/v1/users",
    tags=["users"],
)

# -------------------------------------------------------------
# 🟦 Create User (일반 회원가입용)
# -------------------------------------------------------------
@router.post(
    "/",
    response_model=UserOut,
    status_code=status.HTTP_201_CREATED,
)
def create_user(
    user_in: UserCreate,
    db: Session = Depends(get_db),
):
    user = UserDAL.create(db, user_in)
    return user


# -------------------------------------------------------------
# 🟦 Get User by ID
# -------------------------------------------------------------
@router.get(
    "/{user_id}",
    response_model=UserOut,
)
def get_user(
    user_id: str,
    db: Session = Depends(get_db),
):
    user = UserDAL.get(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


# -------------------------------------------------------------
# 🟦 List Users
# -------------------------------------------------------------
@router.get(
    "/",
    response_model=List[UserOut],
)
def list_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    users = UserDAL.list(db, skip=skip, limit=limit)
    return users


# -------------------------------------------------------------
# 🟦 Update User
# -------------------------------------------------------------
@router.patch(
    "/{user_id}",
    response_model=UserOut,
)
def update_user(
    user_id: str,
    user_in: UserUpdate,
    db: Session = Depends(get_db),
):
    user = UserDAL.update(db, user_id, user_in)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


# -------------------------------------------------------------
# 🟦 Soft Delete User
# -------------------------------------------------------------
@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_user(
    user_id: str,
    db: Session = Depends(get_db),
):
    ok = UserDAL.soft_delete(db, user_id)
    if not ok:
        raise HTTPException(status_code=404, detail="User not found")
    return


# -------------------------------------------------------------
# 🟧 현재 로그인된 사용자 정보 조회 (JWT 기반)
# -------------------------------------------------------------
@router.get(
    "/me",
    response_model=UserOut,
)
def get_me(
    current_user: User = Depends(get_current_user),
):
    """
    - 우리 앱 JWT 기반 인증
    - 카카오 토큰과는 무관
    """
    return current_user


# =====================================================================
# 🟪 온보딩 프로필 저장 API
#       POST /v1/users/profile
# =====================================================================
@router.post(
    "/profile",
    response_model=UserOut,
    status_code=status.HTTP_200_OK,
)
def update_profile(
    profile: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    same_data = (
        current_user.habits == profile.habits and
        current_user.conditions == profile.conditions and
        current_user.allergies == profile.allergies
    )

    current_user.habits = profile.habits
    current_user.conditions = profile.conditions
    current_user.allergies = profile.allergies

    db.commit()
    db.refresh(current_user)

    return current_user