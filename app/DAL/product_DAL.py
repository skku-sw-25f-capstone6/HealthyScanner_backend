# app/DAL/product_DAL.py
from typing import List, Optional
from uuid import uuid4

from sqlalchemy.orm import Session

from app.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate


class ProductDAL:
    @staticmethod
    def create(db: Session, product_in: ProductCreate) -> Product:
        product = Product(
            id=str(uuid4()),
            barcode=product_in.barcode,
            barcode_kind=product_in.barcode_kind,
            brand=product_in.brand,
            name=product_in.name,
            category=product_in.category,
            size_text=product_in.size_text,
            image_url=product_in.image_url,
            country=product_in.country,
            notes=product_in.notes,
            score=product_in.score,
        )
        db.add(product)
        db.commit()
        db.refresh(product)
        return product

    @staticmethod
    def get(db: Session, product_id: str) -> Optional[Product]:
        return db.query(Product).filter(Product.id == product_id).first()

    @staticmethod
    def get_by_barcode(db: Session, barcode: str) -> Optional[Product]:
        return db.query(Product).filter(Product.barcode == barcode).first()

    @staticmethod
    def list(
        db: Session,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Product]:
        return db.query(Product).offset(skip).limit(limit).all()

    @staticmethod
    def update(
        db: Session, product_id: str, product_in: ProductUpdate
    ) -> Optional[Product]:
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            return None

        data = product_in.model_dump(exclude_unset=True)
        for field, value in data.items():
            setattr(product, field, value)

        db.commit()
        db.refresh(product)
        return product

    @staticmethod
    def delete(db: Session, product_id: str) -> bool:
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            return False
        db.delete(product)
        db.commit()
        return True
