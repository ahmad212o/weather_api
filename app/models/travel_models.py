from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Dict, Optional


MIN_TEMPERATURE = -100
MAX_TEMPERATURE = 100


class BestMonthResponse(BaseModel):
    city: str
    best_month: int = Field(..., ge=1, le=12)
    min_temp_diff: float
    max_temp_diff: float
    overall_diff: float


class CityComparison(BaseModel):
    city: str
    month: int
    min_temp_avg: float
    max_temp_avg: float


class ComparisonResponse(BaseModel):
    comparisons: List[CityComparison]
