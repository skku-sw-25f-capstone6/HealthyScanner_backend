# app/core/ai_client.py
from openai import AsyncOpenAI
from functools import lru_cache

@lru_cache
def get_openai_client():
    return AsyncOpenAI(api_key="YOUR_OPENAI_KEY")
