# app/services/product_service.py
from typing import Optional, List
from sqlalchemy.orm import Session
from fastapi import UploadFile

from app.DAL.product_DAL import ProductDAL
from app.DAL.nutrition_DAL import NutritionDAL
from app.DAL.ingredient_DAL import IngredientDAL
from app.models.product import Product
from app.models.nutrition import Nutrition
from app.models.ingredient import Ingredient

from app.services.image_storage_service import ImageStorageService

from app.schemas.product import *


class ProductService:
    def __init__(
        self, 
        db: Session,
        product_dal: ProductDAL,
        nutrition_dal: NutritionDAL,
        ingredient_dal: IngredientDAL,
        image_storage: ImageStorageService
    ):
        self.db = db
        self.product_dal = product_dal
        self.nutrition_dal = nutrition_dal
        self.ingredient_dal = ingredient_dal
        self.image_storage = image_storage

    def get_product_detail(
        self,
        product_id: str,
        with_nutrition: bool = True,
        with_ingredient: bool = True,
    ) -> Optional[dict]:
        # 1) 상품 조회
        product: Optional[Product] = self.product_dal.get(self.db, product_id)
        if not product:
            return None

        # 2) 영양 정보
        nutritions: Optional[List[Nutrition]] = None
        if with_nutrition:
            nutritions = self.nutrition_dal.list(
                self.db,
                product_id=product_id,
                skip=0,
                limit=100,
            )

        # 3) 성분 정보
        ingredients: Optional[List[Ingredient]] = None
        if with_ingredient:
            ingredients = self.ingredient_dal.list(
                self.db,
                product_id=product_id,
                skip=0,
                limit=500,
            )

        # 4) 라우터에 넘겨줄 구조 (Pydantic이 알아서 변환해 줌)
        return {
            "product": product,
            "nutritions": nutritions,
            "ingredients": ingredients,
        }
    
    def get_id_by_barcode(self, barcode):
        return self.product_dal.get_by_barcode(self.db, barcode)
    
    async def attach_image(
        self, db: Session, product_id: str, file: UploadFile
    ):
        image_url = await self.image_storage.save_product_image(product_id, file)
        update_in = ProductUpdate(image_url=image_url)
        product = self.product_dal.update(db, product_id, update_in)
        return product
