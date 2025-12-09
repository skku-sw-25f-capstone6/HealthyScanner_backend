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


class NutritionCreate(NutritionBase):
    product_id: str
    label_version: int = 1


class NutritionUpdate(NutritionBase):
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


class NutritionDetail(BaseModel):
    carbs_g: float | None = None
    protein_g: float | None = None
    sodium_mg: float | None = None
    sugar_g: float | None = None
    fat_g: float | None = None
    trans_fat_g: float | None = None
    sat_fat_g: float | None = None
    cholesterol_mg: float | None = None
    calories: float | None = None
    per_serving_grams: float | None = None

    # SQLAlchemy ORM 객체에서 바로 읽어오려고 쓰는 설정
    model_config = ConfigDict(from_attributes=True)


class NutritionDetailOut(BaseModel):
    nutrition: NutritionDetail