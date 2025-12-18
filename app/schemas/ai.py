from pydantic import BaseModel, ConfigDict
from typing import List, Optional, Dict, Any

class AiScanResult(BaseModel):
    decision: str                   # 'avoid' | 'caution' | 'ok'
    ai_total_score: int
    ai_allergy_report: Optional[str]
    ai_condition_report: Optional[str]
    ai_alter_report: Optional[str]
    ai_vegan_report: Optional[str]
    ai_total_report: Optional[str]
    ai_condition_brief: Optional[str]
    ai_alter_brief: Optional[str]
    ai_vegan_brief: Optional[str]
    ai_allergy_brief: Optional[str]
    caution_factors: Optional[List[Dict[str, str]]]
    ai_total_summary: str

    product_name: Optional[str]
    product_nutrition: Optional[Dict[str, Any]]
    product_ingredients: Optional[List[str]]