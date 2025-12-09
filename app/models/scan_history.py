# app/models/scan_history.py
from sqlalchemy import (
    Column,
    String,
    Text,
    Integer,
    DateTime,
    ForeignKey,
)
from sqlalchemy.dialects.mysql import JSON as MySQLJSON
from sqlalchemy.sql import func
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from typing import Any
from app.core.database import Base


class ScanHistory(Base):
    __tablename__ = "scan_history"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, index=True)

    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("user.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    product_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("product.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    
    display_name: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    display_category: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    image_url: Mapped[str] = mapped_column(Text, nullable=True)

    scanned_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), nullable=False)

    # ENUM('avoid','caution','ok') 를 문자열로 매핑
    decision: Mapped[str] = mapped_column(String(16), nullable=True)

    summary: Mapped[str] = mapped_column(String(255), nullable=True)
    ai_total_score: Mapped[int] = mapped_column(Integer, nullable=True)  # TINYINT UNSIGNED(0~255)

    conditions: Mapped[list[str]] = mapped_column(MySQLJSON, nullable=True)
    allergies: Mapped[list[str]] = mapped_column(MySQLJSON, nullable=True)
    habits: Mapped[list[str]] = mapped_column(MySQLJSON, nullable=True)

    ai_allergy_report: Mapped[str] = mapped_column(Text, nullable=True)
    ai_condition_report: Mapped[str] = mapped_column(Text, nullable=True)
    ai_alter_report: Mapped[str] = mapped_column(Text, nullable=True)
    ai_vegan_report: Mapped[str] = mapped_column(Text, nullable=True)
    ai_total_report: Mapped[str] = mapped_column(Text, nullable=True)

    caution_factors: Mapped[list[dict[str, str]] | None] = mapped_column(MySQLJSON, nullable=True)

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
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime)
