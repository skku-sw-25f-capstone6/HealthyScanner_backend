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
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime

class Ingredient(Base):
    __tablename__ = "ingredient"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, index=True)
    product_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("product.id", ondelete="CASCADE"),
        nullable=False,
    )

    raw_ingredient: Mapped[str] = mapped_column(Text, nullable=False)
    norm_text: Mapped[str] = mapped_column(Text, nullable=True)
    allergen_tags: Mapped[str] = mapped_column(Text, nullable=True)  # JSON 문자열

    order_index: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

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
