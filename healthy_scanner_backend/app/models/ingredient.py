# app/models/ingredient.py
from sqlalchemy import (
    Column,
    String,
    Text,
    Integer,
    DateTime,
    ForeignKey,
)
from sqlalchemy.sql import func

from app.core.database import Base


class Ingredient(Base):
    __tablename__ = "ingredient"

    id = Column(String(36), primary_key=True, index=True)
    product_id = Column(
        String(36),
        ForeignKey("product.id", ondelete="CASCADE"),
        nullable=False,
    )

    raw_ingredient = Column(Text, nullable=False)
    norm_text = Column(Text, nullable=True)
    allergen_tags = Column(Text, nullable=True)  # JSON 문자열

    order_index = Column(Integer, nullable=False, default=0)

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
