from fastapi import APIRouter, Form, File, UploadFile, Depends, Body

from app.schemas.scan_flow import ScanResultOut
from app.services.scan_flow_service import ScanFlowService
from app.dependencies import get_scan_flow_service
from app.core.auth import get_current_user
from app.core.errors import AppError, ErrorCode
from fastapi import Request

router = APIRouter(
    prefix="/v1/scan-history",
    tags=["scan-flow"],
)


@router.post("/barcode_image", response_model=ScanResultOut)
async def barcode_image(
    request: Request,
    barcode: str = Form(...),
    image: UploadFile | None = File(None),
    current_user = Depends(get_current_user),
    scan_flow: ScanFlowService = Depends(get_scan_flow_service),
):
    # 1) Content-Type 체크 (multipart/form-data 강제)
    ctype = request.headers.get("content-type", "")
    if not ctype.startswith("multipart/form-data"):
        raise AppError(ErrorCode.UNSUPPORTED_MEDIA_TYPE)

    # 2) barcode 빈 값 방어 (공백만 오는 케이스)
    if not barcode or not barcode.strip():
        raise AppError(ErrorCode.MISSING_BARCODE)
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
