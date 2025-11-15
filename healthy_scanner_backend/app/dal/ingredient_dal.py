# app/dal/ingredient_dal.py
from typing import List, Optional
from uuid import uuid4

from sqlalchemy.orm import Session

from app.models.ingredient import Ingredient
from app.schemas.ingredient import IngredientCreate, IngredientUpdate


class IngredientDal:
    @staticmethod
    def create(db: Session, ing_in: IngredientCreate) -> Ingredient:
        ingredient = Ingredient(
            id=str(uuid4()),
            product_id=ing_in.product_id,
            raw_ingredient=ing_in.raw_ingredient,
            norm_text=ing_in.norm_text,
            allergen_tags=ing_in.allergen_tags,
            order_index=ing_in.order_index,
        )
        db.add(ingredient)
        db.commit()
        db.refresh(ingredient)
        return ingredient

    @staticmethod
    def get(db: Session, ingredient_id: str) -> Optional[Ingredient]:
        return db.query(Ingredient).filter(Ingredient.id == ingredient_id).first()

    @staticmethod
    def list(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        product_id: Optional[str] = None,
    ) -> List[Ingredient]:
        q = db.query(Ingredient)
        if product_id is not None:
            q = q.filter(Ingredient.product_id == product_id)
        # 보통 성분 순서가 중요하니까 order_index 오름차순
        q = q.order_by(Ingredient.order_index.asc(), Ingredient.created_at.asc())
        return q.offset(skip).limit(limit).all()

    @staticmethod
    def update(
        db: Session,
        ingredient_id: str,
        ing_in: IngredientUpdate,
    ) -> Optional[Ingredient]:
        ingredient = db.query(Ingredient).filter(Ingredient.id == ingredient_id).first()
        if not ingredient:
            return None

        data = ing_in.model_dump(exclude_unset=True)
        for field, value in data.items():
            setattr(ingredient, field, value)

        db.commit()
        db.refresh(ingredient)
        return ingredient

    @staticmethod
    def delete(db: Session, ingredient_id: str) -> bool:
        ingredient = db.query(Ingredient).filter(Ingredient.id == ingredient_id).first()
        if not ingredient:
            return False
        db.delete(ingredient)
        db.commit()
        return True
