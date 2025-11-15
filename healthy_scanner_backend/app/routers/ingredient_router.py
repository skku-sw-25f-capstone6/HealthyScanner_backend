# app/routers/ingredient_router.py
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dal.ingredient_dal import IngredientDal
from app.schemas.ingredient import IngredientCreate, IngredientUpdate, IngredientOut

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
    ingredient = IngredientDal.create(db, ing_in)
    return ingredient


@router.get(
    "/{ingredient_id}",
    response_model=IngredientOut,
)
def get_ingredient(
    ingredient_id: str,
    db: Session = Depends(get_db),
):
    ingredient = IngredientDal.get(db, ingredient_id)
    if not ingredient:
        raise HTTPException(status_code=404, detail="Ingredient not found")
    return ingredient


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
    ingredients = IngredientDal.list(
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
    ingredient = IngredientDal.update(db, ingredient_id, ing_in)
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
    ok = IngredientDal.delete(db, ingredient_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Ingredient not found")
    return
