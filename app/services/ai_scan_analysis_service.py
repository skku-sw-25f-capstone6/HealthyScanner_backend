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
    "ai_alter_brief": "null",
    "ai_alter_report": "null",
    "ai_vegan_brief": "string or null",
    "ai_vegan_report": "string or null",
    "ai_total_report": "string or null",
    "product_name": "string or null",
    "product_nutrition": {string: value, ...} or null,
    "product_ingredient": "string or null",
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

NUTRITION_MAP = """
per_serving_grams: 총 내용량 또는 1회 제공량
calories: 열량
carbohydrate: 탄수화물
sugars: 당류
protein: 단백질
fat: 지방
saturated_fat: 포화지방
trans_fat: 트랜스지방
sodium: 나트륨
cholesterol: 콜레스테롤
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

        user_allergies = user_profile.get("allergies", [])
        user_conditions = user_profile.get("conditions", [])

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
# ROLE
당신은 'HealthyScanner' 앱의 전문 AI 영양사입니다. 사용자의 건강 프로필과 식품 정보를 대조하여 안전성을 분석하세요.

# INPUT DATA
1. Analyze Type: {analyze_type}
2. User Profile: {{ "allergies": {user_allergies}, "conditions": {user_conditions}, "diet": "{user_profile.get('habits')}" }}
3. Provided Context:
   - Product Info: {product if product else "N/A"}
   - Nutrition Info: {nutrition if nutrition else "N/A"}
   - Ingredients List: {ingredients if ingredients else "N/A"}
4. Image: (제공된 이미지 참고)

# ANALYSIS STEPS (Chain of Thought)
1. **OCR Data Mining**: 이미지에서 제품명, 영양성분(수치 및 단위), 원재료명을 누락 없이 추출하세요. 텍스트 정보보다 이미지에서 직접 읽은 정보를 최우선합니다.
2. **Safety Check**: 
   - 사용자의 알레르기({user_allergies})가 원재료명에 직접 포함되었는지 확인하세요.
   - "이 제품은 ~을 사용한 제조시설에서 제조하고 있습니다" 같은 혼입 가능성 문구를 찾으세요.
3. **Decision Logic**:
   - **Avoid (Red)**: 알레르기 성분 직접 포함.
   - **Caution (Yellow)**: 제조시설 공유 문구 발견, 혹은 사용자의 질환({user_conditions})에 부적합한 성분(예: 당뇨인데 고당류) 발견 시.
   - **OK (Green)**: 위 위험 요소가 전혀 없을 때.

# RESPONSE CONSTRAINTS (엄격 준수)
- **언어**: 한국어 (친절한 '~해요'체)
- **글자 수**: 
  - `brief`: 공백 포함 15자 이내 (핵심 요약)
  - `report`: 100자 이내 (판단 근거 설명)
  - `ai_total_summary`: 50자 이내 (전체 요약)
- **Caution Factors**: `caution_factors`의 `key` 값은 반드시 **한국어**로 출력하세요. {ENG_TO_KOR}를 참고하여 변환하되(예: 'wheat' -> '밀'), 매핑에 없는 경우 한국어로 번역하여 적으세요.
- **영양성분 Key**: {NUTRITION_MAP}를 참고하여 영어로 변환하세요. 값은 단위(g, mg 등)를 반드시 포함하세요.
- **알레르기 필터링**: 사용자 프로필({user_allergies})에 없는 성분은 제품에 포함되어 있더라도 알레르기 위험으로 언급하지 마세요.

# OUTPUT FORMAT
반드시 아래 JSON 구조만 반환하세요.
{SCAN_RESULT_SCHEMA_HINT}

# REFERENCE (Mapping Guide)
- 질환/알레르기 한글화: {ENG_TO_KOR}
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
            product_ingredient=None,
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
