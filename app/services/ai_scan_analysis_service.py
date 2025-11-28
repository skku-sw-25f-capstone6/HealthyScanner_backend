# app/services/ai_scan_analysis_service.py
from pydantic import BaseModel, ValidationError
from typing import List, Optional, Dict, Any
from app.schemas.ai import AiScanResult
import json
from json import JSONDecodeError
from pydantic import ValidationError

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

        # nutrition
        if nutrition is None:
            nutrition_text = "Nutrition info missing"
        elif "raw_label" in nutrition:
            # 라벨만 있는 케이스
            nutrition_text = f"Raw nutrition label text:\n{nutrition['raw_label']}"
        else:
            # DB 정량 정보 케이스 (예시는 네 스키마에 맞게 조절)
            nutrition_text = (
                "Structured nutrition info:\n"
                f"- calories: {nutrition.get('calories')} kcal\n"
                f"- sugar: {nutrition.get('sugar_g')} g\n"
                f"- fat: {nutrition.get('fat_g')} g\n"
                f"- per saving grams: {nutrition.get('per_saving_grams')} g\n"
                f"- carbs: {nutrition.get('carbs_g')} g\n"
                f"- protein: {nutrition.get('protein_g')} g\n"
                f"- saturated fat: {nutrition.get('sat_fat_g')} g\n"
                f"- trans fat: {nutrition.get('trans_fat_g')} g\n"
                f"- sodium: {nutrition.get('sodium_mg')} mg\n"
                f"- choloesterol: {nutrition.get('choloesterol_mg')} mg\n"
            )

        if ingredients:
            # 예: 각 ingredient의 raw_ingredient만 뽑아서 줄바꿈으로 붙이기
            lines = [ing.get("raw_ingredient", "") for ing in ingredients]
            ingredient_text = "Ingredients:\n" + "\n".join(f"- {l}" for l in lines if l)
        else:
            ingredient_text = "Ingredient list missing"

        return f"""
너는 HealthyScanner 앱에서 쓰이는 "개인 맞춤 영양 분석" 도우미야.

입력은 모두 JSON 형태로 들어온다고 생각하면 돼:

User Profile:
{user_profile}

Product Info:
{product}

Nutrition Info:
{nutrition_text}

Ingredients:
{ingredient_text}

---

해야 할 일:
위 정보를 바탕으로, 이 사용자가 이 제품을 먹어도 되는지 판단해 줘.
알레르기, 질병(당뇨 등), 식습관(저당, 고단백 선호), 비건 여부 등을 전부 고려해서,
사용자에게 보여줄 분석 결과를 만들어줘.

반환 형식은 아래 JSON 형식만 사용해야 해:

{
    "decision": "avoid" | "caution" | "ok",
    "ai_total_score": int,
    "ai_allergy_report": "string or null",
    "ai_condition_report": "string or null",
    "ai_alter_report": "string or null",
    "ai_vegan_report": "string or null",
    "ai_total_report": "string or null",
    "caution_factors": ["list", "of", "strings"] or null,
    "ai_total_summary": "string"
}

Rules:
1. 항상 유효한 JSON만 반환해 줘.
2. decision 은 반드시 "avoid", "caution", "ok" 중 하나여야 해.
3. ai_total_score 는 0~100 사이의 정수여야 해.
4. 애매한 경우에도, 영양 정보 + 성분 정보를 보고 최선의 추론을 해줘.
5. JSON 바깥에는 아무 텍스트도 쓰지 마.
        """.strip()

    def _fallback(self, msg: str) -> AiScanResult:
        return AiScanResult(
            decision="caution",
            ai_total_score=50,
            ai_allergy_report=None,
            ai_condition_report=None,
            ai_alter_report=None,
            ai_vegan_report=None,
            ai_total_report=msg,
            caution_factors=None,
            ai_total_summary="Error, fallback"
        )

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
            return self._fallback("AI 분석 실패, 기본값 적용")

        try:
            content = resp.choices[0].message.content
            data = json.loads(content)
        # resp.choices[0].message.parsed → response_format=json_object 덕분에 Dict로 바로 옴
        # data = resp.choices[0].message.parsed
        except JSONDecodeError as je:
            print("[AI ERROR] JSON decode failed:", je)
            return self._fallback("AI 응답 JSON 파싱 실패. 기본값 적용.")

        try:
            return AiScanResult.model_validate(data)
        except ValidationError as ve:
            print("[AI ERROR] Validation failed:", ve)
            return self._fallback("AI 응답 포맷 오류. 기본값 적용.")
