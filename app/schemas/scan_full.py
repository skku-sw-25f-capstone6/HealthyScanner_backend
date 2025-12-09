# app/schemas/scan_full.py
from pydantic import BaseModel
from typing import Optional

from app.schemas.product import ProductSimpleOut
from app.schemas.scan_history import ScanReports, CautionFactor
from app.schemas.nutrition import NutritionDetail
from app.schemas.ingredient import IngredientText


class ScanPartOut(BaseModel):
    summary: str
    score: int
    reports: ScanReports
    caution_factors: list[CautionFactor]


class ScanFullOut(BaseModel):
    product: ProductSimpleOut
    scan: ScanPartOut
    nutrition: Optional[NutritionDetail] = None
    ingredient: Optional[IngredientText] = None
