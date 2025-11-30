# app/services/scan_history_service.py

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Literal

from fastapi import UploadFile, HTTPException
from sqlalchemy.orm import Session

from app.DAL.scan_history_DAL import ScanHistoryDAL
from app.DAL.user_DAL import UserDAL
from app.DAL.nutrition_DAL import NutritionDAL
from app.DAL.product_DAL import ProductDAL
from app.DAL.ingredient_DAL import IngredientDAL

from app.services.product_service import ProductService
from app.services.ai_scan_analysis_service import AiScanAnalysisService

from app.schemas.scan_history import (
    ScanHistoryCreate,
    ScanHistoryOut,
    ScanDecision,
)
from app.schemas.user import UserOut
from app.schemas.product import ProductOut
from app.schemas.nutrition import NutritionOut
from app.schemas.ingredient import IngredientOut
import base64

AnalyzeType = Literal["barcode_image", "nutrition_label", "image"]

class ScanHistoryService:
    def __init__(
        self,
        db: Session,
        user_dal: UserDAL,
        product_dal: ProductDAL,
        nutrition_dal: NutritionDAL,
        ingredient_dal: IngredientDAL,
        scan_history_dal: ScanHistoryDAL,
        product_service: ProductService,
        ai_service: AiScanAnalysisService,
    ):
        self.db = db
        self.user_dal = user_dal
        self.product_dal = product_dal
        self.nutrition_dal = nutrition_dal
        self.ingredient_dal = ingredient_dal
        self.scan_history_dal = scan_history_dal
        self.product_service = product_service
        self.ai_service = ai_service

    async def analyze_and_save_scan(
        self,
        user_id: str,
        product_id: str | None,
        image: UploadFile | None,
        nutrition_text: str | None,
        analyze_type: AnalyzeType,
    ) -> ScanHistoryOut:    
            
        user = self.user_dal.get(self.db, user_id)
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")

        user_dict = UserOut.model_validate(user).model_dump()
        product_dict: dict | None = None
        nutrition_dict: dict | None = None
        ingredient_list: list[dict] | None = None
        image_data_url: str | None = None

        # 여기서 이미지 저장이 될 수도 있음
        # product_id가 있는 경우에만 이미지 받는 거임 (수정해야 할 수도)
        if analyze_type == "barcode_image":
            if product_id is None:
                raise HTTPException(404, "Product not found")
            
            if image is not None:
                await self.product_service.attach_image(self.db, product_id, image)

            product = self.product_dal.get(self.db, str(product_id))

            nutrition = self.nutrition_dal.get_by_product_id(self.db, str(product_id))
            ingredients = self.ingredient_dal.get_by_product_id(self.db, str(product_id))

            product_dict = ProductOut.model_validate(product).model_dump()
            nutrition_dict = (
                NutritionOut.model_validate(nutrition).model_dump() if nutrition else None
            )
            ingredient_list = [
                IngredientOut.model_validate(i).model_dump() for i in ingredients
            ]
        
        elif analyze_type == "nutrition_label":
            product = None
            nutrition = None
            ingredients = []
            
            # 최소한의 정보만 넘기기
            product_dict = None            # 또는 {"name": None, ...} 같은 placeholder
            nutrition_dict = {"raw_label": nutrition_text} if nutrition_text else None
            ingredient_list = []

            if image is not None:
                # 이미지 파일 읽기
                image_bytes = await image.read()

                b64 = base64.b64encode(image_bytes).decode("ascii")
                
                # content_type 사용해서 data URL 만들기
                mime = image.content_type or "image/jpeg"
                image_data_url = f"data:{mime};base64,{b64}"

        elif analyze_type == "image":
            if image is None:
                raise HTTPException(400, "Image is required for analyze_type 'image'")
            
            # 이미지 파일 읽기
            image_bytes = await image.read()

            b64 = base64.b64encode(image_bytes).decode("ascii")
            
            # content_type 사용해서 data URL 만들기
            mime = image.content_type or "image/jpeg"
            image_data_url = f"data:{mime};base64,{b64}"

        else:
            raise HTTPException(400, "Invalid analyze_type")


        # 여기서 분석 로직이 들어가야 함
        ai_result = await self.ai_service.analyze(
            user_profile=user_dict,
            product=product_dict,
            nutrition=nutrition_dict,
            ingredients=ingredient_list,
            analyze_type = analyze_type,
            image_data_url=image_data_url,
        )


        summary: str = ai_result.ai_total_summary
        decision: ScanDecision = ScanDecision(ai_result.decision)
        ai_total_score: int = ai_result.ai_total_score

        conditions: List[str] = user_dict.get("conditions") or []  # 예: ["diabetes"]
        allergies: List[str] = user_dict.get("allergies") or []   # 예: ["peanut"]
        habits: List[str] = user_dict.get("habits") or []      # 예: ["low_sugar"]

        ai_allergy_report: Optional[str] = ai_result.ai_allergy_report
        ai_condition_report: Optional[str] = ai_result.ai_condition_report
        ai_alter_report: Optional[str] = ai_result.ai_alter_report
        ai_vegan_report: Optional[str] = ai_result.ai_vegan_report
        ai_total_report: Optional[str] = ai_result.ai_total_report

        caution_factors_raw: Optional[List[str]] = ai_result.caution_factors
        caution_factors: Optional[List[Dict[str, Any]]] = (
            [{"factor": factor} for factor in caution_factors_raw]
            if caution_factors_raw
            else None
        )

        scanned_at = datetime.now(timezone.utc)

        data = ScanHistoryCreate(
            user_id=user_id,
            product_id=product_id if product_id is not None else "NULL",
            scanned_at=scanned_at,
            decision=decision,
            summary=summary,
            ai_total_score=ai_total_score,
            conditions=conditions,
            allergies=allergies,
            habits=habits,
            ai_allergy_report=ai_allergy_report,
            ai_condition_report=ai_condition_report,
            ai_alter_report=ai_alter_report,
            ai_vegan_report=ai_vegan_report,
            ai_total_report=ai_total_report,
            caution_factors=caution_factors
        )

        scan = self.scan_history_dal.create(self.db, data)
        return scan
