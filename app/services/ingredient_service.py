# app/services/ingredient_service.py

from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.DAL.ingredient_DAL import IngredientDAL
from app.models.ingredient import Ingredient

class IngredientService:
    def __init__(
        self, 
        db: Session,
        ingredient_dal: IngredientDAL
    ):
        self.db = db
        self.ingredient_dal = ingredient_dal

    def get_id_by_product_id(self, product_id: str) -> Optional[Ingredient]:
        # IngredientDAL 이 static 메서드라면 이런 식으로
        return self.ingredient_dal.get_id_by_product_id(self.db, product_id)