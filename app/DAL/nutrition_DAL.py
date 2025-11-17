# app/DAL/nutrition_DAL.py
from typing import List, Optional
from uuid import uuid4

from sqlalchemy.orm import Session

from app.models.nutrition import Nutrition
from app.schemas.nutrition import NutritionCreate, NutritionUpdate


class NutritionDAL:
    @staticmethod
    def create(db: Session, nutrition_in: NutritionCreate) -> Nutrition:
        nutrition = Nutrition(
            id=str(uuid4()),
            product_id=nutrition_in.product_id,
            per_serving_grams=nutrition_in.per_serving_grams,
            calories=nutrition_in.calories,
            carbs_g=nutrition_in.carbs_g,
            sugar_g=nutrition_in.sugar_g,
            protein_g=nutrition_in.protein_g,
            fat_g=nutrition_in.fat_g,
            sat_fat_g=nutrition_in.sat_fat_g,
            trans_fat_g=nutrition_in.trans_fat_g,
            sodium_mg=nutrition_in.sodium_mg,
            cholesterol_mg=nutrition_in.cholesterol_mg,
            label_version=nutrition_in.label_version or 1,
        )
        db.add(nutrition)
        db.commit()
        db.refresh(nutrition)
        return nutrition

    @staticmethod
    def get(db: Session, nutrition_id: str) -> Optional[Nutrition]:
        return db.query(Nutrition).filter(Nutrition.id == nutrition_id).first()

    @staticmethod
    def list(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        product_id: Optional[str] = None,
    ) -> List[Nutrition]:
        q = db.query(Nutrition)
        if product_id is not None:
            q = q.filter(Nutrition.product_id == product_id)
        return q.offset(skip).limit(limit).all()

    @staticmethod
    def update(
        db: Session,
        nutrition_id: str,
        nutrition_in: NutritionUpdate,
    ) -> Optional[Nutrition]:
        nutrition = db.query(Nutrition).filter(Nutrition.id == nutrition_id).first()
        if not nutrition:
            return None

        data = nutrition_in.model_dump(exclude_unset=True)
        for field, value in data.items():
            setattr(nutrition, field, value)

        db.commit()
        db.refresh(nutrition)
        return nutrition

    @staticmethod
    def delete(db: Session, nutrition_id: str) -> bool:
        nutrition = db.query(Nutrition).filter(Nutrition.id == nutrition_id).first()
        if not nutrition:
            return False
        db.delete(nutrition)
        db.commit()
        return True
