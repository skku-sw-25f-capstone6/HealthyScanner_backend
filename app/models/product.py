# app/models/product.py
from sqlalchemy import Column, String, Integer, Text, DateTime
from sqlalchemy.sql import func

from app.core.database import Base


class Product(Base):
    __tablename__ = "product"

    id = Column(String(36), primary_key=True, index=True)  # CHAR(36)
    barcode = Column(String(32), unique=True, nullable=True)
    barcode_kind = Column(String(16), nullable=True)       # 'EAN13' | ...

    brand = Column(String(128), nullable=True)
    name = Column(String(256), nullable=True)
    category = Column(String(128), nullable=True)
    size_text = Column(String(64), nullable=True)
    image_url = Column(Text, nullable=True)
    country = Column(String(64), nullable=True)
    notes = Column(Text, nullable=True)

    score = Column(Integer, nullable=True)

    created_at = Column(
        DateTime(timezone=False),
        nullable=False,
        server_default=func.now(),
    )
    updated_at = Column(
        DateTime(timezone=False),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
