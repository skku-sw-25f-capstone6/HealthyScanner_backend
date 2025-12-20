from fastapi import UploadFile, HTTPException
from typing import Literal

from app.schemas.scan_history import ScanHistoryOut
from app.schemas.scan_flow import ScanResultOut
from app.services.scan_history_service import ScanHistoryService
from app.services.nutrition_service import NutritionService
from app.services.ingredient_service import IngredientService
from app.services.product_service import ProductService
from app.services.user_daily_score_service import UserDailyScoreService

from app.schemas.user_daily_score import MaxSeverity


AnalyzeType = Literal["barcode_image", "nutrition_label", "image"]


class ScanFlowService:
    """
    바코드 + 이미지 →
      1) 개인화 분석 + 스캔 기록 생성
      2) nutrition / ingredient id 조회
      3) 최종적으로 ScanResultOut 리턴
    """

    def __init__(
        self,
        scan_history_service: ScanHistoryService,
        nutrition_service: NutritionService,
        ingredient_service: IngredientService,
        product_service: ProductService,
        user_daily_score_service: UserDailyScoreService,
    ):
        self.scan_history_service = scan_history_service
        self.nutrition_service = nutrition_service
        self.ingredient_service = ingredient_service
        self.product_service = product_service
        self.user_daily_score_service = user_daily_score_service

    async def from_barcode_and_image(
        self,
        user_id: str,
        barcode: str,
        image: UploadFile | None,
    ) -> ScanResultOut:
        product = self.product_service.get_id_by_barcode(barcode)
        if product is None:
            raise HTTPException(status_code=404, detail="Product not found")

        return await self._scan_and_build_result(
            user_id=user_id,
            product_id=str(product.id),
            image=image,
            nutrition_text=None,
            analyze_type="barcode_image",
        )

    async def from_nutrition_text(
        self,
        user_id: str,
        nutrition_label: str,
        image: UploadFile | None,
    ) -> ScanResultOut:
        return await self._scan_and_build_result(
            user_id=user_id,
            product_id=None,
            image=image,
            nutrition_text=nutrition_label,
            analyze_type="nutrition_label",
        )

    async def from_image(
        self,
        user_id: str,
        image: UploadFile | None,
    ) -> ScanResultOut:
        return await self._scan_and_build_result(
            user_id=user_id,
            product_id=None,
            image=image,
            nutrition_text=None,
            analyze_type="image",
        )

    async def _scan_and_build_result(
        self,
        user_id: str,
        product_id: str | None,
        image: UploadFile | None,
        nutrition_text: str | None,
        analyze_type: AnalyzeType,
    ) -> ScanResultOut:
        scan: ScanHistoryOut = await self.scan_history_service.analyze_and_save_scan(
            user_id=user_id,
            product_id=product_id,
            image=image,
            nutrition_text=nutrition_text,
            analyze_type=analyze_type,
        )

        if product_id is not None:
            nutrition_id = self.nutrition_service.get_id_by_product_id(product_id)
            ingredient_id = self.ingredient_service.get_id_by_product_id(product_id)
        else:
            nutrition_id = None
            ingredient_id = None


        if scan.scanned_at is None:
            raise RuntimeError("scan.scanned_at is None")

        if scan.decision is None:
            raise RuntimeError("scan.decision is None")

        # user_daily_score 갱신
        local_date = scan.scanned_at.date()
        decision_key = scan.decision      # ✅ str 그대로 사용
        severity: MaxSeverity | None = None

        self.user_daily_score_service.update_on_scan(
            user_id=scan.user_id,
            local_date=local_date,
            severity=severity,
            decision_key=decision_key,
        )

        return ScanResultOut(
            scan_id=scan.id,
            product_id=product_id,
            nutrition_id=nutrition_id,
            ingredient_id=ingredient_id,
        )
