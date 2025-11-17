# app/schemas/ingredient.py
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class IngredientBase(BaseModel):
    raw_ingredient: str
    norm_text: Optional[str] = None
    allergen_tags: Optional[str] = None  # 예: '["peanut","wheat"]'
    order_index: int = 0


class IngredientCreate(IngredientBase):
    product_id: str


class IngredientUpdate(BaseModel):
    raw_ingredient: Optional[str] = None
    norm_text: Optional[str] = None
    allergen_tags: Optional[str] = None
    order_index: Optional[int] = None

    model_config = ConfigDict(extra="forbid")


class IngredientOut(IngredientBase):
    id: str
    product_id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
