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


class Nutrition(Base):
    __tablename__ = "nutrition"
    __table_args__ = (
        UniqueConstraint("product_id", "label_version", name="uq_nutrition_product_label"),
    )

    id = Column(String(36), primary_key=True, index=True)
    product_id = Column(String(36), ForeignKey("product.id", ondelete="CASCADE"), nullable=False)

    per_serving_grams = Column(Float, nullable=True)
    calories = Column(Float, nullable=True)
    carbs_g = Column(Float, nullable=True)
    sugar_g = Column(Float, nullable=True)
    protein_g = Column(Float, nullable=True)
    fat_g = Column(Float, nullable=True)
    sat_fat_g = Column(Float, nullable=True)
    trans_fat_g = Column(Float, nullable=True)
    sodium_mg = Column(Float, nullable=True)
    cholesterol_mg = Column(Float, nullable=True)

    label_version = Column(Integer, nullable=False, default=1)

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
