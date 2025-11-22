# app/core/db.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os
from dotenv import load_dotenv

load_dotenv()

# ⚠️ .env 파일에서 DB 설정 읽어오기
MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
MYSQL_HOST = os.getenv("MYSQL_HOST")
MYSQL_PORT = os.getenv("MYSQL_PORT")
MYSQL_DB = os.getenv("MYSQL_DB")

# MySQL 접속 URL 구성
DATABASE_URL = (
    f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}"
    f"@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}"
    "?charset=utf8mb4"
)

# SQLAlchemy 엔진 생성
engine = create_engine(
    DATABASE_URL,
    echo=False,
    pool_pre_ping=True,     # 연결 살펴보고 끊어졌으면 재연결
)

# 세션 팩토리
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base 클래스 (모든 모델이 여기를 상속)
Base = declarative_base()


# FastAPI 의존성
def get_db():
    """
    요청마다 DB 세션을 열고,
    요청이 끝나면 자동으로 닫아줌.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
