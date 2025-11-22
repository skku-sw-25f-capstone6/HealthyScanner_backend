# app/services/ai_scan_analysis_service.py
from pydantic import BaseModel, ValidationError
from typing import List, Optional, Dict, Any

# 이 클래스는 스키마 디렉토리에 넣어도 될 듯. 지금은 귀찮다...
class AiScanResult(BaseModel):
    decision: str                   # 'avoid' | 'caution' | 'ok'
    ai_total_score: int
    ai_allergy_report: Optional[str]
    ai_condition_report: Optional[str]
    ai_alter_report: Optional[str]
    ai_vegan_report: Optional[str]
    ai_total_report: Optional[str]
    caution_factors: Optional[List[str]]


class AiScanAnalysisService:
    def __init__(self, openai_client):
        self.client = openai_client


    def _build_prompt(
        self,
        user_profile: Dict[str, Any],
        product: Dict[str, Any],
        nutrition: Dict[str, Any] | None,
        ingredients: List[Dict[str, Any]] | None,
    ) -> str:

        # nutrition / ingredient optional-safe 처리
        nutrition_text = (
            f"{nutrition}"
            if nutrition is not None else "Nutrition info missing"
        )
        ingredient_text = (
            f"{ingredients}"
            if ingredients else "Ingredient list missing"
        )

        return f"""
You are a nutrition analysis assistant for the HealthyScanner app.

INPUT DATA = JSON

User Profile:
{user_profile}

Product Info:
{product}

Nutrition Info:
{nutrition_text}

Ingredients:
{ingredient_text}

---

TASK:
Analyze this product for this user.
Return STRICT JSON FORM in following format:

{{
    "decision": "avoid" | "caution" | "ok",
    "ai_total_score": int, 
    "ai_allergy_report": "string or null",
    "ai_condition_report": "string or null",
    "ai_alter_report": "string or null",
    "ai_vegan_report": "string or null",
    "ai_total_report": "string or null",
    "caution_factors": ["list", "of", "strings"] or null
}}

Rules:
1. Always return valid JSON.
2. decision must be exactly one of: "avoid", "caution", "ok".
3. ai_total_score must be 0~100.
4. If unsure, produce best guess based on nutrition & ingredients.
5. Do not include explanations outside of JSON.
        """.strip()


    async def analyze(
        self,
        user_profile: dict,
        product: dict,
        nutrition: dict | None,
        ingredients: list[dict] | None,
    ) -> AiScanResult:

        prompt = self._build_prompt(
            user_profile=user_profile,
            product=product,
            nutrition=nutrition,
            ingredients=ingredients,
        )

        try:
            resp = await self.client.chat.completions.create(
                model="gpt-4o-mini",      # 너가 쓰고 싶은 모델로 변경
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
                temperature=0.0,
            )
        except Exception as e:
            print("[AI ERROR] GPT request failed:", e)
            # 실패했을 때 fallback
            return AiScanResult(
                decision="caution",
                ai_total_score=50,
                ai_allergy_report=None,
                ai_condition_report=None,
                ai_alter_report=None,
                ai_vegan_report=None,
                ai_total_report="AI 분석 실패. 기본값 적용.",
                caution_factors=None,
            )

        # resp.choices[0].message.parsed → response_format=json_object 덕분에 Dict로 바로 옴
        data = resp.choices[0].message.parsed

        try:
            return AiScanResult(**data)
        except ValidationError as ve:
            print("[AI ERROR] Validation failed:", ve)
            # fallback
            return AiScanResult(
                decision="caution",
                ai_total_score=50,
                ai_allergy_report=None,
                ai_condition_report=None,
                ai_alter_report=None,
                ai_vegan_report=None,
                ai_total_report="AI 응답 포맷 오류. 기본값 적용.",
                caution_factors=None,
            )
