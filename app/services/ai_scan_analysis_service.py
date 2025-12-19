# app/services/ai_scan_analysis_service.py
from pydantic import BaseModel, ValidationError
from typing import List, Optional, Dict, Any, Literal
from app.schemas.ai import AiScanResult
import json
from json import JSONDecodeError
from pydantic import ValidationError

AnalyzeType = Literal["barcode_image", "nutrition_label", "image"]

SCAN_RESULT_SCHEMA_HINT = """
{
    "decision": "avoid" | "caution" | "ok",
    "ai_total_score": int,
    "ai_allergy_brief": "string or null",
    "ai_allergy_report": "string or null",
    "ai_condition_brief": "string or null",
    "ai_condition_report": "string or null",
    "ai_alter_brief": "string or null",
    "ai_alter_report": "string or null",
    "ai_vegan_brief": "string or null",
    "ai_vegan_report": "string or null",
    "ai_total_report": "string or null",
    "product_name": "string or null",
    "product_nutrition": {string: value, ...} or null,
    "product_ingredients": ["string", ...] or null,
    "caution_factors": [
        {
            "key": "string",
            "level": "red" | "yellow" | "green"
        }
    ] or null
    "ai_total_summary": "string"
}
"""

CONDITIONS_SCHEMA_HINT = """
Output JSON with key "conditions" as an array of strings.
Allowed values:
- none
- hypertension
- liverDisease
- gout
- diabetes
- hyperlipidemia
- kidneyDisease
- thyroidDisease

Example:
{"conditions":["diabetes","hypertension"]}
"""

ALLERGIES_SCHEMA_HINT = """
Output JSON with key "allergies" as an array of strings.
Allowed values:
- none
- crustacean
- wheat
- shellfish
- shrimp
- dairy
- beef
- nut
- peach
- egg
- apple
- pineapple
- fish
- soy

Example:
{"allergies":["wheat","egg"]}
"""

DIET_SCHEMA_HINT = """
Output JSON with key "diet" as a string.
Allowed values:
- regular
- pescatarian
- lactoVegetarian
- ovoVegetarian
- vegan

Example:
{"diet":"pescatarian"}
"""

# 영문 코드를 한글 라벨로 변환하는 마스터 맵
ENG_TO_KOR = """{
    # Diet
    'regular': '일반식',
    'pescatarian': '생선 채식',
    'lactoVegetarian': '유제품 허용 채식',
    'ovoVegetarian': '달걀 허용 채식',
    'vegan': '채식',
    
    # Conditions
    'hypertension': '고혈압',
    'liverDisease': '간질환',
    'gout': '통풍',
    'diabetes': '당뇨병',
    'hyperlipidemia': '고지혈증',
    'kidneyDisease': '신장질환',
    'thyroidDisease': '갑상선질환',
    
    # Allergies
    'crustacean': '갑각류',
    'wheat': '밀',
    'shellfish': '조개류',
    'shrimp': '새우',
    'dairy': '유제품',
    'beef': '소고기',
    'nut': '견과류',
    'peanut': '땅콩',
    'peach': '복숭아',
    'egg': '계란',
    'apple': '사과',
    'pineapple': '파인애플',
    'fish': '생선',
    'soy': '대두(콩)',
}"""

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
너는 HealthyScanner 앱의 "개인 맞춤형 인공지능 영양사"야.
사용자의 프로필과 제품 정보를 바탕으로 섭취 적합성을 판단하고, 사진(OCR)에서 직접 추출한 데이터를 결과물에 포함하는 것이 네 핵심 임무야.

[입력 데이터 정보]
1. Analyze Type: {analyze_type}
2. User Profile: {user_profile}
3. Product Info: {product_text} (N/A일 수 있음)
4. Nutrition Info: {nutrition_text} (N/A일 수 있음)
5. Ingredients: {ingredient_text} (N/A일 수 있음)
6. Image Data: (함께 전달된 이미지 파일)

[수행 지침: 데이터 추출 및 보존]
- **데이터 발굴**: 제공된 텍스트 정보가 부족(N/A 또는 Missing)하더라도, 함께 제공된 이미지를 OCR로 분석하여 다음 필드를 반드시 채워야 해.
  - `product_name`: 이미지에서 확인되는 브랜드와 제품명을 정확히 추출해.
  - `product_nutrition`: 이미지의 영양성분표에서 읽은 구체적 수치(당류, 지방, 단백질 등)를 JSON 형태로 구성해.
  - `product_ingredients`: 이미지의 원재료명 섹션에서 확인되는 모든 성분을 리스트로 만들어.
- **추측 금지**: 이미지나 텍스트에 없는 구체적인 숫자나 성분명을 지어내지 마. 보이지 않는다면 null로 처리하되, 정성적인 분석(예: "당류가 높아 보임")으로 대체해.

[수행 지침: UI 최적화 분석]
- **Decision (판단)**: "avoid", "caution", "ok" 중 하나만 선택해. 정보가 부족하면 사용자의 안전을 위해 보수적으로(avoid/caution) 판단해.
- **Brief vs Report (요약과 상세)**:
  - `ai_*_brief`: 아주 짧고 강렬한 핵심 요약이야. 15자 내외로 반드시 작성해. (예: "당뇨 주의: 고당분", "땅콩 알레르기 위험")
  - `ai_*_report`: 그 판단의 근거를 사용자에게 친절하게 반드시 설명해줘.
- **Summary (전체 요약)**:
  - `ai_total_summary`: 전체 분석 결과를 한두 문장으로 요약해. 반드시 공백 포함 반드시 50자 이내로 작성해야 해.

[반환 형식 준수]
반드시 아래 JSON 구조만 반환하고, JSON 외의 텍스트는 포함하지 마.

{SCAN_RESULT_SCHEMA_HINT}

[값 범위 및 스키마 참조]
- ai_total_score: 0~100 (정수)
- caution_factors: 주의 요소가 있을 때만 {{"key": "이유", "level": "색상"}} 리스트로 구성.
- Conditions/Allergies/Diet 허용값:
{CONDITIONS_SCHEMA_HINT}
{ALLERGIES_SCHEMA_HINT}
{DIET_SCHEMA_HINT}

- Conditions/Allergies/Diet 허용값에 대해서 이걸 보고 한국말로 바꿔줘:
{ENG_TO_KOR}

[언어 및 톤앤매너]
- 모든 설명은 한국어로 작성해.
- 사용자에게 직접 말하듯이 친절하고 쉬운 용어를 사용해.
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
            ai_allergy_brief=None,
            ai_condition_brief=None,
            ai_alter_brief=None,
            ai_vegan_brief=None,
            caution_factors=None,
            ai_total_summary="Error, fallback",
            product_name=None,
            product_nutrition=None,
            product_ingredients=None,
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

        if (analyze_type == "image" or analyze_type == "nutrition_label") and image_data_url is not None:
            content.append(
                {
                    "type": "image_url",
                    "image_url": {"url": image_data_url, "detail": "high"},
                }
            )
        
        elif analyze_type == "image" and image_data_url is None:
            raise RuntimeError("Image data URL is required for analyze_type 'image'")

        try:
            resp = await self.client.chat.completions.create(
                model="gpt-5.2",      # 너가 쓰고 싶은 모델로 변경
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
