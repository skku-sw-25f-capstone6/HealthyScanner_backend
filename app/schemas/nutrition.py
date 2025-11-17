# app/schemas/nutrition.py
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class NutritionBase(BaseModel):
    per_serving_grams: Optional[float] = None
    calories: Optional[float] = None
    carbs_g: Optional[float] = None
    sugar_g: Optional[float] = None
    protein_g: Optional[float] = None
    fat_g: Optional[float] = None
    sat_fat_g: Optional[float] = None
    trans_fat_g: Optional[float] = None
    sodium_mg: Optional[float] = None
    cholesterol_mg: Optional[float] = None

    label_version: Optional[int] = 1


class NutritionCreate(NutritionBase):
    product_id: str


class NutritionUpdate(BaseModel):
    per_serving_grams: Optional[float] = None
    calories: Optional[float] = None
    carbs_g: Optional[float] = None
    sugar_g: Optional[float] = None
    protein_g: Optional[float] = None
    fat_g: Optional[float] = None
    sat_fat_g: Optional[float] = None
    trans_fat_g: Optional[float] = None
    sodium_mg: Optional[float] = None
    cholesterol_mg: Optional[float] = None

    label_version: Optional[int] = None

    model_config = ConfigDict(extra="forbid")


class NutritionOut(NutritionBase):
    id: str
    product_id: str
    label_version: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
