# app/services/get_full_service.py (예시)
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.DAL.scan_history_DAL import ScanHistoryDAL
from app.DAL.product_DAL import ProductDAL
from app.DAL.nutrition_DAL import NutritionDAL
from app.DAL.ingredient_DAL import IngredientDAL

from app.schemas.scan_full import ScanFullOut, ScanPartOut
from app.schemas.product import ProductSimpleOut
from app.schemas.nutrition import NutritionDetail, NutritionBase
from app.schemas.ingredient import IngredientText, IngredientBase

from app.services.scan_history_service import ScanHistoryService




class ScanGetFullService:
    def __init__(
        self,
        db: Session,
        scan_history_dal: ScanHistoryDAL,
        product_dal: ProductDAL,
        nutrition_dal: NutritionDAL,
        ingredient_dal: IngredientDAL,
        scan_history_service: ScanHistoryService
    ):
        self.db = db
        self.scan_history_dal = scan_history_dal
        self.product_dal = product_dal
        self.nutrition_dal = nutrition_dal
        self.ingredient_dal = ingredient_dal
        self.service = scan_history_service

    def _build_fallback_product(self, scan) -> ProductSimpleOut:
        # scanned_at 기준 날짜로 임시 이름 생성
        d = scan.scanned_at.date()
        user_id = scan.user_id
        order = self.scan_history_dal.get_scan_order_for_day(
            db = self.db, 
            user_id = user_id, 
            local_date = d, 
            scan_id = scan.id,
        )
        
        scan_history = self.scan_history_dal.get(self.db, scan.id)

        if scan_history is None:
            raise RuntimeError("scan_history should not be None here")

        name = scan_history.display_name or f"{d.month}월 {d.day}일 {order}번"

        if scan.product_name:
            name = scan.product_name

        category = scan_history.display_category or "Uncategorized"

        product_id = scan_history.product_id
        product = self.product_dal.get(self.db, product_id)


        image_url = ""
        if product and getattr(product, "image_url", None):
            image_url = product.image_url
        elif scan_history.image_url:
            image_url = scan_history.image_url

        return ProductSimpleOut(
            name=name,
            category=category,
            image_url=image_url,  # 이미지 없으면 빈 문자열
        )

    def get_full_scan(self, scan_id: str) -> ScanFullOut:
        scan = self.scan_history_dal.get(self.db, scan_id)
        if scan is None:
            raise HTTPException(status_code=404, detail="Scan not found")

        # product
        product = self.product_dal.get(self.db, scan.product_id)
        if product is None:
            product_out = self._build_fallback_product(scan)
        else:
            product_out = ProductSimpleOut.model_validate(product)

        # scan(요약 + 리포트들)
        scan_detail = self.service.get_scan_detail(scan.id)  # summary / reports / caution_factors 만들던 함수
        scan_part = ScanPartOut(
            summary=scan_detail.summary,
            score=scan.ai_total_score or 0,
            reports=scan_detail.reports,
            caution_factors=scan_detail.caution_factors,
        )

        # nutrition / ingredient는 없을 수도 있으니 Optional
        nutrition = self.nutrition_dal.get_id_by_product_id(self.db, scan.product_id)
        ingredient = self.ingredient_dal.get_id_by_product_id(self.db, scan.product_id)

        if nutrition is None:
            ai_response = scan.product_nutrition
            nutrition = NutritionBase.model_validate(ai_response)

        if ingredient is None:
            ai_response = scan.product_ingredient
            if ai_response:
                ingredient = IngredientBase(raw_ingredient=ai_response)
            else:
                ingredient = IngredientBase(raw_ingredient="")

        return ScanFullOut(
            product=product_out,
            scan=scan_part,
            nutrition=NutritionDetail.model_validate(nutrition) if nutrition else None,
            ingredient=IngredientText(text=ingredient.raw_ingredient) if ingredient else None,
        )
