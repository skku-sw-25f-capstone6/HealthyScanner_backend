# app/services/product_service.py
from typing import Optional, List
from sqlalchemy.orm import Session

from app.DAL.product_DAL import ProductDAL
from app.DAL.nutrition_DAL import NutritionDAL
from app.DAL.ingredient_DAL import IngredientDAL
from app.models.product import Product
from app.models.nutrition import Nutrition
from app.models.ingredient import Ingredient


class ProductService:
    def __init__(self, db: Session):
        self.db = db
        self.product_DAL = ProductDAL()
        self.nutrition_DAL = NutritionDAL()
        self.ingredient_DAL = IngredientDAL()

    def get_product_detail(
        self,
        product_id: str,
        with_nutrition: bool = True,
        with_ingredient: bool = True,
    ) -> Optional[dict]:
        # 1) 상품 조회
        product: Optional[Product] = self.product_DAL.get(self.db, product_id)
        if not product:
            return None

        # 2) 영양 정보
        nutritions: Optional[List[Nutrition]] = None
        if with_nutrition:
            nutritions = self.nutrition_DAL.list(
                self.db,
                product_id=product_id,
                skip=0,
                limit=100,
            )

        # 3) 성분 정보
        ingredients: Optional[List[Ingredient]] = None
        if with_ingredient:
            ingredients = self.ingredient_DAL.list(
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
