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
    caution_factors: Optional[List[str]]
    ai_total_summary: str