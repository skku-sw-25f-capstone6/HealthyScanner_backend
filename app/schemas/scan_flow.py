# app/schemas/scan_flow.py
from pydantic import BaseModel

class ScanResultOut(BaseModel):
    scan_id: str
    product_id: str | None = None
    nutrition_id: str | None = None
    ingredient_id: str | None = None
