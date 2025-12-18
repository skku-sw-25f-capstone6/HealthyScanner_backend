# app/routers/home_router.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Any, Dict

from app.core.database import get_db
from app.dependencies import (
    get_user_daily_score_service,
    get_scan_history_dal,
    get_product_dal,
)

from app.core.auth import get_current_user

from app.services.home_service import HomeService
from app.services.user_daily_score_service import UserDailyScoreService
from app.DAL.scan_history_DAL import ScanHistoryDAL
from app.DAL.product_DAL import ProductDAL

router = APIRouter(
    prefix="/v1/home",
    tags=["home"],
)


# 홈 화면 정보 조회하는 녀석
# 얘로 정보 조회 될 때마다 유저 정보 새로고침함
# scan 흐름에서 바로 갱신하는 게 아님
@router.get("")
def get_home(
    db: Session = Depends(get_db),
    uds_service: UserDailyScoreService = Depends(get_user_daily_score_service),
    scan_history_dal: ScanHistoryDAL = Depends(get_scan_history_dal),
    product_dal: ProductDAL = Depends(get_product_dal),
    current_user=Depends(get_current_user),
) -> Dict[str, Any]:
    service = HomeService(
        db=db,
        user_daily_score_service=uds_service,
        scan_history_dal=scan_history_dal,
        
    )
    return service.get_home(user_id=current_user.id)
