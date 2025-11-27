# app/routers/scan_history_router.py
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.DAL.scan_history_DAL import ScanHistoryDAL
from app.schemas.scan_history import (
    ScanHistoryCreate,
    ScanHistoryUpdate,
    ScanHistoryOut,
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


@router.get(
    "/{scan_id}",
    response_model=ScanHistoryOut,
)
def get_scan_history(
    scan_id: str,
    db: Session = Depends(get_db),
):
    scan = ScanHistoryDAL.get(db, scan_id)
    if not scan:
        raise HTTPException(status_code=404, detail="Scan history not found")
    return scan


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
