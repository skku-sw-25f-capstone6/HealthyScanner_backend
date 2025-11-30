from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # --- DB ---
    DATABASE_URL: str | None = None

    # --- OpenAI ---
    OPENAI_API_KEY: str | None = None

    # --- Kakao ---
    KAKAO_CLIENT_ID: str | None = None
    KAKAO_CLIENT_SECRET: str | None = None
    KAKAO_REDIRECT_URI: str | None = None

    # --- 이미지 저장 설정 ---
    IMAGE_BASE_DIR: str = "/home/yujd0219/capstone/backend/static"
    IMAGE_BASE_URL: str = "/static"

    class Config:
        env_file = ".env"
        extra = "ignore"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()