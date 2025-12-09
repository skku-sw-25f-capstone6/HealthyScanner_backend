# app/routers/ingredient_router.py
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.DAL.ingredient_DAL import IngredientDAL
from app.schemas.ingredient import IngredientCreate, IngredientUpdate, IngredientOut, IngredientDetailOut, IngredientText

router = APIRouter(
    prefix="/v1/ingredients",
    tags=["ingredients"],
)


@router.post(
    "/",
    response_model=IngredientOut,
    status_code=status.HTTP_201_CREATED,
)
def create_ingredient(
    ing_in: IngredientCreate,
    db: Session = Depends(get_db),
):
    ingredient = IngredientDAL.create(db, ing_in)
    return ingredient


@router.get(
    "/{ingredient_id}",
    response_model=IngredientDetailOut,
)
def get_ingredient(
    ingredient_id: str,
    db: Session = Depends(get_db),
) -> IngredientDetailOut:
    ingredient = IngredientDAL.get(db, ingredient_id)
    if not ingredient:
        raise HTTPException(status_code=404, detail="Ingredient not found")
    return IngredientDetailOut(ingredient=IngredientText(text=ingredient.raw_ingredient))


@router.get(
    "/",
    response_model=List[IngredientOut],
)
def list_ingredients(
    skip: int = 0,
    limit: int = 100,
    product_id: Optional[str] = Query(default=None),
    db: Session = Depends(get_db),
):
    ingredients = IngredientDAL.list(
        db, skip=skip, limit=limit, product_id=product_id
    )
    return ingredients


@router.patch(
    "/{ingredient_id}",
    response_model=IngredientOut,
)
def update_ingredient(
    ingredient_id: str,
    ing_in: IngredientUpdate,
    db: Session = Depends(get_db),
):
    ingredient = IngredientDAL.update(db, ingredient_id, ing_in)
    if not ingredient:
        raise HTTPException(status_code=404, detail="Ingredient not found")
    return ingredient


@router.delete(
    "/{ingredient_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_ingredient(
    ingredient_id: str,
    db: Session = Depends(get_db),
):
    ok = IngredientDAL.delete(db, ingredient_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Ingredient not found")
    return
