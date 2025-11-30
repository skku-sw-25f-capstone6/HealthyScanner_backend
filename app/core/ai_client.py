# app/core/ai_client.py
from functools import lru_cache
from openai import AsyncOpenAI

from app.core.config import settings


@lru_cache
def get_openai_client() -> AsyncOpenAI:
    if not settings.OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY is not set in environment")
    return AsyncOpenAI(api_key=settings.OPENAI_API_KEY)