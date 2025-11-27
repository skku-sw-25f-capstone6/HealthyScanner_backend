from sqlalchemy import Column, String, Text, Integer, DateTime
from sqlalchemy.dialects.mysql import JSON as MySQLJSON
from sqlalchemy.sql import func

from app.core.database import Base


class User(Base):
    __tablename__ = "user"

    # 기본 정보
    id = Column(String(50), primary_key=True, index=True)  
    name = Column(String(255), nullable=True)
    profile_image_url = Column(String(500), nullable=True)

    habits = Column(MySQLJSON, nullable=True)
    conditions = Column(MySQLJSON, nullable=True)
    allergies = Column(MySQLJSON, nullable=True)

    # 🔥 카카오 토큰 관련 필드 (신규 추가)
    access_token = Column(Text, nullable=True)
    refresh_token = Column(Text, nullable=True)
    token_type = Column(String(50), nullable=True)
    expires_in = Column(Integer, nullable=True)              # access_token 만료
    refresh_expires_in = Column(Integer, nullable=True)      # refresh_token 만료


    created_at = Column(DateTime(timezone=False), nullable=False, server_default=func.now())
    updated_at = Column(
        DateTime(timezone=False),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
    deleted_at = Column(DateTime(timezone=False), nullable=True)
