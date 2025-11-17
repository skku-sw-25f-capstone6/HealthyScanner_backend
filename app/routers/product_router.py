# app/routers/product_router.py
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.DAL.product_DAL import ProductDAL
from app.schemas.product import ProductCreate, ProductUpdate, ProductOut, ProductDetailOut
from app.services.product_service import ProductService

router = APIRouter(
    prefix="/v1/products",
    tags=["products"],
)


@router.post(
    "/",
    response_model=ProductOut,
    status_code=status.HTTP_201_CREATED,
)
def create_product(
    product_in: ProductCreate,
    db: Session = Depends(get_db),
):
    product = ProductDAL.create(db, product_in)
    return product


@router.get(
    "/{product_id}",
    response_model=ProductOut,
)
def get_product(
    product_id: str,
    db: Session = Depends(get_db),
):
    product = ProductDAL.get(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.get(
    "/",
    response_model=List[ProductOut],
)
def list_products(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    products = ProductDAL.list(db, skip=skip, limit=limit)
    return products


@router.patch(
    "/{product_id}",
    response_model=ProductOut,
)
def update_product(
    product_id: str,
    product_in: ProductUpdate,
    db: Session = Depends(get_db),
):
    product = ProductDAL.update(db, product_id, product_in)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.delete(
    "/{product_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_product(
    product_id: str,
    db: Session = Depends(get_db),
):
    ok = ProductDAL.delete(db, product_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Product not found")
    return


@router.get(
    "/{product_id}/detail",
    response_model=ProductDetailOut,
)
def get_product_detail(
    product_id: str,
    with_nutrition: bool = Query(True),
    with_ingredient: bool = Query(True),
    db: Session = Depends(get_db),
):
    service = ProductService(db)
    result = service.get_product_detail(
        product_id=product_id,
        with_nutrition=with_nutrition,
        with_ingredient=with_ingredient,
    )

    if result is None:
        raise HTTPException(status_code=404, detail="Product not found")

    return result