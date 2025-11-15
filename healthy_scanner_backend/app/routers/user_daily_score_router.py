# app/routers/user_daily_score_router.py
from datetime import date
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dal.user_daily_score_dal import UserDailyScoreDal
from app.schemas.user_daily_score import (
    UserDailyScoreCreate,
    UserDailyScoreUpdate,
    UserDailyScoreOut,
)

router = APIRouter(
    prefix="/v1/user-daily-scores",
    tags=["user_daily_score"],
)


@router.post(
    "/",
    response_model=UserDailyScoreOut,
    status_code=status.HTTP_201_CREATED,
)
def create_user_daily_score(
    uds_in: UserDailyScoreCreate,
    db: Session = Depends(get_db),
):
    uds = UserDailyScoreDal.create(db, uds_in)
    return uds


@router.get(
    "/{user_id}/{local_date}",
    response_model=UserDailyScoreOut,
)
def get_user_daily_score(
    user_id: str,
    local_date: date,
    db: Session = Depends(get_db),
):
    uds = UserDailyScoreDal.get(db, user_id, local_date)
    if not uds:
        raise HTTPException(status_code=404, detail="User daily score not found")
    return uds


@router.get(
    "/",
    response_model=List[UserDailyScoreOut],
)
def list_user_daily_scores(
    user_id: Optional[str] = Query(default=None),
    date_from: Optional[date] = Query(default=None),
    date_to: Optional[date] = Query(default=None),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    items = UserDailyScoreDal.list(
        db,
        user_id=user_id,
        date_from=date_from,
        date_to=date_to,
        skip=skip,
        limit=limit,
    )
    return items


@router.patch(
    "/{user_id}/{local_date}",
    response_model=UserDailyScoreOut,
)
def update_user_daily_score(
    user_id: str,
    local_date: date,
    uds_in: UserDailyScoreUpdate,
    db: Session = Depends(get_db),
):
    uds = UserDailyScoreDal.update(db, user_id, local_date, uds_in)
    if not uds:
        raise HTTPException(status_code=404, detail="User daily score not found")
    return uds


@router.delete(
    "/{user_id}/{local_date}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_user_daily_score(
    user_id: str,
    local_date: date,
    db: Session = Depends(get_db),
):
    ok = UserDailyScoreDal.soft_delete(db, user_id, local_date)
    if not ok:
        raise HTTPException(status_code=404, detail="User daily score not found")
    return
