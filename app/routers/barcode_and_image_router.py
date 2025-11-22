from fastapi import APIRouter, Form, File, UploadFile, Depends

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
    barcode: str = Form(...),
    image: UploadFile | None = File(None),
    current_user = Depends(get_current_user),
    scan_flow: ScanFlowService = Depends(get_scan_flow_service),
):
    return await scan_flow.from_barcode_and_image(
        user_id=current_user.id,
        barcode=barcode,
        image=image,
    )
