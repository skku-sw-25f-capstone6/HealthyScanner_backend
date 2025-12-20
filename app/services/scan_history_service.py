# app/services/scan_history_service.py

from datetime import datetime, timezone, date
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
from app.services.image_storage_service import ImageStorageService

from app.schemas.scan_history import (
    ScanHistoryCreate,
    ScanHistoryOut,
    ScanDecision,
    ScanDetailOut,
    ScanReports,
    ReportBlock,
    AlternativeReport,
    CautionFactor,
    RiskLevel,
    FaceType,
    ScanHistoryUpdate,
    ScanHistoryNameCategoryOut,
    ScanSummaryOut,
    ScanHistoryListOut
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
        image_storage: ImageStorageService,
    ):
        self.db = db
        self.user_dal = user_dal
        self.product_dal = product_dal
        self.nutrition_dal = nutrition_dal
        self.ingredient_dal = ingredient_dal
        self.scan_history_dal = scan_history_dal
        self.product_service = product_service
        self.ai_service = ai_service
        self.image_storage = image_storage

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
        saved_image_url: str | None = None
        display_name = None
        display_category = None
        

        # 여기서 이미지 저장이 될 수도 있음
        # product_id가 있는 경우에만 이미지 받는 거임 (수정해야 할 수도)
        if analyze_type == "barcode_image":
            if product_id is None:
                raise HTTPException(404, "Product not found")
            
            if image is not None:
                await self.product_service.attach_image(self.db, product_id, image)

            product = self.product_dal.get(self.db, str(product_id))
            
            # db에 무조건 있다는 가정
            # Unknown Product는 안 될 거임
            tmp_display_name = product.name if product else "Unknown Product"
            tmp_display_category = product.category if product else "Uncategorized"
            saved_image_url = getattr(product, "image_url", None)

            nutrition = self.nutrition_dal.get_by_product_id(self.db, str(product_id))

            if nutrition:
                print(f"DEBUG TYPE CHECK: id={nutrition[0].id}, type={type(nutrition[0].id)}")
                print(f"DEBUG TYPE CHECK: product_id={nutrition[0].product_id}, type={type(nutrition[0].product_id)}")
                
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

            d = datetime.now(timezone.utc)
            n = self.scan_history_dal.count_scans_date(
                db=self.db,
                user_id=user_id,
                local_date=d.date(),
            ) + 1

            tmp_display_name = f"{d.month}월 {d.day}일 {n}번"
            tmp_display_category = "Uncategorized"

            if image is not None:
                image_bytes = await image.read()
                saved_image_url = await self.image_storage.save_scan_image_bytes(image.content_type, image_bytes)

                # AI용 data URL은 필요하면 따로 만들기
                b64 = base64.b64encode(image_bytes).decode("ascii")
                mime = image.content_type or "image/jpeg"
                image_data_url = f"data:{mime};base64,{b64}"

        elif analyze_type == "image":
            if image is None:
                raise HTTPException(400, "Image is required for analyze_type 'image'")
            
            image_bytes = await image.read()
            saved_image_url = await self.image_storage.save_scan_image_bytes(image.content_type, image_bytes)

            # AI용 data URL은 필요하면 따로 만들기
            b64 = base64.b64encode(image_bytes).decode("ascii")
            mime = image.content_type or "image/jpeg"
            image_data_url = f"data:{mime};base64,{b64}"
            
            d = datetime.now(timezone.utc)
            n = self.scan_history_dal.count_scans_date(
                db=self.db,
                user_id=user_id,
                local_date=d.date(),
            ) + 1

            tmp_display_name = f"{d.month}월 {d.day}일 {n}번"
            tmp_display_category = "Uncategorized"

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
        display_name = tmp_display_name
        display_category = tmp_display_category
        image_url = saved_image_url

        conditions: List[str] = user_dict.get("conditions") or []  # 예: ["diabetes"]
        allergies: List[str] = user_dict.get("allergies") or []   # 예: ["peanut"]
        habits: List[str] = user_dict.get("habits") or []      # 예: ["low_sugar"]

        ai_allergy_report: Optional[str] = ai_result.ai_allergy_report
        ai_condition_report: Optional[str] = ai_result.ai_condition_report
        ai_alter_report: Optional[str] = ai_result.ai_alter_report
        ai_vegan_report: Optional[str] = ai_result.ai_vegan_report
        ai_total_report: Optional[str] = ai_result.ai_total_report

        ai_allergy_brief: Optional[str] = ai_result.ai_allergy_brief
        ai_condition_brief: Optional[str] = ai_result.ai_condition_brief
        ai_alter_brief: Optional[str] = ai_result.ai_alter_brief
        ai_vegan_brief: Optional[str] = ai_result.ai_vegan_brief

        caution_factors_raw: Optional[List[Dict[str, str]]] = ai_result.caution_factors
        caution_factors: Optional[List[Dict[str, str]]] = caution_factors_raw
    
        product_name: Optional[str] = ai_result.product_name
        product_nutrition: Optional[dict[str, str]] = ai_result.product_nutrition
        product_ingredient: Optional[str] = ai_result.product_ingredient

        now_aware = datetime.now(timezone.utc)
        scanned_at = now_aware.replace(tzinfo=None)  # naive datetime 저장
    
        data = ScanHistoryCreate(
            user_id=user_id,
            product_id=product_id,
            scanned_at=scanned_at,
            display_name=display_name,
            display_category=display_category,
            image_url=image_url,
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
            caution_factors=caution_factors,
            ai_vegan_brief=ai_vegan_brief,
            ai_alter_brief=ai_alter_brief,
            ai_condition_brief=ai_condition_brief,
            ai_allergy_brief=ai_allergy_brief,
            product_name=product_name,
            product_nutrition=product_nutrition,
            product_ingredient=product_ingredient,
            dirty=False
        )

        scan = self.scan_history_dal.create(self.db, data)
        return scan


    async def update_name_category(
        self, 
        scan_id: str, 
        display_name: str, 
        display_category: str
    ) -> ScanHistoryNameCategoryOut:
        scan = self.scan_history_dal.get(self.db, scan_id)
        if scan is None:
            raise HTTPException(status_code=404, detail="Scan not found")
        
        update_in = ScanHistoryUpdate(
            display_name=display_name,
            display_category=display_category,
            dirty=True,
        )

        scan = self.scan_history_dal.update(self.db, scan_id, update_in)
        if scan is None:
            raise HTTPException(status_code=404, detail="Scan not found")

        return ScanHistoryNameCategoryOut(
            name=scan.display_name,
            category=scan.display_category,
            updated_at=scan.updated_at
        )

    async def get_scan_list_by_date(
        self, user_id: str, date: datetime
    ) -> ScanHistoryListOut:
        scans = self.scan_history_dal.get_by_date(self.db, user_id, date)

        scan_list = []
        for s in scans:
            decision = (s.decision or "ok").lower()
            risk_level = {
                "avoid": RiskLevel.red,
                "caution": RiskLevel.yellow,
                "ok": RiskLevel.green,
            }.get(decision, RiskLevel.green)

            scan_list.append(
                ScanSummaryOut(
                    name=s.product_name if not s.dirty else s.display_name,
                    category=s.display_category,
                    scanID=s.id,
                    riskLevel=risk_level,     # DB에 컬럼 있으면
                    summary=s.summary,  # or summary 필드
                    url=s.image_url,            # 이미지 저장한 컬럼명
                )
            )

        return ScanHistoryListOut(scan=scan_list)

    def get_scan_detail(self, scan_id: str) -> ScanDetailOut:
        scan = self.scan_history_dal.get(self.db, scan_id)
        if scan is None:
            raise HTTPException(status_code=404, detail="Scan not found")

        # 1) decision -> risk_level
        decision = (scan.decision or "ok").lower()
        risk_level = {
            "avoid": RiskLevel.red,
            "caution": RiskLevel.yellow,
            "ok": RiskLevel.green,
        }.get(decision, RiskLevel.green)

        def face_for_negative() -> FaceType:
            if risk_level == RiskLevel.red:
                return FaceType.NO
            if risk_level == RiskLevel.yellow:
                return FaceType.NOT_BAD
            return FaceType.GOOD

        # 2) 각 보고서 블록 만들기 (AI 컬럼 매핑)
        allergies_block = None
        if scan.ai_allergy_report:
            allergies_block = ReportBlock(
                brief_report=scan.ai_allergy_brief,
                face=face_for_negative(),
                report=scan.ai_allergy_report,
            )

        condition_block = None
        if scan.ai_condition_report:
            condition_block = ReportBlock(
                brief_report=scan.ai_condition_brief,
                face=face_for_negative(),
                report=scan.ai_condition_report,
            )

        alternatives_list: List[AlternativeReport] = []
        if scan.ai_alter_report:
            alternatives_list.append(
                AlternativeReport(
                    brief_report=scan.ai_alter_brief,
                    face=FaceType.GOOD,
                    report=scan.ai_alter_report,
                )
            )

        vegan_block = None
        if scan.ai_vegan_report:
            vegan_block = ReportBlock(
                brief_report=scan.ai_vegan_brief,
                face=face_for_negative(),
                report=scan.ai_vegan_report,
            )

        # 3) caution_factors(list[str]) -> list[CautionFactor]
        caution_factors_list: List[CautionFactor] = []
        if scan.caution_factors:
            for cf in scan.caution_factors:   # cf = {"key": "...", "level": "red"}
                factor = cf["key"]
                level = cf["level"]

                eval_map = {
                    "red": "NO",
                    "yellow": "CAUTION",
                    "green": "OK",
                }
                eval_code = eval_map.get(level, "CAUTION")

                caution_factors_list.append(
                    CautionFactor(factor=factor, evaluation=eval_code)
                )

        return ScanDetailOut(
            summary=scan.summary or "",
            risk_level=risk_level,
            reports=ScanReports(
                allergies=allergies_block,
                condition=condition_block,
                alternatives=alternatives_list,
                vegan=vegan_block,
            ),
            caution_factors=caution_factors_list,
        )