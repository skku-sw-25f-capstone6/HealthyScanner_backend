# app/schemas/product.py
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict

from app.schemas.nutrition import NutritionOut
from app.schemas.ingredient import IngredientOut



class ProductBase(BaseModel):
    barcode: Optional[str] = None
    barcode_kind: Optional[str] = None

    brand: Optional[str] = None
    name: Optional[str] = None
    category: Optional[str] = None
    size_text: Optional[str] = None
    image_url: Optional[str] = None
    country: Optional[str] = None
    notes: Optional[str] = None

    score: Optional[int] = None


class ProductCreate(ProductBase):
    # 일단 전부 optional로 두고, 서버에서 필요한 최소값만 나중에 검증해도 됨
    pass


class ProductUpdate(BaseModel):
    barcode: Optional[str] = None
    barcode_kind: Optional[str] = None

    brand: Optional[str] = None
    name: Optional[str] = None
    category: Optional[str] = None
    size_text: Optional[str] = None
    image_url: Optional[str] = None
    country: Optional[str] = None
    notes: Optional[str] = None

    score: Optional[int] = None

    model_config = ConfigDict(extra="forbid")


class ProductOut(ProductBase):
    id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ProductDetailOut(BaseModel):
    product: ProductOut
    nutritions: Optional[List[NutritionOut]] = None
    ingredients: Optional[List[IngredientOut]] = None

    model_config = ConfigDict(from_attributes=True)


class ProductSimpleOut(BaseModel):
    name: str
    category: str
    image_url: str   # 실제론 image_url 이나 cdn_url일 수도 있음

    # Product 모델에서 바로 읽어오고 싶으면 from_attributes 사용
    model_config = ConfigDict(from_attributes=True)