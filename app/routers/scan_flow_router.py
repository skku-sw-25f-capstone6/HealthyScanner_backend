from fastapi import APIRouter, Form, File, UploadFile, Depends, Body

from app.schemas.scan_flow import ScanResultOut
from app.services.scan_flow_service import ScanFlowService
from app.dependencies import get_scan_flow_service
from app.core.auth import get_current_user

router = APIRouter(
    prefix="/v1/scan-history",
    tags=["scan-flow"],
)


@router.post("/barcode_image", response_model=ScanResultOut)
async def barcode_image(
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


@router.post("/nutrition_label", response_model=ScanResultOut)
async def nutrition_label(
    nutrition_label: str = Form(...),
    image: UploadFile | None = File(None),
    current_user = Depends(get_current_user),
    scan_flow: ScanFlowService = Depends(get_scan_flow_service),
):
    return await scan_flow.from_nutrition_text(
        user_id=current_user.id,
        nutrition_label=nutrition_label,
        image=image
    )


@router.post("/image", response_model=ScanResultOut)
async def image(
    image: UploadFile = File(None),
    current_user = Depends(get_current_user),
    scan_flow: ScanFlowService = Depends(get_scan_flow_service),
):
    return await scan_flow.from_image(
        user_id=current_user.id,
        image=image,
    )
