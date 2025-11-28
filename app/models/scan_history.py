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

from app.core.database import Base


class ScanHistory(Base):
    __tablename__ = "scan_history"

    id = Column(String(36), primary_key=True, index=True)

    user_id = Column(
        String(36),
        ForeignKey("user.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    product_id = Column(
        String(36),
        ForeignKey("product.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )

    scanned_at = Column(DateTime(timezone=False), nullable=False)

    # ENUM('avoid','caution','ok') 를 문자열로 매핑
    decision = Column(String(16), nullable=True)

    summary = Column(String(255), nullable=True)
    ai_total_score = Column(Integer, nullable=True)  # TINYINT UNSIGNED(0~255)

    conditions = Column(MySQLJSON, nullable=True)
    allergies = Column(MySQLJSON, nullable=True)
    habits = Column(MySQLJSON, nullable=True)

    ai_allergy_report = Column(Text, nullable=True)
    ai_condition_report = Column(Text, nullable=True)
    ai_alter_report = Column(Text, nullable=True)
    ai_vegan_report = Column(Text, nullable=True)
    ai_total_report = Column(Text, nullable=True)

    caution_factors = Column(MySQLJSON, nullable=True)

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
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime)
