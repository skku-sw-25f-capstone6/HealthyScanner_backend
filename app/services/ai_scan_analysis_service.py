# app/services/ai_scan_analysis_service.py
from pydantic import BaseModel, ValidationError
from typing import List, Optional, Dict, Any, Literal
from app.schemas.ai import AiScanResult
import json
from json import JSONDecodeError
from pydantic import ValidationError
from app.services.scan_flow_service import AnalyzeType

class AiScanAnalysisService:
    def __init__(self, openai_client):
        self.client = openai_client


    def _build_prompt(
        self,
        user_profile: Dict[str, Any],
        product: Dict[str, Any] | None,
        nutrition: Dict[str, Any] | None,
        ingredients: List[Dict[str, Any]] | None,
        analyze_type: AnalyzeType,
    ) -> str:
        # user_profile: 현재 유저 정보(딕셔너리)
        # product: 현재 상품 정보(딕셔너리)

        # 얘네 둘은 애초에 함수가 호출될 때부터 기본값은 일단 갖고 있다고 보는 거임

        # 바코드와 이미지 분석의 경우 없는 정보가 없음
        if analyze_type == "barcode_image":
            if nutrition is None:
                nutrition_text = "Nutrition info missing"
            
            else:
                nutrition_text = (
                    "Structured nutrition info:\n"
                    f"- calories: {nutrition.get('calories')} kcal\n"
                    f"- sugar: {nutrition.get('sugar_g')} g\n"
                    f"- fat: {nutrition.get('fat_g')} g\n"
                    f"- per serving grams: {nutrition.get('per_serving_grams')} g\n"
                    f"- carbs: {nutrition.get('carbs_g')} g\n"
                    f"- protein: {nutrition.get('protein_g')} g\n"
                    f"- saturated fat: {nutrition.get('sat_fat_g')} g\n"
                    f"- trans fat: {nutrition.get('trans_fat_g')} g\n"
                    f"- sodium: {nutrition.get('sodium_mg')} mg\n"
                    f"- cholesterol: {nutrition.get('cholesterol_mg')} mg\n"
                )

        # 영양 라벨 텍스트만 있는 경우는 상품 이름, 재료 정보 없음
        elif analyze_type == "nutrition_label":
            if nutrition is not None and "raw_label" in nutrition:
                nutrition_text = f"Raw nutrition label text:\n{nutrition['raw_label']}"
            else:
                nutrition_text = "Nutrition info missing"            

        elif analyze_type == "image":
            nutrition_text = "No nutrition info provided"
        
        else:
            raise ValueError(f"Unknown analyze_type: {analyze_type}")


        if ingredients:
            lines = [ing.get("raw_ingredient", "") for ing in ingredients]
            ingredient_text = "Ingredients:\n" + "\n".join(f"- {l}" for l in lines if l)
        else:
            ingredient_text = "Ingredient list missing"


        if product:
            product_text = f"{product}"
        else:
            product_text = "Product info missing"
        return f"""
너는 HealthyScanner 앱에서 쓰이는 "개인 맞춤 영양 분석" 도우미야.

analyze_type 값에 따라 입력 형태가 달라져:

analyze_type이 "barcode_image" 또는 "nutrition_label"일 때, 입력은 JSON 문자열이라고 생각하면 돼:

analyze_type: {analyze_type}

User Profile:
{user_profile}

Product Info:
{product_text}

Nutrition Info:
{nutrition_text}

Ingredients:
{ingredient_text}

analyze_type이 "image"일 때는, 사용자 정보 + 이미지가 함께 주어져:

analyze_type: {analyze_type}

User Profile:
{user_profile}

(이미지는 별도로 함께 전달됨)


해야 할 일:
- 위 정보를 바탕으로, 이 사용자가 이 제품을 먹어도 되는지 판단해 줘.
- 알레르기, 질병(예: 당뇨), 식습관(저당, 고단백 선호), 비건 여부 등을 모두 고려해서,
  사용자에게 보여줄 분석 결과를 만들어줘.
- analyze_type에 따라 사용할 수 있는 정보가 다르다는 점을 인지하고 동작해야 해:
  - "barcode_image", "nutrition_label": user_profile + product_text + nutrition_text + ingredient_text를 최우선으로 사용해.
  - "image": user_profile + 이미지에서 직접 보이는 정보(제품명, 제로/무가당/고단백 문구, 비건 마크 등)만 사용해.
    보이지 않는 영양 성분 수치나 성분명은 절대 지어내지 마.


반환 형식은 아래 JSON 형식만 사용해야 해 (필드 이름, 구조를 변경하면 안 됨):

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


추가 규칙:

1. 항상 유효한 JSON만 반환해 줘.
   - JSON 바깥에는 어떤 텍스트도 쓰지 마.

2. decision은 반드시 "avoid", "caution", "ok" 중 하나여야 해.
   - 정보가 부족해서 애매하면, 사용자의 안전을 위해 더 보수적인 쪽("avoid" 또는 "caution")을 선택해.

3. ai_total_score는 0~100 사이의 정수여야 해.
   - 0~33: 나쁨, 34~66: 보통, 67~100: 좋음 정도 기준으로 생각해.

4. "barcode_image", "nutrition_label"에서는 영양 정보 + 성분 정보를 최우선으로 보고 최선의 추론을 해줘.
   - 구체적인 숫자(예: 당류 23g)를 모르면 절대 임의로 만들지 마.
   - 대신, "당류가 많아 보임", "포화지방이 높은 편"처럼 정성적인 표현만 사용해.

5. "image" analyze_type에서는 이미지에서 눈으로 직접 확인할 수 있는 정보만 사용해.
   - 보이지 않는 영양 성분, 세부 함량, 성분명은 절대 추측하지 마.
   - 대신 정보가 부족하면 "정확한 영양 성분을 알 수 없어 보수적으로 판단함"이라고 설명해.

6. missing 정보(user_profile, product_text, nutrition_text, ingredient_text 중 일부가 비어 있거나 null)인 경우:
   - 그 정보는 "모른다"로 간주하고 사용하지 마.
   - 모르는 정보를 채우기 위해 새로운 사실을 만들어내지 마.
   - 단, 그 상태에서라도 사용자의 안전을 위해 최선의 보수적 판단을 내려야 해.

7. 모든 설명(ai_*_report, ai_total_summary)은 한국어로, 사용자에게 직접 말하듯이 쉽게 써 줘.
   - ai_total_summary는 한두 문장짜리 짧은 요약으로 써 줘.
   - ai_*_report 값이 정말로 할 말이 없으면 null을 넣어도 돼.

8. caution_factors는, 주의해야 할 요소(예: "당류가 높음", "포화지방이 많음", "땅콩 알레르기 위험")가 있을 때만 리스트로 채우고,
   없으면 null로 해.
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
        product: dict | None,
        nutrition: dict | None,
        ingredients: list[dict] | None,
        analyze_type: AnalyzeType,
        image_data_url: str | None,
    ) -> AiScanResult:

        prompt = self._build_prompt(
            user_profile=user_profile,
            product=product,
            nutrition=nutrition,
            ingredients=ingredients,
            analyze_type = analyze_type,
        )

        content: list[dict] = [{"type": "text", "text": prompt}]

        if analyze_type == "image" and image_data_url is not None:
            content.append(
                {
                    "type": "image_url",
                    "image_url": {"url": image_data_url},
                }
            )
        
        elif analyze_type == "image" and image_data_url is None:
            raise RuntimeError("Image data URL is required for analyze_type 'image'")

        try:
            resp = await self.client.chat.completions.create(
                model="gpt-4o-mini",      # 너가 쓰고 싶은 모델로 변경
                messages=[
                    {
                        "role": "user", 
                        "content": content,
                    }
                ],
                response_format={"type": "json_object"},
                temperature=0.0,
            )
        except Exception as e:
            print("[AI ERROR] GPT request failed:", e)
            # 실패했을 때 fallback
            return self._fallback("AI 분석 실패, 기본값 적용")

        try:
            result = resp.choices[0].message.content
            data = json.loads(result)
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
