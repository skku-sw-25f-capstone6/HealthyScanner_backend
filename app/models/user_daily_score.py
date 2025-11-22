# app/models/user_daily_score.py
from sqlalchemy import (
    Column,
    String,
    Integer,
    Date,
    DateTime,
    ForeignKey,
    SmallInteger,
)
from sqlalchemy.dialects.mysql import JSON as MySQLJSON
from sqlalchemy.sql import func
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime

from app.core.database import Base


class UserDailyScore(Base):
    __tablename__ = "user_daily_score"

    # 복합 PK: user_id + local_date
    user_id = Column(
        String(36),
        ForeignKey("user.id", ondelete="CASCADE"),
        primary_key=True,
    )
    local_date = Column(
        Date,
        primary_key=True,
    )

    score = Column(SmallInteger, nullable=False)  # 0~100 (DB는 TINYINT UNSIGNED)

    num_scans: Mapped[int | None] = mapped_column(Integer)
    max_severity = Column(String(16), nullable=True)  # 'none' | 'info' | 'warning' | 'danger'
    decision_counts = Column(MySQLJSON, nullable=True)

    formula_version = Column(Integer, nullable=False, default=1)
    dirty = Column(SmallInteger, nullable=False, default=0)
    last_computed_at = Column(DateTime(timezone=False), nullable=True)

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
    sync_state = Column(SmallInteger, nullable=False, default=1)
