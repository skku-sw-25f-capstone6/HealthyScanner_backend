# app/services/nutrition_service.py

from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import UploadFile, HTTPException
from sqlalchemy.orm import Session

from app.DAL.nutrition_DAL import NutritionDAL
from app.models.nutrition import Nutrition

class NutritionService:
    def __init__(
        self, 
        db: Session,
        nutrition_dal: NutritionDAL
    ):
        self.db = db
        self.nutrition_dal = nutrition_dal

    def get_id_by_product_id(self, product_id: str) -> Optional[Nutrition]:
        # NutritionDAL 이 static 메서드라면 이런 식으로
        return self.nutrition_dal.get_id_by_product_id(self.db, product_id)