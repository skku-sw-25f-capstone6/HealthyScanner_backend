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

# 🔥 카카오 토큰 자동 갱신 함수 import
from app.routers.auth_router import ensure_valid_kakao_access_token

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
# 🟧 현재 로그인된 사용자 정보 조회 (+ 카카오 Access Token 자동 갱신)
# -------------------------------------------------------------
@router.get(
    "/me",
    response_model=UserOut,
)
def get_me(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    - JWT로 현재 로그인 사용자 확인
    - 카카오 access_token 유효성 검사
    - 만료 시 refresh_token으로 자동 재발급
    - 최신 사용자 정보 반환
    """

    valid_access_token = ensure_valid_kakao_access_token(current_user, db)

    if not valid_access_token:
        raise HTTPException(
            status_code=401,
            detail="카카오 토큰이 만료되었습니다. 다시 로그인 해주세요.",
        )

    return current_user


# =====================================================================
# 🟪 신규 기능: 온보딩 프로필 저장 API
#       POST /v1/users/profile
# =====================================================================

@router.post(
    "/profile",
    response_model=UserOut,
    status_code=status.HTTP_200_OK,
)
def update_profile(
    profile: UserUpdate,  # ⬅ UserProfileUpdate → UserUpdate 로 변경
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    사용자 온보딩 정보(habits, conditions, allergies) 저장 API

    - JWT 인증된 사용자만 접근 가능
    - 이미 저장된 값과 동일하면 409 Conflict
    - 정상 저장 시 업데이트된 user 정보 반환
    """

    # ✔ Conflict 체크
    same_data = (
        current_user.habits == profile.habits and
        current_user.conditions == profile.conditions and
        current_user.allergies == profile.allergies
    )

    if same_data:
        raise HTTPException(
            status_code=409,
            detail="이미 동일한 내용의 프로필이 존재합니다."
        )

    # ✔ 업데이트
    current_user.habits = profile.habits
    current_user.conditions = profile.conditions
    current_user.allergies = profile.allergies

    db.commit()
    db.refresh(current_user)

    return current_user