# app/routers/scan_history_router.py
from typing import List, Optional
from datetime import datetime, date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.DAL.scan_history_DAL import ScanHistoryDAL
from app.models.user import User
from app.core.auth import get_current_user

from app.services.scan_history_service import ScanHistoryService
from app.services.scan_get_full_service import ScanGetFullService
from app.dependencies import get_scan_get_full_service, get_scan_history_service

from app.schemas.scan_history import (
    ScanHistoryCreate,
    ScanHistoryUpdate,
    ScanHistoryOut,
    ScanDetailOut,
    ScanHistoryNameCategoryIn,
    ScanHistoryNameCategoryOut,
    ScanSummaryOut,
    ScanHistoryListOut
)

from app.schemas.scan_full import (
    ScanFullOut
)

router = APIRouter(
    prefix="/v1/scan-history",
    tags=["scan_history"],
)


@router.post(
    "/",
    response_model=ScanHistoryOut,
    status_code=status.HTTP_201_CREATED,
)
def create_scan_history(
    sh_in: ScanHistoryCreate,
    db: Session = Depends(get_db),
):
    scan = ScanHistoryDAL.create(db, sh_in)
    return scan


# app/routers/scan_router.py
@router.get(
    "/{scan_id}",
    response_model=ScanDetailOut,
)
def get_scan_detail(
    scan_id: str,
    scan_service: ScanHistoryService = Depends(get_scan_history_service)
):
    service = scan_service
    return service.get_scan_detail(scan_id)


@router.get(
    "/",
    response_model=List[ScanHistoryOut],
)
def list_scan_history(
    skip: int = 0,
    limit: int = 100,
    user_id: Optional[str] = Query(default=None),
    product_id: Optional[str] = Query(default=None),
    db: Session = Depends(get_db),
):
    scans = ScanHistoryDAL.list(
        db,
        skip=skip,
        limit=limit,
        user_id=user_id,
        product_id=product_id,
    )
    return scans

"""
@router.patch(
    "/{scan_id}",
    response_model=ScanHistoryOut,
)
def update_scan_history(
    scan_id: str,
    sh_in: ScanHistoryUpdate,
    db: Session = Depends(get_db),
):
    scan = ScanHistoryDAL.update(db, scan_id, sh_in)
    if not scan:
        raise HTTPException(status_code=404, detail="Scan history not found")
    return scan
"""

@router.patch(
    "/{scan_id}",
    response_model=ScanHistoryNameCategoryOut,
)
async def update_scan_history_info(
    scan_id: str,
    body: ScanHistoryNameCategoryIn,
    service: ScanHistoryService = Depends(get_scan_history_service),
):
    return await service.update_name_category(
        scan_id=scan_id,
        display_name=body.name,
        display_category=body.category,
    )

@router.delete(
    "/{scan_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_scan_history(
    scan_id: str,
    db: Session = Depends(get_db),
):
    ok = ScanHistoryDAL.soft_delete(db, scan_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Scan history not found")
    return

@router.get(
    "/{scan_id}/details",
    response_model=ScanFullOut
)
def get_full_scan_history(
    scan_id: str,
    scan_get_full_service: ScanGetFullService = Depends(get_scan_get_full_service)
) -> ScanFullOut:
    service = scan_get_full_service
    return service.get_full_scan(scan_id)

@router.get(
    "",
    response_model=ScanHistoryListOut,
)
async def get_scan_list(
    date: datetime,
    current_user: User = Depends(get_current_user),
    service: ScanHistoryService = Depends(get_scan_history_service),
):
    """
    특정 날짜(date)의 스캔 기록 목록 조회
    """
    return await service.get_scan_list_by_date(
        user_id=current_user.id,
        date=date,
    )