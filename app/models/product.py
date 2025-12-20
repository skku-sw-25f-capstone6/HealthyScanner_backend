# app/models/product.py
from sqlalchemy import Column, String, Integer, Text, DateTime
from sqlalchemy.sql import func

from app.core.database import Base
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime

class Product(Base):
    __tablename__ = "product"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, index=True)  # CHAR(36)
    barcode: Mapped[str] = mapped_column(String(32), unique=True, nullable=True)
    barcode_kind: Mapped[str] = mapped_column(String(16), nullable=True)       # 'EAN13' | ...

    brand: Mapped[str] = mapped_column(String(128), nullable=True)
    name: Mapped[str] = mapped_column(String(256), nullable=True)
    category: Mapped[str] = mapped_column(String(128), nullable=True)
    size_text: Mapped[str] = mapped_column(String(64), nullable=True)
    image_url: Mapped[str] = mapped_column(Text, nullable=True)
    country: Mapped[str] = mapped_column(String(64), nullable=True)
    notes: Mapped[str] = mapped_column(Text, nullable=True)

    score: Mapped[int] = mapped_column(Integer, nullable=True)

    allergens: Mapped[str] = mapped_column(Text, nullable=True)
    trace_allergens: Mapped[str] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
