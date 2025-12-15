from typing import Optional
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.mysql import JSON as MySQLJSON
from sqlalchemy import String, Text, Integer, DateTime
from sqlalchemy.sql import func
from datetime import datetime
from app.core.database import Base


class User(Base):
    __tablename__ = "user"

    id: Mapped[str] = mapped_column(String(50), primary_key=True, index=True)
    name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    profile_image_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    habits: Mapped[Optional[list[str]]] = mapped_column(MySQLJSON, nullable=True)
    conditions: Mapped[Optional[list[str]]] = mapped_column(MySQLJSON, nullable=True)
    allergies: Mapped[Optional[list[str]]] = mapped_column(MySQLJSON, nullable=True)

    kakao_access_token: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    kakao_refresh_token: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    kakao_token_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    kakao_expires_in: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    kakao_refresh_expires_in: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    app_refresh_token: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True, index=True
    )



    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
    deleted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=False), nullable=True
    )
