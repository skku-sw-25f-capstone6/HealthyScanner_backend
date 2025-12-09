# app/models/nutrition.py
from sqlalchemy import (
    Column,
    String,
    Float,
    Integer,
    DateTime,
    ForeignKey,
    UniqueConstraint,
)
from sqlalchemy.sql import func

from app.core.database import Base
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime

class Nutrition(Base):
    __tablename__ = "nutrition"
    __table_args__ = (
        UniqueConstraint("product_id", "label_version", name="uq_nutrition_product_label"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, index=True)
    product_id: Mapped[str] = mapped_column(String(36), ForeignKey("product.id", ondelete="CASCADE"), nullable=False)

    per_serving_grams: Mapped[float] = mapped_column(Float, nullable=True)
    calories: Mapped[float] = mapped_column(Float, nullable=True)
    carbs_g: Mapped[float] = mapped_column(Float, nullable=True)
    sugar_g: Mapped[float] = mapped_column(Float, nullable=True)
    protein_g: Mapped[float] = mapped_column(Float, nullable=True)
    fat_g: Mapped[float] = mapped_column(Float, nullable=True)
    sat_fat_g: Mapped[float] = mapped_column(Float, nullable=True)
    trans_fat_g: Mapped[float] = mapped_column(Float, nullable=True)
    sodium_mg: Mapped[float] = mapped_column(Float, nullable=True)
    cholesterol_mg: Mapped[float] = mapped_column(Float, nullable=True)

    label_version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

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
