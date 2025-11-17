# app/routers/nutrition_router.py
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.DAL.nutrition_DAL import NutritionDAL
from app.schemas.nutrition import NutritionCreate, NutritionUpdate, NutritionOut

router = APIRouter(
    prefix="/v1/nutrition",
    tags=["nutrition"],
)


@router.post(
    "/",
    response_model=NutritionOut,
    status_code=status.HTTP_201_CREATED,
)
def create_nutrition(
    nutrition_in: NutritionCreate,
    db: Session = Depends(get_db),
):
    nutrition = NutritionDAL.create(db, nutrition_in)
    return nutrition


@router.get(
    "/{nutrition_id}",
    response_model=NutritionOut,
)
def get_nutrition(
    nutrition_id: str,
    db: Session = Depends(get_db),
):
    nutrition = NutritionDAL.get(db, nutrition_id)
    if not nutrition:
        raise HTTPException(status_code=404, detail="Nutrition not found")
    return nutrition


@router.get(
    "/",
    response_model=List[NutritionOut],
)
def list_nutrition(
    skip: int = 0,
    limit: int = 100,
    product_id: Optional[str] = Query(default=None),
    db: Session = Depends(get_db),
):
    nutritions = NutritionDAL.list(
        db, skip=skip, limit=limit, product_id=product_id
    )
    return nutritions


@router.patch(
    "/{nutrition_id}",
    response_model=NutritionOut,
)
def update_nutrition(
    nutrition_id: str,
    nutrition_in: NutritionUpdate,
    db: Session = Depends(get_db),
):
    nutrition = NutritionDAL.update(db, nutrition_id, nutrition_in)
    if not nutrition:
        raise HTTPException(status_code=404, detail="Nutrition not found")
    return nutrition


@router.delete(
    "/{nutrition_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_nutrition(
    nutrition_id: str,
    db: Session = Depends(get_db),
):
    ok = NutritionDAL.delete(db, nutrition_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Nutrition not found")
    return
