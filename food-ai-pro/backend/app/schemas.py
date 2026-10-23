from pydantic import BaseModel, Field
from typing import List, Optional, Dict

class Point2D(BaseModel):
    x: float
    y: float

class Macros(BaseModel):
    kcal: float
    protein: float
    carbs: float
    fat: float

class AnalyzedFoodItem(BaseModel):
    box: List[float]  # [x1, y1, x2, y2]
    polygon_mask: List[Point2D]
    food_name: str
    food_slug: str
    volume_cm3: float
    weight_g: float
    macros: Macros

class AnalysisResponse(BaseModel):
    items: List[AnalyzedFoodItem]
    totals: Macros

class RecalculateRequestItem(BaseModel):
    food_slug: str
    weight_g: float
    added_kcal: Optional[float] = 0.0
    added_fat: Optional[float] = 0.0

class RecalculateRequest(BaseModel):
    items: List[RecalculateRequestItem]

class BarcodeScanResponse(BaseModel):
    ean13: str
    name: str
    serving_size_g: float
    macros: Macros

class FoodSearchResponseItem(BaseModel):
    slug: str
    name_pt: str
    name_en: str
    category: str
    density_g_cm3: float
    kcal_100g: float
    protein_100g: float
    carbs_100g: float
    fat_100g: float
