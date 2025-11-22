from fastapi import UploadFile, HTTPException


from app.schemas.scan_history import ScanHistoryOut
from app.schemas.scan_flow import ScanResultOut
from app.services.scan_history_service import ScanHistoryService
from app.services.nutrition_service import NutritionService
from app.services.ingredient_service import IngredientService
from app.services.product_service import ProductService


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
        product_service : ProductService,
    ):
        self.scan_history_service = scan_history_service
        self.nutrition_service = nutrition_service
        self.ingredient_service = ingredient_service
        self.product_service = product_service


    async def from_barcode_and_image(
        self,
        user_id: str,
        barcode: str,
        image: UploadFile | None,
    ) -> ScanResultOut:
        # 1) 바코드로 product 찾기
        product = self.product_service.get_id_by_barcode(barcode)
        if product is None:
            raise HTTPException(status_code=404, detail="Product not found")

        # 2) 공통 함수 호출 (product_id 기준)
        return await self._build_report_and_save_history(
            user_id=user_id,
            product_id=str(product.id),
            image=image,
        )
    
    async def from_nutrition_text(
            self,
            user_id: str,
            nutrition_text: str,
    ) -> ScanResultOut:
        # 1) 스캔 + 개인화 분석 + scan_history 저장
        scan: ScanHistoryOut = await self.scan_history_service.analyze_and_save_scan(
            user_id=user_id,
            product_id=None,
            image=None,
            nutrition_text=nutrition_text
        )

        return ScanResultOut(
            scan_id=scan.id,
            product_id=None,
            nutrition_id=None,
            ingredient_id=None,
        )

    async def _build_report_and_save_history(
        self,
        user_id: str,
        product_id: str,
        image: UploadFile | None,
    ) -> ScanResultOut:
        # 1) 스캔 + 개인화 분석 + scan_history 저장
        scan: ScanHistoryOut = await self.scan_history_service.analyze_and_save_scan(
            user_id=user_id,
            product_id=product_id,   # 여기서 barcode 안 씀
            image=image,
            nutrition_text=None,
        )

        # 2) nutrition / ingredient 조회
        nutrition_id = self.nutrition_service.get_id_by_product_id(product_id)
        ingredient_id = self.ingredient_service.get_id_by_product_id(product_id)

        # 3) 응답 조립
        return ScanResultOut(
            scan_id=scan.id,
            product_id=product_id,
            nutrition_id=nutrition_id,
            ingredient_id=ingredient_id,
        )
