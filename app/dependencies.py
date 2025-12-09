# app/dependencies.py
from fastapi import Depends
from sqlalchemy.orm import Session
from pathlib import Path

from app.DAL.scan_history_DAL import ScanHistoryDAL
from app.DAL.product_DAL import ProductDAL
from app.DAL.nutrition_DAL import NutritionDAL
from app.DAL.ingredient_DAL import IngredientDAL
from app.DAL.user_DAL import UserDAL
from app.DAL.user_daily_score_DAL import UserDailyScoreDAL

from app.services.scan_history_service import ScanHistoryService
from app.services.ingredient_service import IngredientService
from app.services.nutrition_service import NutritionService
from app.services.product_service import ProductService
from app.services.user_service import UserService
from app.services.user_daily_score_service import UserDailyScoreService
from app.services.scan_flow_service import ScanFlowService
from app.services.image_storage_service import ImageStorageService
from app.services.ai_scan_analysis_service import AiScanAnalysisService
from app.services.scan_get_full_service import ScanGetFullService


from app.core.database import get_db
from app.core.ai_client import get_openai_client
from app.core.config import settings


def get_user_dal() -> UserDAL:
    return UserDAL()

def get_ingredient_dal() -> IngredientDAL:
    return IngredientDAL()

def get_user_daily_score_dal() -> UserDailyScoreDAL:
    return UserDailyScoreDAL()

def get_scan_history_dal() -> ScanHistoryDAL:
    return ScanHistoryDAL()

def get_product_dal() -> ProductDAL:
    return ProductDAL()

def get_nutrition_dal() -> NutritionDAL:
    return NutritionDAL()

def get_image_storage_service() -> ImageStorageService:
    return ImageStorageService(
        base_dir=Path(settings.IMAGE_BASE_DIR),
        base_url=settings.IMAGE_BASE_URL
    )

def get_nutrition_service(
        db: Session = Depends(get_db),
        nutrition_dal: NutritionDAL = Depends(get_nutrition_dal)
    ) -> NutritionService:
    return NutritionService(
        db = db,
        nutrition_dal = nutrition_dal
    )


def get_ingredient_service(
        db: Session = Depends(get_db),
        ingredient_dal: IngredientDAL = Depends(get_ingredient_dal)
    ) -> IngredientService:
    return IngredientService(
        db=db,
        ingredient_dal=ingredient_dal
    )

def get_product_service(
        db: Session = Depends(get_db),
        product_dal: ProductDAL = Depends(get_product_dal),
        nutrition_dal: NutritionDAL = Depends(get_nutrition_dal),
        ingredient_dal: IngredientDAL = Depends(get_ingredient_dal),
        image_storage: ImageStorageService = Depends(get_image_storage_service)
) -> ProductService:
    return ProductService(db, product_dal, nutrition_dal, ingredient_dal, image_storage)


def get_user_daily_score_service(
        db: Session = Depends(get_db),
        uds_dal: UserDailyScoreDAL = Depends(get_user_daily_score_dal),
        scan_history_dal: ScanHistoryDAL = Depends(get_scan_history_dal),
) -> UserDailyScoreService:
    return UserDailyScoreService(
        db=db,
        user_daily_score_dal=uds_dal,
        scan_history_dal=scan_history_dal
    )



def get_ai_scan_analysis_service():
    client = get_openai_client()
    return AiScanAnalysisService(openai_client=client)


def get_scan_history_service(
    db: Session = Depends(get_db),
    user_dal: UserDAL = Depends(get_user_dal),
    product_dal: ProductDAL = Depends(get_product_dal),
    nutrition_dal: NutritionDAL = Depends(get_nutrition_dal),
    ingredient_dal: IngredientDAL = Depends(get_ingredient_dal),
    scan_history_dal: ScanHistoryDAL = Depends(get_scan_history_dal),
    product_service: ProductService = Depends(get_product_service),
    ai_service: AiScanAnalysisService = Depends(get_ai_scan_analysis_service)
) -> ScanHistoryService:
    return ScanHistoryService(
        db = db,
        user_dal = user_dal,
        product_dal =  product_dal,
        nutrition_dal = nutrition_dal,
        ingredient_dal = ingredient_dal, 
        scan_history_dal = scan_history_dal,
        product_service = product_service,
        ai_service = ai_service
    )

def get_scan_get_full_service(
    db: Session = Depends(get_db),
    scan_history_dal: ScanHistoryDAL = Depends(get_scan_history_dal),
    product_dal: ProductDAL = Depends(get_product_dal),
    nutrition_dal: NutritionDAL = Depends(get_nutrition_dal),
    ingredient_dal: IngredientDAL = Depends(get_ingredient_dal),
    scan_history_service: ScanHistoryService = Depends(get_scan_history_service)
) -> ScanGetFullService:
    return ScanGetFullService(
        db=db,
        scan_history_dal=scan_history_dal,
        product_dal=product_dal,
        nutrition_dal=nutrition_dal,
        ingredient_dal=ingredient_dal,
        scan_history_service=scan_history_service
    )

def get_user_service(
    db: Session = Depends(get_db),
    user_dal: UserDAL = Depends(get_user_dal),
    user_daily_score_dal: UserDailyScoreDAL = Depends(get_user_daily_score_dal),
) -> UserService:
    return UserService(db, user_dal, user_daily_score_dal)


def get_scan_flow_service(
    scan_history_service: ScanHistoryService = Depends(get_scan_history_service),
    nutrition_service: NutritionService = Depends(get_nutrition_service),
    ingredient_service: IngredientService = Depends(get_ingredient_service),
    product_service: ProductService = Depends(get_product_service),
    user_daily_score_service: UserDailyScoreService = Depends(get_user_daily_score_service),
) -> ScanFlowService:
    return ScanFlowService(
        scan_history_service=scan_history_service,
        product_service=product_service,
        nutrition_service=nutrition_service,
        ingredient_service=ingredient_service,
        user_daily_score_service=user_daily_score_service,
    )

