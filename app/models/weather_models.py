from pydantic import BaseModel, validator, Field
from typing import Dict, List, Tuple, Optional
from datetime import date

class DailyData(BaseModel):
    time: List[str]
    temperature_2m_max: List[float]
    temperature_2m_min: List[float]

class WeatherRequestParams(BaseModel):
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    start_date: str = Field(...)
    end_date: str = Field(...)
    timezone: str = Field(default="auto")
    disable_bias_correction: str = Field(default="true")
    daily: List[str] = Field(default=["temperature_2m_max", "temperature_2m_min"])


class Coordinates(BaseModel):
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)


class WeatherResponse(BaseModel):
    city: str
    month: int
    min_temp_avg: float
    max_temp_avg: float
