from fastapi import APIRouter, Body, Depends

from app.schemas.scan_flow import ScanResultOut
from app.services.scan_flow_service import ScanFlowService
from app.dependencies import get_scan_flow_service
from app.core.auth import get_current_user

router = APIRouter(
    prefix="/v1",
    tags=["scan-history"],
)


@router.post("/scan-history", response_model=ScanResultOut)
async def get_report(
    nutrition_label: str = Body(..., embed=True),
    current_user = Depends(get_current_user),
    scan_flow: ScanFlowService = Depends(get_scan_flow_service),
):
    return await scan_flow.from_nutrition_text(
        user_id=current_user.id,
        nutrition_text=nutrition_label
    )
