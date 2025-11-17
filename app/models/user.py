from sqlalchemy import Column, String, Text, DateTime
from sqlalchemy.dialects.mysql import JSON as MySQLJSON
from sqlalchemy.sql import func

from app.core.database import Base

class User(Base):
    __tablename__ = "user"

    id = Column(String(50), primary_key=True, index=True)  # UUID v4
    name = Column(String(255), nullable=True)

    habits = Column(MySQLJSON, nullable=True)
    conditions = Column(MySQLJSON, nullable=True)
    allergies = Column(MySQLJSON, nullable=True)

    # 토큰 관련
    refresh_token_hash = Column(Text, nullable=True)
    refresh_token_issued_at = Column(Text, nullable=True)
    refresh_token_expires_at = Column(Text, nullable=True)
    refresh_token_revoked_at = Column(Text, nullable=True)

    # 프로필 이미지
    profile_image_url = Column(String(500), nullable=True)

    created_at = Column(DateTime(timezone=False), nullable=False, server_default=func.now())
    updated_at = Column(
        DateTime(timezone=False),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
    deleted_at = Column(DateTime(timezone=False), nullable=True)
