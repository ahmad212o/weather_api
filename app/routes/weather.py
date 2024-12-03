from fastapi import APIRouter, Query, HTTPException
from services.weather_service import get_monthly_weather_averages
from utils.metrics import track_metrics
from aiocache import cached

router = APIRouter()


@router.get("/monthly-profile")
@cached(ttl=3600)
@track_metrics("/weather/monthly-profile")
async def get_monthly_weather_profile(
    city: str = Query(..., description="City name"),
    month: int = Query(..., ge=1, le=12, description="Month number (1-12)"),
):
    try:
        profile = await get_monthly_weather_averages(city=city, month=month)
        return profile
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
