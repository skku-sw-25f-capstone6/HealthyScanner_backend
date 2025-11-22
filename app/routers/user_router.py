# app/routers/user_router.py
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.models.user import User 

from app.core.database import get_db
from app.core.auth import get_current_user
from app.DAL.user_DAL import UserDAL
from app.schemas.user import UserCreate, UserUpdate, UserOut

router = APIRouter(
    prefix="/v1/users",
    tags=["users"],
)


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
    # 204는 바디 없음
    return
